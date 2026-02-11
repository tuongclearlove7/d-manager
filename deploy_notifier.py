import asyncio
import json
import sys
import os
from datetime import datetime
import subprocess
import websockets

# =========================
# CONFIG
# =========================
SERVER = os.getenv("WS_SERVER", "ws://socket-server:9000")

# =========================
# INPUT VALIDATION
# =========================
if len(sys.argv) < 2:
    print("Usage: deploy_notifier.py STATUS [MESSAGE]")
    sys.exit(1)

status = sys.argv[1]
message = sys.argv[2] if len(sys.argv) > 2 else ""

# =========================
# GET GIT COMMIT
# =========================
def get_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL
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

# =========================
# SEND FUNCTION
# =========================
async def send():
    print(f"[NOTIFIER] connecting → {SERVER}", flush=True)

    try:
        async with websockets.connect(SERVER, open_timeout=3) as ws:
            msg = {
                "type": "deploy",
                "payload": payload
            }

            print("[NOTIFIER] sending payload:", flush=True)
            print(json.dumps(msg, indent=2), flush=True)

            await ws.send(json.dumps(msg))

            print("[NOTIFIER] send success ✅", flush=True)
            return 0

    except Exception as e:
        print(f"[NOTIFIER][ERROR] {e}", flush=True)
        return 1

# =========================
# RUN
# =========================
exit_code = asyncio.run(send())
sys.exit(exit_code)
