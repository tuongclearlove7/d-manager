import asyncio
import json
import sys
from datetime import datetime
import subprocess
import websockets

SERVER = "ws://127.0.0.1:9000"

status = sys.argv[1]
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

async def send():
    print("[NOTIFIER] connecting to server...", flush=True)
    try:
        async with websockets.connect(SERVER) as ws:
            msg = {
                "type": "deploy",
                "payload": payload
            }
            print(f"[NOTIFIER] send={msg}", flush=True)
            await ws.send(json.dumps(msg))
            print("[NOTIFIER] send success", flush=True)
    except Exception as e:
        print(f"[NOTIFIER][ERROR] {e}", flush=True)

asyncio.run(send())
