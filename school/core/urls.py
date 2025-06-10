from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from .views import *


router = routers.DefaultRouter()
router.register(r'students', studentViewSet)
router.register(r'teachers', teacherViewSet)
router.register(r'principal', principalViewSet)
router.register(r'users', userViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserInfoView.as_view(), name = 'user-info'),
    path('admin/register/', Register.as_view(), name = 'register')
]