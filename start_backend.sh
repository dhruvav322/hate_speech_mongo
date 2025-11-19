#!/bin/bash
# Start the Hate Speech Moderation Backend

echo "🚀 Starting Hate Speech Moderation Backend..."
echo "📍 Port: 8001 (to avoid conflict with other services)"
echo ""

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

