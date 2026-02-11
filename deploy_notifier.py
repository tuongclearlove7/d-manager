import asyncio
import json
import sys
import os
from datetime import datetime
import subprocess
import websockets

SERVER = os.getenv("WS_SERVER", "ws://socket-server:9000")
PROJECT_NAME = "d-manager"
DATA_FILE = "data.txt"

if len(sys.argv) < 2:
    print("Usage: deploy_notifier.py STATUS [MESSAGE]")
    sys.exit(1)

status = sys.argv[1]
message = sys.argv[2] if len(sys.argv) > 2 else ""

# =========================
# GIT INFO
# =========================
def get_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"]
        ).decode().strip()
    except:
        return "unknown"

def get_commit_message():
    try:
        return subprocess.check_output(
            ["git", "log", "-1", "--pretty=%B"]
        ).decode().strip()
    except:
        return "unknown"

def get_changed_files():
    try:
        files = subprocess.check_output(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]
        ).decode().strip().split("\n")
        return files
    except:
        return []

payload = {
    "project": PROJECT_NAME,
    "status": status,
    "message": message,
    "commit": get_commit(),
    "commit_message": get_commit_message(),
    "files_changed": get_changed_files(),
    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

# =========================
# SAVE TO FILE
# =========================
with open(DATA_FILE, "a") as f:
    f.write(json.dumps(payload) + "\n")

# =========================
# SEND TO SOCKET
# =========================
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
