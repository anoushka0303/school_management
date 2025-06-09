from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from .models import User
from rest_framework.views import APIView

from .models import Student, Teacher, Principal
from .serializers import StudentSerializer, TeacherSerializer, PrincipalSerializer
from .permissions import IsStudent, IsTeacher, IsPrincipal

# Create your views here.

user = get_user_model()

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
    permission_classes = [AllowAny]  # Allow anyone to access this

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