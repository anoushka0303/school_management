from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.views import APIView

from .models import User, Student, Teacher, Principal, Course, Enrollment
from .serializers import *
from .permissions import IsStudent, IsTeacher, IsPrincipal, IsUser, IsAdmin

from django.utils import timezone

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsUser]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]


class PrincipalViewSet(viewsets.ModelViewSet):
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
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class GradeUpdateView(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = GradeUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role')

        if not email or not password or not role:
            return Response({"error": "Email, password and role required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()

        if not user or not user.check_password(password):
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.role != role:
            return Response({"error": f"User role mismatch. Expected role '{user.role}'."}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        return Response({
            "access": str(access_token),
            "refresh" : str(refresh_token),
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


class Register(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request):
        role = request.data.get('role')
        email = request.data.get('email')
        password = request.data.get('password')
        profile_data = request.data.get('profile', {})

        if not all([email, password, role]):
            return Response({"error": "email, password, and role are required"}, status=400)

        if role not in ['student', 'teacher', 'principal']:
            return Response({"error": "Only student or teacher can be created by admin"}, status=400)

        user = User.objects.create_user(email=email, password=password, role=role, created_date = timezone.now())
        profile_data['user'] = user.id

        

        if role == 'student':
            serializer = StudentSerializer(data=profile_data)
        else:
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



class UpdateView(viewsets.ModelViewSet):
    def get_queryset(self):
        update_type = self.request.data.get('update_type')
        if update_type == 'grade':
            return Enrollment.objects.all()
        return Student.objects.all()

    def get_object(self):
        update_type = self.request.data.get('update_type')
        if update_type == 'grade':
            return Enrollment.objects.get(pk=self.kwargs['pk'])
        return super().get_object()

    def get_serializer_class(self):
        update_type = self.request.data.get('update_type')
        if update_type == 'personal':
            return StudentPersonalInfoSerializer
        elif update_type == 'academic':
            return StudentAcademicInfoSerializer
        elif update_type == 'fee-status':
            return StudentFeeStatusSerializer
        elif update_type == 'address':
            return StudentAddressSerializer
        elif update_type == 'grade':
            return GradeUpdateSerializer
        else:
            raise ValidationError({'detail': 'Invalid update_type'})

    def get_permissions(self):
        update_type = self.request.data.get('update_type')
        perms = [permissions.IsAuthenticated()]

        if update_type in ['personal', 'address']:
            perms.append(IsStudent())
        elif update_type in ['academic', 'fee-status']:
            perms.append(IsAdmin())
        elif update_type == 'grade':
            perms.append(IsTeacher())
        return perms

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)