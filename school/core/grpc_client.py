import grpc
import core_pb2
import core_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:8000')
    stub = core_pb2_grpc.AuthServiceStub(channel)

    login_request = core_pb2.LoginRequest(
        email="anoushka.prakash@hashstudioz.com",
        password="admin123",
        role="admin"
    )
    login_reply = stub.Login(login_request)

    print("✅ Login successful!")
    print("Access Token:", login_reply.access_token)
    print("User:", login_reply.user)

    access_token = login_reply.access_token

    register_request = core_pb2.RegisterRequest(
        email="student1001@example.com",
        password="student123",
        role="student",
        student_profile=core_pb2.Student(
            name="John Doe",
            guardian_name="Jane Doe",
            guardian_contact="1234567890",
            student_contact="9876543210",
            course_ids=[1, 2, 3],
            class_name="10A",
            semester=1,
            address="123 School Street"
        )
    )

    metadata = [('authorization', f'{access_token}')]

    register_reply = stub.Register(register_request, metadata=metadata)

    print("✅ Register successful!")
    print("User Created:")
    print("ID:", register_reply.user.id)
    print("Email:", register_reply.user.email)
    print("Role:", register_reply.user.role)
    print("Student Name:", register_reply.student_profile.name)

if __name__ == '__main__':
    run()