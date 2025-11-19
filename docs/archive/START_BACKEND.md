# 🚀 Start the Backend - Step by Step

## The Problem
The frontend shows "offline" because the backend isn't running on port 8001.

## Solution: Start Backend Manually

### Step 1: Open a NEW Terminal Window
(Keep your frontend terminal running separately)

### Step 2: Navigate to Project
```bash
cd /Users/dhruvav/Desktop/hate_speech
```

### Step 3: Set API Key
```bash
export API_KEY=industry-demo-key-12345
```

### Step 4: Install Dependencies (if needed)
```bash
pip install -r requirements.txt
```

**Note:** This may take 5-10 minutes. You only need to do this once.

### Step 5: Start the Backend
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### Step 6: Look for Success Message
You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
🛡️  Hate Speech Moderation System Started
```

### Step 7: Test It (in another terminal)
```bash
curl http://localhost:8001/health
```

Should return JSON like:
```json
{"status":"healthy","version":"1.0.0",...}
```

### Step 8: Refresh Your Browser
Go to http://localhost:3000 and the sidebar should show **🟢 online**

---

## Common Errors & Fixes

### Error: "ModuleNotFoundError: No module named 'X'"
**Fix:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Error: "API_KEY is required"
**Fix:** Set the environment variable:
```bash
export API_KEY=industry-demo-key-12345
```

### Error: "Port 8001 already in use"
**Fix:** Use a different port:
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
```
Then update frontend `.env.local`:
```bash
cd frontend-next
echo "NEXT_PUBLIC_API_URL=http://localhost:8002" > .env.local
```

### Error: MongoDB connection failed
**Fix:** If using local MongoDB, make sure it's running:
```bash
# Check if MongoDB is running
brew services list | grep mongodb
# Or start it:
brew services start mongodb-community
```

---

## Quick Start Script

I've created a helper script. Run:
```bash
./start_backend_simple.sh
```

This will:
1. Check dependencies
2. Install if missing
3. Start the backend

---

## Once Backend is Running

✅ **Backend terminal shows:** "Uvicorn running on http://0.0.0.0:8001"
✅ **Browser sidebar shows:** 🟢 online
✅ **Console errors stop:** No more "Failed to load resource"
✅ **You can analyze text:** The analyze page will work

---

## Keep Backend Running

**Important:** Keep the backend terminal window open. If you close it, the backend stops and the frontend will show offline again.

To stop the backend: Press `Ctrl+C` in the backend terminal.

