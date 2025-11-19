# 🌐 Website Deployment Guide

## How to Make Your Hate Speech Moderation System Available to Users

This guide shows you how to deploy your system as a public website that users can access.

---

## 🎯 What You'll Deploy

1. **Backend API** (FastAPI) - Handles moderation requests
2. **Frontend UI** (React) - User interface for text analysis
3. **Database** (MongoDB) - Stores results and analytics

---

## 🚀 Deployment Options

### Option 1: Quick & Free (Render + Vercel) ⚡
**Best for**: Testing, demos, small projects  
**Cost**: FREE  
**Setup Time**: 15 minutes

### Option 2: Professional (AWS/DigitalOcean) 💼
**Best for**: Production, businesses  
**Cost**: $10-50/month  
**Setup Time**: 1-2 hours

### Option 3: Enterprise (Kubernetes) 🏢
**Best for**: Large scale, multiple regions  
**Cost**: $100+/month  
**Setup Time**: 1 day

---

## ⚡ OPTION 1: Quick Deploy (FREE)

### Step 1: Deploy Backend to Render (10 min)

#### 1.1 Prepare Your Repository
```bash
cd /Users/dhruvav/Desktop/hate_speech

# Create render.yaml
cat > render.yaml << 'EOF'
services:
  - type: web
    name: hate-speech-api
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: API_KEY
        generateValue: true
      - key: ENVIRONMENT
        value: production
      - key: ALLOWED_ORIGINS
        value: https://your-frontend.vercel.app
      - key: MONGO_ROOT_PASSWORD
        generateValue: true
    healthCheckPath: /health

  - type: pserv
    name: mongodb
    env: docker
    dockerContext: ./
    dockerfilePath: ./Dockerfile.mongo
    disk:
      name: mongo-data
      mountPath: /data/db
      sizeGB: 1
EOF

# Commit to Git
git add .
git commit -m "Add deployment configuration"
git push
EOF
```

#### 1.2 Deploy on Render
1. Go to https://render.com
2. Sign up (free account)
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repo
5. Render will auto-detect `render.yaml`
6. Click **"Create Web Service"**
7. Wait 5-10 minutes for deployment

**Your API will be at**: `https://your-app-name.onrender.com`

---

### Step 2: Deploy Frontend to Vercel (5 min)

#### 2.1 Update Frontend Config
```bash
cd frontend

# Create .env.production
cat > .env.production << EOF
REACT_APP_API_URL=https://your-api.onrender.com
REACT_APP_API_KEY=your-generated-api-key-from-render
EOF
```

#### 2.2 Deploy to Vercel
1. Go to https://vercel.com
2. Sign up (free account)
3. Click **"Add New Project"**
4. Import your GitHub repo
5. Set **Root Directory** to `frontend`
6. Add environment variables:
   - `REACT_APP_API_URL` = your Render API URL
   - `REACT_APP_API_KEY` = your API key
7. Click **"Deploy"**

**Your website will be at**: `https://your-app.vercel.app`

✅ **Done!** Your website is now live and accessible to anyone!

---

## 💼 OPTION 2: Professional Deploy (AWS/DigitalOcean)

### Using DigitalOcean App Platform

#### Step 1: Set Up DigitalOcean Account
1. Sign up at https://digitalocean.com
2. Get $200 free credit (for new users)

#### Step 2: Deploy Backend

```bash
# Install doctl (DigitalOcean CLI)
brew install doctl  # macOS
# or: snap install doctl  # Linux

# Login
doctl auth init

# Create app spec
cat > .do/app.yaml << 'EOF'
name: hate-speech-moderation
services:
  - name: api
    github:
      repo: your-username/your-repo
      branch: main
      deploy_on_push: true
    dockerfile_path: Dockerfile
    http_port: 8000
    instance_count: 1
    instance_size_slug: basic-xs
    routes:
      - path: /
    envs:
      - key: API_KEY
        value: ${API_KEY}
      - key: ENVIRONMENT
        value: production
      - key: ALLOWED_ORIGINS
        value: https://your-domain.com
      - key: MONGO_ROOT_PASSWORD
        value: ${MONGO_PASSWORD}
    health_check:
      http_path: /health

  - name: frontend
    github:
      repo: your-username/your-repo
      branch: main
    source_dir: /frontend
    build_command: npm run build
    http_port: 3000
    instance_count: 1
    instance_size_slug: basic-xs
    envs:
      - key: REACT_APP_API_URL
        value: ${api.PUBLIC_URL}

databases:
  - name: mongodb
    engine: MONGODB
    version: "6"
    size: db-s-1vcpu-1gb
EOF

# Deploy
doctl apps create --spec .do/app.yaml
```

#### Step 3: Add Custom Domain

1. Go to DigitalOcean Dashboard
2. Navigate to **Networking** → **Domains**
3. Add your domain (e.g., `moderationai.com`)
4. Update DNS records at your domain registrar:
   ```
   Type: A
   Host: @
   Value: [DigitalOcean IP]
   
   Type: CNAME
   Host: www
   Value: your-app.ondigitalocean.app
   ```

5. In App settings, add custom domain
6. Enable **"Manage HTTPS"** (free SSL)

✅ **Your website**: `https://moderationai.com`

---

## 🔧 Complete Setup with Custom Domain

### Prerequisites
1. Purchase a domain (GoDaddy, Namecheap, Google Domains)
2. Choose a hosting provider (Render, DigitalOcean, AWS)

### Step-by-Step Domain Setup

#### 1. Backend Domain Setup (api.yourdomain.com)

**On Your Hosting Platform**:
1. Deploy backend as shown above
2. Note the default URL (e.g., `your-app.onrender.com`)

**On Your Domain Registrar**:
1. Go to DNS settings
2. Add CNAME record:
   ```
   Type: CNAME
   Name: api
   Value: your-app.onrender.com
   TTL: 3600
   ```

**Enable HTTPS**:
- Most platforms (Render, Vercel, DigitalOcean) auto-provision SSL
- If not, use Let's Encrypt (free)

#### 2. Frontend Domain Setup (app.yourdomain.com or www.yourdomain.com)

**On Vercel/Hosting**:
1. Go to project settings
2. Add custom domain: `app.yourdomain.com`
3. Vercel will provide DNS records

**On Your Domain Registrar**:
1. Add the records provided by Vercel
2. Usually:
   ```
   Type: CNAME
   Name: app
   Value: cname.vercel-dns.com
   ```

**Update Frontend Config**:
```bash
# frontend/.env.production
REACT_APP_API_URL=https://api.yourdomain.com
```

---

## 🐳 Docker Deployment (VPS)

For deploying to your own server (e.g., AWS EC2, DigitalOcean Droplet)

### Step 1: Set Up Server

```bash
# SSH into your server
ssh root@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Step 2: Clone and Configure

```bash
# Clone your repo
git clone https://github.com/your-username/hate_speech.git
cd hate_speech

# Create .env file
nano .env
# Add all your environment variables

# Generate API key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Set Up Nginx Reverse Proxy

```bash
# Install Nginx
apt update && apt install nginx certbot python3-certbot-nginx -y

# Create Nginx config
cat > /etc/nginx/sites-available/hate-speech << 'EOF'
# API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend
server {
    listen 80;
    server_name app.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/hate-speech /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 4: Get SSL Certificate (HTTPS)

```bash
# Get free SSL from Let's Encrypt
certbot --nginx -d api.yourdomain.com -d app.yourdomain.com

# Auto-renewal is configured automatically
```

### Step 5: Start Services

```bash
# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

✅ **Your website is now live at**:
- Frontend: `https://app.yourdomain.com`
- API: `https://api.yourdomain.com`

---

## 📱 Make it User-Friendly

### 1. Create Landing Page

Add to your frontend:

```jsx
// frontend/src/components/LandingPage.js
import React from 'react';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center text-white">
          <h1 className="text-6xl font-bold mb-6">
            🛡️ Hate Speech Moderation
          </h1>
          <p className="text-2xl mb-8">
            AI-powered content moderation to keep your community safe
          </p>
          <Link to="/analyze" className="bg-white text-blue-600 px-8 py-4 rounded-lg text-xl font-semibold hover:bg-gray-100">
            Try it Free →
          </Link>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8 mt-16 text-white">
          <div className="bg-white/10 backdrop-blur p-6 rounded-lg">
            <h3 className="text-2xl font-bold mb-4">⚡ Fast</h3>
            <p>Analyze text in milliseconds with advanced ML models</p>
          </div>
          <div className="bg-white/10 backdrop-blur p-6 rounded-lg">
            <h3 className="text-2xl font-bold mb-4">🎯 Accurate</h3>
            <p>Multi-model ensemble for highest accuracy</p>
          </div>
          <div className="bg-white/10 backdrop-blur p-6 rounded-lg">
            <h3 className="text-2xl font-bold mb-4">🔐 Secure</h3>
            <p>Enterprise-grade security and privacy</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
```

### 2. Add SEO & Meta Tags

```jsx
// frontend/public/index.html
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  
  <!-- SEO -->
  <title>Hate Speech Moderation - AI Content Moderation API</title>
  <meta name="description" content="AI-powered hate speech detection and content moderation. Keep your community safe with real-time text analysis." />
  <meta name="keywords" content="hate speech detection, content moderation, AI moderation, toxic content filter" />
  
  <!-- Open Graph (Facebook, LinkedIn) -->
  <meta property="og:title" content="Hate Speech Moderation - AI Content Moderation" />
  <meta property="og:description" content="AI-powered hate speech detection for safer online communities" />
  <meta property="og:image" content="https://yourdomain.com/og-image.png" />
  <meta property="og:url" content="https://yourdomain.com" />
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Hate Speech Moderation" />
  <meta name="twitter:description" content="AI-powered content moderation" />
  <meta name="twitter:image" content="https://yourdomain.com/twitter-image.png" />
</head>
```

### 3. Add Analytics

```jsx
// frontend/src/index.js
import ReactGA from 'react-ga4';

// Initialize Google Analytics
ReactGA.initialize('G-XXXXXXXXXX');

// Track page views
ReactGA.send("pageview");
```

---

## 🔐 Security for Public Website

### 1. Environment Variables (Production)

```bash
# .env (Backend)
API_KEY=use-secrets-manager-in-production
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
ENVIRONMENT=production
MONGO_ROOT_PASSWORD=very-strong-password-here

# Rate limits for public use
MAX_REQUESTS_PER_MINUTE=10  # Per user
```

### 2. Add User Accounts (Optional)

If you want users to sign up:

```bash
# Install Auth library
pip install fastapi-users[sqlalchemy]

# Add authentication endpoints
# See: https://fastapi-users.github.io/fastapi-users/
```

### 3. Add API Key Generation for Users

```python
# src/api/routes/users.py
@router.post("/generate-key")
async def generate_api_key(user_id: str):
    """Generate API key for user"""
    api_key = secrets.token_urlsafe(32)
    
    # Store in database
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"api_key": api_key}}
    )
    
    return {"api_key": api_key}
```

---

## 💰 Pricing Tiers (If Monetizing)

```python
# src/models/pricing.py
PRICING_TIERS = {
    "free": {
        "requests_per_day": 100,
        "rate_limit": "10/minute"
    },
    "basic": {
        "price": 9.99,
        "requests_per_day": 10000,
        "rate_limit": "60/minute"
    },
    "pro": {
        "price": 49.99,
        "requests_per_day": 100000,
        "rate_limit": "300/minute"
    }
}
```

---

## 📊 Monitoring & Analytics

### Add Google Analytics
```jsx
// frontend
npm install react-ga4

// Track API usage
ReactGA.event({
  category: "API",
  action: "analyze_text",
  label: "success"
});
```

### Add Error Tracking (Sentry)
```bash
# Backend
pip install sentry-sdk

# Python
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

---

## ✅ Pre-Launch Checklist

Before making your website public:

- [ ] Domain purchased and configured
- [ ] SSL certificate installed (HTTPS)
- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] API keys configured
- [ ] Rate limiting active
- [ ] MongoDB secured with password
- [ ] CORS configured correctly
- [ ] Error tracking enabled (Sentry)
- [ ] Analytics enabled (Google Analytics)
- [ ] Terms of Service page added
- [ ] Privacy Policy page added
- [ ] Contact page added
- [ ] Documentation/Help page added
- [ ] Tested on mobile devices
- [ ] Tested on different browsers
- [ ] Load testing completed
- [ ] Backup system configured

---

## 🚀 Quick Deploy Commands Summary

### Option 1: Render + Vercel (FREE)
```bash
# 1. Push to GitHub
git push

# 2. Deploy backend on Render.com (via dashboard)
# 3. Deploy frontend on Vercel.com (via dashboard)
```

### Option 2: DigitalOcean
```bash
doctl apps create --spec .do/app.yaml
```

### Option 3: Own Server
```bash
# On your server
git clone your-repo
cd hate_speech
docker-compose up -d
certbot --nginx -d yourdomain.com
```

---

## 🎉 You're Live!

Your website is now accessible to users worldwide! 

**Share your website**:
- 🌐 Website: `https://yourdomain.com`
- 📚 API Docs: `https://api.yourdomain.com/docs`
- 💻 GitHub: `https://github.com/your-repo`

**Next Steps**:
1. Share on social media
2. Submit to Product Hunt
3. Add to AI tool directories
4. Create demo videos
5. Write blog posts

---

Need help with deployment? Let me know which option you prefer!

