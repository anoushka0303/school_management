from rest_framework.serializers import ModelSerializer
from .models import *

class StudentSerializer(ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"

class TeacherSerializer(ModelSerializer):
    class Meta:
        model = Teacher
        fields = "__all__"

class PrincipalSerializer(ModelSerializer):
    class Meta:
        model = Principal
        fields = "__all__"

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"