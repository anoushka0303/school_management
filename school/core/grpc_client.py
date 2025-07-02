import grpc
import core_pb2
import core_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:8000')

    auth_stub = core_pb2_grpc.AuthServiceStub(channel)
    student_stub = core_pb2_grpc.StudentServiceStub(channel)

    login_request = core_pb2.LoginRequest(
        email="anoushka.prakash@hashstudioz.com",
        password="admin123",
        role="admin"
    )
    login_reply = auth_stub.Login(login_request)

    print("Login successful!")
    print("Access Token:", login_reply.access_token)
    print("User:", login_reply.user)

    metadata = [('authorization', f'Bearer {login_reply.access_token}')]

    get_students_request = core_pb2.GetStudentsRequest()

    get_students_reply = student_stub.ListStudents(get_students_request, metadata=metadata)

    print("All students listed!")
    for student in get_students_reply.students:
        print(f"ID: {student.student_id} | Name: {student.name}")

if __name__ == '__main__':
    run()