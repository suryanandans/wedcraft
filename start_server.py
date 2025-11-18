#!/usr/bin/env python3
"""
WedCraft Server Startup Script
This script initializes the database and starts the FastAPI server
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def initialize_database():
    """Initialize the database"""
    print("🗄️  Initializing database...")
    try:
        subprocess.check_call([sys.executable, "init_db.py"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting WedCraft server...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")

def main():
    """Main startup function"""
    print("🎉 Welcome to WedCraft!")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    print("\n🎯 Server will be available at:")
    print("   🌐 http://localhost:8000")
    print("   📱 http://localhost:8000/login.html")
    print("   📊 http://localhost:8000/dashboard.html")
    print("   📚 http://localhost:8000/docs (API Documentation)")
    print("\n🔐 Default Login Credentials:")
    print("   Admin: admin@wedcraft.com / admin123")
    print("   User: john.sarah@example.com / password123")
    print("\n" + "=" * 50)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()