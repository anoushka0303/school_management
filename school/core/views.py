from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.views import APIView

from .models import User, Student, Teacher, Principal, Course, Enrollment
from .serializers import *
from .permissions import IsStudent, IsTeacher, IsPrincipal, IsUser, IsAdminOrSelf, IsAdmin 

from django.utils import timezone

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsUser]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.IsAuthenticated(), IsStudent()]


    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"only admin can delete users."}, status= status.HTTP_403_FORBIDDEN)
        
        instance = self.get_object()
        instance.user.is_active = False
        instance.user.save()
        return Response({"user has been deleted."}, status= status.HTTP_204_NO_CONTENT)


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.IsAuthenticated(), IsTeacher()]


    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"only admin can delete users."}, status= status.HTTP_403_FORBIDDEN)
        
        instance = self.get_object()
        instance.user.is_active = False
        instance.user.save()
        return Response({"user has been deleted."}, status= status.HTTP_204_NO_CONTENT)


class PrincipalViewSet(viewsets.ModelViewSet):
    queryset = Principal.objects.all()
    serializer_class = PrincipalSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.IsAuthenticated(), IsPrincipal()]


    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"only admin can delete users."}, status= status.HTTP_403_FORBIDDEN)
        
        instance = self.get_object()
        instance.user.is_active = False
        instance.user.save()
        return Response({"user has been deleted."}, status= status.HTTP_204_NO_CONTENT)


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
    
    
class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        old_password = request.data.get('old_password')

        if not email or not old_password:
            return Response({"error": "Email and previous password is required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        if not user.is_active:
            return Response({"error" : "This user does not exist."}, status= 403)
        
        if not user.check_password(old_password):
            return Response({"error" : "Cannot change passowrd. Old password does not match"}, status= 403)

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