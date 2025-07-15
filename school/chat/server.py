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
                            print("❌ Authenticated user does not match sender")
                            continue

                        if receiver_name == 0:
                            user_msg = msg.message.strip().lower()
                            print(f"[SERVER BOT] User {sender_id} says: {user_msg}")

                            if user_msg in ['1', 'account', 'account issues']:
                                bot_message = "You chose Account Issues.\nPlease visit: https://example.com/account-help"
                            elif user_msg in ['2', 'payment', 'payments', 'refund']:
                                bot_message = "You chose Payments & Refunds.\nPlease visit: https://example.com/payment-help"
                            elif user_msg in ['3', 'technical', 'tech support']:
                                bot_message = "You chose Technical Support.\nPlease visit: https://example.com/tech-support"
                            elif user_msg.startswith('/handover'):
                                parts = user_msg.split()
                                if len(parts) == 2 and parts[1].isdigit():
                                    human_id = int(parts[1])
                                    if not User.objects.filter(id=human_id).exists():
                                        print(f"[SERVER] Unknown receiver: {human_id}")
                                        continue
                                    print(f"[SERVER] {sender_id} → {human_id}: {msg.message}")
                                    found_receiver = False
                                    with self.lock:
                                        for cq, sname in self.clients:
                                            if sname == human_id:
                                                cq.put(chat_pb2.ChatMessage(
                                                    sender=int(sender_id),
                                                    receiver=int(human_id),
                                                    message=msg.message
                                                ))
                                                found_receiver = True
                                                break
                                    if not found_receiver:
                                        print(f"[SERVER] Receiver {human_id} not connected.")
                                        break
                                    bot_message = f"Connecting you to human agent {human_id}..."
                                else:
                                    bot_message = "Usage: /handover <receiver_id>"
                            else:
                                bot_message = (
                                    "I didn’t understand that.\n"
                                    "Please select:\n"
                                    "1 Account Issues\n"
                                    "2 Payments & Refunds\n"
                                    "3 Technical Support\n"
                                    "Or type /handover <receiver_id> to chat with a human."
                                )

                            with self.lock:
                                for cq, sname in self.clients:
                                    if sname == sender_id:
                                        cq.put(chat_pb2.ChatMessage(
                                            sender=0,
                                            receiver=int(sender_id),
                                            message=bot_message
                                        ))
                                        break

                        else:
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