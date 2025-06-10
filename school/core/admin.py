from django.contrib import admin
from .models import User, Student, Teacher, Principal, Course, Enrollment

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    fields = ('course', 'grade')

class CourseInline(admin.TabularInline):
    model = Course
    extra = 1
    fields = ('course_name',)

class StudentInline(admin.StackedInline):
    model = Student
    extra = 0

class TeacherInline(admin.StackedInline):
    model = Teacher
    extra = 0

class PrincipalInline(admin.StackedInline):
    model = Principal
    extra = 0

class StudentAdmin(admin.ModelAdmin):
    inlines = [EnrollmentInline]
    list_display = ['name', 'class_name', 'semester']

class CourseAdmin(admin.ModelAdmin):
    inlines = [EnrollmentInline]
    list_display = ['course_name', 'course_id', 'teacher']

class TeacherAdmin(admin.ModelAdmin):
    inlines = [CourseInline]
    list_display = ['name', 'subject']

class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'role', 'is_staff']
    inlines = []

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        if obj.role == 'student':
            return [StudentInline(self.model, self.admin_site)]
        elif obj.role == 'teacher':
            return [TeacherInline(self.model, self.admin_site)]
        elif obj.role == 'principal':
            return [PrincipalInline(self.model, self.admin_site)]
        return []

    def save_model(self, request, obj, form, change):
        if not change:
            if obj.role == 'student':
                obj.set_password('student123')
            elif obj.role == 'teacher':
                obj.set_password('teacher123')
            elif obj.role == 'principal':
                obj.set_password('principal123')
                obj.is_superuser = True
                obj.is_staff = True
        super().save_model(request, obj, form, change)

admin.site.register(User, UserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment)
admin.site.register(Teacher, TeacherAdmin)