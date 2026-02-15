@echo off
cd /d %~dp0
set BACKEND_UP=
for /f "tokens=1,2,3,4,5" %%a in ('netstat -ano ^| findstr /R /C:":8000 .*LISTENING"') do (
    set BACKEND_UP=1
)

if not defined BACKEND_UP (
    echo Backend is not running on port 8000. Starting backend...
    start "Jarvis Backend" cmd /c "cd /d ..\backend && run_backend_stable.bat"
    timeout /t 3 >nul
)

echo Starting Jarvis Desktop App...
..\backend\.venv\Scripts\python.exe main.py
pause
