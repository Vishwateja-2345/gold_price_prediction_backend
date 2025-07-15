#!/usr/bin/env python
"""
Script to run the Gold Price Prediction API and scheduler locally
"""

import subprocess
import sys
import os
import time
import signal
import webbrowser

def run_api_and_scheduler():
    """Run the API and scheduler in separate processes"""
    print("🟡 Starting Gold Price Prediction System locally...\n")
    
    # Start the API in a separate process
    print("🚀 Starting API server...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Wait a bit for the API to start
    time.sleep(2)
    
    # Start the scheduler in a separate process
    print("⏰ Starting scheduler...")
    scheduler_process = subprocess.Popen(
        [sys.executable, "scheduler.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Open the API in the default web browser
    print("🌐 Opening API in web browser...")
    webbrowser.open("http://localhost:8000")
    
    print("\n[SUCCESS] System is running!")
    print("API: http://localhost:8000")
    print("\nPress Ctrl+C to stop all processes and exit")
    
    # Monitor the processes and print their output
    try:
        while api_process.poll() is None and scheduler_process.poll() is None:
            # Print API output
            api_line = api_process.stdout.readline()
            if api_line:
                print(f"[API] {api_line.strip()}")
            
            # Print scheduler output
            scheduler_line = scheduler_process.stdout.readline()
            if scheduler_line:
                print(f"[SCHEDULER] {scheduler_line.strip()}")
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all processes...")
    finally:
        # Terminate both processes
        if api_process.poll() is None:
            api_process.terminate()
            api_process.wait()
        
        if scheduler_process.poll() is None:
            scheduler_process.terminate()
            scheduler_process.wait()
        
        print("[SUCCESS] All processes stopped")

if __name__ == "__main__":
    run_api_and_scheduler()