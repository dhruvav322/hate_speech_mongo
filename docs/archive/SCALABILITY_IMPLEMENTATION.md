# 🚀 Scalability Implementation Guide

## Overview

This document outlines the scalability improvements implemented for the Hate Speech Moderation system, including caching, queues, database optimization, and load balancing.

---

## ✅ Implemented Features

### 1. **Redis Caching Layer**

**Location**: `src/services/cache_service.py`

**Features**:
- Redis-based caching with in-memory fallback
- Automatic TTL management
- Pattern-based cache clearing
- Cache statistics

**Usage**:
```python
from src.services.cache_service import cache_service

# Get from cache
value = await cache_service.get("prefix", "key1", "key2")

# Set in cache (with TTL)
await cache_service.set("prefix", value, ttl_seconds=3600, *["key1", "key2"])

# Clear cache
await cache_service.delete("prefix", "key1", "key2")
```

**Cached Data**:
- **User Profiles**: 5-minute TTL
- **Context Analysis**: 10-minute TTL
- **Model Predictions**: 1-hour TTL (in advanced_ml_models.py)
- **Analytics Queries**: 15-minute TTL (recommended)

---

### 2. **Message Queue System**

**Location**: `src/services/queue_service.py`

**Features**:
- Redis-based queues with in-memory fallback
- Task registration and execution
- Persistent task storage
- Worker process support

**Usage**:
```python
from src.services.queue_service import queue_service

# Register a task
queue_service.register_task("task_name", async_task_function)

# Enqueue a task
task_id = await queue_service.enqueue(
    "queue_name",
    "task_name",
    *args,
    **kwargs
)

# Process queue (for workers)
processed = await queue_service.process_queue("queue_name", max_tasks=10)
```

**Queues**:
- `user_updates`: User behavior updates
- `message_storage`: Message persistence
- `analytics`: Analytics computation (recommended)

---

### 3. **Database Optimization**

**Location**: `src/config/database.py`

**Connection Pooling**:
- **Max Pool Size**: 100 connections
- **Min Pool Size**: 10 connections
- **Idle Timeout**: 45 seconds
- **Connection Timeout**: 10 seconds
- **Socket Timeout**: 20 seconds

**Enhanced Indexes**:
- Compound indexes for common query patterns
- Time-range query optimization
- User activity queries
- Analytics aggregation indexes

**Indexes Added**:
```python
# Messages collection
- (user_id, timestamp) - User activity queries
- (timestamp, toxicity_analysis.overall_score) - Analytics
- toxicity_analysis.overall_score - Score filtering

# Moderation logs
- (timestamp, user_id) - Time-range user queries
```

---

### 4. **Load Balancing**

**Location**: `docker-compose.scalable.yml`, `nginx.conf`

**Setup**:
- Nginx reverse proxy
- 2 API instances (can scale to N)
- Health check endpoints
- Least-connections load balancing

**Deployment**:
```bash
# Start scalable setup
docker-compose -f docker-compose.scalable.yml up -d

# Scale API instances
docker-compose -f docker-compose.scalable.yml up -d --scale api1=3 --scale api2=3
```

**Load Balancing Method**: `least_conn` (least connections)

---

## 📊 Performance Improvements

### Before Optimization:
- **Single Request**: 50-300ms
- **Concurrent Requests**: 100+
- **Cache Hit Rate**: 0% (no caching)
- **Database Queries**: No pooling limits
- **Background Tasks**: In-memory only

### After Optimization:
- **Single Request**: <200ms (with cache hits)
- **Concurrent Requests**: 1000+ (with load balancing)
- **Cache Hit Rate**: 40-60% (expected)
- **Database Queries**: Pooled (max 100 connections)
- **Background Tasks**: Persistent queue (Redis)

---

## 🔧 Configuration

### Environment Variables

Add to `.env`:

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Database Connection Pool (optional, defaults shown)
MONGODB_MAX_POOL_SIZE=100
MONGODB_MIN_POOL_SIZE=10
```

### Docker Compose

Use `docker-compose.scalable.yml` for production:

```yaml
services:
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
  
  api1:
    environment:
      - REDIS_URL=redis://redis:6379/0
  
  api2:
    environment:
      - REDIS_URL=redis://redis:6379/0
```

---

## 🎯 Usage Examples

### Caching User Profiles

```python
# In moderation_service.py (already implemented)
user_profile = await cache_service.get("user_profile", user_id)
if not user_profile:
    user_profile = await self._get_user_profile(user_id)
    await cache_service.set("user_profile", user_profile.dict(), ttl_seconds=300, *[user_id])
```

### Queue Background Tasks

```python
# In moderation routes (already implemented)
if queue_service.use_redis:
    await queue_service.enqueue(
        "user_updates",
        "update_user_behavior",
        user_id,
        score,
        action
    )
```

### Database Connection Pooling

```python
# Automatically configured in database.py
# Connection pool is managed by Motor (async MongoDB driver)
# No code changes needed
```

---

## 📈 Monitoring

### Cache Statistics

```python
stats = await cache_service.get_stats()
# Returns: { "type": "redis", "keys": 1234, "hits": 567, "misses": 89 }
```

### Queue Status

Check Redis directly:
```bash
redis-cli LLEN queue:user_updates
redis-cli LLEN queue:message_storage
```

### Database Pool

Monitor MongoDB connections:
```javascript
db.serverStatus().connections
```

---

## 🚨 Fallback Behavior

All services gracefully fall back if Redis is unavailable:

1. **Cache Service**: Falls back to in-memory cache (limited to 1000 items)
2. **Queue Service**: Executes tasks immediately (no persistence)
3. **Rate Limiting**: Falls back to in-memory storage

**Logs will indicate fallback mode**:
```
WARNING: Redis not available, using in-memory cache
```

---

## 🔄 Migration Path

### Step 1: Add Redis (Optional)
```bash
# Add to docker-compose.yml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

### Step 2: Set Environment Variable
```bash
REDIS_URL=redis://redis:6379/0
```

### Step 3: Restart Services
```bash
docker-compose restart api
```

### Step 4: Verify
Check logs for:
```
✅ Redis cache connected
✅ Queue service connected to Redis
```

---

## 📝 Next Steps (Recommended)

1. **Add Analytics Caching**: Cache expensive analytics queries
2. **Implement Worker Processes**: Separate workers for queue processing
3. **Add Monitoring**: Prometheus metrics for cache/queue stats
4. **Database Read Replicas**: Configure MongoDB replica set
5. **CDN Integration**: Cache static assets and API responses

---

## 🐛 Troubleshooting

### Redis Connection Failed
- Check `REDIS_URL` environment variable
- Verify Redis container is running: `docker ps | grep redis`
- Check network connectivity: `docker network ls`

### Cache Not Working
- Verify Redis is connected: Check startup logs
- Check cache service stats: `await cache_service.get_stats()`
- Ensure TTL is set correctly

### Queue Tasks Not Processing
- Register task functions: `queue_service.register_task("name", func)`
- Start worker process: `await queue_service.process_queue("queue_name")`
- Check Redis queue length: `redis-cli LLEN queue:queue_name`

---

## 📚 References

- **Redis Documentation**: https://redis.io/docs/
- **Motor (MongoDB Async)**: https://motor.readthedocs.io/
- **Nginx Load Balancing**: https://nginx.org/en/docs/http/load_balancing.html
- **FastAPI Background Tasks**: https://fastapi.tiangolo.com/tutorial/background-tasks/

