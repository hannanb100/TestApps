#!/bin/bash

# Restart Server Script
# ====================
# This script kills any process running on port 8002 and starts the web interface

echo "🔄 Restarting Agent Team Web Server..."
echo "======================================"

# Find and kill any process running on port 8002
echo "🔍 Checking for processes on port 8002..."
PID=$(lsof -ti:8002)

if [ ! -z "$PID" ]; then
    echo "🛑 Found process $PID running on port 8002"
    echo "💀 Killing process $PID..."
    kill $PID
    sleep 2
    
    # Check if process was killed successfully
    if kill -0 $PID 2>/dev/null; then
        echo "⚠️  Process still running, force killing..."
        kill -9 $PID
        sleep 1
    fi
    
    echo "✅ Process killed successfully"
else
    echo "✅ No process found on port 8002"
fi

# Wait a moment for the port to be released
echo "⏳ Waiting for port to be released..."
sleep 2

# Start the web interface
echo "🚀 Starting web interface..."
echo "======================================"
python web_interface_fixed.py

