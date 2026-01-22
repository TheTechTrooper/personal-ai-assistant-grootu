# import speech_recognition as sr
# import sounddevice as sd
# import warnings

# warnings.filterwarnings("ignore")

# def listen():
#     recognizer = sr.Recognizer()
#     samplerate = 16000
#     duration = 4  # seconds

#     print("🎤 Listening...")

#     recording = sd.rec(
#         int(duration * samplerate),
#         samplerate=samplerate,
#         channels=1,
#         dtype="int16",
#         blocking=True
#     )

#     audio = sr.AudioData(recording.tobytes(), samplerate, 2)

#     try:
#         text = recognizer.recognize_google(audio)
#         print(f"✅ You said: {text}")
#         return text
#     except sr.UnknownValueError:
#         return "Sorry, I could not understand."
#     except sr.RequestError:
#         return "Speech service is unavailable."


import speech_recognition as sr
import sounddevice as sd
import warnings

warnings.filterwarnings("ignore")

# Lock default input device
sd.default.device = None  # use system default
sd.default.channels = 1
sd.default.samplerate = 16000

def listen():
    recognizer = sr.Recognizer()
    duration = 4

    print("🎤 Listening...")

    recording = sd.rec(
        int(duration * sd.default.samplerate),
        blocking=True,
        dtype="int16"
    )

    audio = sr.AudioData(recording.tobytes(), sd.default.samplerate, 2)

    try:
        text = recognizer.recognize_google(audio)
        print(f"✅ You said: {text}")
        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand."
