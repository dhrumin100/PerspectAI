@echo off
echo Starting PerspectAI System...

echo Starting Backend (Port 8000)...
start "PerspectAI Backend" /min cmd /k "set PYTHONPATH=%PYTHONPATH%;%~dp0 && python backend/app/main.py"

echo Starting Frontend (Port 5173)...
cd frontend
start "PerspectAI Frontend" /min cmd /k "npm run dev"

echo System is running!
echo Frontend: http://localhost:5173
echo Backend: http://localhost:8000
pause
