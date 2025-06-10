'''from django.contrib import admin
from .models import Student, Teacher, Principal, User, UserManager


admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Principal)
admin.site.register(User)'''
from django.contrib import admin
from .models import User, Student, Teacher, Principal

class StudentInline(admin.StackedInline):
    model = Student
    extra = 0

class TeacherInline(admin.StackedInline):
    model = Teacher
    extra = 0

class PrincipalInline(admin.StackedInline):
    model = Principal
    extra = 0

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