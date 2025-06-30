"""
Setup script for Intel AI Healthcare Kiosk
Run this script to set up and launch the application
"""

import os
import subprocess
import sys
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import streamlit
        import google.generativeai
        import pandas
        import plotly
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("📝 Please copy .env.example to .env and add your Google AI Studio API key")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
        if 'GOOGLE_API_KEY=your_google_ai_studio_api_key_here' in content:
            print("❌ Please update your Google AI Studio API key in .env file")
            return False
        elif 'GOOGLE_API_KEY=' in content:
            print("✅ Environment file configured")
            return True
        else:
            print("❌ GOOGLE_API_KEY not found in .env file")
            return False

def create_env_file():
    """Create .env file from template"""
    if not Path(".env").exists():
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("📋 Created .env file from template")
            print("🔑 Please edit .env and add your Google AI Studio API key")
        else:
            print("❌ .env.example file not found")

def run_streamlit():
    """Run the Streamlit application"""
    try:
        print("🚀 Starting Intel AI Healthcare Kiosk...")
        print("🌐 The application will open in your default web browser")
        print("📍 URL: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the application")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to start Streamlit application")
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")

def main():
    """Main setup and launch function"""
    print("🏥 Intel AI Healthcare Kiosk Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found. Please run this script from the project root directory.")
        return
    
    # Check requirements
    if not check_requirements():
        print("📦 Installing requirements...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Requirements installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install requirements")
            return
    
    # Check .env file
    if not check_env_file():
        create_env_file()
        if not check_env_file():
            print("\n🔧 Setup Instructions:")
            print("1. Edit the .env file")
            print("2. Replace 'your_google_ai_studio_api_key_here' with your actual API key")
            print("3. Get your API key from: https://makersuite.google.com/app/apikey")
            print("4. Run this script again")
            return
    
    print("\n✅ Setup complete!")
    print("🎯 All components are ready")
    
    # Ask user if they want to start the application
    start_app = input("\n🚀 Would you like to start the application now? (y/N): ").lower().strip()
    if start_app in ['y', 'yes']:
        run_streamlit()
    else:
        print("\n📋 To start the application later, run:")
        print("   streamlit run app.py")
        print("\n🌐 Or use the VS Code task: 'Run Intel AI Healthcare Kiosk'")

if __name__ == "__main__":
    main()
