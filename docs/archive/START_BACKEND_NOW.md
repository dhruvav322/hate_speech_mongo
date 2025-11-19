# 🚨 Backend Dependencies Missing - Quick Fix

## The Issue
The backend can't start because Python dependencies are not installed.

## Quick Solution (Run These Commands)

### 1. Install all dependencies:
```bash
cd /Users/dhruvav/Desktop/hate_speech
pip install -r requirements.txt
```

This will install:
- FastAPI, Uvicorn
- MongoDB drivers (pymongo, motor)
- ML libraries (detoxify, sentence-transformers, torch)
- Rate limiting (slowapi)
- And all other required packages

**Note:** This may take 5-10 minutes, especially for ML libraries.

### 2. Set the API key:
```bash
export API_KEY=industry-demo-key-12345
```

### 3. Start the backend:
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### 4. Verify it's working:
Open a new terminal and run:
```bash
curl http://localhost:8001/health
```

You should see JSON output.

### 5. Refresh your browser:
The frontend at http://localhost:3000 should now show **🟢 online** status.

---

## Alternative: Use Conda Environment

If you're using Anaconda/Conda:

```bash
# Create environment
conda create -n hate_speech python=3.9 -y
conda activate hate_speech

# Install dependencies
pip install -r requirements.txt

# Set API key
export API_KEY=industry-demo-key-12345

# Start backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

---

## What You'll See When It Works

**Backend terminal:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
🛡️  Hate Speech Moderation System Started
```

**Frontend sidebar:**
- Status dot changes from 🔴 to 🟢
- Text changes from "offline" to "online"

**Browser console:**
- No more "Failed to load resource" errors
- Health check requests succeed

---

## Still Having Issues?

1. **Check Python version:** `python --version` (should be 3.9+)
2. **Check if MongoDB is running** (if using local MongoDB)
3. **Check port 8001 is free:** `lsof -i:8001`
4. **Check API key is set:** `echo $API_KEY`

