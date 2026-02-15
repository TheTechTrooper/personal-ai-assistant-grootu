# Personal Jarvis (Local V1)

Offline-first personal assistant with:
- Local LLM via Ollama
- Voice input/output
- Short-term + long-term memory
- Desktop control UI
- Basic command execution

## V1 Stack
- LLM: `ollama` (`llama3:8b`, `mistral:7b`, or `phi3`)
- STT: Faster-Whisper (offline)
- TTS: pyttsx3 (offline)
- Memory:
  - Short-term: in-memory conversation window (last 20 turns)
  - Long-term: SQLite (`backend/assistant_memory.db`)
- Backend: FastAPI + WebSocket
- Desktop UI: Flet (`desktop_app/main.py`)

## Quick Start
1. Install Ollama and pull a model:
```powershell
ollama pull mistral:7b
ollama run mistral:7b
```

2. Create environment and install dependencies:
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Run CLI mode (Phase 2):
```powershell
set OLLAMA_MODEL=mistral:7b
python -m app.cli
```

4. Run backend voice mode:
```powershell
set OLLAMA_MODEL=mistral:7b
uvicorn app.main:app --reload
```

5. Run desktop app:
```powershell
run_backend.bat
run_ui.bat
```

Or run direct:
```powershell
cd desktop_app
..\backend\.venv\Scripts\python.exe main.py
```

## Implemented V1 Capabilities
- Conversation loop with local Ollama
- Wake-word voice flow:
  - Say `hey jarvis` once to start a session
  - Continue with follow-up commands without repeating wake word
  - Say `stop` / `stop speaking` to stop and return to wake-word mode
- Desktop voice-state cue panel:
  - `Speak now` when listening
  - `Thinking...` when processing
  - reconnect status when backend is unavailable
- Memory commands:
  - `my name is ...`
  - `what is my name`
  - `remember this: ...`
  - `what do you know about ...`
- Task commands:
  - `add task ...`
  - `show pending tasks`
  - `complete task <id>`
- System commands:
  - `open vscode`
  - `show today git commits`

## Notes
- Configure model with env var:
  - `OLLAMA_MODEL` (default: `mistral:7b`)
- Configure STT with env vars:
  - `STT_MODEL_SIZE` (default: `small.en`; options: `base.en`, `small.en`, `medium.en`)
  - `STT_DEVICE` (default: `cpu`)
  - `STT_COMPUTE_TYPE` (default: `int8`)
  - `STT_ENERGY_THRESHOLD` (default: `0.012`)
- Memory DB path can be overridden:
  - `ASSISTANT_MEMORY_DB`
- Memory growth controls:
  - `ASSISTANT_MAX_NOTES` (default: `5000`)
  - `ASSISTANT_MAX_TASKS` (default: `10000`)
  - `ASSISTANT_DONE_TASK_RETENTION_DAYS` (default: `90`)
- Runtime memory management commands:
  - `show memory stats`
  - `cleanup memory`
- Useful launchers:
  - `run_backend.bat`
  - `run_ui.bat`
  - `backend/run_backend_stable.bat`

## Next Steps for V1.5
- Improve tool/action execution for browser and app automation
- Add richer agent actions and confirmations for external operations
- Optional: replace pyttsx3 with streaming TTS
