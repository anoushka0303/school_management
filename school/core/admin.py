from django.contrib import admin
from .models import Student, Teacher, Principal


admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Principal)