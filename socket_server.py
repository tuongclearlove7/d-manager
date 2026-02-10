import socket
import json

HOST = "0.0.0.0"
PORT = 9000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)

print(f"[SOCKET SERVER] Listening on {HOST}:{PORT}", flush=True)

while True:
    conn, addr = server.accept()
    print(f"[CONNECT] {addr}", flush=True)

    try:
        data = conn.recv(4096).decode()
        if not data:
            conn.close()
            continue

        payload = json.loads(data)

        print("====== DEPLOY EVENT ======", flush=True)
        print(f"Service : {payload.get('service')}", flush=True)
        print(f"Status  : {payload.get('status')}", flush=True)
        print(f"Message : {payload.get('message')}", flush=True)
        print(f"Commit  : {payload.get('commit')}", flush=True)
        print(f"Time    : {payload.get('time')}", flush=True)
        print("==========================", flush=True)

    except Exception as e:
        print("[ERROR]", e, flush=True)

    conn.close()
