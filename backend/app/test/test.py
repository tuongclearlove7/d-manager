import asyncio
import sys
import os

# Thêm root project vào path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.websocket.manager import start_websocket_server
from app.listen import watch_git


async def main():
    print("=== STARTING TEST ENVIRONMENT ===")

    # Tạo task cho websocket server
    websocket_task = asyncio.create_task(start_websocket_server())

    # Tạo task cho git listener
    listen_task = asyncio.create_task(watch_git())

    # Chạy song song
    await asyncio.gather(
        websocket_task,
        listen_task
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n=== STOPPED BY USER ===")
