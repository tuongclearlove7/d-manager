import asyncio
import json
import websockets
import os

DATA_FILE = "/app/data.txt"
MAX_EVENTS = 50


class WebSocketManager:
    def __init__(self):
        self.connected = set()

    def load_data(self):
        events = []

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                for line in f:
                    try:
                        events.append(json.loads(line.strip()))
                    except:
                        pass

        return events[-MAX_EVENTS:]

    async def handler(self, websocket):
        self.connected.add(websocket)
        print(f"[CONNECT] {websocket.remote_address}")

        events = self.load_data()

        await websocket.send(json.dumps({
            "type": "init",
            "data": events
        }))

        try:
            async for message in websocket:
                data = json.loads(message)

                if data.get("type") == "deploy":
                    payload = data.get("payload")
                    await self.broadcast(payload)

        except Exception:
            pass
        finally:
            self.connected.remove(websocket)

    async def broadcast(self, payload):
        for ws in self.connected.copy():
            try:
                await ws.send(json.dumps({
                    "type": "deploy",
                    "data": payload
                }))
            except:
                self.connected.remove(ws)


manager = WebSocketManager()


# 🔥 Đây là hàm main.py đang gọi
async def start_websocket_server():
    async with websockets.serve(manager.handler, "0.0.0.0", 9000):
        print("WebSocket running on :9000")
        await asyncio.Future()  # giữ server chạy mãi
