# 🤖 Personal AI Assistant

A voice-based personal AI assistant designed to work across **Windows** and **iOS**, customized to the user's preferences.  
This project is being built incrementally with clear daily milestones.

---

## ✨ Features (Planned & In Progress)

### ✅ Implemented (Day 1)
- 🎙️ Voice-based interaction (Speech to Text & Text to Speech)
- 🔊 AI voice output
- 🎧 Microphone input handling (Windows-safe)
- ⚙️ FastAPI backend running locally
- 🧪 End-to-end voice loop (speak → listen → respond)

### 🚧 Planned
- 🧠 Memory system (remembers preferences, notes, tasks)
- 💻 Coding assistant (Python, FastAPI, MongoDB)
- 💰 Personal finance assistant
- 🏋️ Workout & diet assistant
- 🌐 Internet search capability
- 📱 iOS mobile application
- 🖥️ Windows desktop application

---

## 📁 Project Structure




---

## ⚙️ Tech Stack

- **Language:** Python 3.10
- **Backend:** FastAPI, Uvicorn
- **Voice (STT):** SpeechRecognition + sounddevice
- **Voice (TTS):** pyttsx3
- **OS:** Windows (Day 1)
- **IDE:** Visual Studio Code

---

## ▶️ How to Run (Backend)

### 1️⃣ Create & activate virtual environment
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate


