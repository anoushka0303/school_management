from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from .models import User, UserManager
from rest_framework.views import APIView

from .models import Student, Teacher, Principal
from .serializers import StudentSerializer, TeacherSerializer, PrincipalSerializer, UserSerializer
from .permissions import IsStudent, IsTeacher, IsPrincipal, IsUser

# Create your views here.

user = get_user_model()

class userViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsUser, permissions.IsAuthenticated]

class studentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsStudent, permissions.IsAuthenticated]

class teacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

class principalViewSet(viewsets.ModelViewSet):
    queryset = Principal.objects.all()
    serializer_class = PrincipalSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrincipal]

class RegisterOrLoginView(APIView):
    permission_classes = [AllowAny]  

    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role')
        
        if not email or not password or not role:
            return Response({"error": "Email, password, and role are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        
        if user:
            if not user.check_password(password):
                return Response({"error": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = User.objects.create_user(email=email, password=password, role=role)
        
        access_token = AccessToken.for_user(user)
        
        return Response({
            "access": str(access_token),
            "user": {
                "email": user.email,
                "role": user.role,
            }
        }, status=status.HTTP_200_OK)



class UserInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return Response(StudentSerializer(student, context={'request': request}).data)
            except Student.DoesNotExist:
                return Response({"error": "Student info not found"}, status=status.HTTP_404_NOT_FOUND)
        
        elif user.role == 'teacher':
            try:
                teacher = Teacher.objects.get(user=user)
                return Response(TeacherSerializer(teacher, context={'request': request}).data)
            except Teacher.DoesNotExist:
                return Response({"error": "Teacher info not found"}, status=status.HTTP_404_NOT_FOUND)

        elif user.role == 'principal':
            try:
                principal = Principal.objects.get(user=user)
                return Response(PrincipalSerializer(principal, context={'request': request}).data)
            except Principal.DoesNotExist:
                return Response({"error": "Principal info not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)