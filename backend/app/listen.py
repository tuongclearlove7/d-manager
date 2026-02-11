import asyncio
import json
import os
import stat
from datetime import datetime
import websockets

SERVER = os.getenv("WS_SERVER", "ws://socket-server:9000")
PROJECT_NAME = "d-manager"

DATA_DIR = "/app/data"
DATA_FILE = os.path.join(DATA_DIR, "data.txt")
DEPLOY_TRIGGER = os.path.join(DATA_DIR, "deploy.txt")

def ensure_data_directory():
    try:
        # Tạo thư mục nếu chưa có
        os.makedirs(DATA_DIR, exist_ok=True)

        # Set quyền 777 cho folder
        os.chmod(DATA_DIR, 0o777)

        print("[PERMISSION] Data directory ready")

    except Exception as e:
        print("[PERMISSION ERROR]", e)


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


def save_to_file(payload):
    ensure_data_directory()

    try:
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")

        # Set quyền file sau khi tạo
        os.chmod(DATA_FILE, 0o666)

        print("[LISTEN] Saved to data.txt")

    except Exception as e:
        print("[FILE ERROR]", e)


async def watch_deploy():
    print("[LISTEN] Waiting for deploy trigger...")

    ensure_data_directory()
    last_content = ""

    while True:
        try:
            if os.path.exists(DEPLOY_TRIGGER):
                with open(DEPLOY_TRIGGER, "r") as f:
                    content = f.read().strip()

                if content and content != last_content:
                    last_content = content

                    payload = {
                        "project": PROJECT_NAME,
                        "status": "SUCCESS",
                        "message": content,
                        "commit": "auto",
                        "commit_message": content,
                        "files_changed": [],
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    save_to_file(payload)
                    await send(payload)

            await asyncio.sleep(2)

        except Exception as e:
            print("[WATCH ERROR]", e)
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(watch_deploy())
