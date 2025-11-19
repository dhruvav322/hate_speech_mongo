# Backend Connection Issue - Quick Fix

## Problem
Port 8000 is currently being used by another service (optiroute). The frontend can't connect to the hate speech backend.

## Solution Options

### Option 1: Use Port 8001 (Recommended - No Conflicts)

1. **Start the backend on port 8001:**
   ```bash
   cd /Users/dhruvav/Desktop/hate_speech
   python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
   ```

2. **Update frontend environment:**
   The `.env.local` file has been created with port 8001. If you need to update it manually:
   ```bash
   cd frontend-next
   echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > .env.local
   echo "NEXT_PUBLIC_API_KEY=industry-demo-key-12345" >> .env.local
   ```

3. **Restart the frontend** (if it's running):
   - The frontend will automatically pick up the new port
   - Refresh your browser

### Option 2: Stop Other Service and Use Port 8000

1. **Stop the service on port 8000:**
   ```bash
   # Find the process
   lsof -ti:8000
   
   # Kill it (replace PID with the number from above)
   kill <PID>
   ```

2. **Start hate speech backend on port 8000:**
   ```bash
   cd /Users/dhruvav/Desktop/hate_speech
   python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Update frontend to use port 8000:**
   ```bash
   cd frontend-next
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   echo "NEXT_PUBLIC_API_KEY=industry-demo-key-12345" >> .env.local
   ```

## Verify Backend is Running

After starting the backend, test it:
```bash
curl http://localhost:8001/health
# or
curl http://localhost:8000/health
```

You should see a JSON response with status information.

## System Status Indicator

The sidebar will automatically show:
- 🟢 **Green (online)** - Backend is connected
- 🟡 **Yellow (checking)** - Initial connection check
- 🔴 **Red (offline)** - Backend is not reachable

The status checks every 30 seconds automatically.

