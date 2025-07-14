'''import grpc
import threading
import chat_pb2
import chat_pb2_grpc
import sys
import queue  

stop_event = threading.Event()

def send_messages(sender_name, receiver_name, send_queue):
    while not stop_event.is_set():
        msg = send_queue.get()
        if msg is None:
            break
        print(f"[CLIENT] Sending: {sender_name} → {receiver_name}: {msg}")
        yield chat_pb2.ChatMessage(
            sender= int(sender_name),
            receiver= int(receiver_name),
            message=msg
        )

def receive_messages(responses):
    try:
        for response in responses:
            print(f"\r{response.sender} → {response.receiver}: {response.message}\n> ", end="", flush=True)
    except grpc.RpcError as e:
        print(f"\n[CLIENT ERROR] {e}")
    finally:
        stop_event.set()

def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py <sender_name> <receiver_name>")
        sys.exit(1)

    sender_name = sys.argv[1]
    receiver_name = sys.argv[2]

    channel = grpc.insecure_channel('localhost:50051')
    chat_stub = chat_pb2_grpc.ChatStub(channel)

    jwt_token = ""

    metadata = [('authorization', f'Bearer {jwt_token}')]

    send_queue = queue.Queue()
    request_stream = send_messages(sender_name, receiver_name, send_queue)
    responses = chat_stub.ChatStream(request_stream, metadata= metadata)
    recv_thread = threading.Thread(target=receive_messages, args=(responses,), daemon=True)
    recv_thread.start()

    print(f"Connected as '{sender_name}'. Messages will go to '{receiver_name}'. Type /quit to exit.")

    try:
        while not stop_event.is_set():
            msg = input('> ')
            if msg.strip().lower() == '/quit':
                break
            send_queue.put(msg)
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        send_queue.put(None)
        stop_event.set()
        recv_thread.join(timeout=2)

if __name__ == '__main__':
    main()'''
import grpc
import threading
import chat_pb2
import chat_pb2_grpc
import sys
import queue

stop_event = threading.Event()

def send_messages(sender_id, receiver_id, send_queue):
    while not stop_event.is_set():
        msg = send_queue.get()
        if msg is None:
            break
        print(f"[CLIENT] Sending: {sender_id} → {receiver_id}: {msg}")
        yield chat_pb2.ChatMessage(
            sender=int(sender_id),  # still needed for proto
            receiver=int(receiver_id),
            message=msg
        )

def receive_messages(responses):
    try:
        for response in responses:
            print(f"\r[CLIENT] Receiving: {response.sender} → {response.receiver}: {response.message}\n> ", end="", flush=True)
    except grpc.RpcError as e:
        print(f"\n[CLIENT ERROR] {e}")
    finally:
        stop_event.set()

def main():
    if len(sys.argv) != 4:
        print("Usage: python client.py <sender_id> <receiver_id> <jwt_token>")
        sys.exit(1)

    sender_id = sys.argv[1]
    receiver_id = sys.argv[2]
    jwt_token = sys.argv[3]

    channel = grpc.insecure_channel('localhost:50052')
    chat_stub = chat_pb2_grpc.ChatStub(channel)

    metadata = [('authorization', f'Bearer {jwt_token}')]

    send_queue = queue.Queue()
    request_stream = send_messages(sender_id, receiver_id, send_queue)
    responses = chat_stub.ChatStream(request_stream, metadata=metadata)

    recv_thread = threading.Thread(target=receive_messages, args=(responses,), daemon=True)
    recv_thread.start()

    print(f"✅ Connected as '{sender_id}' → '{receiver_id}'. Type /quit to exit.")

    try:
        while not stop_event.is_set():
            msg = input('> ')
            if msg.strip().lower() == '/quit':
                break
            send_queue.put(msg)
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        send_queue.put(None)
        stop_event.set()
        recv_thread.join(timeout=2)

if __name__ == '__main__':
    main()