from rest_framework import serializers
from .models import *


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

    class Meta:
        model = Student
        fields = [
            'student_id', 'user', 'name', 'guardian_name', 'guardian_contact',
            'student_contact', 'class_name', 'semester', 'enrollments',
            'updated_date', 'updated_by', 'created_date', 'created_by',
            'deleted_date', 'deleted_by'
        ]


class StudentPersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['name', 'guardian_name', 'guardian_contact', 'student_contact']

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if user.role != 'student' or instance.user != user:
            raise serializers.ValidationError("You are not authorized to update this information.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updated_by = user
        instance.save()
        return instance


class StudentAcademicInfoSerializer(serializers.ModelSerializer):
    enrollments = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['class_name', 'semester', 'enrollments']

    def get_enrollments(self, obj):
        enrollments = Enrollment.objects.filter(student=obj)
        return StudentCourseEnrollmentSerializer(enrollments, many=True).data

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.role == 'admin':
            instance.class_name = validated_data.get('class_name', instance.class_name)
            instance.semester = validated_data.get('semester', instance.semester)
            instance.updated_by = user
            instance.save()
            return instance

        raise serializers.ValidationError("Only admins can update academic information here.")


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


'''class AdminSerializer(serializers.Serializer):
    students = StudentSerializer(source='get_students', many=True)
    teachers = TeacherSerializer(source='get_teachers', many=True)
    principals = PrincipalSerializer(source='get_principals', many=True)
    courses = serializers.SerializerMethodField()

    def get_students(self, obj):
        return Student.objects.all()

    def get_teachers(self, obj):
        return Teacher.objects.all()

    def get_principals(self, obj):
        return Principal.objects.all()

    def get_courses(self, obj):
        return Course.objects.all()'''


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
        instance.name = validated_data.get('name', instance.name)
        instance.guardian_name = validated_data.get('guardian_name', instance.guardian_name)
        instance.guardian_contact = validated_data.get('guardian_contact', instance.guardian_contact)
        instance.student_contact = validated_data.get('student_contact', instance.student_contact)
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        return instance

class TeacherUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    subject = serializers.CharField(required=False)

    class Meta:
        model = Teacher
        fields = ['name', 'subject']

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.subject = validated_data.get('subject', instance.subject)
        instance.save()
        return instance

class PrincipalUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)

    class Meta:
        model = Principal
        fields = ['name']

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance