import socket
import json
import sys
from datetime import datetime
import subprocess

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000

status = sys.argv[1] if len(sys.argv) > 1 else "UNKNOWN"
message = sys.argv[2] if len(sys.argv) > 2 else ""

def get_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"]
        ).decode().strip()
    except:
        return "unknown"

payload = {
    "service": "d-manager",
    "status": status,
    "message": message,
    "commit": get_commit(),
    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    sock.connect((SERVER_HOST, SERVER_PORT))
    sock.send(json.dumps(payload).encode())
    sock.close()
except:
    pass
