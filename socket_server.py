import asyncio
import json
import websockets
from datetime import datetime

DEPLOY_EVENTS = []
MAX_EVENTS = 50

async def handler(websocket):
    client = websocket.remote_address
    print(f"[CONNECT] client={client}", flush=True)

    # gửi init data
    print(f"[SEND][INIT] events={len(DEPLOY_EVENTS)}", flush=True)
    await websocket.send(json.dumps({
        "type": "init",
        "data": DEPLOY_EVENTS
    }))

    try:
        async for message in websocket:
            print(f"[RECV] raw={message}", flush=True)

            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "deploy":
                payload = data.get("payload")
                print(f"[DEPLOY] payload={payload}", flush=True)

                DEPLOY_EVENTS.append(payload)
                DEPLOY_EVENTS[:] = DEPLOY_EVENTS[-MAX_EVENTS:]

                print(f"[STORE] total_events={len(DEPLOY_EVENTS)}", flush=True)

                # broadcast
                for ws in websocket.server.websockets:
                    print(f"[BROADCAST] to={ws.remote_address}", flush=True)
                    await ws.send(json.dumps({
                        "type": "deploy",
                        "data": payload
                    }))
            else:
                print(f"[WARN] unknown type={msg_type}", flush=True)

    except websockets.ConnectionClosed:
        print(f"[DISCONNECT] client={client}", flush=True)

    except Exception as e:
        print(f"[ERROR] {e}", flush=True)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 9000):
        print("[WS SERVER] listening on :9000", flush=True)
        await asyncio.Future()

asyncio.run(main())
