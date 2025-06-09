from django.contrib import admin
from .models import Student, Teacher, Principal, User


admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Principal)
admin.site.register(User)