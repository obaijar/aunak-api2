from django.db import models
from django.contrib.auth.models import User

class Teacher(models.Model):
    name = models.CharField(max_length=255)
    age = models.CharField(max_length=255)
    def __str__(self):
        return self.name

  
class Video(models.Model):
    GRADE_CHOICES = [
        ('9', '9th Grade'),
        ('12', '12th Grade'),
    ]
    SUBJECT_CHOICES = [
        ('physics', 'Physics'),
        ('math', 'Math'),
    ]
    SUBJECT_TYPE_CHOICES = [
        ('1', 'mukathefat'),
        ('2', 't2ses'),
        ('3', 'jalsat_e'),
    ]

    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, default='9')
    subject = models.CharField(max_length=7, choices=SUBJECT_CHOICES, default='physics')
    subject_type = models.CharField(max_length=7, choices=SUBJECT_TYPE_CHOICES, default='1')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
 
    def __str__(self):
        return self.title

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    videos = models.ManyToManyField(Video)

    def __str__(self):
        return self.title

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} purchased {self.course.title}"
    
class VideoView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    view_count = models.PositiveIntegerField(default=0)
    
        