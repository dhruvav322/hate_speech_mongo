# 🛡️ Hate Speech Moderation React Frontend

A professional, minimal, and interactive React frontend for the industry-ready hate speech moderation API.

## 🌟 Features

### **Core Functionality**
- ✨ **Modern UI** - Clean, professional interface with smooth animations
- 🎯 **Real-time Analysis** - Instant text moderation with visual feedback
- 📊 **Analytics Dashboard** - Beautiful charts and performance metrics
- 🔄 **MLOps Feedback Loop** - Submit feedback to improve model accuracy
- 🔐 **API Integration** - Seamless connection to industry-ready backend
- 📱 **Responsive Design** - Works perfectly on desktop and mobile

### **Interactive Components**
- **Moderation Interface** - Text analysis with detailed results
- **Feedback Form** - MLOps integration for model improvement
- **Analytics Dashboard** - Real-time charts and statistics
- **Health Monitoring** - API status indicator

---

## 🚀 Quick Start

### **Prerequisites**
- Node.js 14+ installed
- Industry-ready API running on http://localhost:8000

### **Installation & Run**

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start the development server
npm start
```

The app will open at http://localhost:3000

---

## 🎮 How to Use

### **1. Text Moderation**
1. Enter text in the moderation interface
2. Click "Analyze Text"
3. View detailed results with toxicity scores
4. See recommended action (Allow/Flag/Block)

### **2. Submit Feedback**
1. After analysis, switch to Feedback tab
2. Select the correct action that should have been taken
3. Add optional feedback text
4. Submit to help improve the model

### **3. View Analytics**
1. Switch to Analytics tab
2. View real-time charts and statistics
3. Monitor model performance
4. See moderation trends

---

## 🎨 UI Features

### **Modern Design**
- Clean, minimal interface with professional aesthetics
- Smooth animations and transitions
- Color-coded toxicity indicators
- Responsive grid layouts

### **Interactive Elements**
- Real-time API status monitoring
- Loading states with spinners
- Hover effects and micro-interactions
- Tab-based navigation

### **Data Visualization**
- Pie charts for message distribution
- Bar charts for action summaries
- Progress bars for toxicity scores
- Performance metrics dashboard

---

## 🔧 Configuration

### **Environment Variables**
Create `.env` file (already included):
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_KEY=industry-demo-key-12345
```

### **For Production**
```env
REACT_APP_API_URL=https://your-production-api.com
REACT_APP_API_KEY=your-production-api-key
```

---

## 📁 Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── ModerationInterface.js    # Main moderation UI
│   │   ├── AnalyticsDashboard.js     # Charts and analytics
│   │   └── FeedbackForm.js          # MLOps feedback
│   ├── services/
│   │   └── api.js                   # API service layer
│   ├── utils/
│   ├── App.js                       # Main app component
│   ├── index.js                     # Entry point
│   └── index.css                    # Global styles
├── package.json
├── .env                             # Environment variables
└── README.md
```

---

## 🌐 API Integration

The frontend seamlessly integrates with the industry-ready backend:

### **Connected Endpoints**
- `POST /api/v1/moderation/analyze` - Text analysis
- `POST /api/v1/feedback` - Feedback submission
- `GET /api/v1/analytics` - Analytics data
- `GET /api/v1/model-performance` - Model stats
- `GET /api/v1/health` - Health check

### **Authentication**
- API key automatically included in all requests
- Configurable via environment variables
- Secure header-based authentication

---

## 📊 Analytics Features

### **Real-time Dashboard**
- Total messages processed
- Toxic message detection
- Flagged and blocked content
- Model performance metrics

### **Interactive Charts**
- Message distribution pie chart
- Action summary bar chart
- Response time monitoring
- Cache hit rate tracking

---

## 🔄 MLOps Integration

### **Feedback Loop**
- Submit corrections for moderation decisions
- Provide context for model improvement
- Track feedback submissions
- Contribute to model retraining

### **Feedback Features**
- Action selection (Allow/Flag/Block)
- Optional feedback text
- Message ID tracking
- User attribution

---

## 🎯 Industry Features

### **Professional UI/UX**
- Clean, corporate-friendly design
- Accessibility compliance
- Error handling and validation
- Loading states and feedback

### **Performance**
- Optimized API calls
- Efficient state management
- Minimal dependencies
- Fast loading times

### **Security**
- API key authentication
- Input validation
- Error message sanitization
- Secure communication

---

## 🚀 Deployment

### **Development**
```bash
npm start
# Runs on http://localhost:3000
```

### **Production Build**
```bash
npm run build
# Builds optimized production files in build/
```

### **Docker Deployment**
```bash
# Add to your Docker setup
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

---

## 🛠️ Technology Stack

- **React 18** - Modern UI framework
- **Axios** - HTTP client for API calls
- **Lucide React** - Professional icons
- **Recharts** - Interactive charts
- **CSS3** - Modern styling with animations
- **ES6+** - Modern JavaScript features

---

## 🎉 You're Ready to Go!

Your professional React frontend is now connected to your industry-ready hate speech moderation API!

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**All Features Working:**
✅ Text moderation with real-time analysis
✅ Interactive feedback submission
✅ Beautiful analytics dashboard
✅ API authentication
✅ Responsive design
✅ Error handling
✅ Professional UI/UX

Enjoy your complete industry-ready hate speech moderation system! 🛡️✨