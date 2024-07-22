from .views import RegisterAPI, LoginAPI
from django.urls import path, include
from knox import views as knox_views
from .views import RegisterAPI, SubjectCreateView, SubjectSearchView,SubjectListView, LoginAPI, CourseSearchView, GradeListView, TeacherListView, TeacherCreateView, CourseCreateView, UserPurchasesListView, PurchaseListCreateView, PurchaseDetailView, VideoDeleteAPIView, CourseListView, TrackViewAPIView, VideoListCreateAPI, TeacherViewSet, VideoDetailAPI, VideoListAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# Removed 'api/' prefix here
router.register(r'teachers', TeacherViewSet, basename='teacher')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', LoginAPI.as_view(), name='login'),
    path('api/logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('api/logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path('api/videos_upload/', VideoListCreateAPI.as_view(),
         name='video-list-create'),
    path('api/videos/<int:pk>/', VideoDetailAPI.as_view(), name='video-detail'),
    path('api/videos/<str:subject>/<str:subject_type>/<str:grade>/<str:teacher>/',
         VideoListAPIView.as_view(), name='video-list'),
    # when the user open the video ....
    path('videos/<int:video_id>/track-view/',
         TrackViewAPIView.as_view(), name='track-view'),
    path('videos/<int:id>/delete/',
         VideoDeleteAPIView.as_view(), name='video-delete'),
    path('api/courses/', CourseListView.as_view(), name='course_list'),
    path('api/courses/create/', CourseCreateView.as_view(), name='course-create'),
    path('api/courses/search/<int:grade>/<int:subject>/<int:subject_type>/<int:teacher>/',
         CourseSearchView.as_view(), name='course-search'),

    path('api/purchases/', PurchaseListCreateView.as_view(), name='purchase_list'),
    path('api/purchases/<int:id>/',
         PurchaseDetailView.as_view(), name='purchase_detail'),
    path('purchases/user/<int:user_id>/', UserPurchasesListView.as_view(),
         name='user-purchases-list'),  # see the purchaesd courses for a user
    path('api/teachers/<str:grade>/<str:subject>/',
         TeacherListView.as_view(), name='teacher-list'),
    path('api/add-teacher/', TeacherCreateView.as_view(), name='add-teacher'),
    path('api/Grade/', GradeListView.as_view(), name='add-teacher'),
    path('api/Subject/', SubjectListView.as_view(), name='add-teacher'),
    path('api/subject_create/', SubjectCreateView.as_view(), name='subject-create'),
    path('api/Subject/<int:grade>/', SubjectSearchView.as_view(), name='Search'), 
]
