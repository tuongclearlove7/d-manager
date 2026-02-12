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
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        os.chmod(DATA_DIR, 0o777)
    except:
        pass
    print("[INIT] Data directory ready")


# =========================
# SAFE SUBPROCESS RUNNER
# =========================
def run_command(cmd):
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        return result.returncode, result.stdout.strip(), result.stderr.strip()

    except Exception as e:
        return 1, "", str(e)


# =========================
# GIT FUNCTIONS
# =========================
def get_commit():
    code, out, err = run_command(["git", "rev-parse", "--short", "HEAD"])
    if code == 0:
        return out
    return None


def get_commit_message():
    code, out, err = run_command(["git", "log", "-1", "--pretty=%B"])
    return out if code == 0 else ""


def get_changed_files():
    code, out, err = run_command(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]
    )
    if code == 0 and out:
        return out.split("\n")
    return []


# =========================
# DEPLOY FUNCTION
# =========================
def run_deploy():
    print("[DEPLOY] Running docker compose up -d --build")

    code, out, err = run_command(
        ["docker", "compose", "up", "-d", "--build"]
    )

    if code == 0:
        print("[DEPLOY] SUCCESS")
        return "SUCCESS", out[-1000:]
    else:
        print("[DEPLOY] FAILED")
        return "FAILED", (err or out)[-1000:]


# =========================
# SAVE HISTORY
# =========================
def save_to_file(payload):
    ensure_data_directory()
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")

    try:
        os.chmod(DATA_FILE, 0o666)
    except:
        pass

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

    # 🚫 KHÔNG DEPLOY NGAY KHI START
    last_commit = get_commit()

    if not last_commit:
        print("[INIT ERROR] Cannot read git commit")
        return

    print(f"[INIT] Current commit: {last_commit}")

    while True:
        try:
            current_commit = get_commit()

            if current_commit and current_commit != last_commit:
                print(f"[CHANGE DETECTED] {current_commit}")
                last_commit = current_commit

                status, deploy_log = run_deploy()

                payload = {
                    "project": PROJECT_NAME,
                    "status": status,
                    "message": deploy_log,
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
