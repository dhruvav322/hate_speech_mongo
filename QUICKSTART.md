# ⚡ Quick Start Guide

## 🎯 Get Running in 5 Minutes

### Step 1: Generate API Key (30 seconds)
```bash
cd /Users/dhruvav/Desktop/hate_speech
python3 -c "import secrets; print('API_KEY=' + secrets.token_urlsafe(32))"
```
**Copy the output** - you'll need it!

---

### Step 2: Create .env File (1 minute)
```bash
# Copy the example
cp .env.example .env

# Edit it
nano .env  # or code .env or vim .env
```

**Required changes in .env**:
1. Paste your API_KEY from Step 1
2. Set MONGO_ROOT_PASSWORD (any strong password)
3. Update ALLOWED_ORIGINS if deploying to domain

**Minimum .env**:
```bash
API_KEY=your-generated-key-from-step-1
MONGO_ROOT_PASSWORD=strongpassword123
ALLOWED_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

---

### Step 3: Install Dependencies (2 minutes)
```bash
# Python packages
pip install -r requirements.txt

# Frontend (optional, if using React UI)
cd frontend && npm install && cd ..
```

---

### Step 4: Start with Docker (1 minute)
```bash
# Start everything
docker-compose up -d

# Check it's running
docker-compose ps
docker-compose logs -f api
```

---

### Step 5: Test It! (30 seconds)
```bash
# Test with your API key (replace YOUR_API_KEY)
curl -X POST http://localhost:8000/api/v1/moderation/analyze \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a test message",
    "user_id": "test_user"
  }'
```

**Expected response**:
```json
{
  "message_id": "msg_...",
  "overall_score": 0.05,
  "toxicity_scores": {...},
  "moderation_action": {
    "action": "none",
    "confidence": 0.92
  },
  ...
}
```

---

## 🎉 You're Done!

### Access Points:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Frontend** (if started): http://localhost:3000

---

## 🧪 Quick Tests

### Test Authentication:
```bash
# Should fail (no API key)
curl http://localhost:8000/api/v1/moderation/analyze

# Should work (with API key)
curl -H "X-API-Key: YOUR_KEY" http://localhost:8000/api/v1/moderation/analyze
```

### Test Rate Limiting:
```bash
# Run 15 times quickly - should see 429 after 10
for i in {1..15}; do
  curl -H "X-API-Key: YOUR_KEY" \
    -X POST http://localhost:8000/api/v1/moderation/analyze \
    -H "Content-Type: application/json" \
    -d '{"text": "test '$i'", "user_id": "test"}'
done
```

---

## 🔧 Troubleshooting

### "API_KEY is required" error
```bash
# Check .env file exists
ls -la .env

# Check it has API_KEY
cat .env | grep API_KEY

# Restart
docker-compose restart
```

### "Connection refused" error
```bash
# Check containers are running
docker-compose ps

# Check logs
docker-compose logs api
docker-compose logs mongo

# Restart
docker-compose down && docker-compose up -d
```

### Port already in use
```bash
# Kill existing processes
sudo lsof -ti:8000 | xargs kill -9

# Or change port in .env
API_PORT=8001
```

---

## 📚 Next Steps

1. **Read Full Documentation**:
   - `SETUP_INSTRUCTIONS.md` - Detailed setup
   - `SECURITY_AUDIT.md` - Security details
   - `CHANGES_SUMMARY.md` - What changed

2. **Configure for Production**:
   - Set `ENVIRONMENT=production` in .env
   - Configure HTTPS
   - Set up monitoring

3. **Test Thoroughly**:
   - Run `pytest tests/`
   - Test all endpoints
   - Load testing

---

## 🆘 Need Help?

- Check logs: `docker-compose logs -f`
- Read docs: http://localhost:8000/docs
- See detailed setup: `SETUP_INSTRUCTIONS.md`
- Review changes: `CHANGES_SUMMARY.md`

---

**Happy Moderating! 🛡️**

