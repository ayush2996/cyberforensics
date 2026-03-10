#!/bin/bash

# CyberGuard AI - Startup Script for Linux/macOS
# This script starts both the backend and frontend servers

clear

echo ""
echo "========================================================"
echo "   CyberGuard AI - Cyber Crime Reporting System"
echo "========================================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found. Please install Python 3.8 or later."
    exit 1
fi

# Check dependencies
echo "Checking dependencies..."
python3 -c "import streamlit, fastapi, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Missing required packages."
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Installation failed!"
        exit 1
    fi
fi

echo "✓ Dependencies verified"

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Start backend
echo ""
echo "Starting Backend Server..."
cd "$DIR"
python3 main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting Frontend Server..."
python3 -m streamlit run ui.py > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Display information
echo ""
echo "========================================================"
echo "   Starting Services..."
echo "========================================================"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:8501"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Browser should open automatically to the frontend."
echo "If not, please visit: http://localhost:8501"
echo ""
echo "========================================================"
echo ""
echo "Backend PID:  $BACKEND_PID  (logs: backend.log)"
echo "Frontend PID: $FRONTEND_PID (logs: frontend.log)"
echo ""
echo "To stop the services:"
echo "  kill $BACKEND_PID   # Stop backend"
echo "  kill $FRONTEND_PID  # Stop frontend"
echo ""
echo "Or press Ctrl+C to stop both services"
echo ""

# Default: open browser
if command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open "http://localhost:8501" 2>/dev/null &
elif command -v open &> /dev/null; then
    # macOS
    open "http://localhost:8501" 2>/dev/null &
fi

# Keep script running, catch Ctrl+C
trap 'echo "Shutting down..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

wait
