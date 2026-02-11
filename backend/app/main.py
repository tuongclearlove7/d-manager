import asyncio
from websocket.manager import start_websocket_server


if __name__ == "__main__":
    asyncio.run(start_websocket_server())
