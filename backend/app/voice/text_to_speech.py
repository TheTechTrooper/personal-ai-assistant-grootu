import pyttsx3

def speak(text: str):
    print(f"🔊 AI says: {text}")

    engine = pyttsx3.init()   # re-initialize every time
    engine.setProperty("rate", 170)
    engine.setProperty("volume", 1.0)

    engine.say(text)
    engine.runAndWait()
    engine.stop()
