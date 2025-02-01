from django.urls import path
from .views import (chat_list, upload_file, start_private_chat, chat_room, instructor_groups, )

urlpatterns = [
    path('', chat_list, name='chat_list'),
    path('upload_endpoint/', upload_file, name='upload_file_in_chat'),
    path('start_private_chat/<int:user_id>/', start_private_chat, name='start_private_chat'),
    path('get_group_members/', views.get_group_members, name='get_group_members'),
    path('create_group/', views.create_group, name='create_group'),
    path('<str:room_name>/', chat_room, name='chat_room'),
    path('instructor/groups/', instructor_groups, name='instructor_groups'),
    
    ]