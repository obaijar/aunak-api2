from django.contrib import admin
from .models import Video,DropboxToken, VideoView, Subject_type, Teacher, Course, Purchase, Grade, Subject
# Register your models here.
admin.site.register(Video)
admin.site.register(VideoView)
admin.site.register(Teacher)
admin.site.register(Purchase)
admin.site.register(Course)
admin.site.register(Grade)
admin.site.register(Subject)
admin.site.register(Subject_type)
admin.site.register(DropboxToken)

