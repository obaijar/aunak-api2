from django.db import models
from django.contrib.auth.models import User


class DropboxToken(models.Model):
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    token_type = models.CharField(max_length=50, blank=True, null=True)
    expires_in = models.IntegerField(blank=True, null=True)
    scope = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.access_token


class Grade(models.Model):
    GRADE_CHOICES = [
        ('9', '9th Grade'),
        ('12', '12th Grade 3lme'),
        ('13', '12th Grade adabe'),
    ]
    level = models.CharField(max_length=2, choices=GRADE_CHOICES, default='9')

    def __str__(self):
        return self.level


class Subject(models.Model):
    # SUBJECT_CHOICES = [
    #   ('physics', 'Physics'),
    # ('math', 'Math'),
    #   ('arabic', 'Arabic'),
    #  ('Philosophy', 'Philosophy'),
    #  ('Social Studies', 'Social Studies'),
    # ]
    # name = models.CharField(
    #    max_length=100, choices=SUBJECT_CHOICES, default='physics')
    name = models.CharField(max_length=255)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Subject_type(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Teacher(models.Model):

    name = models.CharField(max_length=255) 
    email= models.CharField(max_length=255)
    subjects = models.ManyToManyField(Subject, related_name='teachers')
    grades = models.ManyToManyField(Grade, related_name='teachers')

    def __str__(self):
        return self.name


class Video(models.Model):
    GRADE_CHOICES = [
        ('9', '9th Grade'),
        ('12', '12th Grade 3lme'),
        ('13', '12th Grade adabe'),
    ] 

    title = models.CharField(max_length=255)
    preview_link = models.CharField(max_length=255)
    video_file_path = models.CharField(max_length=1024)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, default='9')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    subject_type = models.ForeignKey(Subject_type, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    videos = models.ManyToManyField(Video)
    subject_type = models.ForeignKey(Subject_type, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)

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
