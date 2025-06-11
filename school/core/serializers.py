from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import *


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class EnrollmentSerializer(ModelSerializer):
    course = CourseSerializer(read_only=True)
    class Meta:
        model = Enrollment
        fields = ['course', 'grade']


class StudentCourseEnrollmentSerializer(ModelSerializer):
    student = SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['student', 'grade']

    def get_student(self, obj):
        return {
            "name": obj.student.name,
            "student_id": obj.student.student_id
        }


class StudentSerializer(ModelSerializer):
    enrollments = EnrollmentSerializer(source='enrollment_set', many=True, read_only=True)

    class Meta:
        model = Student
        fields = ['student_id', 'user', 'name', 'guardian_name', 'guardian_contact', 'student_contact', 'class_name', 'semester', 'enrollments']


class TeacherCourseSerializer(ModelSerializer):
    students = SerializerMethodField()

    class Meta:
        model = Course
        fields = ['course_id', 'course_name', 'students']

    def get_students(self, course):
        enrollments = Enrollment.objects.filter(course=course)
        return StudentCourseEnrollmentSerializer(enrollments, many=True).data


class TeacherSerializer(ModelSerializer):
    courses = TeacherCourseSerializer(read_only=True)

    class Meta:
        model = Teacher
        fields = ['faculty_id', 'user', 'name', 'subject', 'courses']


class PrincipalSerializer(ModelSerializer):
    class Meta:
        model = Principal
        fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'