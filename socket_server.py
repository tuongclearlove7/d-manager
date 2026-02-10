import socket
import json
from datetime import datetime

HOST = "0.0.0.0"
PORT = 9000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

print(f"[SOCKET SERVER] Listening on - {HOST}:{PORT}")

while True:
    conn, addr = server.accept()
    print(f"[CONNECT] {addr}")

    try:
        data = conn.recv(4096).decode()
        if not data:
            conn.close()
            continue

        payload = json.loads(data)
        print("====== DEPLOY EVENT ======")
        print(f"Service : {payload.get('service')}")
        print(f"Status  : {payload.get('status')}")
        print(f"Commit  : {payload.get('commit')}")
        print(f"Time    : {payload.get('time')}")
        print("==========================")

    except Exception as e:
        print("[ERROR]", e)

    conn.close()
