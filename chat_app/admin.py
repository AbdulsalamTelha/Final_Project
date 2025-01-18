from django.contrib import admin
from .models import ChatRoom, Message

# Register the ChatRoom model
@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Fields to display in the admin list view
    filter_horizontal = ('members',)  # Makes selecting members easier in the admin interface
    search_fields = ('name',)  # Enables search functionality by name

# Register the Message model
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'timestamp')  # Fields to display in the admin list view
    list_filter = ('room', 'sender', 'timestamp')  # Adds filters for these fields
    search_fields = ('content',)  # Enables search functionality by message content
    date_hierarchy = 'timestamp'  # Adds a date-based navigation hierarchy