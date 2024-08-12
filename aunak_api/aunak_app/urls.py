from django.urls import path, include
from knox import views as knox_views
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Removed 'api/' prefix here
router.register(r'teachers', views.TeacherViewSet, basename='teacher')
# router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('api/', include(router.urls)),
    path('delete-user/<int:user_id>/',
         views.UserDeleteView.as_view(), name='delete-user'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('api/register/', views.RegisterAPI.as_view(), name='register'),
    path('api/login/', views.LoginAPI.as_view(), name='login'),
    path('api/admin/change-password/', views.AdminChangePasswordView.as_view(), name='admin-change-password'),
    path('api/change-password/', views.ChangePasswordAPI.as_view(),
         name='change-password'),
    path('api/logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('api/logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path('upload-video/', views.upload_video, name='upload-video'),
    path('get-video/', views.get_videos, name='get-video'),
    path('get-all-videos/', views.get_all_videos, name='get-all-videos'),
    path('videos/delete/<int:video_id>/',
         views.delete_video, name='delete_video'),
    path('api/videos_upload/', views.VideoListCreateAPI.as_view(),
         name='video-list-create'),
    path('api/videos/', views.VideoListView.as_view(), name='video-list'),
    path('api/videos/<int:pk>/', views.VideoDetailAPI.as_view(), name='video-detail'),
    path('api/videos/<str:subject>/<str:subject_type>/<str:grade>/<str:teacher>/',
         views.VideoListAPIView.as_view(), name='video-list'),
    # when the user open the video ....
    path('videos/<int:video_id>/track-view/',
         views.TrackViewAPIView.as_view(), name='track-view'),
    path('videos/<int:id>/delete/',
         views.VideoDeleteAPIView.as_view(), name='video-delete'),
    path('api/courses/', views.CourseListView.as_view(), name='course_list'),
    path('api/courses/create/',
         views.CourseCreateView.as_view(), name='course-create'),
    path('api/courses/search/<int:grade>/<int:subject>/<int:subject_type>/<int:teacher>/',
         views.CourseSearchView, name='course-search'),
    path('api/courses/delete/<int:course_id>/',
         views.delete_course, name='delete_course'),
    path('api/courses/<int:pk>/', views.UpdateCourseView.as_view(), name='update_course'),
    path('api/purchases/', views.PurchaseListCreateView.as_view(),
         name='purchase_list'),  # purchase a new course
    path('api/purchases/<int:id>/',
         views.PurchaseDetailView.as_view(), name='purchase_detail'),
    path('purchases/user/<int:user_id>/', views.UserPurchasesListView.as_view(),
         name='user-purchases-list'),  # see the purchaesdcourses for a user
    path('api/purchase/delete/<int:id>/',
         views.PurchaseDeleteView.as_view(), name='purchase-delete'),
    path('api/teachers/<str:grade>/<str:subject>/',
         views.TeacherListView.as_view(), name='teacher-list'),
    path('api/add-teacher/', views.TeacherCreateView.as_view(), name='add-teacher'),
     path('teacher/<int:pk>/', views.TeacherDelete.as_view(), name='teacher-detail'),

    path('api/Grade/', views.GradeListView.as_view(), name='grade-list'),
    path('api/Subject/', views.SubjectListView.as_view(), name='Subject-list'),
    path('api/subject_create/', views.SubjectCreateView.as_view(),
         name='subject-create'),
    path('api/Subject/<int:grade>/',
         views.SubjectSearchView.as_view(), name='Search-subject'),
    path('api/subject/delete/<int:subject_id>/',
         views.delete_subject, name='delete_subject'),
     path('api/subjects/edit/<int:pk>/', views.SubjectUpdateView.as_view(), name='subject-update'),
    path('api/Subject_type/', views.SubjectTypeListView.as_view(),
         name='subjectType-list'),
    path('api/subject_type/delete/<int:subject_type_id>/',
         views.delete_subject_type, name='delete_subject_type'),
    path('api/subject-type/add/',  views.SubjectTypeCreateView.as_view(), name='subject-type-create'),
    path('api/subject-type/edit/<int:pk>/',  views.SubjectTypeUpdateView.as_view(), name='subject-type-create'),
]
