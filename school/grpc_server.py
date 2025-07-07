import os
import django

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

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
core_pb2_grpc.add_StudentServiceServicer_to_server(StudentService(), server)
server.add_insecure_port('[::]:50051')
print("starting gRPC server at port 50051")
server.start()
server.wait_for_termination()