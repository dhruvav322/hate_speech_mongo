#!/bin/bash
# Simple script to start the backend

echo "🚀 Starting Hate Speech Moderation Backend..."
echo ""

cd "$(dirname "$0")"

# Set API key
export API_KEY=industry-demo-key-12345

# Check if dependencies are installed
echo "Checking dependencies..."
python -c "import fastapi, slowapi, pymongo" 2>/dev/null || {
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
}

# Start the backend
echo "Starting backend on port 8001..."
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

