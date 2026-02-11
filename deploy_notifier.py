import asyncio
import json
import sys
import os
from datetime import datetime
import websockets

SERVER = os.getenv("WS_SERVER", "ws://socket-server:9000")
PROJECT_NAME = "d-manager"

if len(sys.argv) < 3:
    print("Usage: deploy_notifier.py STATUS MESSAGE COMMIT COMMIT_MSG FILES")
    sys.exit(1)

status = sys.argv[1]
message = sys.argv[2]
commit = sys.argv[3] if len(sys.argv) > 3 else "unknown"
commit_message = sys.argv[4] if len(sys.argv) > 4 else "unknown"
files_changed = sys.argv[5].split(",") if len(sys.argv) > 5 and sys.argv[5] else []

payload = {
    "project": PROJECT_NAME,
    "status": status,
    "message": message,
    "commit": commit,
    "commit_message": commit_message,
    "files_changed": files_changed,
    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

async def send():
    try:
        async with websockets.connect(SERVER) as ws:
            await ws.send(json.dumps({
                "type": "deploy",
                "payload": payload
            }))
            print("[NOTIFIER] sent successfully")
    except Exception as e:
        print("[NOTIFIER ERROR]", e)

asyncio.run(send())
