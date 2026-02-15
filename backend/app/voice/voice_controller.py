import threading
import time
import re

from app.brain.ai_engine import process_input
from app.voice.speech_to_text import listen, listen_for_seconds
from app.voice.text_to_speech import is_speaking, speak, speak_async, stop_speaking

STOP_WORDS = {"stop"}
EXIT_WORDS = {"quit", "exit", "bye", "close"}
WAKE_PHRASES = ["hey jarvis", "ok jarvis", "hello jarvis"]


class VoiceAssistant:
    def __init__(self, on_event=None):
        self.on_event = on_event
        self.running = False
        self.thread = None
        self.wake_window_seconds = 15
        self.awake_until = 0.0
        self.session_awake = False
        self._barge_in_text = None
        self._last_wake_prompt_at = 0.0

    def _emit(self, event_type, data):
        if self.on_event:
            self.on_event(event_type, data)

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        stop_speaking()
        if self.thread:
            self.thread.join(timeout=1)

    def _is_stop_command(self, text: str) -> bool:
        words = set(text.lower().split())
        return any(word in words for word in STOP_WORDS)

    def _is_exit_command(self, text: str) -> bool:
        words = set(text.lower().split())
        return any(word in words for word in EXIT_WORDS)

    def _is_awake(self) -> bool:
        return time.time() <= self.awake_until

    def _contains_wake_phrase(self, text: str) -> bool:
        normalized = self._normalize_text(text)
        return any(phrase in normalized for phrase in WAKE_PHRASES)

    def _strip_wake_phrase(self, text: str) -> str:
        lowered = self._normalize_text(text)
        for phrase in WAKE_PHRASES:
            if phrase in lowered:
                idx = lowered.find(phrase)
                after = lowered[idx + len(phrase) :].strip(" ,.:;!?")
                return after
        return text.strip()

    def _normalize_text(self, text: str) -> str:
        lowered = (text or "").lower().strip()
        return re.sub(r"[^a-z0-9]+", " ", lowered).strip()

    def _speak_with_interrupt(self, response: str):
        speech_thread = speak_async(response)
        if speech_thread is None:
            return

        while self.running and speech_thread.is_alive():
            heard = listen_for_seconds(timeout_seconds=1.0)
            if not heard:
                continue

            self._emit("user_speech", heard)
            lowered = heard.lower().strip()
            if self._is_stop_command(lowered):
                stop_speaking()
                self._emit("ai_response", "Okay, I stopped speaking.")
                break
            if self._is_exit_command(lowered):
                stop_speaking()
                self._emit("ai_response", "Goodbye.")
                self.running = False
                break

            # Treat non-stop speech during TTS as the next user command.
            self._barge_in_text = heard
            stop_speaking()
            break

        speech_thread.join(timeout=1)

    def _loop(self):
        self._emit("status", "connected")
        speak("Hello. Say hey jarvis when you need me.")

        while self.running:
            if self._barge_in_text:
                text = self._barge_in_text
                self._barge_in_text = None
            else:
                self._emit("status", "listening")
                text = listen()
                if not text:
                    time.sleep(0.2)
                    continue

            self._emit("user_speech", text)
            print(f"Heard: {text}")
            lowered = text.lower().strip()

            if self._is_stop_command(lowered):
                if is_speaking():
                    stop_speaking()
                self.session_awake = False
                self._emit("ai_response", "Okay, I stopped. Say hey jarvis when you need me again.")
                continue

            if self._is_exit_command(lowered):
                response = "Goodbye."
                self._emit("ai_response", response)
                speak(response)
                self.running = False
                break

            # Wake-word gate for voice: process only after "hey jarvis".
            if not self.session_awake:
                if not self._contains_wake_phrase(lowered):
                    now = time.time()
                    if now - self._last_wake_prompt_at >= 4:
                        self._emit("ai_response", "Say hey jarvis first.")
                        self._last_wake_prompt_at = now
                    continue
                self.session_awake = True
                self.awake_until = time.time() + self.wake_window_seconds
                command_text = self._strip_wake_phrase(text)
                if not command_text or self._contains_wake_phrase(command_text):
                    response = "Yes?"
                    self._emit("ai_response", response)
                    self._speak_with_interrupt(response)
                    continue
                text = command_text
            elif self._contains_wake_phrase(lowered):
                self.awake_until = time.time() + self.wake_window_seconds
                stripped = self._strip_wake_phrase(text)
                if stripped and not self._contains_wake_phrase(stripped):
                    text = stripped

            # Keep the session awake until user explicitly says stop.
            self.session_awake = True
            self.awake_until = time.time() + self.wake_window_seconds

            self._emit("status", "processing")
            response = process_input(text)
            self._emit("ai_response", response)
            self._speak_with_interrupt(response)
            time.sleep(0.2)

    def handle_text_input(self, text: str):
        if not text:
            return

        def _process():
            lowered = text.lower().strip()
            self._emit("user_speech", text)

            if self._is_stop_command(lowered):
                stop_speaking()
                self.session_awake = False
                self._emit("ai_response", "Okay, I stopped. Say hey jarvis when you need me again.")
                return

            if self._is_exit_command(lowered):
                stop_speaking()
                self._emit("ai_response", "Goodbye.")
                self.running = False
                return

            self._emit("status", "processing")
            response = process_input(text)
            self._emit("ai_response", response)
            self._speak_with_interrupt(response)
            self._emit("status", "listening")

        threading.Thread(target=_process, daemon=True).start()


assistant = VoiceAssistant()
