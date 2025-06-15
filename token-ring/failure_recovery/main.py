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
    def __init__(self, process_id, listen_port, ring_ports):
        self.process_id = process_id
        self.listen_port = listen_port
        self.ring_ports = ring_ports  # Lista com todas as portas na ordem do anel
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
                        time.sleep(random.uniform(1, 2))
                        log(f"[Process {self.process_id}] EXITING critical section 🔴")
                    else:
                        log(f"[Process {self.process_id}] Skipping critical section ❌")

                    time.sleep(3)
                    self.pass_token()

                conn.close()

            except Exception as e:
                log(f"[Process {self.process_id}] Server error: {e}")

    def pass_token(self):
        time.sleep(1)
        next_index = (self.ring_ports.index(self.listen_port) + 1) % len(self.ring_ports)
        tried_ports = set()

        while True:
            target_port = self.ring_ports[next_index]
            if target_port in tried_ports:
                log(f"[Process {self.process_id}] No alive processes found. Stopping token circulation.")
                return
            tried_ports.add(target_port)

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1.5)
                    s.connect((HOST, target_port))
                    s.sendall("token".encode())
                    log(f"[Process {self.process_id}] Passed token ➡️ Port {target_port}")
                    return
            except Exception as e:
                log(f"[Process {self.process_id}] Failed to pass token to port {target_port}: {e}")

                # Tenta o próximo da lista
                next_index = (next_index + 1) % len(self.ring_ports)

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
    if len(sys.argv) < 4:
        print("Usage: python token_ring_node.py <process_id> <listen_port> <ring_port1> <ring_port2> ...")
        sys.exit(1)

    process_id = int(sys.argv[1])
    listen_port = int(sys.argv[2])
    ring_ports = list(map(int, sys.argv[3:]))

    node = TokenRingNode(process_id, listen_port, ring_ports)
    node.start(start_with_token=(process_id == 0))
