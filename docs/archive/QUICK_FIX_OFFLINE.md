# Quick Fix: System Status Shows "Offline"

## The Problem
Your frontend is trying to connect to the backend but getting "network connection was lost" errors.

## Root Cause
The backend needs to be started manually. Port 8000 is occupied by another service (optiroute).

## Solution: Start the Backend

### Step 1: Open a new terminal window

### Step 2: Navigate to the project directory
```bash
cd /Users/dhruvav/Desktop/hate_speech
```

### Step 3: Activate your Python environment (if you have one)
```bash
# If you have a virtual environment:
source .venv/bin/activate
# OR
source venv/bin/activate
```

### Step 4: Install dependencies (if not already installed)
```bash
pip install -r requirements.txt
```

### Step 5: Set the API key environment variable
```bash
export API_KEY=industry-demo-key-12345
```

### Step 6: Start the backend on port 8001
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
🛡️  Hate Speech Moderation System Started
```

### Step 7: Verify it's working
In another terminal, test:
```bash
curl http://localhost:8001/health
```

You should get a JSON response.

### Step 8: Refresh your browser
The frontend at http://localhost:3000 should now show **🟢 online** in the sidebar.

## Alternative: Use Port 8000 (Stop Other Service First)

If you want to use port 8000 instead:

1. **Stop the service on port 8000:**
   ```bash
   lsof -ti:8000 | xargs kill
   ```

2. **Start backend on port 8000:**
   ```bash
   python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Update frontend .env.local:**
   ```bash
   cd frontend-next
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   echo "NEXT_PUBLIC_API_KEY=industry-demo-key-12345" >> .env.local
   ```

4. **Restart the frontend** (if needed):
   ```bash
   # Stop current frontend (Ctrl+C)
   # Then restart:
   npm run dev
   ```

## Troubleshooting

### "Module not found" errors
Install dependencies:
```bash
pip install -r requirements.txt
```

### "API_KEY is required" error
Set the environment variable:
```bash
export API_KEY=industry-demo-key-12345
```

### Port already in use
Use a different port (8002, 8003, etc.) and update `.env.local` accordingly.

### MongoDB connection errors
Make sure MongoDB is running:
```bash
# If using Docker:
docker-compose up -d mongodb

# Or start MongoDB service manually
```

## Quick Test

Once the backend is running, test the analyze endpoint:
```bash
curl -X POST http://localhost:8001/api/v1/moderation/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: industry-demo-key-12345" \
  -d '{"text": "Hello world", "user_id": "test"}'
```

You should get a JSON response with toxicity scores.

