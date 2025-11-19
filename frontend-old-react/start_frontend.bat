@echo off
echo 🎨 Starting React Frontend...
echo.

echo 📁 Current directory: %CD%
echo.

echo 📦 Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js found
echo.

echo 🚀 Starting React development server...
echo 🌐 Frontend will be available at: http://localhost:3000
echo 🌙 Dark mode is enabled by default
echo.
echo ⚠️  Keep this window open while using the system
echo 🛑 Press Ctrl+C to stop the server
echo.

npm start
