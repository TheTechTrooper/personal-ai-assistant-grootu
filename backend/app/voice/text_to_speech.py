import threading
import time

import pyttsx3

_engine_lock = threading.Lock()
_current_engine = None
_speaking_event = threading.Event()


def _set_current_engine(engine):
    global _current_engine
    with _engine_lock:
        _current_engine = engine


def is_speaking() -> bool:
    return _speaking_event.is_set()


def stop_speaking() -> None:
    with _engine_lock:
        engine = _current_engine
    if engine is not None:
        try:
            engine.stop()
        except Exception:
            pass


def speak(text: str):
    if not text:
        return

    print(f"AI says: {text}")
    engine = None
    _speaking_event.set()
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 165)
        engine.setProperty("volume", 1.0)

        for voice in engine.getProperty("voices"):
            if "zira" in voice.name.lower():
                engine.setProperty("voice", voice.id)
                break

        _set_current_engine(engine)
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass
    finally:
        if engine is not None:
            try:
                engine.stop()
            except Exception:
                pass
        _set_current_engine(None)
        _speaking_event.clear()
        time.sleep(0.2)


def speak_async(text: str) -> threading.Thread | None:
    if not text:
        return None
    thread = threading.Thread(target=speak, args=(text,), daemon=True)
    thread.start()
    return thread
