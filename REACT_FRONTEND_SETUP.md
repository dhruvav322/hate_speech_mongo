# 🎨 React Frontend Setup Guide

## 🚀 **Complete Frontend + Backend Setup**

Your professional React frontend has been built and is ready to use! Here's how to get it running:

---

## 📋 **Prerequisites**

- **Node.js 14+** installed on your system
- **Industry-ready API** running on http://localhost:8000
- **npm** or **yarn** package manager

---

## 🛠️ **Step-by-Step Setup**

### **Step 1: Pull Latest Changes**
```bash
cd hate_speech_mongo
git pull origin main
```

### **Step 2: Make Sure Backend API is Running**
In one terminal:
```bash
python industry_ready_api.py
```
You should see: "Server running on http://localhost:8000"

### **Step 3: Set Up React Frontend**
In a NEW terminal:
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

### **Step 4: Access Your Frontend**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🎮 **What You'll See**

### **Main Frontend Features:**
1. **🛡️ Moderation Interface** - Clean UI for text analysis
2. **📊 Analytics Dashboard** - Beautiful charts and metrics
3. **💬 Feedback Form** - MLOps feedback submission
4. **🔗 API Status** - Real-time connection monitoring

### **Modern UI Elements:**
- ✨ Professional design with smooth animations
- 📱 Responsive layout (works on mobile)
- 🎨 Color-coded toxicity indicators
- 📈 Interactive charts and graphs
- 🔐 Secure API authentication

---

## 🧪 **Testing the Complete System**

### **1. Test Text Moderation**
1. Open http://localhost:3000
2. Enter text: "I think this is a wonderful day!"
3. Click "Analyze Text"
4. See green "ALLOWED" result with toxicity score

### **2. Test Toxic Content**
1. Enter text: "I hate everyone and they should die"
2. Click "Analyze Text"
3. See yellow "FLAGGED" or red "BLOCKED" result
4. View detailed toxicity breakdown

### **3. Test Feedback Loop**
1. After analysis, click "Feedback" tab
2. Select what the correct action should have been
3. Add feedback text (optional)
4. Submit to improve the model

### **4. View Analytics**
1. Click "Analytics" tab
2. See real-time charts and statistics
3. Monitor model performance
4. View message distribution

---

## 🔧 **Configuration Options**

### **Environment Variables**
Edit `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_KEY=industry-demo-key-12345
```

### **For Production Deployment**
```env
REACT_APP_API_URL=https://your-production-api.com
REACT_APP_API_KEY=your-production-api-key
```

---

## 🎨 **Frontend Features Explained**

### **Moderation Interface**
- **Real-time analysis** with loading states
- **Toxicity scores** with visual progress bars
- **Category breakdown** showing different toxicity types
- **Action recommendations** (Allow/Flag/Block)
- **Detailed reasoning** for each decision

### **Analytics Dashboard**
- **Pie charts** for message distribution
- **Bar charts** for action summaries
- **Performance metrics** with response times
- **Model status** and health monitoring
- **Refresh capability** for real-time updates

### **Feedback System**
- **Action selection** with visual buttons
- **Context feedback** for model improvement
- **Success confirmation** with clear messaging
- **MLOps integration** for continuous learning

### **Professional UI/UX**
- **Tab-based navigation** for easy access
- **Status indicators** showing API connectivity
- **Error handling** with user-friendly messages
- **Responsive design** for all screen sizes
- **Smooth animations** and micro-interactions

---

## 📱 **Responsive Design**

The frontend works perfectly on:
- 💻 **Desktop** - Full-featured interface
- 📱 **Mobile** - Touch-optimized layout
- 📟 **Tablet** - Adaptive grid system

---

## 🚀 **Production Deployment**

### **Option 1: Build Static Files**
```bash
cd frontend
npm run build
# Deploy the build/ folder to any static host
```

### **Option 2: Docker**
```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### **Option 3: Netlify/Vercel**
- Connect your GitHub repository
- Set build command: `cd frontend && npm run build`
- Set publish directory: `frontend/build`

---

## 🔗 **API Integration Details**

### **Connected Endpoints**
- `POST /api/v1/moderation/analyze` - Text moderation
- `POST /api/v1/feedback` - Feedback submission
- `GET /api/v1/analytics` - Analytics data
- `GET /api/v1/model-performance` - Model stats
- `GET /api/v1/health` - Health checks

### **Authentication**
- API key automatically included in headers
- Secure X-API-Key header authentication
- Configurable via environment variables

---

## 🎯 **Complete System Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │  Backend API    │    │  ML Models      │
│  (Port 3000)    │◄──►│ (Port 8000)     │◄──►│   + Storage     │
│                 │    │                 │    │                 │
│ • Modern UI     │    │ • API Auth      │    │ • Toxicity      │
│ • Charts        │    │ • Background    │    │   Analysis      │
│ • Feedback      │    │   Processing    │    │ • Feedback      │
│ • Analytics     │    │ • MLOps Loop    │    │   Loop          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🎉 **Success! You're All Set!**

Your complete industry-ready hate speech moderation system is now running with:

✅ **Professional React Frontend** (Port 3000)
✅ **Industry-Ready Backend API** (Port 8000)
✅ **All 4 Industry Features** Implemented
✅ **MLOps Feedback Loop** Active
✅ **Real-time Analytics** Working
✅ **Modern UI/UX** Responsive Design

**Access Points:**
- 🎨 **Frontend**: http://localhost:3000
- 🔐 **Backend API**: http://localhost:8000
- 📖 **API Documentation**: http://localhost:8000/docs

**Enjoy your complete professional hate speech moderation system!** 🛡️✨