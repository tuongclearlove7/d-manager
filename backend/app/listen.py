import asyncio
import json
import os
import subprocess
from datetime import datetime
import websockets

SERVER = os.getenv("WS_SERVER", "ws://socket-server:9000")

DATA_DIR = "/app/data"
DATA_FILE = os.path.join(DATA_DIR, "data.txt")

PROJECT_NAME = "d-manager"


# =========================
# ENSURE DATA FOLDER
# =========================
def ensure_data_directory():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        os.chmod(DATA_DIR, 0o777)
        print("[PERMISSION] Data directory ready")
    except Exception as e:
        print("[PERMISSION ERROR]", e)


# =========================
# GIT FUNCTIONS
# =========================
def get_commit():
    return subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"]
    ).decode().strip()


def get_commit_message():
    return subprocess.check_output(
        ["git", "log", "-1", "--pretty=%B"]
    ).decode().strip()


def get_changed_files():
    files = subprocess.check_output(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]
    ).decode().strip().split("\n")

    return [f for f in files if f]


# =========================
# SAVE HISTORY
# =========================
def save_to_file(payload):
    ensure_data_directory()

    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")

    os.chmod(DATA_FILE, 0o666)
    print("[LISTEN] Saved to data.txt")


# =========================
# SEND TO SOCKET
# =========================
async def send(payload):
    try:
        async with websockets.connect(SERVER) as ws:
            await ws.send(json.dumps({
                "type": "deploy",
                "payload": payload
            }))
            print("[LISTEN] Sent to WebSocket")
    except Exception as e:
        print("[SOCKET ERROR]", e)


# =========================
# WATCH GIT HEAD
# =========================
async def watch_git():
    print("[LISTEN] Watching for new commits...")

    ensure_data_directory()
    last_commit = None

    while True:
        try:
            current_commit = get_commit()

            if current_commit != last_commit:
                last_commit = current_commit

                payload = {
                    "project": PROJECT_NAME,
                    "status": "SUCCESS",
                    "message": "New deploy detected",
                    "commit": current_commit,
                    "commit_message": get_commit_message(),
                    "files_changed": get_changed_files(),
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                save_to_file(payload)
                await send(payload)

            await asyncio.sleep(5)

        except Exception as e:
            print("[WATCH ERROR]", e)
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(watch_git())
