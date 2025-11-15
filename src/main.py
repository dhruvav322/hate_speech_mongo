"""Main FastAPI application for hate speech moderation system."""

import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from src.config.settings import settings
from src.config.database import db_manager, create_indexes
from src.services.toxicity_detector import toxicity_detector
from src.services.embedding_service import embedding_service
from src.services.moderation_service import moderation_service
from src.api.routes import moderation, users, conversations, analytics, feedback
from src.api.middleware.auth import api_key_manager, is_public_endpoint
from src.api.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from src.api.middleware.security_headers import SecurityHeadersMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    try:
        # Initialize database connection
        await db_manager.connect_async()

        # Create database indexes
        await create_indexes()

        # Pre-load ML models (optional - will fail gracefully if not installed)
        try:
            await toxicity_detector.health_check()
        except Exception as e:
            print(f"Warning: Toxicity detector not available: {e}")
        try:
            await embedding_service.health_check()
        except Exception as e:
            print(f"Warning: Embedding service not available: {e}")

        logger.info("="*60)
        logger.info("🛡️  Hate Speech Moderation System Started")
        logger.info("="*60)
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Database: {settings.mongodb_db_name}")
        logger.info(f"Toxicity Model: {settings.detoxify_model}")
        logger.info(f"Embedding Model: {settings.sentence_transformer_model}")
        logger.info(f"API Authentication: ✅ Enabled")
        logger.info(f"Rate Limiting: ✅ Enabled")
        logger.info(f"CORS Origins: {settings.allowed_origins}")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

    yield

    # Shutdown
    try:
        await db_manager.disconnect_async()
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Hate Speech Moderation API",
    description="Adaptive hate speech moderation system with context-aware scoring and user behavior learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add Security Headers Middleware (first)
app.add_middleware(SecurityHeadersMiddleware)

# Add CORS middleware (configured securely)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key", "Authorization"],
    max_age=3600,
)

# Add Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Request Size Limit Middleware
@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    """Limit request body size"""
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_request_size:
            return JSONResponse(
                status_code=413,
                content={"detail": f"Request body too large. Maximum size: {settings.max_request_size} bytes"}
            )
    return await call_next(request)

# API Key Authentication Middleware
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
            content={
                "detail": "Invalid or missing API key. Include X-API-Key header.",
                "docs": "/docs"
            }
        )
    
    response = await call_next(request)
    return response

# Include routers
app.include_router(
    moderation.router,
    prefix="/api/v1/moderation",
    tags=["Moderation"]
)

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["Users"]
)

app.include_router(
    conversations.router,
    prefix="/api/v1/conversations",
    tags=["Conversations"]
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)

app.include_router(
    feedback.router,
    prefix="/api/v1/feedback",
    tags=["Feedback"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Hate Speech Moderation API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check all components
        moderation_health = await moderation_service.health_check()

        overall_status = "healthy"
        if moderation_health.get("status") != "healthy":
            overall_status = "degraded"

        return {
            "status": overall_status,
            "version": "1.0.0",
            "components": moderation_health.get("components", {}),
            "uptime": "operational",
            "database": "connected" if moderation_health.get("components", {}).get("database", {}).get("status") == "connected" else "disconnected"
        }

    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "version": "1.0.0"
            }
        )


@app.get("/api/v1/models/info")
async def get_models_info():
    """Get information about loaded ML models."""
    try:
        return {
            "toxicity_detector": toxicity_detector.get_model_info(),
            "embedding_service": embedding_service.get_model_info(),
            "configuration": {
                "default_toxicity_threshold": settings.default_toxicity_threshold,
                "context_window_size": settings.context_window_size,
                "batch_size": settings.batch_size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {e}")


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.log_level == "DEBUG" else "Something went wrong"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
