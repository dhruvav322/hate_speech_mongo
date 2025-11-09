@echo off
echo 🛡️ Starting Hate Speech Detection System...
echo.

echo 📁 Current directory: %CD%
echo.

echo 🐍 Activating Python virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
echo.

echo 🚀 Starting API server on port 8000...
echo 📝 API will be available at: http://localhost:8000
echo 📚 API docs will be available at: http://localhost:8000/docs
echo.
echo ⚠️  Keep this window open while using the system
echo 🛑 Press Ctrl+C to stop the server
echo.

.venv\Scripts\uvicorn industry_ready_api:app --host 0.0.0.0 --port 8000
