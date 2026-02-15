@echo off
cd /d %~dp0
title Jarvis Backend

:restart
echo [Backend] Starting server on 127.0.0.1:8000 ...
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
echo [Backend] Server exited with code %ERRORLEVEL%.
echo [Backend] Restarting in 2 seconds...
timeout /t 2 >nul
goto restart
