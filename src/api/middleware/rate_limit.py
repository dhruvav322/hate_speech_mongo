"""Rate Limiting Middleware"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

from src.config.settings import settings

logger = logging.getLogger(__name__)


def get_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting.
    Uses API key if available, otherwise IP address.
    """
    # Prefer API key for user-based limiting
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"key:{api_key[:16]}"  # Use first 16 chars
    
    # Fallback to IP address
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_identifier,
    default_limits=["100/hour"],
    storage_uri=settings.redis_url if settings.redis_url else "memory://",
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit error handler"""
    logger.warning(
        f"Rate limit exceeded for {get_identifier(request)}: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": exc.detail if hasattr(exc, 'detail') else "60 seconds",
        },
        headers={"Retry-After": "60"} if not hasattr(exc, 'headers') else exc.headers,
    )

