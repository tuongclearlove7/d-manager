import asyncio
import json
import websockets
import os

DATA_FILE = "data.txt"
MAX_EVENTS = 50


class WebSocketManager:
    def __init__(self):
        self.deploy_events = []
        self.connected = set()
        self.load_data()

    # 🔥 Load dữ liệu khi server start
    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                for line in f:
                    try:
                        self.deploy_events.append(json.loads(line.strip()))
                    except:
                        pass

            self.deploy_events = self.deploy_events[-MAX_EVENTS:]

    async def handler(self, websocket):
        self.connected.add(websocket)
        print(f"[CONNECT] {websocket.remote_address}")

        # gửi dữ liệu cũ
        await websocket.send(json.dumps({
            "type": "init",
            "data": self.deploy_events
        }))

        try:
            async for message in websocket:
                data = json.loads(message)

                if data.get("type") == "deploy":
                    payload = data.get("payload")

                    self.deploy_events.append(payload)
                    self.deploy_events = self.deploy_events[-MAX_EVENTS:]

                    # 🔥 Lưu file
                    with open(DATA_FILE, "a") as f:
                        f.write(json.dumps(payload) + "\n")

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


async def start_websocket_server():
    async with websockets.serve(manager.handler, "0.0.0.0", 9000):
        print("WebSocket running on :9000")
        await asyncio.Future()
