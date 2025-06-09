from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Permission, Group

# Create your models here.

role_choices = (
    ('student', 'Student'),
    ('teacher', 'Teacher'),
    ('principal', 'Principal'),
    )

'''class User(AbstractBaseUser):
    role = models.CharField(max_length= 50, choices= role_choices)
    email = models.CharField(max_length= 50, unique= True)'''

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, role='principal', **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=role_choices)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        related_name='core_user',  
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    # Override user_permissions field similarly
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='core_user_permissions',  # change this from default 'user_set'
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    objects = UserManager()

    def __str__(self):
        return self.email

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete= models.CASCADE)
    name = models.CharField(max_length= 100)
    guardian_name = models.CharField(max_length= 100)
    guardian_contact = models.CharField(max_length=10)
    student_contact = models.CharField(max_length=10)
    #role = models.CharField(max_length= 50, choices= role_choices)

    def __str__(self):
        return f"{self.name} ({self.user.role})"
    
    def clean(self):
        if self.user.role != 'student':
            raise ValidationError("invalid role for student. the role should be 'student'")
    
class Teacher(models.Model):
    faculty_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete= models.CASCADE)
    name = models.CharField(max_length= 100)
    subject = models.CharField(max_length= 50)
    #role = models.CharField(max_length= 50, choices= role_choices)

    def __str__(self):
        return f"{self.name} ({self.user.role})"
    
    def clean(self):
        if self.user.role != 'teacher':
            raise ValidationError("invalid role for teacher. the role should be 'teacher'")
    

class Principal(models.Model):
    principal_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length= 50)
    user = models.OneToOneField(User, on_delete= models.CASCADE)
    #role = models.CharField(max_length= 50, choices= role_choices)

    def clean(self):
        if self.user.role != 'principal':
            raise ValidationError("invalid role for principal. the role should be 'principal'")

    def __str__(self):
        return f"{self.name} ({self.user.role})"