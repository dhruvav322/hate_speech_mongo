#!/bin/bash

# 🚀 Industry-Ready Hate Speech API - VS Code Setup Script
# This script helps you set up the new industry-ready API in VS Code

echo "🛡️ Setting up Industry-Ready Hate Speech API for VS Code..."

# Create .vscode directory if it doesn't exist
mkdir -p .vscode

# Create launch.json for debugging
cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Industry-Ready API",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/industry_ready_api.py",
            "console": "integratedTerminal",
            "env": {
                "API_KEY": "industry-demo-key-12345",
                "ENVIRONMENT": "development",
                "LOG_LEVEL": "INFO"
            }
        }
    ]
}
EOF

echo "✅ Created .vscode/launch.json"

# Create tasks.json for running tasks
cat > .vscode/tasks.json << 'EOF'
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
EOF

echo "✅ Created .vscode/tasks.json"

# Create test-api.http for REST Client testing
cat > test-api.http << 'EOF'
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
EOF

echo "✅ Created test-api.http"

# Stop any old running processes
echo "🛑 Stopping any old API processes..."
pkill -f "python main.py" 2>/dev/null || true
pkill -f "python main_enhanced.py" 2>/dev/null || true

echo ""
echo "🎉 Setup Complete! Here's how to use the new Industry-Ready API:"
echo ""
echo "1️⃣ Open VS Code in this directory"
echo "2️⃣ Press F5 or use 'Run > Start Debugging' to start the API"
echo "3️⃣ Or use 'Terminal > Run Task > Start Industry-Ready API'"
echo "4️⃣ Open http://localhost:8000/docs for interactive documentation"
echo "5️⃣ Test with the provided test-api.http file"
echo ""
echo "🔐 API Key: industry-demo-key-12345"
echo "🌐 Server: http://localhost:8000"
echo "📖 Docs: http://localhost:8000/docs"
echo ""
echo "📝 For more details, see VSCODE_SETUP_GUIDE.md"
echo "📋 Full deployment info in DEPLOYMENT_SUMMARY.md"
echo ""
echo "✨ Your industry-ready API is ready to go!"