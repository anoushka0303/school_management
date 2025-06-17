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
router.register(r'grades', GradeUpdateView, basename='grade') 

urlpatterns = [
    # Authentication and admin management URLs
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/reset-password/request/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('auth/reset-password/confirm/', ConfirmPasswordResetView.as_view(), name='confirm-password-reset'),
    path('admin/register/', Register.as_view(), name='admin-register'),

    # Admin endpoints for viewing users
    path('admin/users/', UserViewSet.as_view({'get': 'list'}), name='all-users'),
    path('admin/users/students/', StudentViewSet.as_view({'get': 'list'}), name='all-students'),
    path('admin/users/teachers/', TeacherViewSet.as_view({'get': 'list'}), name='all-teachers'),
    path('admin/users/principals/', PrincipalViewSet.as_view({'get': 'list'}), name='all-principals'),
    path('admin/users/<int:pk>/', UserViewSet.as_view({'get': 'retrieve'}), name='user-detail'),

    # Student endpoints
    # path('student/profile/<int:pk>/', StudentViewSet.as_view({'get': 'retrieve'}), name='student-profile'),
    path('student/profile/update/', StudentUpdateView.as_view({'patch': 'partial_update'}), name='student-update'),

    # Teacher endpoints
    # path('teacher/profile/<int:pk>/', TeacherViewSet.as_view({'get': 'retrieve'}), name='teacher-profile'),
    path('teacher/profile/update/', TeacherUpdateView.as_view({'patch': 'partial_update'}), name='teacher-update'),

    # Principal endpoints
    #path('principal/profile/<int:pk>/', PrincipalViewSet.as_view({'get': 'retrieve'}), name='principal-profile'),
    path('principal/profile/update/', PrincipalUpdateView.as_view({'patch': 'partial_update'}), name='principal-update'),

    path('enrollments/<int:pk>/update-grade/', GradeUpdateView.as_view({'patch': 'partial_update'}), name='update-grade'),

    # Update fee status
    path('fee-status/<int:pk>/update/', UpdateFeeStatusView.as_view({'patch': 'partial_update'}), name='fee-status-update'),

    path('student/bulk-download/', BulkDownloadStudentExcelView.as_view(), name = 'bulk-download'),

    # All router-based URLs
    path('', include(router.urls)),
]