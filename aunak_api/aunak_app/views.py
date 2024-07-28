import dropbox
from rest_framework.decorators import permission_classes
from django.conf import settings
from rest_framework import viewsets
from django.shortcuts import render
from .models import Video, VideoView, Teacher, Subject_type, Course, Purchase, Subject, Grade
# Create your views here.
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializer import SubjectTypeSerializer, VideoSerializer2, UserSerializer, CourseSerializer2, SubjectSerializer, GradeSerializer, TeacherSerializer2, PurchaseSerializer, CourseSerializer, RegisterSerializer, VideoSerializer, TeacherSerializer
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
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError


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
            # Admin user, no view count increment
            video_url = request.build_absolute_uri(video.video_file.url)
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
    permission_classes = [permissions.AllowAny]


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def update(self, request, *args, **kwargs):
        # Your custom update logic here
        return super().update(request, *args, **kwargs)


class PurchaseListCreateView(generics.ListCreateAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer


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
            subject_instance = get_object_or_404(Subject, name=subject)
            queryset = queryset.filter(subject_id=subject_instance.id)
        if teacher is not None:
            queryset = queryset.filter(teacher_id=teacher)
        if subject_type is not None:
            queryset = queryset.filter(subject_type_id=subject_type)

        return queryset


@api_view(['PATCH'])
def update_course(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'detail': 'Course not found'}, status=status.not_found)

    serializer = CourseSerializer(course, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_course(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        course.delete()
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_video(request):
    if request.method == 'POST':
        title = request.data.get('title')
        grade = request.data.get('grade')
        subject = request.data.get('subject')
        subject_type = request.data.get('subject_type')
        teacher_id = request.data.get('teacher')
        video_file = request.FILES['video_file']

        # Get the teacher instance
        try:
            teacher = Teacher.objects.get(id=teacher_id)
        except Teacher.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)

        # Upload video to Dropbox
        dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)
        dropbox_path = f'/videos/{video_file.name}'

        try:
            dbx.files_upload(video_file.read(), dropbox_path)
        except dropbox.exceptions.ApiError as err:
            return Response({'error': f'Dropbox API error: {err}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create video instance
        video = Video(
            title=title,
            video_file_path=dropbox_path,
            grade=grade,
            subject=subject,
            subject_type=subject_type,
            teacher=teacher,
            uploaded_by=request.user
        )
        video.save()

        return Response({'success': 'Video uploaded successfully'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video(request):
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

    try:
        video = Video.objects.get(grade=grade, subject=subject, subject_type=subject_type, teacher=teacher)
    except Video.DoesNotExist:
        return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)

    # Fetch the video from Dropbox
    dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)
    dropbox_path = video.video_file_path
    try:
        # Check if a shared link already exists
        links = dbx.sharing_list_shared_links(path=dropbox_path)
        if links.links:
            shared_link = links.links[0].url
        else:
            # Create a shared link with settings
            shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
            shared_link = shared_link_metadata.url

        # Modify the shared link to enable direct video preview
        preview_link = shared_link.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '?raw=1')
    except dropbox.exceptions.ApiError as err:
        return Response({'error': f'Dropbox API error: {err}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    video_data = VideoSerializer2(video).data
    video_data['dropbox_link'] = preview_link

    return Response(video_data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_videos(request):
    videos = Video.objects.all()
    dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)
    video_list = []

    for video in videos:
        dropbox_path = video.video_file_path
        try:
            # Check if a shared link already exists
            links = dbx.sharing_list_shared_links(path=dropbox_path)
            if links.links:
                shared_link = links.links[0].url
            else:
                # Create a shared link with settings
                shared_link_metadata = dbx.sharing_create_shared_link_with_settings(
                    dropbox_path)
                shared_link = shared_link_metadata.url

            # Modify the shared link to enable direct video preview
            preview_link = shared_link.replace(
                'www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '?raw=1')
        except dropbox.exceptions.ApiError as err:
            return Response({'error': f'Dropbox API error: {err}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        video_data = VideoSerializer2(video).data
        video_data['dropbox_link'] = preview_link
        video_list.append(video_data)

    return Response(video_list, status=status.HTTP_200_OK)
