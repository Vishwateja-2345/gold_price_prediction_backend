#!/usr/bin/env python
"""
Test script to verify the application is ready for deployment
"""

import os
import sys
import subprocess
import requests
import time
import json

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        import pandas
        import numpy
        import tensorflow
        import yfinance
        import schedule
        print("[SUCCESS] All required Python packages are installed")
        return True
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {str(e)}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_files():
    """Check if all required files exist"""
    print("\n🔍 Checking required files...")
    required_files = [
        "main.py",
        "fetcher.py",
        "train_model.py",
        "predict_model.py",
        "scheduler.py",
        "requirements.txt",
        "Procfile",
        "runtime.txt"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"[SUCCESS] {file} exists")
        else:
            print(f"[ERROR] {file} is missing")
            all_exist = False
    
    return all_exist

def check_data_files():
    """Check if data files exist"""
    print("\n🔍 Checking data files...")
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    if not os.path.exists(data_dir):
        print(f"[ERROR] Data directory is missing")
        return False
    
    data_files = [
        os.path.join(data_dir, "gold_data.csv"),
        os.path.join(data_dir, "historical_prices.json")
    ]
    
    all_exist = True
    for file in data_files:
        if os.path.exists(file):
            print(f"[SUCCESS] {os.path.basename(file)} exists")
        else:
            print(f"[ERROR] {os.path.basename(file)} is missing")
            all_exist = False
    
    return all_exist

def test_api():
    """Start the API and test endpoints"""
    print("\n🚀 Starting API for testing...")
    
    # Start the API in the background
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for the API to start
    print("Waiting for API to start...")
    time.sleep(3)
    
    # Test endpoints
    try:
        print("\n🔍 Testing API endpoints...")
        
        # Test root endpoint
        print("Testing / endpoint...")
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print(f"[SUCCESS] Root endpoint is working (status code: {response.status_code})")
        else:
            print(f"[ERROR] Root endpoint failed (status code: {response.status_code})")
        
        # Test health endpoint
        print("Testing /health endpoint...")
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"[SUCCESS] Health endpoint is working (status: {health_data['status']})")
        else:
            print(f"[ERROR] Health endpoint failed (status code: {response.status_code})")
        
        # Test predict endpoint
        print("Testing /predict endpoint...")
        response = requests.get("http://localhost:8000/predict")
        if response.status_code == 200:
            predict_data = response.json()
            print(f"[SUCCESS] Predict endpoint is working (status: {predict_data['status']})")
            print(f"   Predicted price: {predict_data['predicted_price']} INR per 10g")
        else:
            print(f"[ERROR] Predict endpoint failed (status code: {response.status_code})")
            
    except Exception as e:
        print(f"[ERROR] Error testing API: {str(e)}")
    finally:
        # Stop the API
        print("\n🛑 Stopping API...")
        api_process.terminate()
        api_process.wait()

def main():
    print("🟡 Gold Price Prediction API - Deployment Test\n")
    
    all_checks_passed = True
    
    if not check_dependencies():
        all_checks_passed = False
    
    if not check_files():
        all_checks_passed = False
    
    if not check_data_files():
        all_checks_passed = False
    
    if all_checks_passed:
        test_api()
        print("\n[SUCCESS] All tests passed! The application is ready for deployment.")
        print("To deploy to Heroku, run: python deploy.py")
    else:
        print("\n[ERROR] Some checks failed. Please fix the issues before deploying.")

if __name__ == "__main__":
    main()