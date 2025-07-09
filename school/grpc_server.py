import os
import django
import jwt

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings')
django.setup()


import grpc
from concurrent import futures
from core import core_pb2, core_pb2_grpc
from core.models import *
from core.serializers import *
from datetime import datetime
from django.utils.dateparse import parse_datetime
#from django.utils.timezone import is_aware, make_aware
from django.utils import timezone
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

from django.utils.dateparse import parse_datetime
from datetime import datetime, timezone as dt_timezone
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.response import Response
from core.utils import send_email


def safe_proto_timestamp(proto_field, dt_value):
    dt = None
    if isinstance(dt_value, datetime):
        dt = dt_value
    elif isinstance(dt_value, str):
        dt = parse_datetime(dt_value)
    if dt and dt.tzinfo is None:
        dt = dt.replace(tzinfo=dt_timezone.utc)
    if dt:
        proto_field.FromDatetime(dt)


def verify_jwt(context):
    metadata = dict(context.invocation_metadata())
    auth_header = metadata.get('authorization')
    if not auth_header:
        context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing authorization header")

    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    try:
        validated_token = AccessToken(token)
        user_id = validated_token['user_id']
        user = User.objects.get(id=user_id)
        return user
    except Exception as e:
        context.abort(grpc.StatusCode.UNAUTHENTICATED, f"Invalid token: {str(e)}")


class StudentService(core_pb2_grpc.StudentServiceServicer):
    def ListStudents(self, request, context):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many = True)
        reply = core_pb2.GetStudentsReply()
        #print(serializer.data)
        for student in serializer.data:
            student_msg = reply.students.add()
            '''if not student_msg.created_date:
                print("none")
            print(student["created_date"])'''
            safe_proto_timestamp(student_msg.created_date, student["created_date"])
            '''if not student_msg.created_date:
                print("none")
            else:
                print(student_msg.created_date)
            print(student["created_date"])'''
            student_msg.student_id = student["student_id"]
            student_msg.user_id.id = student["user"]["id"]
            student_msg.name = student["name"]
            student_msg.guardian_name = student["guardian_name"]
            student_msg.guardian_contact = student["guardian_contact"]
            #student_msg.created_date = student["created_date"]
            #student_msg.address = student["address"]
            student_msg.class_name = student["class_name"]
            student_msg.semester = student["semester"]
            #student_msg.fee_status = student["fee_status"]
        print("ListStudents called!")
        return reply

    def GetStudentById(self, request, context):
        reply = core_pb2.GetStudentReply()
        print("GetStudentById called!")
        return reply

    def DeleteStudent(self, request, context):
        reply = core_pb2.DeleteStudentReply()
        print("DeleteStudent called!")
        return reply
    


class AuthService(core_pb2_grpc.AuthServiceServicer):
    def Login(self, request, context):
        email= request.email
        password = request.password
        role = request.role
        print("login method called")
        try:
            user = User.objects.get(email= email)
            print(user)
        except Exception as e:
            context.set_details("user not found")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return core_pb2.LoginReply()
        
        if not user.check_password(password):
            context.set_details("invalid credentials")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            return core_pb2.LoginReply()
        
        access_token = str(AccessToken.for_user(user))
        refresh_token = str(RefreshToken.for_user(user))

        #print(f"access token {access_token}, refresh token {refresh_token}")

        user_msg = core_pb2.User(
            id=user.id,
            email=user.email,
            role=role
        )

        reply = core_pb2.LoginReply(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_msg
        )

        if role == "student":
            student = Student.objects.get(user=user)
            reply.student_profile.student_id = student.student_id
            reply.student_profile.class_name = student.class_name
        elif role == "teacher":
            teacher = Teacher.objects.get(user = user)
            reply.teacher_profile.teacher_id = teacher.faculty_id
        elif role == "principal":
            principal = Principal.objects.get(user = user)
            reply.principal_profile.principal_id = principal.principal_id

        if reply.HasField("student_profile"):
            print(reply)
        else:
            print(1)

        print(reply)

        return reply
    
    def Register(self, request, context):
        print("Register method called")
        email = request.email
        password = request.password
        role = request.role

        user = verify_jwt(context)
        print(user.id)
        print(type(user.id))
        if user.role != "admin":
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Only admins can register new users.")
        else:
            print("admin verified")

        if not all([email, password, role]):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Email, password, and role are required.")

        if role not in ["student", "teacher", "principal"]:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid role.")

        if User.objects.filter(email=email).exists():
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "User with this email already exists.")

        new_user = User.objects.create_user(
            email=email,
            password=password,
            role=role,
            created_date=timezone.now()
        )
        if role == "student" and request.HasField("student_profile"):
            profile_data = {
                "user": new_user.id,
                "name": request.student_profile.name,         
                "guardian_name": request.student_profile.guardian_name,
                "guardian_contact": request.student_profile.guardian_contact,
                "student_contact": request.student_profile.student_contact,
                "class_name": request.student_profile.class_name,
                "semester": request.student_profile.semester,
                "address": request.student_profile.address,
                "fee_status": request.student_profile.fee_status,
                "courses" : list(request.student_profile.course_ids),
                "created_date" : timezone.now().isoformat(),
                "created_by" : user.id
            }
            print(profile_data["created_by"])
            serializer = StudentSerializer(data=profile_data, context={'admin_user': user})
            
        elif role == "teacher" and request.HasField("teacher_profile"):
            profile_data = {"user": new_user.id}
            serializer = TeacherSerializer(data=profile_data)
        elif role == "principal" and request.HasField("principal_profile"):
            profile_data = {"user": new_user.id}
            serializer = PrincipalSerializer(data=profile_data)
        else:
            user.delete()
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Missing or invalid profile data.")

        if serializer.is_valid():
            instance = serializer.save()
            instance.created_date = timezone.now()
            instance.save()

            subject = "You have been registered on the platform"
            html = f"""
            <p>Hello,</p>
            <p>You have been registered as a <strong>{role}</strong> on the platform.</p>
            <p>Login email: <strong>{email}</strong></p>
            <p>Password : {password}</p>
            <p>Please reset your password after logging in.</p>
            """

            send_email(to_email=email,subject= subject,html_content= html)

            user_msg = core_pb2.User(
                id=new_user.id,
                email=new_user.email,
                role=new_user.role
            )

            reply = core_pb2.RegisterReply(user=user_msg)

            if role == "student":
                print(instance.created_by)
                reply.student_profile.student_id = instance.student_id
                reply.student_profile.name = instance.name
                reply.student_profile.guardian_name = instance.guardian_name
                reply.student_profile.guardian_contact = instance.guardian_name
                reply.student_profile.student_contact = instance.student_contact
                reply.student_profile.course_ids.extend(
                    instance.courses.values_list('course_id', flat=True)
                )
                reply.student_profile.class_name = instance.class_name
                reply.student_profile.semester = instance.semester
                safe_proto_timestamp(reply.student_profile.created_date, instance.created_date)
                #reply.student_profile.created_date = instance.created_date,
                #if instance.created_by is not None:
                    #reply.student_profile.created_by = instance.created_by
                #reply.student_profile.created_by = instance.created_by
                if instance.deleted_by is not None:
                    reply.student_profile.deleted_by = instance.deleted_by
            elif role == "teacher":
                reply.teacher_profile.teacher_id = instance.faculty_id
            elif role == "principal":
                reply.principal_profile.principal_id = instance.principal_id
            return reply

        else:
            new_user.delete()
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Profile validation error: {serializer.errors}")
        

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    core_pb2_grpc.add_StudentServiceServicer_to_server(StudentService(), server)
    core_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port('[::]:50051')
    print("starting gRPC server at port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()