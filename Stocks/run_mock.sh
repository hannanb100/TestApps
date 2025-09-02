#!/bin/bash

# 🚀 AI Stock Tracking Agent - Mock SMS Launcher
# ==============================================

echo "📈 AI STOCK TRACKING AGENT (MOCK SMS)"
echo "======================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.11+ and try again"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION+ is required, but you have Python $PYTHON_VERSION"
    echo "Please upgrade Python and try again"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment found"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import fastapi, uvicorn, langchain, openai, yfinance" 2>/dev/null; then
    echo "⚠️ Some dependencies are missing. Installing..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "✅ All dependencies are available"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found"
    if [ -f "env.example" ]; then
        echo "📋 Copying env.example to .env..."
        cp env.example .env
        echo "✅ .env file created from template"
        echo "🔧 Please edit .env file with your API keys and configuration"
        echo ""
        echo "Required configuration:"
        echo "  - OPENAI_API_KEY (for AI analysis)"
        echo "  - Other settings are optional for mock testing"
        echo ""
        read -p "Press Enter to continue after configuring .env file..."
    else
        echo "❌ No .env file or env.example template found"
        echo "Please create a .env file with your configuration"
        exit 1
    fi
else
    echo "✅ .env file found"
fi

# Validate environment variables
echo "🔍 Validating environment configuration..."
python3 -c "
import os
from dotenv import load_dotenv

load_dotenv()

# Only check OpenAI API key for mock testing
if not os.getenv('OPENAI_API_KEY'):
    print('⚠️ OPENAI_API_KEY not set - AI analysis will use mock data')
    print('   Set OPENAI_API_KEY in .env for full AI functionality')
else:
    print('✅ OPENAI_API_KEY is set - AI analysis enabled')
"

echo ""
echo "🚀 Starting AI Stock Tracking Agent (Mock SMS Mode)..."
echo "======================================================"
echo ""
echo "📱 Mock SMS Commands:"
echo "  • Add AAPL    - Add stock to watchlist"
echo "  • Remove TSLA - Remove stock from watchlist"
echo "  • List        - Show tracked stocks"
echo "  • Status      - Check system status"
echo "  • Help        - Show available commands"
echo "  • Test        - Run stock analysis test"
echo "  • History     - Show message history"
echo "  • Quit        - Exit the application"
echo ""
echo "💡 All SMS messages will be displayed in the console"
echo "   No external services required!"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the console interface
python3 test_console.py
