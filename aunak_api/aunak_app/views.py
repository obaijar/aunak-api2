import json
from rest_framework.decorators import api_view, permission_classes
from .utils import refresh_dropbox_token
from .models import Teacher, Video
import dropbox
from rest_framework.decorators import permission_classes
from rest_framework import viewsets
from .models import Video, DropboxToken, VideoView, Teacher, Subject_type, Course, Purchase, Subject, Grade
# Create your views here.
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializer import SubjectTypeSerializer, AdminChangePasswordSerializer,VideoSerializer2, UserSerializer, CourseSerializer2, SubjectSerializer, GradeSerializer, TeacherSerializer2, PurchaseSerializer, CourseSerializer, RegisterSerializer, VideoSerializer, TeacherSerializer
from .serializer import VideoSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from knox.models import AuthToken
from knox.auth import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from knox.auth import TokenAuthentication
from rest_framework.authentication import BasicAuthentication
from django.contrib.auth.models import User
from .utils import refresh_dropbox_token
from django.db.models.signals import post_delete
import urllib.parse
from django.db.models import Q

class UserDeleteView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAdminUser]

    def delete(self, request, user_id, format=None):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class AdminChangePasswordView(generics.GenericAPIView):
    serializer_class = AdminChangePasswordSerializer
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(pk=user_id)
            user.set_password(new_password)
            user.save()

            return Response({"status": "password set"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
 

class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": AuthToken.objects.create(user)[1]
            })
        except ValidationError as e:
            if 'username' in e.detail:
                return Response({"detail": "A user with this username already exists."}, status=status.HTTP_403_FORBIDDEN)
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)


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
                'email': user.email,  # Include the email in the response
                'token': token,
                'isadmin': user.is_staff
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class ChangePasswordAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        # Check if current password is correct
        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate new password
        try:
            user.set_password(new_password)
            user.full_clean()  # This will run validators, such as password validation
            user.save()
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)


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


"""
@receiver(post_delete, sender=Video)
def delete_video_file(sender, instance, **kwargs):
     
    #Deletes the video file associated with the deleted Video object.
    
    if instance.video_file:
        if instance.video_file.storage.exists(instance.video_file.name):
            instance.video_file.delete(save=False)"""


class VideoDetailAPI(generics.RetrieveAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class VideoListView(generics.ListAPIView):
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


class TrackViewAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        video_id = self.kwargs.get('video_id')
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({"detail": "Video not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.is_staff:
            video_url = request.build_absolute_uri(video.preview_link)
            return Response(
                {"detail": "Admin access, view count not incremented.",
                    "video_url": video_url},
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
        video_url = request.build_absolute_uri(video.preview_link)
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
    permission_classes = [permissions.AllowAny]


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def update(self, request, *args, **kwargs):
        # Your custom update logic here
        return super().update(request, *args, **kwargs)


import logging

logger = logging.getLogger(__name__)

class PurchaseListCreateView(generics.ListCreateAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        logger.debug(f"Creating purchase for user: {user.id} - {user.username}")
        
        purchase = serializer.save(user=user)  # Save the purchase with the correct user
        course = purchase.course  # Access the purchased course

        # Get all videos associated with the course
        videos = Video.objects.filter(course=course)
        logger.debug(f"Found {videos.count()} videos for course: {course.id}")

        # Loop through each video and reset the user's view count
        for video in videos:
            video_view = VideoView.objects.filter(user=user, video=video).first()
            if video_view:
                logger.debug(f"Found VideoView for video: {video.id} - {video.title}, user: {user.id}")
                video_view.view_count = 0  # Reset view count
                video_view.save()  # Save changes
                logger.debug(f"Reset view count for video: {video.id} - {video.title} to 0")
            else:
                logger.debug(f"No VideoView found for video: {video.id} - {video.title}, user: {user.id}")

        logger.debug(f"Purchase and view counts reset completed for user: {user.id}")
        return purchase


class PurchaseDetailView(generics.RetrieveAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    lookup_field = 'id'


class PurchaseDeleteView(generics.DestroyAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    lookup_field = 'id'
    # Optionally set permissions
    permission_classes = [permissions.IsAuthenticated]


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
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Get grade and subject from URL parameters
        grade_id = self.kwargs['grade']
        subject_id = self.kwargs['subject']

        # Filter teachers by grade and subject IDs
        return Teacher.objects.filter(
            Q(grades__id=grade_id),
            Q(subjects__id=subject_id)
        ).distinct()


class TeacherCreateView(generics.CreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer2


class GradeListView(generics.ListAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.AllowAny]


class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.AllowAny]


class SubjectTypeListView(generics.ListAPIView):
    queryset = Subject_type.objects.all()
    serializer_class = SubjectTypeSerializer
    permission_classes = [permissions.AllowAny]


class SubjectCreateView(generics.CreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

from django.http import JsonResponse

@api_view(['GET'])
def CourseSearchView(request, grade, subject, subject_type, teacher):
    # Perform the search based on provided parameters
    courses = Course.objects.filter(
        grade=grade,
        subject=subject,
        subject_type=subject_type,
        teacher=teacher
    )

    # Serialize the queryset
    serializer = CourseSerializer(courses, many=True)

    # Return a JSON response
    return Response({'courses': serializer.data})

class UpdateCourseView(APIView):
    def patch(self, request, pk, format=None):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseSerializer(course, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            if 'videos' in request.data:
                videos_data = request.data['videos']

                # Debugging: Log the type and content of videos_data
      

                # Handle the case where videos_data is a string
                if isinstance(videos_data, str):
                    try:
                        videos_data = json.loads(videos_data) 
                    except json.JSONDecodeError:
                        return Response({'detail': 'Invalid data format for videos'}, status=status.HTTP_400_BAD_REQUEST)

                # Ensure that videos_data is now a list of integers
                if isinstance(videos_data, list) and all(isinstance(video_id, int) for video_id in videos_data):
                    videos = Video.objects.filter(id__in=videos_data)
                    course.videos.set(videos)
                else:
                    return Response({'detail': 'Invalid data format for videos'}, status=status.HTTP_400_BAD_REQUEST)

            updated_course = CourseSerializer(course)
            return Response(updated_course.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_course(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Course.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Course.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_subject_type(request, subject_type_id):
    try:
        subject_type = Subject_type.objects.get(id=subject_type_id)
        subject_type.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Course.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
class SubjectSearchView(generics.ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        grade_id = self.kwargs.get('grade')
        queryset = Subject.objects.filter(grade_id=grade_id)
        return queryset


def get_dropbox_client():
    # Fetch the latest access token from the database
    token_instance = DropboxToken.objects.get(id=1)
    return dropbox.Dropbox(token_instance.access_token)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_video(request):
    if request.method == 'POST':
        title = request.data.get('title')
        grade = request.data.get('grade')
        subject_id = request.data.get('subject')
        subject_type_id = request.data.get('subject_type')
        teacher_id = request.data.get('teacher')
        video_file = request.FILES.get('video_file')

        if not video_file:
            return Response({'error': 'No video file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a video with the same file name already exists in the database
        if Video.objects.filter(video_file_path=f'/videos/{video_file.name}').exists():
            return Response({'error': 'A video with this file name already exists. Please rename the file or upload a different video.'},
                            status=status.HTTP_207_MULTI_STATUS)

        # Get the teacher instance
        try:
            teacher = Teacher.objects.get(id=teacher_id)
        except Teacher.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get the subject instance
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get the subject_type instance
        try:
            subject_type = Subject_type.objects.get(id=subject_type_id)
        except Subject_type.DoesNotExist:
            return Response({'error': 'Subject type not found'}, status=status.HTTP_404_NOT_FOUND)

        def get_valid_dropbox_client():
            try:
                dbx = get_dropbox_client()
                dbx.users_get_current_account()
                return dbx
            except dropbox.exceptions.AuthError:
                refresh_dropbox_token()
                return get_dropbox_client()

        dbx = get_valid_dropbox_client()

        # Define the original path and the potential copy path
        dropbox_path = f'/videos/{video_file.name}'
        dropbox_copy_path = f'/videos/copy_{video_file.name}'

        try:
            try:
                # Check if the file already exists in Dropbox
                existing_file_metadata = dbx.files_get_metadata(dropbox_path)
                file_exists = True
            except dropbox.exceptions.ApiError as e:
                if isinstance(e.error, dropbox.files.GetMetadataError) and e.error.is_path():
                    file_exists = False
                else:
                    raise e

            if file_exists:
                # File exists, create a copy
                video_file.seek(0)  # Reset file pointer
                dbx.files_upload(video_file.read(), dropbox_copy_path)
                links_copy = dbx.sharing_list_shared_links(path=dropbox_copy_path)
                if links_copy.links:
                    shared_link_copy = links_copy.links[0].url
                else:
                    shared_link_metadata_copy = dbx.sharing_create_shared_link_with_settings(dropbox_copy_path)
                    shared_link_copy = shared_link_metadata_copy.url

                preview_link_copy = shared_link_copy.replace(
                    'www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '?raw=1')

                # Create a copy video instance
                video_copy = Video(
                    title=f'{title} - Copy',
                    video_file_path=dropbox_copy_path,
                    preview_link=preview_link_copy,
                    grade=grade,
                    subject=subject,
                    subject_type=subject_type,
                    teacher=teacher,
                    uploaded_by=request.user
                )
                video_copy.save()

            else:
                # Upload the original file
                video_file.seek(0)  # Reset file pointer again
                dbx.files_upload(video_file.read(), dropbox_path)
                links = dbx.sharing_list_shared_links(path=dropbox_path)
                if links.links:
                    shared_link = links.links[0].url
                else:
                    shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
                    shared_link = shared_link_metadata.url

                preview_link = shared_link.replace(
                    'www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '?raw=1')

                # Create the original video instance
                video = Video(
                    title=title,
                    video_file_path=dropbox_path,
                    preview_link=preview_link,
                    grade=grade,
                    subject=subject,
                    subject_type=subject_type,
                    teacher=teacher,
                    uploaded_by=request.user
                )
                video.save()

            return Response({'success': 'Video uploaded successfully'}, status=status.HTTP_201_CREATED)

        except dropbox.exceptions.ApiError as err:
            return Response({'error': f'Dropbox API error: {err}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_videos(request):
    grade = request.data.get('grade')
    subject = request.data.get('subject')
    subject_type = request.data.get('subject_type')
    teacher_id = request.data.get('teacher')

    if not all([grade, subject, subject_type, teacher_id]):
        return Response({'error': 'Missing query parameters'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        teacher = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)

    videos = Video.objects.filter(
        grade=grade, subject=subject, subject_type=subject_type, teacher=teacher)
    if not videos.exists():
        return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)

    video_list = []
    for video in videos:
        video_data = VideoSerializer2(video).data
        video_list.append(video_data)

    return Response(video_list, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_videos(request):
    # Fetch all video objects from the database
    videos = Video.objects.all()

    # Serialize video data
    video_list = VideoSerializer2(videos, many=True).data

    return Response(video_list, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_video(request, video_id):
    try:
        # Fetch the video instance
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the requesting user is the one who uploaded the video or is an admin
    if video.uploaded_by != request.user and not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    dropbox_path = video.video_file_path

    # Ensure Dropbox client is ready
    def get_valid_dropbox_client():
        try:
            dbx = get_dropbox_client()
            # Test a simple operation to verify token validity
            dbx.users_get_current_account()
            return dbx
        except dropbox.exceptions.AuthError:
            refresh_dropbox_token()
            return get_dropbox_client()

    try:
        dbx = get_valid_dropbox_client()
        dbx.files_delete_v2(dropbox_path)
    except dropbox.exceptions.AuthError:
        refresh_dropbox_token()
        dbx = get_dropbox_client()
        try:
            dbx.files_delete_v2(dropbox_path)
        except dropbox.exceptions.ApiError as err:
            return Response({'error': f'Dropbox API error: {err}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except dropbox.exceptions.ApiError as err:
        return Response({'error': f'Dropbox API error: {err}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Delete the video instance from the database
    video.delete()

    return Response({'success': 'Video deleted successfully'}, status=status.HTTP_200_OK)


@receiver(post_delete, sender=Video)
def delete_video_from_dropbox(sender, instance, **kwargs):
    def get_valid_dropbox_client():
        try:
            dbx = get_dropbox_client()
            dbx.users_get_current_account()
            return dbx
        except dropbox.exceptions.AuthError:
            refresh_dropbox_token()
            return get_dropbox_client()

    dropbox_path = instance.video_file_path
    dbx = get_valid_dropbox_client()

    try:
        dbx.files_delete_v2(dropbox_path)
    except dropbox.exceptions.ApiError as err:
        print(f'Failed to delete video from Dropbox: {err}')

class SubjectTypeCreateView(APIView):
    def post(self, request):
        serializer = SubjectTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TeacherDelete(APIView):
    permission_classes = [IsAuthenticated]  # Add appropriate permission classes
    
    def delete(self, request, pk, format=None):
        try:
            teacher = Teacher.objects.get(pk=pk)
            teacher.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Teacher.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class SubjectUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class SubjectTypeUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Subject_type.objects.all()
    serializer_class = SubjectTypeSerializer