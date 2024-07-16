from rest_framework import serializers , generics
from django.contrib.auth.models import User
from .models import Video , Teacher ,Course, Purchase

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ('id', 'name', 'age') 
    
class RegisterSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'is_admin')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        is_admin = validated_data.pop('is_admin', False)
        user = User.objects.create_user(**validated_data)
        user.is_staff = is_admin
        user.save()
        return user

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'video_file', 'grade', 'subject','subject_type','teacher']
        read_only_fields = ['uploaded_by']


class CourseSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True)

    class Meta:
        model = Course
        fields = "__all__"

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ['id', 'user', 'course', 'purchase_date']

    def to_representation(self, instance):
        self.fields['course'] = CourseSerializer()
        self.fields['user'] = serializers.StringRelatedField()
        return super(PurchaseSerializer, self).to_representation(instance)