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
        
        access_token = jwt.encode(
            {"user_id": user.id, "role": role},
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        refresh_token = jwt.encode(
            {"user_id": user.id, "role": role, "refresh": True},
            settings.SECRET_KEY,
            algorithm="HS256"
        )

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

        #print(reply)

        return reply



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