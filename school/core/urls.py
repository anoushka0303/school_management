from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'teachers', TeacherViewSet, basename='teacher')
router.register(r'principals', PrincipalViewSet, basename='principal')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    # Auth
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/reset-password/request/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('auth/reset-password/confirm/', ConfirmPasswordResetView.as_view(), name='confirm-password-reset'),

    # Admin
    path('admin/register/', Register.as_view(), name='admin-register'),

    # Users
    path('users/<int:pk>/profile/', UserViewSet.as_view({'get': 'retrieve'}), name='user-profile'),
    path('users/<int:pk>/update/', UpdateView.as_view({'patch': 'partial_update'}), name='update-profile'),

    # RESTful routes
    path('', include(router.urls)),
]