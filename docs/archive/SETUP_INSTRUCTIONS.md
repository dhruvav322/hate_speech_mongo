# 🚀 Quick Setup Instructions

## ✅ Security Fixes Implemented

All critical security issues have been fixed:

- ✅ **API Key Authentication** - Required on all endpoints
- ✅ **Rate Limiting** - Prevents API abuse
- ✅ **Input Sanitization** - Blocks injection attacks
- ✅ **CORS Protection** - Configured with specific origins
- ✅ **MongoDB Authentication** - Database secured with passwords
- ✅ **Security Headers** - XSS, clickjacking protection
- ✅ **Request Size Limits** - Prevents memory attacks

---

## 🔧 Setup Steps

### 1. Generate API Keys

```bash
# Generate secure API key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Create .env File

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
nano .env  # or use your favorite editor
```

**Required values:**
- `API_KEY` - Use the key generated in step 1
- `MONGO_ROOT_PASSWORD` - Strong password for MongoDB
- `ALLOWED_ORIGINS` - Your frontend domain(s)

### 3. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 4. Start with Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Check health
curl http://localhost:8000/health
```

### 5. Test Authentication

```bash
# This should fail (no API key)
curl http://localhost:8000/api/v1/moderation/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "user_id": "test_user"}'

# This should work (with API key)
curl http://localhost:8000/api/v1/moderation/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"text": "test message", "user_id": "test_user"}'
```

---

## 🔐 Security Checklist

Before deploying to production:

- [ ] Generated strong API key (32+ characters)
- [ ] Set strong MongoDB password
- [ ] Configured CORS with your domain
- [ ] Changed all default passwords
- [ ] Reviewed `.env` file - no defaults
- [ ] Tested API authentication
- [ ] Tested rate limiting
- [ ] Configured HTTPS (production only)
- [ ] Set up monitoring/alerts
- [ ] Configured backups

---

## 📊 What Changed

### New Files Added:
```
src/api/middleware/
├── auth.py              # API key authentication
├── rate_limit.py        # Rate limiting
├── sanitization.py      # Input sanitization
└── security_headers.py  # Security headers
```

### Files Modified:
```
src/config/settings.py   # Added security settings
src/main.py              # Applied all middleware
src/api/routes/*.py      # Added rate limits, sanitization
docker-compose.yml       # MongoDB authentication
requirements.txt         # Security packages added
```

### Files Deleted (Duplicates):
```
❌ main.py (root)
❌ main_backup.py
❌ main_enhanced.py
❌ industry_ready_api.py
❌ browser-extension.zip
❌ browser-extension.rar
❌ browser-extension (2).zip
```

---

## 🧪 Testing

### Test Security Features:

```bash
# 1. Test API authentication
curl -X POST http://localhost:8000/api/v1/moderation/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}'
# Should return 403 Forbidden

# 2. Test rate limiting
for i in {1..15}; do
  curl -X POST http://localhost:8000/api/v1/moderation/analyze \
    -H "X-API-Key: YOUR_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"text": "test '$i'", "user_id": "test"}' &
done
wait
# Should see 429 after 10 requests

# 3. Test input sanitization
curl -X POST http://localhost:8000/api/v1/moderation/analyze \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "$where: malicious", "user_id": "test"}'
# Should return 400 Bad Request

# 4. Test security headers
curl -I http://localhost:8000/
# Should show X-Content-Type-Options, X-Frame-Options, etc.
```

---

## 🌐 Frontend Setup

Update `frontend/.env`:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_KEY=your-api-key-here
```

Start frontend:

```bash
cd frontend
npm start
```

Access at: http://localhost:3000

---

## 📈 Monitoring

### Check System Status:

```bash
# API health
curl http://localhost:8000/health

# Model information
curl -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:8000/api/v1/models/info

# Statistics
curl -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:8000/api/v1/moderation/statistics
```

### View Logs:

```bash
# Docker logs
docker-compose logs -f

# Application logs
tail -f logs/*.log
```

---

## 🚨 Troubleshooting

### "API_KEY is required" error
- Make sure `.env` file exists
- Check `API_KEY` is set and not a default value
- Restart the application

### "Invalid or missing API key" error
- Verify X-API-Key header is included
- Check key matches the one in `.env`
- Ensure no extra spaces in key

### "Rate limit exceeded" error
- Wait 60 seconds and try again
- This is normal - means rate limiting is working
- Adjust limits in settings if needed

### MongoDB connection errors
- Check `MONGO_ROOT_PASSWORD` is set
- Verify MongoDB container is running
- Check connection string format

---

## 📚 Documentation

- **Security Audit**: See `SECURITY_AUDIT.md`
- **Implementation Guide**: See `IMPLEMENTATION_GUIDE.md`
- **API Documentation**: http://localhost:8000/docs
- **Complete README**: See `README.md`

---

## 🎯 Next Steps

1. **Production Deployment**:
   - Set up HTTPS with Let's Encrypt or CloudFlare
   - Use AWS Secrets Manager or HashiCorp Vault
   - Configure CloudFlare for DDoS protection
   - Set up monitoring (DataDog, New Relic, etc.)

2. **Optional Enhancements**:
   - Add Claude API for improved detection
   - Set up Redis for distributed rate limiting
   - Configure Prometheus + Grafana monitoring
   - Implement automated backups

3. **Security**:
   - Regular security audits
   - Penetration testing
   - Dependency updates (weekly)
   - Key rotation (monthly)

---

## ✅ Verification

Your system is secure when:

- [ ] API requires authentication ✓
- [ ] Rate limiting is active ✓
- [ ] CORS is configured (not wildcard) ✓
- [ ] MongoDB has authentication ✓
- [ ] No hardcoded secrets in code ✓
- [ ] Security headers are present ✓
- [ ] Input is sanitized ✓
- [ ] HTTPS is configured (production) ⏳

---

**🎉 Your hate speech moderation system is now production-ready!**

For questions or issues, refer to the documentation files in this directory.

