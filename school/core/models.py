from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

role_choices = (
    ('student', 'Student'),
    ('teacher', 'Teacher'),
    ('principal', 'Principal'),
    )

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length= 100)
    guardian_name = models.CharField(max_length= 100)
    guardian_contact = models.CharField(max_length=10)
    student_contact = models.CharField(max_length=10)
    role = models.CharField(max_length= 50, choices= role_choices)

    def __str__(self):
        return f"{self.name} ({self.role})"
    
    def clean(self):
        if self.role != 'student':
            raise ValidationError("invalid role for student. the role should be 'student'")
    
class Teacher(models.Model):
    faculty_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length= 100)
    subject = models.CharField(max_length= 50)
    role = models.CharField(max_length= 50, choices= role_choices)

    def __str__(self):
        return f"{self.name} ({self.role})"
    
    def clean(self):
        if self.role != 'teacher':
            raise ValidationError("invalid role for teacher. the role should be 'teacher'")
    

class Principal(models.Model):
    name = models.CharField(max_length= 50)
    role = models.CharField(max_length= 50, choices= role_choices)

    def clean(self):
        if self.role != 'principal':
            raise ValidationError("invalid role for principal. the role should be 'principal'")

    def __str__(self):
        return f"{self.name}"