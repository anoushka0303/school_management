from rest_framework import serializers
from .models import *

class StudentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"

class TeacherSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Teacher
        fields = "__all__"

class PrincipalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Principal
        fields = "__all__"