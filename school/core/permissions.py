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
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')
    
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