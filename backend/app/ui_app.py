import flet as ft
import websockets
import asyncio
import json
import threading

# Configuration
# Configuration
BACKEND_WS_URL = "ws://localhost:8000/ws"
global_ws = None
global_loop = None

def main(page: ft.Page):
    page.title = "Personal AI Assistant"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 450
    page.window_height = 800
    
    # UI Components
    chat_list = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )
    
    status_text = ft.Text("Disconnected", color="red400", size=12)
    
    input_field = ft.TextField(
        hint_text="Type a message...",
        expand=True,
        border_radius=20,
        on_submit=lambda e: send_message(e)
    )

    def add_message(text, is_user=False):
        timestamp = 0 # TODO: Add timestamp
        alignment = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        bg_color = "blue700" if is_user else "grey800"
        
        chat_list.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(text, size=16),
                        padding=15,
                        border_radius=20,
                        bgcolor=bg_color,
                        constraints=ft.BoxConstraints(max_width=300),
                    )
                ],
                alignment=alignment,
            )
        )
        page.update()

    def update_status(status):
        status_text.value = f"Status: {status}"
        if status == "listening":
            status_text.color = "green400"
        elif status == "processing":
            status_text.color = "yellow400"
        else:
            status_text.color = "grey400"
        page.update()

    async def ws_loop():
        global global_ws
        while True:
            try:
                async with websockets.connect(BACKEND_WS_URL) as websocket:
                    global_ws = websocket
                    update_status("Connected")
                    
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        event_type = data.get("type")
                        content = data.get("data")
                        
                        if event_type == "user_speech":
                            add_message(content, is_user=True)
                        elif event_type == "ai_response":
                            add_message(content, is_user=False)
                        elif event_type == "status":
                            update_status(content)
                            
            except Exception as e:
                update_status("Reconnecting...")
                await asyncio.sleep(2)

    def start_ws_thread():
        global global_loop
        loop = asyncio.new_event_loop()
        global_loop = loop
        asyncio.set_event_loop(loop)
        loop.run_until_complete(ws_loop())

    # Start WebSocket thread
    threading.Thread(target=start_ws_thread, daemon=True).start()

    def send_message(e):
        if not input_field.value:
            return
            
        text = input_field.value
        input_field.value = ""
        
        # Optimistically verify connection
        if global_ws and global_loop and global_ws.open:
            payload = json.dumps({"type": "text_input", "data": text})
            asyncio.run_coroutine_threadsafe(global_ws.send(payload), global_loop)
        else:
            add_message("Error: Not connected to backend", is_user=True) # Or just log it
            
        page.update()

    # Layout
    page.add(
        ft.Column(
            [
                ft.Row([
                    ft.Text("Grootu AI", size=24, weight="bold"),
                    ft.Container(expand=True),
                    status_text
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                chat_list,
                ft.Divider(),
                ft.Row([
                    input_field,
                    ft.IconButton(icon=ft.icons.Icons.SEND, on_click=send_message)
                ])
            ],
            expand=True
        )
    )

import sys

if __name__ == "__main__":
    if "--web" in sys.argv:
        print("📱 Running in Web Mode (iOS compatible)")
        print("🔗 Open this URL on your iPhone: http://YOUR_PC_IP:8550")
        ft.app(target=main, port=8550, view=ft.AppView.WEB_BROWSER, host="0.0.0.0")
    else:
        ft.app(target=main)
