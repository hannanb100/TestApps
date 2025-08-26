#!/bin/bash

echo "🔄 Stopping Flask app..."
pkill -f "python app.py"

echo "⏳ Waiting for processes to stop..."
sleep 2

echo "🐍 Activating virtual environment..."
source venv/bin/activate

echo "🚀 Starting Flask app..."
python app.py
