from django.shortcuts import render
from .models import ChatRoom

def chat_list(request):
    user = request.user
    chat_rooms = user.chat_rooms.all()
    return render(request, 'chat_app/chat_list.html', {'chat_rooms': chat_rooms})

def chat_room(request, room_name):
    room = ChatRoom.objects.get(name=room_name)
    messages = room.messages.all().order_by('timestamp')
    return render(request, 'chat_app/chat_room.html', {'room': room, 'messages': messages})