#!/bin/bash
# Production startup script for Railway deployment

echo "🚀 Starting AI Stock Tracking Agent..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements-prod.txt

# Start the application
echo "🌟 Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
