from rest_framework import serializers
from .models import *
from django.utils import timezone


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'grade']


class StudentCourseEnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['student', 'grade']

    def get_student(self, obj):
        return {
            "name": obj.student.name,
            "student_id": obj.student.student_id
        }


class StudentSerializer(serializers.ModelSerializer):
    enrollments = EnrollmentSerializer(source='enrollment_set', many=True, read_only=True)
    courses = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Course.objects.all(), write_only=True
    )
    courses_display = serializers.StringRelatedField(
        many=True, source='courses', read_only=True
    )
    user_email = serializers.EmailField(source='user.email', read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Student
        fields = [
            'student_id', 'user', 'user_email', 'name', 'guardian_name', 'guardian_contact',
            'student_contact', 'class_name', 'semester',
            'courses', 'courses_display', 'enrollments',
            'updated_date', 'updated_by', 'created_date', 'created_by',
            'deleted_date', 'deleted_by'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None

        courses = validated_data.pop('courses', [])
        student = Student.objects.create(**validated_data)
        student.courses.set(courses)

        student.created_by = user
        student.updated_by = user
        student.save()

        return student

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user if request else None

        courses = validated_data.pop('courses', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if courses is not None:
            instance.courses.set(courses)

        instance.updated_by = user
        instance.save()

        return instance

class GradeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['grade']

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.role != 'teacher':
            raise serializers.ValidationError("Only teachers can update grades.")

        if instance.course.teacher.user != user:
            raise serializers.ValidationError("You are not authorized to update this student's grade.")

        instance.grade = validated_data.get('grade', instance.grade)
        instance.updated_by = user
        instance.student.user.updated_by = user
        instance.student.update_date = timezone.now()
        instance.student.user.updated_by = user 
        instance.student.user.updated_date = timezone.now()
        instance.save()
        return instance


class StudentFeeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['fee_status']

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if user.role != 'admin':
            raise serializers.ValidationError("Only admins can update fee status.")

        instance.fee_status = validated_data.get('fee_status', instance.fee_status)
        instance.updated_by = user
        instance.updated_date = timezone.now()
        instance.user.updated_by = user 
        instance.user.updated_date = timezone.now()
        instance.save()
        return instance


class TeacherCourseSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'course_id', 'course_name', 'students'
        ]

    def get_students(self, course):
        enrollments = Enrollment.objects.filter(course=course)
        return StudentCourseEnrollmentSerializer(enrollments, many=True).data


class TeacherSerializer(serializers.ModelSerializer):
    courses = TeacherCourseSerializer(read_only=True)

    class Meta:
        model = Teacher
        fields = ['faculty_id', 'user', 'name', 'subject', 'courses']


class PrincipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Principal
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class StudentUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    guardian_name = serializers.CharField(required=False)
    guardian_contact = serializers.CharField(required=False)
    student_contact = serializers.CharField(required=False)
    address = serializers.CharField(required=False)

    class Meta:
        model = Student
        fields = ['name', 'guardian_name', 'guardian_contact', 'student_contact', 'address']

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.name = validated_data.get('name', instance.name)
        instance.guardian_name = validated_data.get('guardian_name', instance.guardian_name)
        instance.guardian_contact = validated_data.get('guardian_contact', instance.guardian_contact)
        instance.student_contact = validated_data.get('student_contact', instance.student_contact)
        instance.address = validated_data.get('address', instance.address)
        instance.updated_by = user 
        instance.updated_date = timezone.now()
        instance.user.updated_by = user 
        instance.user.updated_date = timezone.now()
        instance.save()
        return instance

class TeacherUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    subject = serializers.CharField(required=False)

    class Meta:
        model = Teacher
        fields = ['name', 'subject']

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.name = validated_data.get('name', instance.name)
        instance.subject = validated_data.get('subject', instance.subject)
        instance.updated_by = user 
        instance.updated_date = timezone.now()
        instance.user.updated_by = user 
        instance.user.updated_date = timezone.now()
        instance.save()
        return instance

class PrincipalUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)

    class Meta:
        model = Principal
        fields = ['name']

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.name = validated_data.get('name', instance.name)
        instance.updated_by = user 
        instance.updated_date = timezone.now()
        instance.user.updated_by = user 
        instance.user.updated_date = timezone.now()
        instance.save()
        return instance