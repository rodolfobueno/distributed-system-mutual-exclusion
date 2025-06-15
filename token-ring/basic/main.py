import socket
import threading
import time
import sys
import random

HOST = '127.0.0.1'
BUFFER_SIZE = 1024

def log(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

class TokenRingNode:
    def __init__(self, process_id, listen_port, next_port, next_host=HOST):
        self.process_id = process_id
        self.listen_port = listen_port
        self.next_host = next_host
        self.next_port = next_port
        self.running = True

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, self.listen_port))
        server.listen()

        log(f"[Process {self.process_id}] Listening on port {self.listen_port}...")

        while self.running:
            try:
                conn, _ = server.accept()
                token = conn.recv(BUFFER_SIZE).decode()
                if token == "token":
                    log(f"[Process {self.process_id}] Received token ✅")

                    should_enter = random.choice([True, False])

                    if should_enter:
                        log(f"[Process {self.process_id}] ENTERING critical section 🟢")
                        time.sleep(random.uniform(1, 10))
                        log(f"[Process {self.process_id}] EXITING critical section 🔴")
                    else:
                        log(f"[Process {self.process_id}] Skipping critical section ❌")

                    self.pass_token()

                conn.close()

            except Exception as e:
                log(f"[Process {self.process_id}] Error in server loop: {e}")

    def pass_token(self):
        time.sleep(2)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.next_host, self.next_port))
                s.sendall("token".encode())
                log(f"[Process {self.process_id}] Passed token ➡️ Port {self.next_port}")
        except Exception as e:
            log(f"[Process {self.process_id}] Failed to pass token: {e}")

    def start(self, start_with_token=False):
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()

        if start_with_token:
            log(f"[Process {self.process_id}] Waiting 3 seconds before sending first token...")
            time.sleep(3)
            self.pass_token()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            log(f"[Process {self.process_id}] Shutting down...")

if __name__ == "__main__":
    if len(sys.argv) not in [4, 5]:
        print("Usage: python token_ring_node.py <process_id> <listen_port> <next_port> [<next_host (default 127.0.0.1)>]")
        sys.exit(1)

    process_id = int(sys.argv[1])
    listen_port = int(sys.argv[2])
    next_port = int(sys.argv[3])
    next_host = sys.argv[4] if len(sys.argv) == 5 else HOST

    node = TokenRingNode(process_id, listen_port, next_port, next_host)
    node.start(start_with_token=(process_id == 0))
