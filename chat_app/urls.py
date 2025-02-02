from django.urls import path
from .views import ( chat_list, create_group, get_group_members, manage_group, upload_file, start_private_chat, chat_room,  )

urlpatterns = [
    path('', chat_list, name='chat_list'),
    path('upload_endpoint/', upload_file, name='upload_file_in_chat'),
    path('start_private_chat/<int:user_id>/', start_private_chat, name='start_private_chat'),
    path('get_group_members/', get_group_members, name='get_group_members'),
    path('manage_group/<int:group_id>/', manage_group, name='manage_group'),
    path('create_group/', create_group, name='create_group'),
    path('<str:room_name>/', chat_room, name='chat_room'),
    
    ]