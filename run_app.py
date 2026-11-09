"""
Startup script for Insurance Document Intelligence.
This script helps run both the FastAPI backend and Streamlit frontend.
"""

import subprocess
import sys
import time
import webbrowser
from threading import Thread

def run_backend():
    """Run the FastAPI backend."""
    print("🚀 Starting FastAPI backend...")
    subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"])

def run_frontend():
    """Run the Streamlit frontend."""
    print("🎨 Starting Streamlit frontend...")
    time.sleep(3)  # Wait for backend to start
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])

def main():
    """Main function to start both services."""
    print("=" * 60)
    print("🏢 Insurance Document Intelligence")
    print("=" * 60)
    print("Starting both backend and frontend services...")
    print()

    # Start backend in a separate thread
    backend_thread = Thread(target=run_backend, daemon=True)
    backend_thread.start()

    # Wait a moment then start frontend
    time.sleep(2)

    print("✅ Backend started on http://localhost:8000")
    print("✅ Frontend will start on http://localhost:8501")
    print()
    print("📋 Upload your ACORD 125 forms and extract comprehensive business insurance data!")
    print()

    # Start frontend (this will block)
    run_frontend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Shutting down services...")
        sys.exit(0)
