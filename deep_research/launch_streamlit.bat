@echo off
REM Launch script for Deep Research Streamlit App

echo ========================================
echo Deep Research System - Streamlit Launcher
echo ========================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Streamlit app...
echo App will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

streamlit run streamlit_app/app.py

pause
