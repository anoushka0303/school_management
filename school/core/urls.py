from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from .views import *


router = routers.DefaultRouter()
router.register(r'students', studentViewSet)
router.register(r'teachers', teacherViewSet)
router.register(r'principal', principalViewSet)

urlpatterns = [
    path('', include(router.urls))
]