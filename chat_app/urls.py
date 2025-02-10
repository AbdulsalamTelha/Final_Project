import django.contrib
from django.urls import path
from .views import ( chat_list, create_group, get_group_members, manage_group, upload_file, start_private_chat, chat_room,  
                    get_group_members, create_group, )

from admin_app.views import (custom_400, custom_403, custom_404, custom_405, custom_500)

urlpatterns = [
    path('', chat_list, name='chat_list'),
    path('upload_endpoint/', upload_file, name='upload_file_in_chat'),
    path('start_private_chat/<int:user_id>/', start_private_chat, name='start_private_chat'),
    path('get_group_members/', get_group_members, name='get_group_members'),
    path('manage_group/<int:group_id>/', manage_group, name='manage_group'),
    path('create_group/', create_group, name='create_group'),
    path('<str:room_name>/', chat_room, name='chat_room'),
    
    path('400/', custom_400, name='400'),
    path('403/', custom_403, name='403'),
    path('404/', custom_404, name='404'),
    path('405/', custom_405, name='405'),
    path('500/', custom_500, name='500'),
    
    ]

handler400 = 'admin_app.views.custom_400'
handler403 = 'admin_app.views.custom_403'
handler404 = 'admin_app.views.custom_404'
handler500 = 'admin_app.views.custom_500'