# 🚀 Deployment Guide

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Scalable Production Setup

```bash
# Use scalable configuration with load balancing
docker-compose -f docker-compose.scalable.yml up -d
```

This includes:
- Nginx load balancer
- Multiple API instances
- Redis for caching
- MongoDB with connection pooling

## Manual Deployment

### Backend

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Start server**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8001
   ```

### Frontend

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your API URL
   ```

3. **Build and start**
   ```bash
   npm run build
   npm start
   ```

## Production Checklist

- [ ] Set strong API keys in `.env`
- [ ] Configure CORS origins
- [ ] Enable Redis for caching
- [ ] Set up MongoDB indexes
- [ ] Configure rate limiting
- [ ] Set up monitoring/logging
- [ ] Enable HTTPS
- [ ] Configure backup strategy

## Environment Variables

See `.env.example` for all required variables.
