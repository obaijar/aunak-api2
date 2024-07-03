from django.db import models
from django.contrib.auth.models import User
class Video(models.Model):
    GRADE_CHOICES = [
        ('9', '9th Grade'),
        ('12', '12th Grade'),
    ]
    SUBJECT_CHOICES = [
        ('physics', 'Physics'),
        ('math', 'Math'),
    ]

    SUBJECT_type_CHOICES = [
        ('1', 'mukathefat'),
        ('2', 't2ses'),
        ('3', 'jalsat_e'),
    ]
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, default='9')
    subject = models.CharField(max_length=7, choices=SUBJECT_CHOICES, default='physics')
    subject_type = models.CharField(max_length=7, choices=SUBJECT_type_CHOICES, default='physics')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class VideoView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    view_count = models.PositiveIntegerField(default=0)

        