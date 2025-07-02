import grpc
from concurrent import futures
from django.conf import settings

import core_pb2
import core_pb2_grpc

import sys
import os
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings')
django.setup()

from core.models import User, Student, Teacher, Principal
from django.utils import timezone

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


def verify_jwt(token_string):
    try:
        token = AccessToken(token_string)
        user_id = token["user_id"]
        role = token["role"]
        return {"user_id": user_id, "role": role}
    except Exception:
        return None


class AuthService(core_pb2_grpc.AuthServiceServicer):

    def Register(self, request, context):

        metadata = dict(context.invocation_metadata())
        auth_header = metadata.get("authorization")

        if not auth_header:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing Authorization header")

        if not auth_header:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid Authorization header")

        token_string = auth_header
        payload = verify_jwt(token_string)

        if not payload:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or expired token")

        if payload["role"] != "admin":
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Only admins can register new users")

        role = request.role
        email = request.email
        password = request.password

        if not all([role, email, password]):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Email, password, and role are required")

        if role not in ["student", "teacher", "principal"]:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid role")

        user = User.objects.create_user(
            email=email,
            password=password,
            role=role,
            created_date=timezone.now()
        )

        if role == "student":
            profile = Student.objects.create(
                user=user,
                name=request.student_profile.name,
                guardian_name=request.student_profile.guardian_name,
                guardian_contact=request.student_profile.guardian_contact,
                student_contact=request.student_profile.student_contact,
                class_name=request.student_profile.class_name,
                semester=request.student_profile.semester,
                address=request.student_profile.address,
                created_date=timezone.now(),
            )

            return core_pb2.RegisterReply(
                user=core_pb2.User(
                    id=user.id,
                    email=user.email,
                    role=user.role,
                    is_active=user.is_active
                ),
                student_profile=core_pb2.Student(
                    student_id=profile.student_id,
                    user_id=user.id,
                    name=profile.name,
                    guardian_name=profile.guardian_name,
                    guardian_contact=profile.guardian_contact,
                    student_contact=profile.student_contact,
                    class_name=profile.class_name,
                    semester=profile.semester,
                    address=profile.address
                )
            )

        elif role == "teacher":
            profile = Teacher.objects.create(
                user=user,
                name=request.teacher_profile.name,
                subject=request.teacher_profile.subject,
                created_date=timezone.now()
            )

            return core_pb2.RegisterReply(
                user=core_pb2.User(
                    id=user.id,
                    email=user.email,
                    role=user.role,
                    is_active=user.is_active
                ),
                teacher_profile=core_pb2.Teacher(
                    faculty_id=profile.faculty_id,
                    user_id=user.id,
                    name=profile.name,
                    subject=profile.subject
                )
            )

        elif role == "principal":
            profile = Principal.objects.create(
                user=user,
                name=request.principal_profile.name,
                created_date=timezone.now()
            )

            return core_pb2.RegisterReply(
                user=core_pb2.User(
                    id=user.id,
                    email=user.email,
                    role=user.role,
                    is_active=user.is_active
                ),
                principal_profile=core_pb2.Principal(
                    principal_id=profile.principal_id,
                    user_id=user.id,
                    name=profile.name
                )
            )

    def Login(self, request, context):
        email = request.email
        password = request.password
        role = request.role

        try:
            user = User.objects.get(email = email)
        except User.DoesNotExist:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "invalid credentials")

        if not user.check_password(password):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "invalid credentials")

        if not user.role == role:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "role mismatch")

        access_token = AccessToken.for_user(user)
        access_token['role'] = user.role
        refresh_token = RefreshToken.for_user(user)
        refresh_token['role'] = user.role

        profile = {}
        if user.role == "student":
            student = Student.objects.get(user=user)
            profile = {"student_profile": student}
        elif user.role == "teacher":
            teacher = Teacher.objects.get(user=user)
            profile = {"teacher_profile": teacher}
        elif user.role == "principal":
            principal = Principal.objects.get(user=user)
            profile = {"principal_profile": principal}

        return core_pb2.LoginReply(
            access_token=str(access_token),
            refresh_token=str(refresh_token),
            user=core_pb2.User(
                id=user.id,
                email=user.email,
                role=user.role
            ),
            **profile
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    core_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port('[::]:8000')
    server.start()
    print("gRPC server started on port 8000 🚀")
    server.wait_for_termination()


if __name__ == '__main__':
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings')
    django.setup()

    serve()