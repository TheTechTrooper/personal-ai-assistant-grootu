from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from app.voice.voice_controller import assistant
from app.event_bus import bus

app = FastAPI(title="Personal AI Assistant")

# Enable CORS for Desktop/Web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Broadcast helper (thread-safe)
def broadcast_event(event_type, data):
    asyncio.run_coroutine_threadsafe(
        bus.emit(event_type, data), 
        loop
    )

@app.on_event("startup")
async def startup_event():
    global loop
    loop = asyncio.get_event_loop()
    
    # Store the loop for the thread-safe broadcaster
    assistant.on_event = broadcast_event
    assistant.start()

@app.on_event("shutdown")
def shutdown_event():
    assistant.stop()

@app.get("/")
def root():
    return {"status": "Personal AI Assistant is running 🚀"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Subscribe this socket to the event bus
    async def send_message(payload):
        try:
            await websocket.send_json(payload)
        except:
            pass # Handle disconnects gracefully
            
    bus.subscribe(send_message)
    
    try:
        while True:
            # Keep connection alive & listen for incoming (e.g., text chat)
            data_str = await websocket.receive_text()
            
            try:
                import json
                payload = json.loads(data_str)
                
                if payload.get("type") == "text_input":
                    text = payload.get("data")
                    if text:
                        assistant.handle_text_input(text)
            except Exception as e:
                print(f"Error handling WS message: {e}")

    except WebSocketDisconnect:
        bus.unsubscribe(send_message)
