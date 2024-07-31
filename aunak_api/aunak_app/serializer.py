from rest_framework import serializers, generics
from django.contrib.auth.models import User
from .models import Video, Teacher, Course, Purchase, Subject, Grade, Subject_type


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class SubjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject_type
        fields = "__all__"


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = "__all__"


class TeacherSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)
    grades = GradeSerializer(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = "__all__"


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
        fields = ['id', 'title', 'video_file_path', 'grade',
                  'subject', 'subject_type', 'teacher', 'preview_link']
        read_only_fields = ['uploaded_by']


class VideoSerializer2(serializers.ModelSerializer):

    class Meta:
        model = Video
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True)

    class Meta:
        model = Course
        fields = "__all__"


class CourseSerializer2(serializers.ModelSerializer):

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


class TeacherSerializer2(serializers.ModelSerializer):
    subjects = serializers.SlugRelatedField(
        slug_field='name', queryset=Subject.objects.all(), many=True)
    grades = serializers.SlugRelatedField(
        slug_field='level', queryset=Grade.objects.all(), many=True)

    class Meta:
        model = Teacher
        fields = ['name', 'age', 'subjects', 'grades']

    def create(self, validated_data):
        subjects_data = validated_data.pop('subjects')
        grades_data = validated_data.pop('grades')
        teacher = Teacher.objects.create(**validated_data)
        teacher.subjects.set(subjects_data)
        teacher.grades.set(grades_data)
        return teacher
