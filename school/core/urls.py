from django.urls import path, include
from rest_framework import routers
from .views import *
#from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'principal', PrincipalViewSet)
router.register(r'users', UserViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('view-profile/', UserInfoView.as_view(), name='user-info'),
    path('admin/register/', Register.as_view(), name='register'),
    path('update-profile/<int:pk>/', UpdateView.as_view({'patch': 'partial_update'}), name='update-profile'),
]