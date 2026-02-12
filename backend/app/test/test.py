import asyncio
import sys
import os

# =====================================================
# FIX PYTHON PATH
# =====================================================
# test.py nằm ở: backend/app/test/test.py
# Ta cần thêm thư mục backend vào sys.path

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")
)
sys.path.insert(0, BASE_DIR)

# =====================================================
# IMPORT MODULES
# =====================================================
try:
    from app.websocket.manager import start_websocket_server
    from app.listen import watch_git
    print("[TEST] Import modules OK")
except Exception as e:
    print("[TEST ERROR] Import failed:", e)
    sys.exit(1)


# =====================================================
# TEST WEBSOCKET STARTUP
# =====================================================
async def test_websocket():
    print("[TEST] Starting WebSocket server...")

    try:
        task = asyncio.create_task(start_websocket_server())

        # Chờ 3 giây xem có crash không
        await asyncio.sleep(3)

        task.cancel()

        print("[TEST] WebSocket startup OK")
        return True

    except Exception as e:
        print("[TEST ERROR] WebSocket failed:", e)
        return False


# =====================================================
# MAIN TEST RUNNER
# =====================================================
async def main():
    print("===================================")
    print("       RUNNING DEPLOY TEST         ")
    print("===================================")

    ws_ok = await test_websocket()

    if not ws_ok:
        print("[RESULT] TEST FAILED")
        sys.exit(1)

    print("[RESULT] ALL TESTS PASSED")
    sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print("[FATAL ERROR]", e)
        sys.exit(1)
