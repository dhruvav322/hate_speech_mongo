# 🛠️ Security Implementation Guide

## Step-by-Step Implementation Plan

This guide provides code and commands to fix all critical security issues.

---

## 🔴 CRITICAL FIX #1: Add API Key Authentication

### Step 1: Create Authentication Middleware

Create file: `src/api/middleware/auth.py`

```python
"""API Key Authentication Middleware"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import List
import secrets

from src.config.settings import settings

# API Key Header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyManager:
    """Manage API keys securely"""
    
    def __init__(self):
        # Load valid API keys from environment/database
        self._valid_keys = self._load_api_keys()
    
    def _load_api_keys(self) -> set:
        """Load API keys from secure storage"""
        # For now, load from settings
        # TODO: Load from database or secrets manager
        keys = set()
        
        if settings.api_key:
            keys.add(settings.api_key)
        
        # Support multiple keys (comma-separated)
        additional_keys = settings.additional_api_keys
        if additional_keys:
            keys.update(additional_keys.split(','))
        
        if not keys:
            raise ValueError("No API keys configured. Set API_KEY environment variable.")
        
        return keys
    
    def verify_key(self, api_key: str) -> bool:
        """Verify API key using constant-time comparison"""
        if not api_key:
            return False
        
        # Use secrets.compare_digest for timing attack prevention
        return any(secrets.compare_digest(api_key, valid_key) 
                  for valid_key in self._valid_keys)
    
    def generate_key(self) -> str:
        """Generate a new API key"""
        return secrets.token_urlsafe(32)


# Global instance
api_key_manager = APIKeyManager()


async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Verify API key from request header.
    
    Args:
        api_key: API key from X-API-Key header
        
    Returns:
        Validated API key
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if not api_key_manager.verify_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key


# Optional: Public endpoints that don't need auth
PUBLIC_ENDPOINTS = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
}


def is_public_endpoint(path: str) -> bool:
    """Check if endpoint is public"""
    return path in PUBLIC_ENDPOINTS
```

### Step 2: Update Settings

Add to `src/config/settings.py`:

```python
class Settings(BaseSettings):
    # ... existing fields ...
    
    # API Keys
    api_key: str = Field(..., env="API_KEY")  # Required, no default
    additional_api_keys: Optional[str] = Field(None, env="ADDITIONAL_API_KEYS")
    
    @validator('api_key')
    def validate_api_key(cls, v, values):
        """Ensure API key is secure"""
        if not v:
            raise ValueError("API_KEY is required")
        
        if v == "industry-demo-key-12345":
            raise ValueError("Default API key not allowed in production!")
        
        if len(v) < 32:
            raise ValueError("API key must be at least 32 characters")
        
        return v
```

### Step 3: Apply to Main App

Update `src/main.py`:

```python
from src.api.middleware.auth import verify_api_key, is_public_endpoint, APIKeyManager
from fastapi import Request, Depends

# Add global middleware for ALL routes
@app.middleware("http")
async def enforce_api_key(request: Request, call_next):
    """Enforce API key on all non-public endpoints"""
    
    # Skip public endpoints
    if is_public_endpoint(request.url.path):
        return await call_next(request)
    
    # Skip OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        return await call_next(request)
    
    # Verify API key
    api_key = request.headers.get("X-API-Key")
    if not api_key or not api_key_manager.verify_key(api_key):
        return JSONResponse(
            status_code=403,
            content={"detail": "Invalid or missing API key"}
        )
    
    response = await call_next(request)
    return response
```

### Step 4: Update All Route Files

Update `src/api/routes/moderation.py` and other route files:

```python
from src.api.middleware.auth import verify_api_key
from fastapi import Depends

@router.post("/analyze", response_model=ModerationResponse)
async def analyze_message(
    request: ModerationRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_database),
    api_key: str = Depends(verify_api_key)  # ✅ ADD THIS
):
    """Analyze message with API key authentication"""
    # ... existing code ...
```

---

## 🔴 CRITICAL FIX #2: Implement Rate Limiting

### Step 1: Install Dependencies

```bash
pip install slowapi redis
```

### Step 2: Create Rate Limiter

Create file: `src/api/middleware/rate_limit.py`

```python
"""Rate Limiting Middleware"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
import redis
from typing import Optional

from src.config.settings import settings


class RateLimitManager:
    """Manage rate limiting with Redis backend"""
    
    def __init__(self):
        # Redis backend (optional, falls back to memory)
        self.redis_client = None
        if settings.redis_url:
            try:
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True
                )
                self.redis_client.ping()
                print("✅ Redis connected for rate limiting")
            except Exception as e:
                print(f"⚠️  Redis unavailable, using in-memory rate limiting: {e}")
        
        # Create limiter
        self.limiter = Limiter(
            key_func=self._get_identifier,
            storage_uri=settings.redis_url if self.redis_client else "memory://",
            default_limits=["100/hour"],
        )
    
    def _get_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting.
        Uses API key if available, otherwise IP address.
        """
        # Prefer API key for user-based limiting
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"key:{api_key[:16]}"  # Use first 16 chars
        
        # Fallback to IP address
        return get_remote_address(request)


# Global instance
rate_limiter = RateLimitManager()
limiter = rate_limiter.limiter


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit error handler"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": exc.headers.get("Retry-After"),
        },
        headers=exc.headers,
    )
```

### Step 3: Apply to Main App

Update `src/main.py`:

```python
from src.api.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add SlowAPI middleware
from slowapi.middleware import SlowAPIMiddleware
app.add_middleware(SlowAPIMiddleware)
```

### Step 4: Apply to Endpoints

```python
from src.api.middleware.rate_limit import limiter
from fastapi import Request

@router.post("/analyze")
@limiter.limit("10/minute")  # 10 requests per minute
async def analyze_message(
    request: Request,  # Required for rate limiting
    moderation_request: ModerationRequest,
    ...
):
    """Analyze message with rate limiting"""
    # ... existing code ...


@router.post("/batch")
@limiter.limit("2/minute")  # Batch is more expensive
async def analyze_batch(
    request: Request,
    ...
):
    """Batch analysis with stricter rate limiting"""
    # ... existing code ...
```

---

## 🔴 CRITICAL FIX #3: Fix CORS Configuration

Update `src/main.py`:

```python
# Update settings.py first
class Settings(BaseSettings):
    # ... existing ...
    
    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000"],
        env="ALLOWED_ORIGINS"
    )
    
    @validator('allowed_origins', pre=True)
    def parse_origins(cls, v):
        """Parse comma-separated origins"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # ✅ From settings
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # ✅ Specific methods
    allow_headers=["Content-Type", "X-API-Key", "Authorization"],  # ✅ Specific headers
    max_age=3600,  # Cache preflight for 1 hour
)
```

---

## 🔴 CRITICAL FIX #4: MongoDB Authentication

### Step 1: Update docker-compose.yml

```yaml
services:
  mongo:
    image: mongo:6.0
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USER:-admin}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
      MONGO_INITDB_DATABASE: hate_speech_db
    ports:
      - "127.0.0.1:27017:27017"  # ✅ Only localhost
    volumes:
      - mongo_data:/data/db
      - ./scripts/init-mongo.js:/docker-entrypoint-initdb.d/init-mongo.js:ro
    restart: unless-stopped
    command: ["--auth"]  # ✅ Enable authentication
    
  api:
    environment:
      - MONGODB_URL=mongodb://${MONGO_ROOT_USER:-admin}:${MONGO_ROOT_PASSWORD}@mongo:27017/hate_speech_db?authSource=admin
```

### Step 2: Create Init Script

Update `scripts/init-mongo.js`:

```javascript
// Create application user with limited permissions
db = db.getSiblingDB('hate_speech_db');

db.createUser({
  user: 'hate_speech_app',
  pwd: process.env.MONGO_APP_PASSWORD,
  roles: [
    {
      role: 'readWrite',
      db: 'hate_speech_db'
    }
  ]
});

// Create indexes
db.messages.createIndex({ "user_id": 1, "timestamp": -1 });
db.messages.createIndex({ "conversation_id": 1, "timestamp": -1 });
db.messages.createIndex({ "timestamp": -1 });
db.users.createIndex({ "user_id": 1 }, { unique: true });
db.conversations.createIndex({ "conversation_id": 1 }, { unique: true });
db.moderation_logs.createIndex({ "timestamp": -1 });

print("✅ MongoDB initialized with authentication and indexes");
```

---

## 🔴 CRITICAL FIX #5: Add Input Sanitization

Create file: `src/api/middleware/sanitization.py`

```python
"""Input Sanitization Middleware"""

import bleach
import re
from fastapi import HTTPException
from typing import Any, Dict


class InputSanitizer:
    """Sanitize user input to prevent injection attacks"""
    
    # Dangerous patterns for NoSQL injection
    NOSQL_INJECTION_PATTERNS = [
        r'\$where',
        r'\$regex',
        r'\$gt',
        r'\$lt',
        r'\$ne',
        r'\$or',
        r'\$and',
        r'javascript:',
        r'<script',
    ]
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 10000) -> str:
        """
        Sanitize text input.
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
            
        Raises:
            HTTPException: If input is invalid
        """
        if not isinstance(text, str):
            raise HTTPException(400, "Text must be a string")
        
        # Check length
        if len(text) > max_length:
            raise HTTPException(
                400,
                f"Text exceeds maximum length of {max_length} characters"
            )
        
        # Check for NoSQL injection patterns
        text_lower = text.lower()
        for pattern in InputSanitizer.NOSQL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                raise HTTPException(
                    400,
                    "Input contains potentially dangerous patterns"
                )
        
        # Clean HTML/XSS
        text = bleach.clean(text, strip=True, tags=[])
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        return text.strip()
    
    @staticmethod
    def sanitize_user_id(user_id: str) -> str:
        """Sanitize user ID"""
        if not user_id or not isinstance(user_id, str):
            raise HTTPException(400, "Invalid user_id")
        
        # Only allow alphanumeric, underscore, hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
            raise HTTPException(
                400,
                "user_id can only contain letters, numbers, underscore, and hyphen"
            )
        
        if len(user_id) > 100:
            raise HTTPException(400, "user_id too long")
        
        return user_id
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary"""
        sanitized = {}
        for key, value in data.items():
            # Sanitize keys
            if not re.match(r'^[a-zA-Z0-9_]+$', key):
                raise HTTPException(400, f"Invalid key: {key}")
            
            # Sanitize values
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_text(value)
            elif isinstance(value, dict):
                sanitized[key] = InputSanitizer.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    InputSanitizer.sanitize_text(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized


# Apply to Pydantic models
from pydantic import validator

class ModerationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    
    @validator('text')
    def sanitize_text(cls, v):
        return InputSanitizer.sanitize_text(v)
    
    @validator('user_id', 'conversation_id')
    def sanitize_ids(cls, v):
        if v:
            return InputSanitizer.sanitize_user_id(v)
        return v
```

---

## 🔴 CRITICAL FIX #6: Add Security Headers

Create file: `src/api/middleware/security_headers.py`

```python
"""Security Headers Middleware"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # Prevent XSS attacks
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS (only if using HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'"
        )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=()"
        )
        
        return response
```

Apply in `src/main.py`:

```python
from src.api.middleware.security_headers import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)
```

---

## 🛠️ Environment Variables Setup

Create `.env.example`:

```bash
# API Configuration
API_KEY=your-secure-api-key-at-least-32-characters-long
ADDITIONAL_API_KEYS=key1,key2,key3
ENVIRONMENT=production

# Database
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=your-strong-password-here
MONGO_APP_PASSWORD=app-user-password
MONGODB_URL=mongodb://admin:your-strong-password@localhost:27017/hate_speech_db?authSource=admin

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Rate Limiting
REDIS_URL=redis://localhost:6379/0

# ML Models
DETOXIFY_MODEL=multilingual
USE_CLAUDE=false

# Logging
LOG_LEVEL=INFO
```

---

## 📝 Deployment Checklist

```bash
# 1. Generate secure API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Set environment variables
cp .env.example .env
# Edit .env with your values

# 3. Test locally
docker-compose -f docker-compose.yml up -d

# 4. Verify security
curl -X POST http://localhost:8000/api/v1/moderation/analyze
# Should return 401/403 (unauthorized)

# 5. Test with API key
curl -X POST http://localhost:8000/api/v1/moderation/analyze \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"text": "test message", "user_id": "test_user"}'

# 6. Check security headers
curl -I https://your-domain.com

# 7. Test rate limiting
for i in {1..15}; do
  curl -X POST http://localhost:8000/api/v1/moderation/analyze \
    -H "X-API-Key: your-api-key" \
    -H "Content-Type: application/json" \
    -d '{"text": "test '$i'", "user_id": "test_user"}'
done
# Should see 429 (rate limit) after 10 requests
```

---

## 🧪 Testing Security

Create `tests/test_security.py`:

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_requires_api_key():
    """Test that endpoints require API key"""
    response = client.post("/api/v1/moderation/analyze", json={
        "text": "test",
        "user_id": "test_user"
    })
    assert response.status_code in [401, 403]

def test_invalid_api_key():
    """Test that invalid API key is rejected"""
    response = client.post(
        "/api/v1/moderation/analyze",
        json={"text": "test", "user_id": "test_user"},
        headers={"X-API-Key": "invalid-key"}
    )
    assert response.status_code == 403

def test_valid_api_key(api_key):
    """Test that valid API key works"""
    response = client.post(
        "/api/v1/moderation/analyze",
        json={"text": "test message", "user_id": "test_user"},
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200

def test_rate_limiting(api_key):
    """Test rate limiting"""
    for i in range(15):
        response = client.post(
            "/api/v1/moderation/analyze",
            json={"text": f"test {i}", "user_id": "test_user"},
            headers={"X-API-Key": api_key}
        )
        
        if i < 10:
            assert response.status_code == 200
        else:
            assert response.status_code == 429

def test_input_sanitization():
    """Test input sanitization"""
    dangerous_inputs = [
        {"text": "$where: '1==1'"},
        {"text": "'; DROP TABLE users; --"},
        {"text": "<script>alert('xss')</script>"},
    ]
    
    for data in dangerous_inputs:
        response = client.post(
            "/api/v1/moderation/analyze",
            json=data,
            headers={"X-API-Key": "valid-key"}
        )
        # Should either sanitize or reject
        assert response.status_code in [200, 400]
```

---

**Priority**: Implement in order presented (1-6)  
**Timeline**: Complete all critical fixes within 1 week

