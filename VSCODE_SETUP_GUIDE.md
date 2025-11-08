# 📝 VS Code Setup Guide - Industry-Ready Hate Speech API

## 🔄 Replace Old Files with New Industry-Ready API

### Step 1: Pull Latest Changes
```bash
cd hate_speech_mongo
git pull origin main
```

### Step 2: Stop Any Running Old API Processes
```bash
# Kill any running Python processes from old API
pkill -f "python main.py"
pkill -f "python main_enhanced.py"

# Or if using VS Code terminal, just Ctrl+C the running processes
```

### Step 3: Use the New Industry-Ready API

#### Option A: Run Directly (Recommended for Development)
```bash
# Run the new industry-ready API
python industry_ready_api.py
```

#### Option B: Run with Docker (Recommended for Production)
```bash
# Simple Docker deployment
docker-compose -f docker-compose.simple.yml up

# Or build and run manually
docker build -f Dockerfile.simple -t hate-speech-api .
docker run -p 8000:8000 -e API_KEY=your-production-key hate-speech-api
```

### Step 4: Update Your VS Code Configuration

#### 1. Update VS Code Configuration (for debugging)
The setup script automatically creates:

**`.vscode/settings.json`** (Fixes Python interpreter issues):
```json
{
    "python.defaultInterpreterPath": "python3",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
```

**`.vscode/launch.json`** (Debugging configuration):
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Industry-Ready API",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/industry_ready_api.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "API_KEY": "industry-demo-key-12345",
                "ENVIRONMENT": "development",
                "LOG_LEVEL": "INFO",
                "PYTHONPATH": "${workspaceFolder}"
            },
            "python": "${command:python.interpreterPath}"
        }
    ]
}
```

**🔧 If you get "Configured debug type 'python' is not supported" error:**
1. Install Python extension in VS Code: `Ctrl+Shift+X` → Search "Python" → Install by Microsoft
2. Reload VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"
3. Try debugging again with F5

#### 2. Update tasks.json (for running tasks)
Create/update `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start Industry-Ready API",
            "type": "shell",
            "command": "python",
            "args": ["industry_ready_api.py"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "Start API with Docker",
            "type": "shell",
            "command": "docker-compose",
            "args": ["-f", "docker-compose.simple.yml", "up"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "problemMatcher": []
        }
    ]
}
```

#### 3. Recommended VS Code Extensions
Make sure you have these extensions installed:
- Python (Microsoft)
- Docker (Microsoft)
- REST Client (Huachao Mao)
- GitLens (GitKraken)

### Step 5: Test the New API

#### Test with REST Client
Create a new file `test-api.http`:
```http
### Health Check
GET http://localhost:8000/api/v1/health

### Analyze Positive Message
POST http://localhost:8000/api/v1/moderation/analyze
Content-Type: application/json
X-API-Key: industry-demo-key-12345

{
    "text": "You are a wonderful person!",
    "user_id": "test_user_123"
}

### Analyze Toxic Message
POST http://localhost:8000/api/v1/moderation/analyze
Content-Type: application/json
X-API-Key: industry-demo-key-12345

{
    "text": "I hate you and you should die",
    "user_id": "test_user_456"
}

### Submit Feedback
POST http://localhost:8000/api/v1/feedback
Content-Type: application/json
X-API-Key: industry-demo-key-12345

{
    "message_id": "msg_20251108_211344_029",
    "correct_action": "block",
    "feedback_text": "This should have been blocked",
    "user_id": "moderator_123"
}

### Get Analytics
GET http://localhost:8000/api/v1/analytics
X-API-Key: industry-demo-key-12345

### Model Performance
GET http://localhost:8000/api/v1/model-performance
X-API-Key: industry-demo-key-12345
```

#### Test with curl
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Analyze message
curl -X POST "http://localhost:8000/api/v1/moderation/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: industry-demo-key-12345" \
  -d '{"text": "Test message", "user_id": "user123"}'
```

### Step 6: Access Documentation
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Deployment Summary**: Open `DEPLOYMENT_SUMMARY.md`

---

## 🔄 Migration Notes

### What Changed:
- ✅ **Single File Solution**: `industry_ready_api.py` replaces complex modular structure
- ✅ **Fixed All Connection Issues**: No more "Connection reset by peer"
- ✅ **API Key Authentication**: All endpoints now require `X-API-Key` header
- ✅ **Industry Features**: All 4 requested features implemented and tested
- ✅ **Production Ready**: Docker configuration, health checks, monitoring

### Files You Can Ignore Now (Old Implementation):
- `main.py` - Old implementation (keep as backup)
- `main_enhanced.py` - Enhanced but still had connection issues
- `src/` directory - Complex modular structure (replaced by single file)
- Complex Docker configurations

### Primary Files to Use:
- **`industry_ready_api.py`** - Main API file (use this)
- **`Dockerfile.simple`** - Production Docker setup
- **`docker-compose.simple.yml`** - Easy deployment
- **`DEPLOYMENT_SUMMARY.md`** - Complete documentation

---

## 🎯 Quick Start Commands

```bash
# 1. Pull latest changes
git pull origin main

# 2. Start the industry-ready API
python industry_ready_api.py

# 3. Test it's working
curl http://localhost:8000/api/v1/health

# 4. Open documentation in browser
open http://localhost:8000/docs
```

That's it! Your industry-ready API is now running with all 4 features implemented and tested. 🚀