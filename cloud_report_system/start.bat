@echo off
REM CyberGuard AI - Startup Script for Windows
REM This script starts both the backend and frontend servers

setlocal enabledelayedexpansion

cls
echo.
echo ========================================================
echo   CyberGuard AI - Cyber Crime Reporting System
echo ========================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8 or later.
    pause
    exit /b 1
)

echo Checking dependencies...
python -c "import streamlit, fastapi, requests" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Missing required packages.
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Installation failed!
        pause
        exit /b 1
    )
)

echo ✓ Dependencies verified

REM Start backend in a new window
echo.
echo Starting Backend Server...
start "CyberGuard Backend" python main.py
timeout /t 3 /nobreak

REM Start frontend in a new window
echo Starting Frontend Server...
start "CyberGuard Frontend" python -m streamlit run ui.py

echo.
echo ========================================================
echo   Starting Services...
echo ========================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8501
echo API Docs: http://localhost:8000/docs
echo.
echo Browser should open automatically to the frontend.
echo If not, please visit: http://localhost:8501
echo.
echo Press any key to continue...
pause
