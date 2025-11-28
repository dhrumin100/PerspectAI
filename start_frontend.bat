@echo off
echo ========================================
echo   PerspectAI - Starting Frontend Dev Server
echo ========================================
echo.

cd frontend

IF NOT EXIST node_modules (
    echo node_modules not found! Installing dependencies...
    call npm install
)

echo.
echo Starting Vite dev server on http://localhost:5173
echo Press Ctrl+C to stop
echo.

call npm run dev
