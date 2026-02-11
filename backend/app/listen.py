import asyncio
import json
import os
from datetime import datetime
import websockets

SERVER = os.getenv("WS_SERVER", "ws://socket-server:9000")
PROJECT_NAME = "d-manager"
DATA_FILE = "/app/data/data.txt"
DEPLOY_TRIGGER = "/app/data/deploy.txt"

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
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")

    print("[LISTEN] Saved to data.txt")


async def watch_deploy():
    print("[LISTEN] Waiting for deploy trigger...")

    last_content = ""

    while True:
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


if __name__ == "__main__":
    asyncio.run(watch_deploy())
