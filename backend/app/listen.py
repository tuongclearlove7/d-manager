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
    except Exception:
        pass  # bỏ qua nếu không set được permission


# =========================
# IMPROVED SUBPROCESS RUNNER
# =========================
def run_command(cmd, clean_docker_env=True):
    env = os.environ.copy()
    
    if clean_docker_env:
        # Loại bỏ các biến có thể gây xung đột với docker context
        env.pop("DOCKER_HOST", None)
        env.pop("DOCKER_CONTEXT", None)
        env.pop("DOCKER_TLS_VERIFY", None)
        env.pop("DOCKER_CERT_PATH", None)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=600,           # tránh treo quá lâu
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", "Command timed out after 600 seconds"
    except Exception as e:
        return 1, "", f"Subprocess error: {str(e)}"


# =========================
# GIT SAFE FUNCTIONS
# =========================
def get_commit():
    code, out, _ = run_command(["git", "rev-parse", "--short", "HEAD"], clean_docker_env=False)
    return out if code == 0 else "unknown"


def get_commit_message():
    code, out, _ = run_command(["git", "log", "-1", "--pretty=%B"], clean_docker_env=False)
    return out.strip() if code == 0 else ""


def get_changed_files():
    code, out, _ = run_command(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
        clean_docker_env=False
    )
    if code == 0 and out:
        return [f for f in out.split("\n") if f.strip()]
    return []


# =========================
# DEPLOY FUNCTION - FIXED
# =========================
def run_deploy():
    print("[DEPLOY] Starting: docker compose up -d --build")

    # Debug: in ra môi trường liên quan để dễ trace
    print("[DEBUG] DOCKER_HOST   :", os.getenv("DOCKER_HOST", "<not set>"))
    print("[DEBUG] DOCKER_CONTEXT:", os.getenv("DOCKER_CONTEXT", "<not set>"))

    # Chạy với môi trường đã clean
    code, out, err = run_command(
        ["docker", "compose", "up", "-d", "--build"],
        clean_docker_env=True
    )

    # In log ngắn để debug
    print(f"[DEPLOY] Exit code: {code}")
    if code != 0:
        print("[DEPLOY ERROR OUTPUT]", err[:1500] or out[:1500])

    if code == 0:
        # Thành công → trả về output (thường ngắn gọn khi -d)
        return "SUCCESS", out[-1200:] or "Containers started"
    else:
        # Thất bại → ưu tiên stderr
        error_msg = err if err else out
        return "FAILED", error_msg[-1500:] or "No error message captured"


# =========================
# SAVE HISTORY
# =========================
def save_to_file(payload):
    ensure_data_directory()
    try:
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        try:
            os.chmod(DATA_FILE, 0o666)
        except Exception:
            pass
        print("[LISTEN] Saved deployment record to data.txt")
    except Exception as e:
        print("[FILE ERROR]", str(e))


# =========================
# SEND TO WEBSOCKET
# =========================
async def send(payload):
    try:
        async with websockets.connect(SERVER, ping_interval=20, ping_timeout=10) as ws:
            await ws.send(json.dumps({
                "type": "deploy",
                "payload": payload
            }, ensure_ascii=False))
            print("[SOCKET] Deploy status sent")
    except Exception as e:
        print("[SOCKET ERROR]", str(e))


# =========================
# WATCH GIT HEAD
# =========================
async def watch_git():
    print("[LISTEN] Git watch service started - checking every 5s")
    ensure_data_directory()

    last_commit = None

    while True:
        try:
            current_commit = get_commit()

            if last_commit is None:
                last_commit = current_commit
                print(f"[INIT] First commit detected: {current_commit}")

            if current_commit != last_commit and current_commit != "unknown":
                print(f"[CHANGE] New commit detected: {current_commit}")
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

        except Exception as e:
            print("[WATCH ERROR]", str(e))
            payload = {
                "project": PROJECT_NAME,
                "status": "ERROR",
                "message": str(e),
                "commit": "unknown",
                "commit_message": "",
                "files_changed": [],
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_to_file(payload)

        await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(watch_git())
    except KeyboardInterrupt:
        print("[SHUTDOWN] Received interrupt, stopping...")
    except Exception as e:
        print("[FATAL]", str(e))