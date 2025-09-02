#!/usr/bin/env python3
"""
Startup script for the Agentic Chatbot
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from parent directory (APPS root)
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

def check_environment():
    """Check if required environment variables are set"""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import langgraph
        import langchain
        import fastapi
        import uvicorn
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip3 install -r requirements.txt")
        return False

def main():
    """Main startup function"""
    print("🚀 Starting Agentic Chatbot...")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ Environment check passed")
    print("🌐 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:8000")
    print("=" * 40)
    
    # Import and run the app
    try:
        from app import app
        import uvicorn
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
