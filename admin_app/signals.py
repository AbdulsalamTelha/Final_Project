from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import os
from .models import User, File

@receiver(pre_save, sender=File)
def delete_old_file(sender, instance, **kwargs):
    """Delete old file when the user updates the file."""
    if instance.pk:
        try:
            old_file = File.objects.get(pk=instance.pk).file
        except File.DoesNotExist:
            return  # Skip if the file doesn't exist
        new_file = instance.file
        # Check if the old file exists and is different from the new file
        if old_file and old_file != new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)

@receiver(post_delete, sender=File)
def delete_file_on_delete(sender, instance, **kwargs):
    """Delete file when the file instance is deleted."""
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)

@receiver(pre_save, sender=User)
def delete_old_image(sender, instance, **kwargs):
    """Delete old image file when the user updates their image."""
    if instance.pk:
        try:
            old_image = User.objects.get(pk=instance.pk).image
        except User.DoesNotExist:
            return  # Skip if the user doesn't exist
        new_image = instance.image
        if old_image and old_image != new_image:
            if os.path.isfile(old_image.path):
                os.remove(old_image.path)

@receiver(post_delete, sender=User)
def delete_image_on_user_delete(sender, instance, **kwargs):
    """Delete image file when the user is deleted."""
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)