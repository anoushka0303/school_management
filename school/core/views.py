from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.views import APIView

from .models import User, Student, Teacher, Principal, Course, Enrollment
from .serializers import *
from .permissions import *

from django.utils import timezone

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

import openpyxl

from openpyxl.utils import get_column_letter
from django.http import HttpResponse

import os
from django.conf import settings

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'list' or self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsAdmin()]
        elif self.action == 'retrieve':
            return [permissions.IsAuthenticated(), IsUser()]
        
    def get_object(self):
        obj = super().get_object()
        user = self.request.user

        if self.action == 'retrieve' and not (user.role == 'admin' or obj == user):
            return Response(
                {"detail": "Forbidden access. You can only view your own profile."},
                status= 403
            )
        


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.IsAuthenticated(), IsAdmin()]
        elif self.action == 'retrieve':
            return [permissions.IsAuthenticated(), IsAdminOrSelfForStudent()]
        elif self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"only admin can delete users."}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        instance.user.is_active = False
        instance.deleted_by = request.user
        instance.deleted_date = timezone.now()
        instance.created_by = request.user
        instance.created_date = timezone.now()
        instance.user.save()
        instance.save()
        return Response({"user has been deleted."}, status=status.HTTP_204_NO_CONTENT)


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.IsAuthenticated(), IsAdmin()]
        elif self.action == 'retrieve':
            return [permissions.IsAuthenticated(), IsAdminOrSelfForTeacher()]
        elif self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"only admin can delete users."}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        instance.user.is_active = False
        instance.deleted_by = request.user
        instance.deleted_date = timezone.now()
        instance.created_by = request.user
        instance.created_date = timezone.now()
        instance.user.save()
        instance.save()
        return Response({"user has been deleted."}, status=status.HTTP_204_NO_CONTENT)


class PrincipalViewSet(viewsets.ModelViewSet):
    queryset = Principal.objects.all()
    serializer_class = PrincipalSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.IsAuthenticated(), IsAdmin()]
        elif self.action == 'retrieve':
            return [permissions.IsAuthenticated(), IsAdminOrSelfForPrincipal()]  
        elif self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"only admin can delete users."}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        instance.user.is_active = False
        instance.deleted_by = request.user
        instance.deleted_date = timezone.now()
        instance.user.created_by = request.user
        instance.user.created_date = timezone.now()

        instance.created_by = request.user
        instance.created_date = timezone.now()
        instance.user.save()
        instance.save()
        return Response({"user has been deleted."}, status=status.HTTP_204_NO_CONTENT)


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
    permission_classes = [permissions.IsAuthenticated, CanUpdateOwnStudentGradeOnly]


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role')

        if not email or not password or not role:
            return Response({
                "message": f"Bad request. Email, password and role needed",
                "status" : 400,
                "has_error" : True
                }, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()

        if not user or not user.check_password(password):
            return Response({
                "message": f"Unauthorized access. Invalid credentials.",
                "status" : 401,
                "has_error" : True,
                }, status=401)

        if user.role != role:
            return Response({
                "message": f"Unauthorized access. User role mismatch. Expected role '{user.role}'.",
                "status" : 401,
                "has_error" : True,
                }, status=401)

        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        return Response({
            "messgae" : "Login Successful",
            "has_error" : False,
            "status" : 200,
            "access": str(access_token),
            "refresh" : str(refresh_token),
            "user": {
                "email": user.email,
                "role": user.role,
            }
        }, status=200)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return User.objects.all()
        return User.objects.filter(id=user.id)


class Register(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request):
        role = request.data.get('role')
        email = request.data.get('email')
        password = request.data.get('password')
        profile_data = request.data.get('profile', {})

        if not all([email, password, role]):
            return Response({
                "has_error" : True,
                "status" : 400,
                "message": "Bad Request. Email, password, and role are required"
                }, status=400)

        if role not in ['student', 'teacher', 'principal']:
            return Response({
                "has_error" : True,
                "status" : 400,
                "message": "Bad Request. Only student, teacher or principal can be created by admin"
                }, status=400)

        user = User.objects.create_user(email=email, password=password, role=role, created_date = timezone.now())
        profile_data['user'] = user.id

        if role == 'student':
            serializer = StudentSerializer(data=profile_data)
        elif role == 'teacher':
            serializer = TeacherSerializer(data=profile_data)
        elif role == 'principal':
            serializer = PrincipalSerializer(data=profile_data)

        if serializer.is_valid():
            instance = serializer.save()
            instance.created_by = request.user
            instance.created_date = timezone.now()
            instance.user.created_by = request.user
            instance.user.created_date = timezone.now()
            instance.save()
            return Response({
                "user": UserSerializer(user).data,
                "profile": serializer.data
            })
        else:
            user.delete()
            return Response(serializer.errors, status=400)



'''class UpdateView(viewsets.ModelViewSet):
    def get_queryset(self):
        update_type = self.request.data.get('update_type')
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
        return super().partial_update(request, *args, **kwargs)'''
    
    
class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        old_password = request.data.get('old_password')

        if not email or not old_password:
            return Response({
                "has_error" : True,
                "status" : 400,
                "message": "Bad request. Email and previous password is required"
                }, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "has_error" : True,
                "status" : 404,
                "message": "User not found"
                }, status=404)
        
        if not user.is_active:
            return Response({
                "has_error" : True,
                "status" : 404,
                "message": "User not found"
                }, status= 404)
        
        if not user.check_password(old_password):
            return Response({
                "has_error" : True,
                "status" : 403,
                "message" : "Forbidden error. Old password does not match."
                }, status= 403)

        uid = urlsafe_base64_encode(force_bytes(user.pk))  
        token = PasswordResetTokenGenerator().make_token(user)  

        return Response({
            "uid": uid,
            "token": token
        }, status=200)
    

class ConfirmPasswordResetView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not all([uid, token, new_password]):
            return Response({"error": "uid, token and new_password are required"}, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid UID"}, status=400)

        if not token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successful"}, status=200)
    
class StudentUpdateView(viewsets.ViewSet):
    serializer_class = StudentUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelfForStudent]

    def get_object(self):
        if self.request.user.is_staff:
            student_id = self.kwargs.get('pk')
            return Student.objects.get(pk=student_id)
        return Student.objects.get(user=self.request.user)

    def partial_update(self, request, pk=None):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherUpdateView(viewsets.ModelViewSet):
    serializer_class = TeacherUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher, IsAdminOrSelfForTeacher]

    def get_object(self):
        return Teacher.objects.get(user=self.request.user)


class PrincipalUpdateView(viewsets.ModelViewSet):
    serializer_class = PrincipalUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelfForPrincipal]
    http_method_names = ['patch']  # restrict to PATCH only

    def get_object(self):
        return Principal.objects.get(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    


class UpdateFeeStatusView(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentFeeStatusSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance) 

        serializer = self.get_serializer(instance, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
import os
import openpyxl

class BulkDownloadStudentExcelView(APIView):

    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        students = Student.objects.all()
        serializer = BulkDownloadSerializer(students, many=True)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Students"

        headers = list(serializer.data[0].keys()) if serializer.data else []
        ws.append(headers)

        for student in serializer.data:
            row = []
            for field in headers:
                value = student.get(field, "")
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                elif isinstance(value, dict):
                    value = str(value)
                row.append(value)
            ws.append(row)

        folder_path = os.path.join(settings.MEDIA_ROOT, 'exports')
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, 'students.xlsx')
        wb.save(file_path)

        file_url = request.build_absolute_uri(settings.MEDIA_URL + 'exports/students.xlsx')

        return Response({'file_url': file_url})