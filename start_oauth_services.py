#!/usr/bin/env python3
"""
Startup script for OAuth services
Runs both Instagram and Facebook Pages OAuth services
"""

import subprocess
import sys
import time
import signal
import os

def start_service(name, module, port):
    """Start a service on the specified port"""
    print(f"🚀 Starting {name} on port {port}...")
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            f"{module}:app", 
            "--reload", 
            "--port", str(port),
            "--host", "0.0.0.0"
        ])
        return process
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

def main():
    print("🎯 OAuth Services Startup Script")
    print("=" * 50)
    
    # Start Instagram OAuth service
    instagram_process = start_service("Instagram OAuth", "instagram", 8000)
    if not instagram_process:
        print("❌ Failed to start Instagram service")
        return
    
    # Start Facebook Pages OAuth service  
    facebook_process = start_service("Facebook Pages OAuth", "facebook_pages", 8001)
    if not facebook_process:
        print("❌ Failed to start Facebook Pages service")
        instagram_process.terminate()
        return
    
    print("\n✅ Both services started successfully!")
    print("📋 Service URLs:")
    print("   Instagram OAuth: http://127.0.0.1:8000")
    print("   Facebook Pages: http://127.0.0.1:8001")
    print("   Instagram Docs: http://127.0.0.1:8000/docs")
    print("   Facebook Pages Docs: http://127.0.0.1:8001/docs")
    print("\n🛑 Press Ctrl+C to stop all services")
    
    def signal_handler(sig, frame):
        print("\n🛑 Stopping services...")
        instagram_process.terminate()
        facebook_process.terminate()
        print("✅ Services stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
