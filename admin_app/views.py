from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import File, User, Instructor, Student,Course
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.shortcuts import render, redirect
# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirect user based on role
            if user.role == User.Roles.ADMIN:
                return redirect('admin_dashboard')  # Admin dashboard view
            elif user.role == User.Roles.INSTRUCTOR:
                return redirect('library')  # Instructor dashboard view
            elif user.role == User.Roles.STUDENT:
                return redirect('library')  # Student dashboard view
            else:
                messages.error(request, "Your role is not recognized.")
                return redirect('access_denied')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

# Logout view
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# Access denied view
def access_denied(request):
    return render(request, 'access_denied.html')

# Library view for students and instructors


@login_required
def library_view(request):
    # Ensure the user has the correct role
    if request.user.role not in [User.Roles.STUDENT, User.Roles.INSTRUCTOR]:
        return redirect('access_denied')

    # Get search and filter parameters
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()
    course_filter = request.GET.get('course', '').strip()
    type_filter = request.GET.get('type', '').strip()

    # Base query
    files = File.objects.all()

    # Apply filters
    if search_query:
        files = files.filter(name__icontains=search_query)

    if category_filter:
        files = files.filter(category=category_filter)

    if course_filter:
        files = files.filter(course__id=course_filter)

    if type_filter:
        files = files.filter(type=type_filter)

    # Fetch distinct data for filters
    categories = File.objects.values_list('category', flat=True).distinct()
    courses = Course.objects.filter(status=True).values('id', 'name')  # Assuming 'Course' model has 'name' and 'status' fields
    file_types = File.objects.values_list('type', flat=True).distinct()

    return render(request, 'library.html', {
        'files': files,
        'search_query': search_query,
        'category_filter': category_filter,
        'course_filter': course_filter,
        'type_filter': type_filter,
        'categories': categories,
        'courses': courses,
        'file_types': file_types,
    })

# Instructor dashboard view
@login_required
def instructor_dashboard_view(request):
    if request.user.role != User.Roles.INSTRUCTOR:
        return redirect('access_denied')

    instructor = get_object_or_404(Instructor, user=request.user)
    courses = instructor.course.all()

    return render(request, 'instructor_dashboard.html', {'file': File, 'courses': courses})

# Student dashboard view
@login_required
def student_library_view(request):
    if request.user.role != User.Roles.STUDENT:
        return redirect('access_denied')

    student = get_object_or_404(Student, user=request.user)
    courses = student.course.all()

    return render(request, 'student_library_view.html', {'student': student, 'courses': courses})

# # File upload view (instructors only)
# @login_required
# def upload_file_view(request):
#     if request.user.role != User.Roles.INSTRUCTOR:
#         return redirect('access_denied')

#     if request.method == 'POST':
#         file = request.FILES.get('file')
#         description = request.POST.get('description')
#         course_id = request.POST.get('course')

#         instructor = get_object_or_404(Instructor, user=request.user)
#         course = get_object_or_404(instructor.course, id=course_id)

#         uploaded_file = File(
#             file=file,
#             description=description,
#             upload_by=request.user,
#             course=course
#         )
#         uploaded_file.save()

#         messages.success(request, "File uploaded successfully.")
#         return redirect('instructor_dashboard')

#     instructor = get_object_or_404(Instructor, user=request.user)
#     courses = instructor.course.all()
#     return render(request, 'upload_file.html', {'courses': courses})

# File approval view (admins only)
# @login_required
# def approve_file_view(request, file_id):
#     if request.user.role != User.Roles.ADMIN:
#         return redirect('access_denied')

#     file = get_object_or_404(File, id=file_id)
#     file.status = 'APPROVED'
#     file.save()

#     messages.success(request, "File approved successfully.")
#     return redirect('admin_dashboard')
