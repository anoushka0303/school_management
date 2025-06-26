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
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/reset-password/request/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('auth/reset-password/confirm/', ConfirmPasswordResetView.as_view(), name='confirm-password-reset'),
    path('admin/register/', Register.as_view(), name='admin-register'),
    path('student/profile/update/', StudentUpdateView.as_view({'patch': 'partial_update'}), name='student-update'),
    path('teacher/profile/update/', TeacherUpdateView.as_view({'patch': 'partial_update'}), name='teacher-update'),
    path('principal/profile/update/', PrincipalUpdateView.as_view({'patch': 'partial_update'}), name='principal-update'),
    path('enrollments/<int:pk>/update-grade/', GradeUpdateView.as_view({'patch': 'partial_update'}), name='update-grade'),
    path('fee-status/<int:pk>/update/', UpdateFeeStatusView.as_view({'patch': 'partial_update'}), name='fee-status-update'),
    path('<str:role>/bulk-download/', BulkDownloadExcelView.as_view(), name = 'bulk-download'),
    path('bulk-upload/', BulkUploadViewSet.as_view({'post' : 'create'}), name = 'bulk-upload'),
    path('bulk-enroll/', BulkEnrollViewSet.as_view({'post' : 'create'}), name = 'bulk-enroll'),
    #path('bulk-upload/', UploadExcel.as_view({'post' : 'create'}), name= 'upload'),
    path('bulk-upload-via-excel/', UploadExcel.as_view({'post' : 'create'}), name= 'bulk-upload-excel'),
    path('download-results/<int:pk>/', DownloadResultViewSet.as_view(), name= 'download-result'),
    path('', include(router.urls)),
]