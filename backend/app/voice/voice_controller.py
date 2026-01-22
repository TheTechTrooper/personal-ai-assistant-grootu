import time
from app.voice.speech_to_text import listen
from app.voice.text_to_speech import speak

def start_voice_test():
    speak("Hello. I am your grootu. Please speak now.")
    text = listen()
    time.sleep(0.5)  # allow audio device to reset
    speak(f"You said {text}")

if __name__ == "__main__":
    start_voice_test()
