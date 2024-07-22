from rest_framework import viewsets
from django.shortcuts import render
from .models import Video, VideoView, Teacher, Course, Purchase , Subject,Grade
# Create your views here.
from rest_framework import generics, permissions
from rest_framework.response import Response

from .serializer import UserSerializer, CourseSerializer2,SubjectSerializer,GradeSerializer,TeacherSerializer2,PurchaseSerializer, CourseSerializer, RegisterSerializer, VideoSerializer, TeacherSerializer
from .serializer import VideoSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from knox.models import AuthToken
from knox.auth import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models.signals import post_delete
from django.dispatch import receiver


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class LoginAPI(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            _, token = AuthToken.objects.create(user)
            return Response({
                'user_id': user.id,
                'user': user.username,
                'token': token,
                'isadmin': user.is_staff
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class VideoListCreateAPI(generics.ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        subject = self.request.query_params.get('subject')
        if subject:
            queryset = queryset.filter(subject=subject)
        return queryset


@receiver(post_delete, sender=Video)
def delete_video_file(sender, instance, **kwargs):
    """
    Deletes the video file associated with the deleted Video object.
    """
    if instance.video_file:
        if instance.video_file.storage.exists(instance.video_file.name):
            instance.video_file.delete(save=False)


class VideoDetailAPI(generics.RetrieveAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class VideoListAPIView(generics.ListAPIView):
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        subject = self.kwargs.get('subject')
        grade = self.kwargs.get('grade')
        subject_type = self.kwargs.get('subject_type')
        teacher = self.kwargs.get('teacher')
        return Video.objects.filter(subject=subject, grade=grade, subject_type=subject_type, teacher=teacher)
    """def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        for video in queryset:
            video_view, created = VideoView.objects.get_or_create(user=request.user, video=video)
            if video_view.view_count >= 5:
                return Response(
                    {"detail": f"View limit reached for video: {video.title}"},
                    status=status.HTTP_403_FORBIDDEN
                )
            video_view.view_count += 1
            video_view.save()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)"""


class TrackViewAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        video_id = self.kwargs.get('video_id')
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({"detail": "Video not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.is_staff:
            # Admin user, no view count increment
            video_url = request.build_absolute_uri(video.video_file.url)
            return Response(
                {"detail": "Admin access, view count not incremented.", "video_url": video_url},
                status=status.HTTP_200_OK
            )

        video_view, created = VideoView.objects.get_or_create(
            user=request.user, video=video)
        if video_view.view_count >= 5:
            return Response(
                {"detail": f"View limit reached for video: {video.title}"},
                status=status.HTTP_403_FORBIDDEN
            )
        video_view.view_count += 1
        video_view.save()
        video_url = request.build_absolute_uri(video.video_file.url)
        return Response(
            {"detail": "View count increased.", "video_url": video_url},
            status=status.HTTP_200_OK
        )


class VideoDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Video.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Add any necessary permission checks here, e.g., check if user owns the video

        # Delete the video file if needed
        if instance.video_file:
            instance.video_file.delete(save=False)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer



class PurchaseListCreateView(generics.ListCreateAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer


class PurchaseDetailView(generics.RetrieveAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    lookup_field = 'id'

class UserPurchasesListView(generics.ListAPIView):
    serializer_class = PurchaseSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Purchase.objects.filter(user_id=user_id)

class CourseCreateView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer2

class TeacherListView(generics.ListAPIView):
    serializer_class = TeacherSerializer

    def get_queryset(self):
        # Get grade and subject from URL parameters
        grade_level = self.kwargs['grade']
        subject_name = self.kwargs['subject']

        # Filter teachers by the given grade and subject
        return Teacher.objects.filter(
            grades__level=grade_level,
            subjects__name=subject_name
        ).distinct()
    
class TeacherCreateView(generics.CreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer2

class GradeListView(generics.ListAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer   

class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer  

class SubjectCreateView(generics.CreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer 

class CourseSearchView(generics.ListAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        queryset = Course.objects.all()
        grade = self.kwargs.get('grade')
        subject = self.kwargs.get('subject')
        teacher = self.kwargs.get('teacher')
        subject_type = self.kwargs.get('subject_type')

        if grade is not None:
            queryset = queryset.filter(grade_id=grade)
        if subject is not None:
            queryset = queryset.filter(subject_id=subject)
        if teacher is not None:
            queryset = queryset.filter(teacher_id=teacher)
        if subject_type is not None:
            queryset = queryset.filter(subject_type_id=subject_type)
        
        return queryset
    
class SubjectSearchView(generics.ListAPIView):
    serializer_class = SubjectSerializer

    def get_queryset(self):
        grade_id = self.kwargs.get('grade')
        queryset = Subject.objects.filter(grade_id=grade_id)
        return queryset