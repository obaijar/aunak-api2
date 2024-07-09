from .views import RegisterAPI, LoginAPI
from django.urls import path
from knox import views as knox_views 
from .views import RegisterAPI, LoginAPI, VideoListCreateAPI, VideoDetailAPI,VideoListAPIView
urlpatterns = [
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', LoginAPI.as_view(), name='login'),
    path('api/logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('api/logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path('api/videos_upload/', VideoListCreateAPI.as_view(), name='video-list-create'),
    path('api/videos/<int:pk>/', VideoDetailAPI.as_view(), name='video-detail'),
    path('api/videos/<str:subject>/<str:subject_type>/<str:grade>/<str:teacher>/', VideoListAPIView.as_view(), name='video-list'),
    
]