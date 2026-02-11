import asyncio
import json
import websockets
import os

DATA_FILE = "/app/data/data.txt"
MAX_EVENTS = 50


class WebSocketManager:
    def __init__(self):
        self.connected = set()

    def load_data(self):
        events = []

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        events.append(json.loads(line.strip()))
                    except:
                        pass

        return events[-MAX_EVENTS:]

    async def handler(self, websocket):
        self.connected.add(websocket)
        print(f"[CONNECT] {websocket.remote_address}")

        try:
            # 🔥 Gửi init ngay khi connect
            events = self.load_data()

            await websocket.send(json.dumps({
                "type": "init",
                "data": events
            }))

            async for message in websocket:
                data = json.loads(message)

                if data.get("type") == "deploy":
                    payload = data.get("payload")

                    # 🔥 Broadcast đúng format
                    await self.broadcast({
                        "type": "deploy",
                        "payload": payload
                    })

        except Exception as e:
            print("[ERROR]", e)

        finally:
            self.connected.discard(websocket)
            print(f"[DISCONNECT] {websocket.remote_address}")

    async def broadcast(self, message):
        if not self.connected:
            return

        await asyncio.gather(
            *[ws.send(json.dumps(message)) for ws in self.connected.copy()],
            return_exceptions=True
        )


manager = WebSocketManager()


async def start_websocket_server():
    async with websockets.serve(manager.handler, "0.0.0.0", 9000):
        print("WebSocket running on :9000")
        await asyncio.Future()
