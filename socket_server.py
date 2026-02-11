import asyncio
import json
import websockets
import os

DATA_FILE = "data.txt"
DEPLOY_EVENTS = []
MAX_EVENTS = 50
CONNECTED = set()

# 🔥 LOAD DATA KHI SERVER START
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        for line in f:
            try:
                DEPLOY_EVENTS.append(json.loads(line.strip()))
            except:
                pass

    DEPLOY_EVENTS[:] = DEPLOY_EVENTS[-MAX_EVENTS:]

async def handler(websocket):
    CONNECTED.add(websocket)
    print(f"[CONNECT] {websocket.remote_address}")

    # gửi dữ liệu cũ
    await websocket.send(json.dumps({
        "type": "init",
        "data": DEPLOY_EVENTS
    }))

    try:
        async for message in websocket:
            data = json.loads(message)

            if data.get("type") == "deploy":
                payload = data.get("payload")

                DEPLOY_EVENTS.append(payload)
                DEPLOY_EVENTS[:] = DEPLOY_EVENTS[-MAX_EVENTS:]

                # 🔥 LƯU FILE
                with open(DATA_FILE, "a") as f:
                    f.write(json.dumps(payload) + "\n")

                # broadcast
                for ws in CONNECTED.copy():
                    try:
                        await ws.send(json.dumps({
                            "type": "deploy",
                            "data": payload
                        }))
                    except:
                        CONNECTED.remove(ws)

    except:
        pass
    finally:
        CONNECTED.remove(websocket)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 9000):
        print("WebSocket running on :9000")
        await asyncio.Future()

asyncio.run(main())
