from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'student')
    
class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'teacher')

class IsPrincipal(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'principal')
    
class IsUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == 'admin' or request.user.role == 'principal'))
    
class IsAdminOrSelf(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'admin':
            return True

        if view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True

        return obj == request.user
    
class IsAdminOrSelfForTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or getattr(user, 'role', None) == 'admin' or getattr(user, 'role', None) == 'principal':
            return True

        if hasattr(user, 'teacher') and obj.user == user:
            return True

        return False

class IsAdminOrSelfForStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or getattr(user, 'role', None) == 'admin' or getattr(user, 'role', None) == 'principal':
            return True

        if hasattr(user, 'student') and obj.user == user:
            return True

        return False
    
class IsAdminOrSelfForPrincipal(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or getattr(user, 'role', None) == 'admin':
            return True

        if hasattr(user, 'principal') and obj.user == user:
            return True

        return False

class CanViewOwnStudentsOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'teacher')

    def has_object_permission(self, request, view, obj):
        return obj.course.teacher.user == request.user

class CanUpdateOwnStudentGradeOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or (
            hasattr(request.user, 'teacher') and obj.course.teacher.user == request.user
        )