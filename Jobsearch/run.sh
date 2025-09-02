#!/bin/bash

# 🚀 Job Search Application Launcher
# ===================================

echo "🔍 JOB SEARCH APPLICATION"
echo "========================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import requests, dotenv" 2>/dev/null; then
    echo "⚠️ Some dependencies are missing. Installing..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "✅ All dependencies are available"
fi

echo ""
echo "🚀 Starting Job Search Application..."
echo ""

# Run the application
python3 job_search.py

