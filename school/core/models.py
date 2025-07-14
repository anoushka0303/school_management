from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
import bcrypt
from django.contrib.auth.hashers import check_password as django_check_password


ROLE_CHOICES = (
    ('student', 'Student'),
    ('teacher', 'Teacher'),
    ('principal', 'Principal'),
    ('admin', 'Admin'),
)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if role not in dict(ROLE_CHOICES):
            raise ValueError("Invalid role specified")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        if role == 'principal':
            user.is_staff = True
        else:
            user.is_staff = False
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
    
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(null = True, blank= True)
    updated_by = models.ForeignKey('self', on_delete=models.SET_NULL, null= True,blank=True, related_name='updated_user')
    created_date = models.DateTimeField(null = True, blank= True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null= True,blank=True, related_name='created_user')
    deleted_date = models.DateTimeField(null = True, blank= True)
    deleted_by = models.ForeignKey('self', on_delete= models.SET_NULL, null= True,blank=True, related_name= 'deleted_user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

    def set_password(self, raw_password):
        hashed = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
        self.password = hashed.decode('utf-8')

    def check_password(self, raw_password):
        try:
            return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))
        except ValueError:
            return django_check_password(raw_password, self.password)



class Teacher(models.Model):
    faculty_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=50)
    updated_date = models.DateTimeField(null = True, blank= True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null= True, related_name='updated_teacher')
    created_date = models.DateTimeField(null = True, blank= True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null= True, related_name='created_teacher')
    deleted_date = models.DateTimeField(null = True, blank= True)
    deleted_by = models.ForeignKey(User, on_delete= models.SET_NULL, null= True, related_name= 'deleted_teacher')

    def __str__(self):
        return f"{self.name} ({self.user.role})"

    def clean(self):
        if self.user.role != 'teacher':
            raise ValidationError("Invalid role: Teacher model must be linked to a user with role 'teacher'.")

class Course(models.Model):
    course_name = models.CharField(max_length=50)
    course_id = models.AutoField(primary_key=True)
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return f"{self.course_name} - {self.teacher.name}"

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    guardian_name = models.CharField(max_length=100)
    guardian_contact = models.CharField(max_length=10)
    student_contact = models.CharField(max_length=10)
    class_name = models.CharField(max_length=20, default='NA')
    semester = models.IntegerField(default=1)
    courses = models.ManyToManyField(Course, through='Enrollment', related_name='students')
    address = models.TextField(null = True, blank= True)
    updated_date = models.DateTimeField(null = True, blank= True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null= True, related_name='updated_student')
    created_date = models.DateTimeField(null= True, blank= True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null= True, related_name='created_student')
    deleted_date = models.DateTimeField(null = True, blank= True)
    deleted_by = models.ForeignKey(User, on_delete= models.SET_NULL, null= True, related_name= 'deleted_student')
    fee_status = models.CharField(max_length=50, default='unpaid')


    def __str__(self):
        return f"{self.name} ({self.user.role})"

    def clean(self):
        if self.user.role != 'student':
            raise ValidationError("Invalid role: Student model must be linked to a user with role 'student'.")

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2, null=True, blank=True)
    updated_date = models.DateTimeField(null = True, blank= True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null= True, related_name='updated_enrollment')

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.name} in {self.course.course_name} - Grade: {self.grade or 'N/A'}"

class Principal(models.Model):
    principal_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    updated_date = models.DateTimeField(null = True, blank= True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null= True, related_name='updated_principal')
    created_date = models.DateTimeField(null = True, blank= True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null= True, related_name='created_principal')
    deleted_date = models.DateTimeField(null = True, blank= True)
    deleted_by = models.ForeignKey(User, on_delete= models.SET_NULL, null= True, related_name= 'deleted_principal')

    def __str__(self):
        return f"{self.name} ({self.user.role})"

    def clean(self):
        if self.user.role != 'principal':
            raise ValidationError("Invalid role: Principal model must be linked to a user with role 'principal'.")
        

class BulkUploadStatus(models.Model):
    status_choices = (
        ('success', 'Success'),
        ('partial_success', 'Partial_success'),
        ('failure', 'Failure'),
        ('uploading', 'Uploading')
    )
    uploaded_by = models.ForeignKey(User, on_delete= models.CASCADE)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices= status_choices, default='uploading')
    file_name = models.CharField(max_length=100)
    total_record = models.IntegerField()
    success_count = models.IntegerField()
    failure_count = models.IntegerField()
    remarks = models.TextField()
    file = models.URLField(null = True, blank= True)

    def __str__(self):
        return f"{self.file_name} - {self.status}"
    

class ChatSystem(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'receiver')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.sender.email} -> {self.receiver.email} : {self.message[:20]}"



@receiver(post_save, sender=Teacher)
def create_course_for_teacher(sender, instance, created, **kwargs):
    if created:
        Course.objects.create(
            course_name=f"{instance.subject} Course",
            teacher=instance
        )

@receiver(m2m_changed, sender=Student.courses.through)
def create_enrollment_on_course_add(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "post_add":
        for course_pk in pk_set:
            course = Course.objects.filter(pk=course_pk).first()
            if course and not Enrollment.objects.filter(student=instance, course=course).exists():
                Enrollment.objects.create(student=instance, course=course)


@receiver(post_save, sender=Student)
def mirror_student_fields_to_user(sender, instance, **kwargs):
    user = instance.user
    updated = False
    if instance.deleted_by and (user.deleted_by != instance.deleted_by or not user.deleted_by):
        user.deleted_by = instance.deleted_by
        updated = True
    if instance.deleted_date and (user.deleted_date != instance.deleted_date or not user.deleted_date):
        user.deleted_date = instance.deleted_date
        updated = True
    if instance.created_by and (user.created_by != instance.created_by or not user.created_by):
        user.created_by = instance.created_by
        updated = True
    if instance.created_date and (user.created_date != instance.created_date or not user.created_date):
        user.created_date = instance.created_date
        updated = True
    if updated:
        user.save()

@receiver(post_save, sender=Teacher)
def mirror_teacher_fields_to_user(sender, instance, **kwargs):
    user = instance.user
    updated = False
    if instance.deleted_by and (user.deleted_by != instance.deleted_by or not user.deleted_by):
        user.deleted_by = instance.deleted_by
        updated = True
    if instance.deleted_date and (user.deleted_date != instance.deleted_date or not user.deleted_date):
        user.deleted_date = instance.deleted_date
        updated = True
    if instance.created_by and (user.created_by != instance.created_by or not user.created_by):
        user.created_by = instance.created_by
        updated = True
    if instance.created_date and (user.created_date != instance.created_date or not user.created_date):
        user.created_date = instance.created_date
        updated = True
    if updated:
        user.save()

@receiver(post_save, sender=Principal)
def mirror_principal_fields_to_user(sender, instance, **kwargs):
    user = instance.user
    updated = False
    if instance.deleted_by and (user.deleted_by != instance.deleted_by or not user.deleted_by):
        user.deleted_by = instance.deleted_by
        updated = True
    if instance.deleted_date and (user.deleted_date != instance.deleted_date or not user.deleted_date):
        user.deleted_date = instance.deleted_date
        updated = True
    if instance.created_by and (user.created_by != instance.created_by or not user.created_by):
        user.created_by = instance.created_by
        updated = True
    if instance.created_date and (user.created_date != instance.created_date or not user.created_date):
        user.created_date = instance.created_date
        updated = True
    if updated:
        user.save()