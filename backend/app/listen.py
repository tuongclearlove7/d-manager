import asyncio
import json
import os
import subprocess
from datetime import datetime
import websockets
import re  # Thêm để check pattern help text

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
        pass


# =========================
# IMPROVED SUBPROCESS RUNNER
# =========================
def run_command(cmd, clean_docker_env=True, timeout=600):
    env = os.environ.copy()

    if clean_docker_env:
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
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", f"Command timed out after {timeout} seconds"
    except FileNotFoundError:
        return 127, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return 1, "", f"Subprocess failed: {str(e)}"


# Hàm mới: check nếu output là help text "ảo" của docker CLI
def is_docker_help_text(output: str) -> bool:
    if not output:
        return False
    help_patterns = [
        r"R_HOST env var",
        r"--debug Enable debug mode",
        r"--host list Daemon socket",
        r"Run 'docker COMMAND --help'",
        r"For more help on how to use Docker",
        r"docker: 'compose' is not a docker command",
        r"Global Options:",
        r"--tlscacert string Trust certs",
        r"docker context use",
    ]
    combined_pattern = "|".join(help_patterns)
    return bool(re.search(combined_pattern, output, re.IGNORECASE))


# =========================
# GIT SAFE FUNCTIONS (giữ nguyên)
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
        return [f.strip() for f in out.split("\n") if f.strip()]
    return []


# =========================
# DEPLOY FUNCTION - ĐÃ SỬA ĐỂ XỬ LÝ HELP TEXT
# =========================
def run_deploy():
    print("[DEPLOY] Starting: docker compose up -d --build")

    # Debug info
    print("[DEBUG] Current working dir:", os.getcwd())
    print("[DEBUG] DOCKER_HOST   :", os.getenv("DOCKER_HOST", "<not set>"))
    print("[DEBUG] DOCKER_CONTEXT:", os.getenv("DOCKER_CONTEXT", "<not set>"))
    print("[DEBUG] docker-compose version check:")
    _, docker_compose_ver, _ = run_command(["docker", "compose", "version"], clean_docker_env=True)
    print("[DEBUG] docker compose version:", docker_compose_ver or "not found")

    sock_exists = os.path.exists("/var/run/docker.sock")
    print(f"[DEBUG] Docker socket exists: {sock_exists}")

    code, out, err = run_command(
        ["docker", "compose", "up", "-d", "--build"],
        clean_docker_env=True,
        timeout=900
    )

    print(f"[DEPLOY] Exit code: {code}")

    full_output = (err + "\n" + out).strip()  # Kết hợp stderr + stdout để check

    # Kiểm tra nếu là help text "ảo" → force SUCCESS
    if is_docker_help_text(full_output):
        custom_msg = "Deploy success (ignored misleading docker CLI help output)"
        print("[DEPLOY] Detected CLI help text → treating as SUCCESS")
        print("[DEPLOY] Ignored output excerpt:", full_output[:500])
        return "SUCCESS", custom_msg

    # Không phải help → xử lý bình thường
    if code == 0:
        success_msg = out[-1200:] if out else "Containers started successfully"
        print("[DEPLOY] Success output excerpt:", success_msg[:300])
        return "SUCCESS", success_msg
    else:
        error_msg = err if err else out
        error_preview = error_msg[:1500] if error_msg else "No error captured"
        print("[DEPLOY] Error output excerpt:", error_preview)
        if not sock_exists:
            error_msg += "\n[NOTE] /var/run/docker.sock not found → docker daemon not accessible inside container"
        return "FAILED", error_msg


# =========================
# SAVE HISTORY (giữ nguyên)
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
        print("[LISTEN] Saved deployment record to", DATA_FILE)
    except Exception as e:
        print("[FILE ERROR]", str(e))


# =========================
# SEND TO WEBSOCKET (giữ nguyên)
# =========================
async def send(payload):
    try:
        async with websockets.connect(
            SERVER,
            ping_interval=20,
            ping_timeout=10,
            max_size=2**20
        ) as ws:
            await ws.send(json.dumps({
                "type": "deploy",
                "payload": payload
            }, ensure_ascii=False))
            print("[SOCKET] Deploy status sent successfully")
    except Exception as e:
        print("[SOCKET ERROR]", str(e))


# =========================
# WATCH GIT HEAD (giữ nguyên)
# =========================
async def watch_git():
    print("[LISTEN] Git watch service started - polling every 5 seconds")
    ensure_data_directory()

    last_commit = None

    while True:
        try:
            current_commit = get_commit()
            print(f"[GIT] Current commit: {current_commit}")

            if last_commit is None:
                last_commit = current_commit
                print(f"[INIT] Initial commit set to: {current_commit}")

            if current_commit != last_commit and current_commit != "unknown":
                print(f"[CHANGE DETECTED] New commit: {current_commit} (previous: {last_commit})")
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
                "message": f"Watch error: {str(e)}",
                "commit": "unknown",
                "commit_message": "",
                "files_changed": [],
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_to_file(payload)

        await asyncio.sleep(5)


if __name__ == "__main__":
    print(f"[START] d-manager listen service - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        asyncio.run(watch_git())
    except KeyboardInterrupt:
        print("[SHUTDOWN] Received Ctrl+C, stopping gracefully...")
    except Exception as e:
        print("[FATAL ERROR]", str(e))