# 🛡️ Hate Speech Detection System - Complete Setup Guide

This guide will help you set up the entire hate speech detection system on any new PC from scratch.

## 📋 **System Requirements**

### **Operating System:**
- Windows 10/11 (Primary)
- macOS 10.15+ (Compatible)
- Linux Ubuntu 18.04+ (Compatible)

### **Software Prerequisites:**
- **Python 3.8+** (Required for ML models)
- **Node.js 16+** (Required for React frontend)
- **Chrome/Edge Browser** (Required for browser extension)
- **Git** (Optional, for version control)

---

## 🚀 **Step-by-Step Installation**

### **Step 1: Install Python**

#### **Windows:**
1. Download Python from https://python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### **macOS:**
```bash
# Install Homebrew first (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

#### **Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### **Step 2: Install Node.js**

#### **Windows:**
1. Download from https://nodejs.org/
2. Install the LTS version
3. Verify installation:
   ```cmd
   node --version
   npm --version
   ```

#### **macOS:**
```bash
brew install node
```

#### **Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### **Step 3: Get the Project Files**

#### **Option A: Copy from USB/Drive**
1. Copy the entire `hate_speech_mongo` folder to your desired location
2. Navigate to the folder in terminal/command prompt

#### **Option B: Download from Repository**
```bash
# If you have the repository URL
git clone <repository-url>
cd hate_speech_mongo
```

---

## ⚙️ **Backend Setup (API Server)**

### **Step 1: Create Python Virtual Environment**

#### **Windows:**
```cmd
cd hate_speech_mongo
python -m venv .venv
.venv\Scripts\activate
```

#### **macOS/Linux:**
```bash
cd hate_speech_mongo
python3 -m venv .venv
source .venv/bin/activate
```

### **Step 2: Install Python Dependencies**

```bash
# Core dependencies (always install these first)
pip install fastapi uvicorn pymongo

# ML dependencies (may take 5-10 minutes)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install detoxify sentence-transformers transformers
pip install scikit-learn

# Additional dependencies
pip install python-multipart python-dotenv structlog
```

**⚠️ Note**: If any package fails, install them individually:
```bash
pip install fastapi
pip install uvicorn
pip install detoxify
# etc.
```

### **Step 3: Start the API Server**

#### **Windows:**
```cmd
.venv\Scripts\uvicorn industry_ready_api:app --host 0.0.0.0 --port 8000
```

#### **macOS/Linux:**
```bash
.venv/bin/uvicorn industry_ready_api:app --host 0.0.0.0 --port 8000
```

**✅ Success Indicators:**
- You should see: `INFO: Uvicorn running on http://0.0.0.0:8000`
- You should see: `✅ Loaded Detoxify original model`
- You should see: `✅ Loaded Sentence Transformer model`

**🌐 Test the API:**
- Open browser: http://localhost:8000
- Should show: `{"status": "operational", "ml_model": "ensemble-detoxify-original+sentence-transformer"}`

---

## 🎨 **Frontend Setup (React Web Interface)**

### **Step 1: Navigate to Frontend Directory**
```bash
cd frontend
```

### **Step 2: Install Node Dependencies**
```bash
npm install
```

**⚠️ If you get errors:**
```bash
# Clear cache and try again
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### **Step 3: Start the React Development Server**
```bash
npm start
```

**✅ Success Indicators:**
- You should see: `Compiled successfully!`
- Browser should open automatically to: http://localhost:3000
- You should see the dark-themed hate speech detection interface

---

## 🌐 **Browser Extension Setup**

### **Step 1: Open Chrome/Edge Extensions**
1. Open Chrome or Edge browser
2. Go to: `chrome://extensions/` (Chrome) or `edge://extensions/` (Edge)
3. Enable **Developer mode** (toggle in top-right corner)

### **Step 2: Load the Extension**
1. Click **"Load unpacked"**
2. Navigate to and select the `browser-extension` folder
3. The extension should appear in your extensions list

### **Step 3: Pin the Extension**
1. Click the puzzle piece icon in browser toolbar
2. Find "Hate Speech Detector"
3. Click the pin icon to pin it to toolbar

**✅ Test the Extension:**
1. Visit any website (Instagram, Twitter, etc.)
2. Click the extension icon
3. Should show platform detection and analysis options

---

## 🔧 **Configuration Files**

### **Backend Configuration (.env)**
Create `hate_speech_mongo/.env` (optional):
```env
API_KEY=industry-demo-key-12345
ENVIRONMENT=development
LOG_LEVEL=INFO
MONGODB_URI=mongodb://localhost:27017/hate_speech_db
```

### **Frontend Configuration**
The file `frontend/.env` should contain:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_KEY=industry-demo-key-12345
```

---

## 🚀 **Running the Complete System**

### **Start Order:**
1. **Backend First**: Start the API server (port 8000)
2. **Frontend Second**: Start React app (port 3000)
3. **Extension Last**: Load browser extension

### **Daily Startup Commands:**

#### **Windows (PowerShell/CMD):**
```cmd
# Terminal 1 - Backend
cd hate_speech_mongo
.venv\Scripts\activate
.venv\Scripts\uvicorn industry_ready_api:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd hate_speech_mongo\frontend
npm start
```

#### **macOS/Linux (Terminal):**
```bash
# Terminal 1 - Backend
cd hate_speech_mongo
source .venv/bin/activate
uvicorn industry_ready_api:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd hate_speech_mongo/frontend
npm start
```

---

## 🎯 **Quick Test Checklist**

### **✅ Backend Working:**
- [ ] API responds at http://localhost:8000
- [ ] Shows `ensemble-detoxify-original+sentence-transformer` model
- [ ] Can analyze text via API docs at http://localhost:8000/docs

### **✅ Frontend Working:**
- [ ] React app loads at http://localhost:3000
- [ ] Dark theme is active
- [ ] Can analyze text in "Text Analysis" tab
- [ ] Analytics dashboard shows data
- [ ] Can reset analytics data

### **✅ Browser Extension Working:**
- [ ] Extension icon appears in browser toolbar
- [ ] Clicking icon shows popup interface
- [ ] Can detect platform (Instagram, Twitter, etc.)
- [ ] "Analyze Page" and "Select Text" buttons work

---

## 🛠️ **Troubleshooting**

### **Common Issues:**

#### **Python/ML Model Issues:**
```bash
# If Detoxify fails to load
pip uninstall detoxify
pip install detoxify

# If torch issues
pip install torch --upgrade

# If memory issues
# Use smaller model: change 'original' to 'multilingual' in code
```

#### **Node.js/React Issues:**
```bash
# If npm install fails
npm cache clean --force
rm -rf node_modules
npm install --legacy-peer-deps

# If port 3000 is busy
# Kill process or change port in package.json
```

#### **Browser Extension Issues:**
- **Extension won't load**: Check manifest.json syntax
- **No permissions**: Enable Developer mode
- **API not connecting**: Ensure backend is running on port 8000

### **Port Conflicts:**
```bash
# Check what's using ports
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# Kill processes if needed
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # macOS/Linux
```

---

## 📁 **Project Structure**

```
hate_speech_mongo/
├── industry_ready_api.py      # Main API server
├── requirements.txt           # Python dependencies
├── .env                      # Environment variables (optional)
├── frontend/                 # React web interface
│   ├── src/
│   ├── package.json
│   └── .env
├── browser-extension/        # Chrome/Edge extension
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   ├── content.js
│   └── background.js
└── SETUP_GUIDE.md           # This file
```

---

## 🎉 **Success! You're Ready**

Once everything is running, you'll have:

### **🌐 Web Interface** (http://localhost:3000)
- **Text Analysis** - Direct text input and analysis
- **Analytics Dashboard** - View statistics and trends
- **Feedback System** - Improve model accuracy

### **🤖 API Server** (http://localhost:8000)
- **REST API** - Programmatic access
- **ML Models** - Detoxify + Sentence Transformers
- **Real-time Analysis** - Fast, accurate results

### **🔌 Browser Extension**
- **Universal Platform Support** - Works on any website
- **Real-time Analysis** - Analyze webpage content
- **Text Selection** - Highlight and analyze specific text

---

## 📞 **Need Help?**

### **Check Logs:**
- **Backend logs**: Look at terminal running uvicorn
- **Frontend logs**: Check browser developer console (F12)
- **Extension logs**: Check chrome://extensions → Details → Inspect views

### **Verify Installation:**
```bash
# Check Python packages
pip list | grep -E "(detoxify|transformers|fastapi)"

# Check Node packages
npm list --depth=0

# Check system versions
python --version
node --version
npm --version
```

**🎯 This system is now ready for production use with industry-grade ML models!**
