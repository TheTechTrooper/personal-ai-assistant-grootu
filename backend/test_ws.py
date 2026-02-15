import asyncio
import json

import websockets


async def test_connection():
    uri = "ws://localhost:8000/ws"
    print(f"[INFO] Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("[OK] Connected to WebSocket!")

            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print(f"[EVENT] Received: {data}")

                if data.get("type") == "status" and data.get("data") == "listening":
                    print("[OK] Voice loop is running.")
                    break
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())
