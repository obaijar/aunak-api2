from django.shortcuts import render
from .models import Video , VideoView , Teacher
# Create your views here.
from rest_framework import generics,permissions
from rest_framework.response import Response
 
from .serializer import UserSerializer , RegisterSerializer,VideoSerializer ,TeacherSerializer
from .serializer import VideoSerializer
from rest_framework.permissions import IsAuthenticated

class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer  
    permission_classes = (permissions.AllowAny,)
    def post(self,request,*args,**kwargs):
        serializer= self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user":UserSerializer(user,context= self.get_serializer_context()).data,
            "token":AuthToken.objects.create(user)[1]
        })


from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView 
from knox.models import AuthToken
from knox.auth import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser


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
        return Video.objects.filter(subject=subject, grade=grade, subject_type=subject_type,teacher=teacher)
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
        
        video_view, created = VideoView.objects.get_or_create(user=request.user, video=video)
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


from rest_framework import viewsets

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer