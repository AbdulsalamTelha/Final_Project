import json
import random
import string
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
from admin_app.models import User
from .models import ChatRoom, Message
from django.db.models import Q
from django.contrib import messages


@login_required
def chat_list(request):
    user = request.user

    # Filter chat rooms into private and group chats
    private_chats = user.chat_rooms.filter(type='private')
    group_chats = user.chat_rooms.filter(type='group')
    all_users = User.objects.exclude(id=request.user.id)

    # Pass both private and group chats to the template
    return render(request, 'chat_app/chat_list.html', {
        'private_chats': private_chats,
        'group_chats': group_chats,
        'all_users': all_users,
    })
    
    
@login_required
def chat_room(request, room_name):
    """
    Render the chat room interface.
    If the room doesn't exist, it will be created when the first message is sent.
    """
    # Fetch the chat room if it exists
    room = ChatRoom.objects.filter(name=room_name).first()

    # Fetch all messages in the room, ordered by timestamp
    messages = room.messages.all().order_by('timestamp') if room else []

    # Fetch all users except the current user for the user list
    all_users = User.objects.exclude(id=request.user.id)

    # Pass the room, messages, and all_users to the template
    context = {
        'room': room,
        'messages': messages,
        'all_users': all_users,
        'room_name': room_name,  # Pass the room name to the template
    }
    return render(request, 'chat_app/chat_room.html', context)

@login_required
def start_private_chat(request, user_id):
    # Get the other user
    other_user = get_object_or_404(User, id=user_id)
    
    # Ensure consistent ordering of user IDs for the room name
    user_ids = sorted([request.user.id, other_user.id])  # Sort the IDs
    room_name = f"private_{user_ids[0]}_{user_ids[1]}"  # Use sorted IDs to name the room
    
    # Check if a private chat room already exists
    chat_room, created = ChatRoom.objects.get_or_create(
        name=room_name,
        defaults={'type': 'private'}  # Ensure it's marked as a private chat
    )
    
    # Add both users to the chat room
    chat_room.members.add(request.user, other_user)
    
    # Redirect to the chat room
    return redirect('chat_room', room_name=room_name)

@csrf_exempt
def upload_file(request):
    """
    Handle file uploads and return the file URL as a JSON response.
    """
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        # Validate file type and size
        allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
        max_size = 10 * 1024 * 1024  # 10 MB

        if uploaded_file.content_type not in allowed_types:
            return JsonResponse({'error': 'File type not allowed'}, status=400)
        if uploaded_file.size > max_size:
            return JsonResponse({'error': 'File size exceeds limit'}, status=400)

        # Save the file to the uploads directory
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Generate the file URL
        file_url = request.build_absolute_uri(settings.MEDIA_URL + 'uploads/' + uploaded_file.name)
        return JsonResponse({'url': file_url})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def send_message(request):
    """
    Handle sending a message and create the chat room if it doesn't exist.
    """
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        content = request.POST.get('content')
        file_url = request.POST.get('file_url', None)
        file_name = request.POST.get('file_name', None)
        file_size = request.POST.get('file_size', None)

        # Get or create the chat room
        room, created = ChatRoom.objects.get_or_create(
            name=room_name,
            defaults={'type': 'private'}
        )

        # Add the current user and the other user to the chat room
        if created:
            user_ids = room_name.replace('private_', '').split('_')
            user1 = User.objects.get(id=int(user_ids[0]))
            user2 = User.objects.get(id=int(user_ids[1]))
            room.members.add(user1, user2)

        # Create the message
        message = Message.objects.create(
            room=room,
            sender=request.user,
            content=content,
            content_type='file' if file_url else 'text',
            file_name=file_name,
            file_size=file_size,
        )

        # Return a success response
        return JsonResponse({
            'status': 'success',
            'message': 'Message sent successfully',
            'message_id': message.id,
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


def instructor_groups(request):
    if request.user.role != 'INSTRUCTOR':
        messages.error(request, "Only instructors can access this page.")
        return redirect('home')

    groups = ChatRoom.objects.filter(created_by=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_group':
            name = request.POST.get('name')
            gender = request.POST.get('gender')
            student_ids = request.POST.getlist('student_ids')

            if not name:
                messages.error(request, "Please enter a group name.")
                return redirect('instructor_groups')

            if gender not in ['male', 'female']:
                messages.error(request, "Please select a gender type (Male Only or Female Only).")
                return redirect('instructor_groups')

            try:
                # استخدم الدالة create_group بدلاً من الإنشاء اليدوي
                group = ChatRoom()
                group.create_group(
                    instructor=request.user,
                    name=name,
                    student_ids=student_ids,
                    is_male_only=(gender == 'male'),
                    is_female_only=(gender == 'female')
                )
                messages.success(request, f"Group '{name}' created successfully!")
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'add_member':
                    group_id = request.POST.get('group_id')
                    student_id = request.POST.get('student_id')

                    group = get_object_or_404(ChatRoom, id=group_id, created_by=request.user)
                    student = get_object_or_404(User, id=student_id, role='STUDENT')

                    try:
                        group.add_member(student)
                        messages.success(request, f"Student '{student.first_name} {student.last_name}' added to the group.")
                    except Exception as e:
                        messages.error(request, str(e))

        elif action == 'delete_member':
            group_id = request.POST.get('group_id')
            student_id = request.POST.get('student_id')

            group = get_object_or_404(ChatRoom, id=group_id, created_by=request.user)
            student = get_object_or_404(User, id=student_id)

            try:
                group.delete_member(student, request.user)
                messages.success(request, f"Student '{student.first_name} {student.last_name}' removed from the group.")
            except Exception as e:
                messages.error(request, str(e))

    # Prepare the list of excluded student IDs for each group
    groups_with_excluded_students = []
    for group in groups:
        excluded_student_ids = list(group.members.values_list('id', flat=True))
        groups_with_excluded_students.append((group, excluded_student_ids))

    students = User.objects.filter(role='STUDENT')

    return render(request, 'chat_app/instructor_groups.html', {
        'groups_with_excluded_students': groups_with_excluded_students,
        'students': students,
    })