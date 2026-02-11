import asyncio
import json
import os
import websockets

SERVER = os.getenv("WS_SERVER", "ws://socket-server:9000")

DATA_DIR = "/app/data"
DATA_FILE = os.path.join(DATA_DIR, "data.txt")
DEPLOY_TRIGGER = os.path.join(DATA_DIR, "deploy.txt")


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
# SAVE HISTORY
# =========================
def save_to_file(payload):
    ensure_data_directory()

    try:
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")

        os.chmod(DATA_FILE, 0o666)
        print("[LISTEN] Saved to data.txt")

    except Exception as e:
        print("[FILE ERROR]", e)


# =========================
# SEND TO SOCKET SERVER
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
# WATCH DEPLOY FILE
# =========================
async def watch_deploy():
    print("[LISTEN] Waiting for deploy trigger...")

    ensure_data_directory()
    last_content = ""

    while True:
        try:
            if os.path.exists(DEPLOY_TRIGGER):

                with open(DEPLOY_TRIGGER, "r", encoding="utf-8") as f:
                    content = f.read().strip()

                # chỉ xử lý khi có nội dung mới
                if content and content != last_content:
                    last_content = content

                    try:
                        payload = json.loads(content)
                    except json.JSONDecodeError:
                        print("[ERROR] deploy.txt is not valid JSON")
                        await asyncio.sleep(2)
                        continue

                    save_to_file(payload)
                    await send(payload)

            await asyncio.sleep(2)

        except Exception as e:
            print("[WATCH ERROR]", e)
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(watch_deploy())
