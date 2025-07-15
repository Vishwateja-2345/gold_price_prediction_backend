#!/usr/bin/env python
"""
Deployment helper script for the Gold Price Prediction API
"""

import os
import subprocess
import sys

def check_requirements():
    """Check if all required tools are installed"""
    try:
        # Check if git is installed
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE)
        print("[SUCCESS] Git is installed")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("[ERROR] Git is not installed. Please install Git first.")
        return False
    
    try:
        # Check if heroku CLI is installed
        subprocess.run(["heroku", "--version"], check=True, stdout=subprocess.PIPE)
        print("[SUCCESS] Heroku CLI is installed")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("[ERROR] Heroku CLI is not installed. Please install the Heroku CLI first.")
        return False
    
    return True

def heroku_login():
    """Log in to Heroku"""
    print("\n🔑 Logging in to Heroku...")
    subprocess.run(["heroku", "login"], check=True)

def create_heroku_app():
    """Create a new Heroku app"""
    app_name = input("\n🚀 Enter a name for your Heroku app (leave blank for random name): ").strip()
    
    cmd = ["heroku", "create"]
    if app_name:
        cmd.append(app_name)
    
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, text=True)
    print(result.stdout)
    
    # Extract app name from output
    for line in result.stdout.splitlines():
        if "https://" in line:
            return line.split("https://")[1].split(".")[0]
    
    return None

def setup_git():
    """Initialize git repository if not already initialized"""
    if not os.path.exists(".git"):
        print("\n📁 Initializing git repository...")
        subprocess.run(["git", "init"], check=True)
    
    print("\n📝 Adding files to git...")
    subprocess.run(["git", "add", "."], check=True)
    
    print("\n💾 Committing changes...")
    subprocess.run(["git", "commit", "-m", "Prepare for Heroku deployment"], check=True)

def deploy_to_heroku():
    """Deploy the app to Heroku"""
    print("\n🚀 Deploying to Heroku...")
    subprocess.run(["git", "push", "heroku", "main"], check=True)

def scale_workers(app_name):
    """Scale the worker dyno"""
    print("\n⚙️ Scaling worker dyno...")
    subprocess.run(["heroku", "ps:scale", "worker=1", "-a", app_name], check=True)

def main():
    print("🟡 Gold Price Prediction API - Deployment Helper\n")
    
    if not check_requirements():
        sys.exit(1)
    
    heroku_login()
    app_name = create_heroku_app()
    
    if not app_name:
        print("[ERROR] Failed to create Heroku app")
        sys.exit(1)
    
    setup_git()
    deploy_to_heroku()
    scale_workers(app_name)
    
    print(f"\n[SUCCESS] Deployment complete! Your API is now running at: https://{app_name}.herokuapp.com")
    print("[SUCCESS] The scheduler is also running and will fetch data every hour")

if __name__ == "__main__":
    main()