@echo off
echo ========================================
echo   PerspectAI - Starting Backend Server
echo ========================================
echo.

cd backend

echo Activating virtual environment...
call venv\Scripts\activate

IF ERRORLEVEL 1 (
    echo Virtual environment not found! Creating one...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
