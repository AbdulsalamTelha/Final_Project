from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('upload_endpoint/', views.upload_file, name='upload_file'),
    path('start_private_chat/<int:user_id>/', views.start_private_chat, name='start_private_chat'),
    path('<str:room_name>/', views.chat_room, name='chat_room'),
    path('instructor/groups/', views.instructor_groups, name='instructor_groups'),

    ]