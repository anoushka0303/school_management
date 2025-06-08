from django.shortcuts import render
from rest_framework import viewsets
from .models import Student, Teacher, Principal
from .serializers import StudentSerializer, TeacherSerializer, PrincipalSerializer

# Create your views here.
class studentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class teacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class principalViewSet(viewsets.ModelViewSet):
    queryset = Principal.objects.all()
    serializer_class = PrincipalSerializer
