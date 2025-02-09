from django.contrib import admin
from .models import ChatRoom

# Register the ChatRoom model
@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Fields to display in the admin list view
    filter_horizontal = ('members',)  # Makes selecting members easier in the admin interface
    search_fields = ('name',)  # Enables search functionality by name
