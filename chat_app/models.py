from django.db import models
from admin_app.models import User
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class ChatRoom(models.Model):
    CHAT_TYPE_CHOICES = [
        ('group', 'Group Chat'),
        ('private', 'Private Chat'),
    ]

    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=10, choices=CHAT_TYPE_CHOICES, default='group')
    members = models.ManyToManyField(User, related_name='chat_rooms', limit_choices_to={'is_active': True})
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_chat_rooms', null=True, blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    is_male_only = models.BooleanField(default=False)
    is_female_only = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.is_male_only and self.is_female_only:
            raise ValidationError("A group cannot be both male-only and female-only.")
        if not self.is_male_only and not self.is_female_only:
            raise ValidationError("A group must be either male-only or female-only.")
        if not self.name:
            raise ValidationError("Group name is required.")

    def add_member(self, user):
        if self.is_male_only and user.gender != 'M':
            logger.error("Failed to add user '%s' to chat room '%s': group is male-only.", user.username, self.name)
            raise ValidationError("This group is for males only.")
        if self.is_female_only and user.gender != 'F':
            logger.error("Failed to add user '%s' to chat room '%s': group is female-only.", user.username, self.name)
            raise ValidationError("This group is for females only.")
        self.members.add(user)
        logger.info("User '%s' added to chat room '%s'.", user.username, self.name)

    def remove_member(self, user):
        if user == self.created_by:
            logger.error("Attempt to remove creator '%s' from chat room '%s' blocked.", user.username, self.name)
            raise ValidationError("The creator of the group cannot be removed.")
        self.members.remove(user)
        logger.info("User '%s' removed from chat room '%s'.", user.username, self.name)


    def delete_member(self, user, instructor):
        if instructor != self.created_by:
            logger.error("User '%s' (not creator) attempted to delete member '%s' from chat room '%s'.", instructor.username, user.username, self.name)
            raise ValidationError("Only the creator of the group can delete members.")
        self.remove_member(user)
        logger.info("User '%s' deleted from chat room '%s' by creator '%s'.", user.username, self.name, instructor.username)


    def is_member(self, user):
        return self.members.filter(id=user.id).exists()

    def create_group(self, instructor, name, student_ids=None, is_male_only=False, is_female_only=False):
        
        self.name = name
        self.created_by = instructor
        self.is_male_only = is_male_only
        self.is_female_only = is_female_only
        self.save()
        logger.info("Chat room '%s' created by user '%s'.", self.name, instructor.username)


        # Add the instructor (creator) to the group
        self.members.add(instructor)
        logger.info("Creator '%s' added as member to chat room '%s'.", instructor.username, self.name)


        # Add students if provided
        if student_ids:
            students = User.objects.filter(id__in=student_ids)
            for student in students:
                try:
                    self.add_member(student)
                except ValidationError as e:
                    logger.error("Failed to add student '%s' to chat room '%s': %s", student.username, self.name, e)

        return self

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} in {self.room}: {self.content}'