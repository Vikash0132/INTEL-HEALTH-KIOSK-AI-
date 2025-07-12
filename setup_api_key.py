#!/usr/bin/env python3
"""
Setup script for Intel AI Healthcare Kiosk
This script helps configure the Google AI Studio API key
"""

import os
import sys

def setup_api_key():
    """Setup Google AI Studio API key"""
    print("=== Intel AI Healthcare Kiosk Setup ===")
    print("\nTo run this application, you need a Google AI Studio API key.")
    print("\nSteps to get your API key:")
    print("1. Go to https://ai.google.dev/")
    print("2. Click 'Get API key in Google AI Studio'")
    print("3. Sign in with your Google account")
    print("4. Create a new API key")
    print("5. Copy the API key")
    
    api_key = input("\nPlease enter your Google AI Studio API key: ").strip()
    
    if not api_key or api_key == "your-google-ai-studio-api-key-here":
        print("❌ No valid API key provided. Setup cancelled.")
        return False
    
    # Update .env file
    env_path = ".env"
    try:
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Replace the placeholder API key
        content = content.replace(
            "GOOGLE_API_KEY=your-google-ai-studio-api-key-here",
            f"GOOGLE_API_KEY={api_key}"
        )
        
        with open(env_path, 'w') as f:
            f.write(content)
        print(f"✅ Updated {env_path}")
    except Exception as e:
        print(f"❌ Error updating {env_path}: {e}")
    
    # Update secrets.toml file
    secrets_path = ".streamlit/secrets.toml"
    try:
        with open(secrets_path, 'r') as f:
            content = f.read()
        
        # Replace the placeholder API key
        content = content.replace(
            'GOOGLE_API_KEY = "your-google-ai-studio-api-key-here"',
            f'GOOGLE_API_KEY = "{api_key}"'
        )
        
        with open(secrets_path, 'w') as f:
            f.write(content)
        print(f"✅ Updated {secrets_path}")
    except Exception as e:
        print(f"❌ Error updating {secrets_path}: {e}")
    
    print("\n🎉 Setup complete! You can now run the application with:")
    print("streamlit run app.py")
    
    return True

if __name__ == "__main__":
    setup_api_key()
