from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save

ROLE_CHOICES = (
    ('student', 'Student'),
    ('teacher', 'Teacher'),
    ('principal', 'Principal'),
)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if role not in dict(ROLE_CHOICES):
            raise ValueError("Invalid role specified")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        if(role == 'principal'):
            user.is_superuser = True
            user.is_staff = True
        else:
            user.is_staff = False
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    guardian_name = models.CharField(max_length=100)
    guardian_contact = models.CharField(max_length=10)
    student_contact = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} ({self.user.role})"

    def clean(self):
        if self.user.role != 'student':
            raise ValidationError("Invalid role: Student model must be linked to a user with role 'student'.")

class Teacher(models.Model):
    faculty_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.user.role})"

    def clean(self):
        if self.user.role != 'teacher':
            raise ValidationError("Invalid role: Teacher model must be linked to a user with role 'teacher'.")

class Principal(models.Model):
    principal_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.user.role})"

    def clean(self):
        if self.user.role != 'principal':
            raise ValidationError("Invalid role: Principal model must be linked to a user with role 'principal'.")
        

'''@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'student':
            Student.objects.create(
                user=instance,
                name='Default Student Name',
                guardian_name='Default Guardian',
                guardian_contact='0000000000',
                student_contact='0000000000',
            )
        elif instance.role == 'teacher':
            Teacher.objects.create(
                user=instance,
                name='Default Teacher Name',
                subject='Default Subject',
            )
        elif instance.role == 'principal':
            Principal.objects.create(
                user=instance,
                name='Default Principal Name',
            )'''