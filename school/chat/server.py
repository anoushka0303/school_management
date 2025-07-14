'''import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings')
django.setup()

from core.models import User

import grpc
from concurrent import futures
import time
import threading
import queue
import chat_pb2
import chat_pb2_grpc
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


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

class ChatServer(chat_pb2_grpc.ChatServicer):
    def __init__(self):
        self.clients = []
        self.lock = threading.Lock()

    def ChatStream(self, request_iterator, context):
        q = queue.Queue()
        sender_name = None
        receiver_name = None

        user = verify_jwt(context)
        sender_id = str(user.id)  
        print(f"[SERVER] Authenticated user {sender_id} with JWT")

        with self.lock:
            self.clients.append((q, None))

        def cleanup():
            with self.lock:
                self.clients = [(cq, sname) for cq, sname in self.clients if cq != q]

        try:
            def read_requests():
                nonlocal sender_name
                nonlocal receiver_name

                try:
                    for msg in request_iterator:
                        if sender_name is None:
                            sender_name = msg.sender
                            receiver_name = msg.receiver
                            if not User.objects.filter(id= sender_name).exists():
                                print(f"[SERVER] Unknown sender: {sender_name}")
                                return
                            
                            if not User.objects.filter(id = receiver_name):
                                print(f"[SERVER] Unknown receiver: {receiver_name}")
                                return

                            with self.lock:
                                for i, (cq, sname) in enumerate(self.clients):
                                    if cq == q:
                                        self.clients[i] = (cq, sender_name)
                                        break

                            print(f"[SERVER] Registered sender: {sender_name}")

                        print(f"[SERVER] {msg.sender} → {msg.receiver}: {msg.message}")
                        if not User.objects.filter(id=msg.receiver).exists():
                            print(f"[SERVER] Unknown receiver: {msg.receiver}")
                            continue

                        found_receiver = False
                        with self.lock:
                            for cq, sname in self.clients:
                                if sname == msg.receiver:
                                    cq.put(msg)
                                    found_receiver = True
                                    break

                        if not found_receiver:
                            print(f"[SERVER] Receiver {msg.receiver} not connected.")


                except Exception as e:
                    print(f"[SERVER] Error in read_requests: {e}")
                    import traceback
                    traceback.print_exc()

            t = threading.Thread(target=read_requests, daemon=True)
            t.start()

            while True:
                try:
                    msg = q.get(timeout=0.1)
                    yield msg
                except queue.Empty:
                    if context.is_active():
                        continue
                    else:
                        break
        finally:
            cleanup()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServicer_to_server(ChatServer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('Server started on port 50051')

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print('Server stopping...')
        server.stop(0)

if __name__ == '__main__':
    serve()'''
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings')
django.setup()

from core.models import User
import grpc
from concurrent import futures
import time
import threading
import queue
import chat_pb2
import chat_pb2_grpc
from rest_framework_simplejwt.tokens import AccessToken

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

class ChatServer(chat_pb2_grpc.ChatServicer):
    def __init__(self):
        self.clients = []
        self.lock = threading.Lock()

    def ChatStream(self, request_iterator, context):
        q = queue.Queue()
        sender_name = None
        receiver_name = None

        # ✅ Verify JWT and get the sender user
        user = verify_jwt(context)
        sender_id = user.id
        print(f"[SERVER] Authenticated user {sender_id} with JWT")

        

        with self.lock:
            self.clients.append((q, sender_id))

        def cleanup():
            with self.lock:
                self.clients = [(cq, sname) for cq, sname in self.clients if cq != q]

        try:
            def read_requests():
                nonlocal sender_name
                nonlocal receiver_name
                try:
                    for msg in request_iterator:
                        sender_name = msg.sender
                        receiver_name = msg.receiver

                        if sender_id != sender_name:
                            print("the authenticated user is not the same as the sender")
                            continue

                        # ✅ Verify receiver exists
                        if not User.objects.filter(id=receiver_name).exists():
                            print(f"[SERVER] Unknown receiver: {receiver_name}")
                            continue

                        print(f"[SERVER] {sender_id} → {receiver_name}: {msg.message}")

                        found_receiver = False
                        with self.lock:
                            for cq, sname in self.clients:
                                if sname == receiver_name:
                                    cq.put(chat_pb2.ChatMessage(
                                        sender=int(sender_id),
                                        receiver=int(receiver_name),
                                        message=msg.message
                                    ))
                                    found_receiver = True
                                    break

                        if not found_receiver:
                            print(f"[SERVER] Receiver {receiver_name} not connected.")
                except Exception as e:
                    print(f"[SERVER] Error in read_requests: {e}")

            t = threading.Thread(target=read_requests, daemon=True)
            t.start()

            while True:
                try:
                    msg = q.get(timeout=0.1)
                    yield msg
                except queue.Empty:
                    if context.is_active():
                        continue
                    else:
                        break
        finally:
            cleanup()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServicer_to_server(ChatServer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print('✅ Server started on port 50052')
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print('Server stopping...')
        server.stop(0)

if __name__ == '__main__':
    serve()