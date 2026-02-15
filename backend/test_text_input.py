import asyncio
import json

import websockets


async def test_text_chat():
    uri = "ws://localhost:8000/ws"
    print(f"[INFO] Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("[OK] Connected!")

            test_msg = "Hello, what is your name?"
            payload = json.dumps({"type": "text_input", "data": test_msg})
            print(f"[SEND] {test_msg}")
            await websocket.send(payload)

            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    event = data.get("type")
                    content = data.get("data")

                    print(f"[EVENT] {event} | Data: {content}")

                    if event == "ai_response":
                        print("[OK] Success! AI responded.")
                        break
                except asyncio.TimeoutError:
                    print("[ERROR] Timeout waiting for AI response.")
                    break
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    asyncio.run(test_text_chat())
