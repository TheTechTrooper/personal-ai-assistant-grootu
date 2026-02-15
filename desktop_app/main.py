import asyncio
import json
import os
import time

import flet as ft
import websockets

BACKEND_WS_URL = os.getenv("BACKEND_WS_URL", "ws://127.0.0.1:8000/ws")

ACCENT = "#00E5FF"
ACCENT_ALT = "#00FFA3"
BG_TOP = "#0B1021"
BG_BOTTOM = "#05070F"
PANEL = "#121827"
PANEL_ALT = "#0F172A"
TEXT = "#D8E6FF"
TEXT_MUTED = "#8FA3C9"
ERROR = "#FF5D6C"

global_ws = None
_last_quick_action: dict[str, float] = {}
_quick_action_cooldown_seconds = 1.5


def main(page: ft.Page):
    page.title = "Jarvis Control Deck"
    page.window_width = 540
    page.window_height = 820
    page.padding = 0
    page.spacing = 0
    page.bgcolor = BG_BOTTOM
    page.theme_mode = ft.ThemeMode.DARK

    status_text = ft.Text("BOOTING", size=11, color=ACCENT_ALT, weight=ft.FontWeight.W_600)
    error_text = ft.Text("", size=11, color=ERROR)
    voice_cue_icon = ft.Icon(ft.Icons.MIC_NONE_ROUNDED, size=20, color=TEXT_MUTED)
    voice_cue_title = ft.Text("Initializing voice...", size=14, color=TEXT, weight=ft.FontWeight.W_600)
    voice_cue_hint = ft.Text("Wait for the app to connect.", size=11, color=TEXT_MUTED)
    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    input_field = ft.TextField(
        hint_text="Enter command or message...",
        hint_style=ft.TextStyle(color=TEXT_MUTED),
        color=TEXT,
        border_color="#20304D",
        focused_border_color=ACCENT,
        bgcolor="#0B1426",
        expand=True,
        on_submit=lambda e: send_message(),
    )

    def set_voice_cue(state: str):
        normalized = (state or "").strip().lower()
        if normalized == "listening":
            voice_cue_icon.name = ft.Icons.MIC_ROUNDED
            voice_cue_icon.color = "#39D98A"
            voice_cue_title.value = "Speak now"
            voice_cue_hint.value = "Jarvis is listening. Start talking."
        elif normalized == "processing":
            voice_cue_icon.name = ft.Icons.PSYCHOLOGY_ALT
            voice_cue_icon.color = "#FFCC66"
            voice_cue_title.value = "Thinking..."
            voice_cue_hint.value = "Jarvis is processing your request."
        elif normalized in {"reconnecting", "disconnected"}:
            voice_cue_icon.name = ft.Icons.SYNC_PROBLEM
            voice_cue_icon.color = ERROR
            voice_cue_title.value = "Reconnecting"
            voice_cue_hint.value = "Please wait while connection is restored."
        else:
            voice_cue_icon.name = ft.Icons.MIC_NONE_ROUNDED
            voice_cue_icon.color = ACCENT
            voice_cue_title.value = "Ready"
            voice_cue_hint.value = "Wait for 'Speak now' before talking."

    def set_status(text: str, color: str = TEXT_MUTED):
        status_text.value = text.upper()
        status_text.color = color
        set_voice_cue(text)
        page.update()

    def set_error(text: str):
        error_text.value = text
        page.update()

    def add_message(text: str, is_user: bool):
        bubble_color = "#0E2A4D" if is_user else PANEL
        border_color = ACCENT if is_user else "#24324F"
        icon = ft.Icons.PERSON if is_user else ft.Icons.MEMORY
        icon_color = ACCENT_ALT if is_user else ACCENT
        align = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        label = "YOU" if is_user else "JARVIS"

        bubble = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icon, size=14, color=icon_color),
                            ft.Text(label, size=10, color=TEXT_MUTED, weight=ft.FontWeight.W_600),
                        ],
                        spacing=6,
                    ),
                    ft.Text(text, size=14, color=TEXT, selectable=True),
                ],
                spacing=6,
                tight=True,
            ),
            padding=12,
            border_radius=12,
            border=ft.Border.all(1, border_color),
            bgcolor=bubble_color,
            width=380,
        )

        chat_list.controls.append(ft.Row(controls=[bubble], alignment=align))
        page.update()

    async def ws_loop():
        global global_ws
        while True:
            try:
                async with websockets.connect(BACKEND_WS_URL) as websocket:
                    global_ws = websocket
                    set_status("Connected", ACCENT_ALT)
                    set_error("")
                    while True:
                        raw = await websocket.recv()
                        event = json.loads(raw)
                        event_type = event.get("type")
                        data = event.get("data")

                        if event_type == "user_speech":
                            add_message(str(data), is_user=True)
                        elif event_type == "ai_response":
                            add_message(str(data), is_user=False)
                        elif event_type == "status":
                            if data == "listening":
                                set_status("Listening", ACCENT_ALT)
                            elif data == "processing":
                                set_status("Processing", "#FFCC66")
                            else:
                                set_status(str(data), TEXT_MUTED)
            except Exception as e:
                global_ws = None
                set_status("Reconnecting", ERROR)
                set_error(f"Connection error: {e}")
                await asyncio.sleep(2)

    async def send_payload_async(payload: dict):
        if not global_ws:
            add_message("[SYSTEM] Backend is not connected.", is_user=False)
            return
        try:
            await global_ws.send(json.dumps(payload))
        except Exception as e:
            add_message(f"[SYSTEM] Send failed: {e}", is_user=False)

    def send_payload(payload: dict):
        page.run_task(send_payload_async, payload)

    def send_message():
        text = (input_field.value or "").strip()
        if not text:
            return
        input_field.value = ""
        page.update()
        send_payload({"type": "text_input", "data": text})

    def send_quick_command(command: str):
        now = time.time()
        last_run = _last_quick_action.get(command, 0)
        if now - last_run < _quick_action_cooldown_seconds:
            set_status("Please wait...", "#FFCC66")
            return
        _last_quick_action[command] = now
        send_payload({"type": "text_input", "data": command})

    page.run_task(ws_loop)

    quick_actions = ft.Row(
        controls=[
            ft.OutlinedButton(
                "Stop Speech",
                icon=ft.Icons.STOP_CIRCLE,
                style=ft.ButtonStyle(color=ERROR, side=ft.BorderSide(1, ERROR)),
                on_click=lambda e: send_quick_command("stop"),
            ),
            ft.OutlinedButton(
                "Tasks",
                icon=ft.Icons.CHECKLIST,
                style=ft.ButtonStyle(color=ACCENT, side=ft.BorderSide(1, ACCENT)),
                on_click=lambda e: send_quick_command("show pending tasks"),
            ),
            ft.OutlinedButton(
                "Memory",
                icon=ft.Icons.STORAGE,
                style=ft.ButtonStyle(color=ACCENT_ALT, side=ft.BorderSide(1, ACCENT_ALT)),
                on_click=lambda e: send_quick_command("show memory stats"),
            ),
        ],
        wrap=True,
        spacing=8,
    )

    top_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ROCKET_LAUNCH, color=ACCENT, size=24),
                        ft.Column(
                            controls=[
                                ft.Text("JARVIS CONTROL DECK", size=16, weight=ft.FontWeight.BOLD, color=TEXT),
                                ft.Text("Assistant Interface", size=11, color=TEXT_MUTED),
                            ],
                            spacing=2,
                            tight=True,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=status_text,
                    padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                    border_radius=999,
                    border=ft.Border.all(1, "#2A3D61"),
                    bgcolor=PANEL_ALT,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        border=ft.Border.only(bottom=ft.BorderSide(1, "#1C2940")),
        bgcolor=PANEL,
    )

    voice_cue_panel = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=voice_cue_icon,
                    width=36,
                    height=36,
                    border_radius=999,
                    bgcolor="#0B1426",
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(
                    controls=[voice_cue_title, voice_cue_hint],
                    spacing=2,
                    tight=True,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=16, vertical=10),
        border=ft.Border.only(bottom=ft.BorderSide(1, "#1C2940")),
        bgcolor="#0C1322",
    )

    chat_panel = ft.Container(
        content=ft.Column(controls=[error_text, chat_list], spacing=8, expand=True),
        padding=16,
        expand=True,
    )

    input_panel = ft.Container(
        content=ft.Column(
            controls=[
                quick_actions,
                ft.Row(
                    controls=[
                        input_field,
                        ft.IconButton(
                            icon=ft.Icons.SEND_ROUNDED,
                            icon_color=BG_BOTTOM,
                            bgcolor=ACCENT,
                            on_click=lambda e: send_message(),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.END,
                ),
            ],
            spacing=10,
        ),
        padding=16,
        border=ft.Border.only(top=ft.BorderSide(1, "#1C2940")),
        bgcolor=PANEL,
    )

    page.add(
        ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                colors=[BG_TOP, BG_BOTTOM],
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
            ),
            content=ft.Column(
                controls=[top_bar, voice_cue_panel, chat_panel, input_panel],
                expand=True,
                spacing=0,
            ),
        )
    )


if __name__ == "__main__":
    ft.run(main)

