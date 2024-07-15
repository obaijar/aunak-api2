from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Video
import os

@receiver(post_delete, sender=Video)
def delete_video_file(sender, instance, **kwargs):
    # Check if the video file exists
    if instance.file:  # Replace 'file' with the actual field name of your video file
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)