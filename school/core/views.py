from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from .models import User, UserManager
from rest_framework.views import APIView

from .models import Student, Teacher, Principal
from .serializers import *
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


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role')

        if not email or not password or not role:
            return Response({"error": "Email, password and role required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()

        if user.role != role:
            return Response({"error": f"User role mismatch. Expected role '{user.role}'."}, status=status.HTTP_401_UNAUTHORIZED)

        if user and user.check_password(password):
            access_token = AccessToken.for_user(user)
            return Response({
                "access": str(access_token),
                "user": {
                    "email": user.email,
                    "role": user.role,
                }
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



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
    
class Register(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        role = request.data.get('role')
        email = request.data.get('email')
        password = request.data.get('password')
        profile_data = request.data.get('profile', {})

        if not all([email, password, role]):
            return Response({"error": "email, password, and role are required"}, status=400)

        if role not in ['student', 'teacher']:
            return Response({"error": "Only student or teacher can be created by admin"}, status=400)

        user = User.objects.create_user(email=email, password=password, role=role)

        if role == 'student':
            profile_data['user'] = user.id
            serializer = StudentSerializer(data=profile_data)
        else:
            profile_data['user'] = user.id
            serializer = TeacherSerializer(data=profile_data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "user": UserSerializer(user).data,
                "profile": serializer.data
            })
        else:
            user.delete()  
            return Response(serializer.errors, status=400)
        
