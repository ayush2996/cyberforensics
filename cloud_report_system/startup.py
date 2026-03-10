#!/usr/bin/env python3
"""
CyberGuard AI Frontend - Startup Manager
Manages both backend and frontend servers with health checks
"""

import subprocess
import time
import requests
import sys
import os
import signal
import platform
from pathlib import Path

# ===================== CONFIGURATION =====================
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"
BACKEND_STARTUP_TIMEOUT = 10
FRONTEND_STARTUP_TIMEOUT = 5

# ===================== UTILITIES =====================
def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def check_health(url, timeout=3):
    """Check if service is healthy"""
    try:
        response = requests.get(url + "/health", timeout=timeout)
        return response.status_code == 200
    except:
        return False

def wait_for_service(url, timeout=10, service_name="Service"):
    """Wait for service to become healthy"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if check_health(url):
            print_success(f"{service_name} is healthy!")
            return True
        
        elapsed = int(time.time() - start_time)
        remaining = timeout - elapsed
        print(f"  Waiting for {service_name}... ({remaining}s remaining)", end='\r')
        time.sleep(1)
    
    print_error(f"{service_name} did not start within {timeout} seconds")
    return False

# ===================== BACKEND STARTUP =====================
def start_backend():
    """Start the FastAPI backend server"""
    print_header("🚀 Starting Backend Server")
    
    # Check if backend is already running
    if check_health(BACKEND_URL):
        print_success("Backend is already running!")
        return True
    
    print_info("Starting FastAPI server...")
    
    try:
        # Determine the backend script location
        current_dir = Path(__file__).parent
        backend_script = current_dir / "main.py"
        
        if not backend_script.exists():
            print_error(f"Backend script not found: {backend_script}")
            return False
        
        # Start backend process
        if platform.system() == "Windows":
            backend_process = subprocess.Popen(
                [sys.executable, str(backend_script)],
                cwd=str(current_dir),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            backend_process = subprocess.Popen(
                [sys.executable, str(backend_script)],
                cwd=str(current_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        # Wait for backend to be healthy
        if wait_for_service(BACKEND_URL, BACKEND_STARTUP_TIMEOUT, "Backend"):
            print_success("Backend server started successfully!")
            print_info(f"API available at: {BACKEND_URL}")
            print_info(f"Interactive docs at: {BACKEND_URL}/docs")
            return True
        else:
            print_error("Backend failed to start")
            return False
    
    except Exception as e:
        print_error(f"Failed to start backend: {str(e)}")
        return False

# ===================== FRONTEND STARTUP =====================
def start_frontend():
    """Start the Streamlit frontend"""
    print_header("🎨 Starting Frontend Server")
    
    print_info("Starting Streamlit app...")
    
    try:
        current_dir = Path(__file__).parent
        frontend_script = current_dir / "ui.py"
        
        if not frontend_script.exists():
            print_error(f"Frontend script not found: {frontend_script}")
            return False
        
        # Start frontend process
        if platform.system() == "Windows":
            subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", str(frontend_script)],
                cwd=str(current_dir),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", str(frontend_script)],
                cwd=str(current_dir)
            )
        
        # Give frontend time to start
        time.sleep(FRONTEND_STARTUP_TIMEOUT)
        
        # Check if frontend is accessible
        try:
            import webbrowser
            print_success("Opening browser to frontend...")
            webbrowser.open(FRONTEND_URL)
        except:
            print_info(f"Please open your browser to: {FRONTEND_URL}")
        
        print_success("Frontend started successfully!")
        return True
    
    except Exception as e:
        print_error(f"Failed to start frontend: {str(e)}")
        return False

# ===================== SYSTEM CHECKS =====================
def check_dependencies():
    """Check if all required packages are installed"""
    print_header("📦 Checking Dependencies")
    
    required_packages = {
        'fastapi': 'FastAPI (Backend)',
        'uvicorn': 'Uvicorn (ASGI Server)',
        'streamlit': 'Streamlit (Frontend)',
        'requests': 'Requests (HTTP Client)',
        'pydantic': 'Pydantic (Validation)',
    }
    
    all_installed = True
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            print_success(f"{name} installed")
        except ImportError:
            print_error(f"{name} NOT installed")
            all_installed = False
    
    if not all_installed:
        print_warning("\nSome packages are missing. Install with:")
        print("  pip install -r requirements.txt")
        return False
    
    return True

def check_ports():
    """Check if required ports are available"""
    print_header("🔌 Checking Ports")
    
    import socket
    
    ports = {
        8000: "Backend (FastAPI)",
        8501: "Frontend (Streamlit)"
    }
    
    for port, service in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        
        if result == 0:
            print_warning(f"Port {port} ({service}) is already in use")
        else:
            print_success(f"Port {port} ({service}) is available")
        
        sock.close()

# ===================== DISPLAY INFORMATION =====================
def display_startup_info():
    """Display startup information"""
    print("\n")
    print("🛡️  ")
    print("CyberGuard AI - Cyber Crime Reporting System")
    print("="*60)
    print("\n📍 Endpoints:")
    print(f"  Backend:  {BACKEND_URL}")
    print(f"  Frontend: {FRONTEND_URL}")
    print(f"  API Docs: {BACKEND_URL}/docs")
    print("\n💡 Tips:")
    print("  • If a port is already in use, the service may already be running")
    print("  • Check backend logs for any startup issues")
    print("  • Frontend will auto-detect backend availability")
    print("\n" + "="*60 + "\n")

def display_success_message():
    """Display success message"""
    print("\n")
    print_header("✨ All Systems Ready!")
    print("""
🎉 Your CyberGuard AI system is now running!

📍 Access Points:
   Frontend:      http://localhost:8501
   Backend API:   http://localhost:8000
   API Docs:      http://localhost:8000/docs

🚀 Next Steps:
   1. Frontend browser window should open automatically
   2. If not, visit: http://localhost:8501
   3. Start by describing your cyber incident
   4. AI will guide you through the rest!

📚 Documentation:
   • User Guide:     FRONTEND_USER_GUIDE.md
   • API Testing:    API_TESTING_GUIDE.md
   • Architecture:   ARCHITECTURE.md
   • Quick Start:    QUICKSTART.md

⌨️  Command Reference:
   • Backend:  http://localhost:8000
   • Frontend: http://localhost:8501
   • Logs:     Check terminal/console output

🛑 To Stop the System:
   • Close the browser window
   • Press Ctrl+C in the terminal
   • Or close the command windows

Questions? Check the documentation files!
    """)

# ===================== MAIN STARTUP FLOW =====================
def main():
    """Main startup flow"""
    
    # Display header
    print("\n" * 2)
    print("🛡️  " + "="*56)
    print("   CyberGuard AI - Startup Manager")
    print("="*60 + "\n")
    
    # Check dependencies
    if not check_dependencies():
        print("\n" + "="*60)
        print("⚠️  Please install missing dependencies first!")
        print("="*60)
        sys.exit(1)
    
    # Check ports
    check_ports()
    
    # Display startup info
    display_startup_info()
    
    # Start backend
    if not start_backend():
        print_error("\nCould not start backend. Please try manually:")
        print(f"  python main.py")
        sys.exit(1)
    
    time.sleep(2)
    
    # Start frontend
    if not start_frontend():
        print_error("\nCould not start frontend. Please try manually:")
        print(f"  streamlit run ui.py")
        sys.exit(1)
    
    # Success!
    display_success_message()
    
    # Keep process running
    print("\n💤 Startup manager is watching... Press Ctrl+C to exit\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_info("\nShutting down...")
        sys.exit(0)

# ===================== ENTRY POINT =====================
if __name__ == "__main__":
    main()
