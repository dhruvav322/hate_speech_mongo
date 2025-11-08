"""Main FastAPI application for hate speech moderation system."""

import uvicorn
from contextlib import asynccontextmanager
<<<<<<< HEAD
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
=======
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config.settings import settings
from src.config.database import db_manager, create_indexes
from src.services.toxicity_detector import toxicity_detector
from src.services.embedding_service import embedding_service
from src.services.moderation_service import moderation_service
from src.api.routes import moderation, users, conversations, analytics, feedback

>>>>>>> compyle/hate-speech-mitigation-agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
<<<<<<< HEAD
    print("🚀 Hate Speech Moderation System starting...")
    yield
    print("📴 Application shutdown")

app = FastAPI(
    title="Hate Speech Moderation API",
    description="Adaptive hate speech moderation system with context-aware scoring",
=======
    # Startup
    try:
        # Initialize database connection
        await db_manager.connect_async()

        # Create database indexes
        await create_indexes()

        # Pre-load ML models
        await toxicity_detector.health_check()
        await embedding_service.health_check()

        print("🚀 Hate Speech Moderation System started successfully")
        print(f"📊 Database: {settings.mongodb_db_name}")
        print(f"🧠 Toxicity Model: {settings.detoxify_model}")
        print(f"🔤 Embedding Model: {settings.sentence_transformer_model}")

    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        raise

    yield

    # Shutdown
    try:
        await db_manager.disconnect_async()
        print("📴 Application shutdown complete")
    except Exception as e:
        print(f"❌ Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Hate Speech Moderation API",
    description="Adaptive hate speech moderation system with context-aware scoring and user behavior learning",
>>>>>>> compyle/hate-speech-mitigation-agent
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

<<<<<<< HEAD
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
=======
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
>>>>>>> compyle/hate-speech-mitigation-agent
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
=======

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


>>>>>>> compyle/hate-speech-mitigation-agent
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Hate Speech Moderation API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

<<<<<<< HEAD
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/moderation/analyze")
async def analyze_message(request: dict):
    """Simple message analysis endpoint."""
    text = request.get("text", "")
    toxic_words = ["hate", "stupid", "ugly", "kill"]
    toxicity_score = sum(1 for word in toxic_words if word.lower() in text.lower()) / max(len(text.split()), 1)
    toxicity_score = min(toxicity_score, 1.0)

    if toxicity_score < 0.3:
        action = "none"
    elif toxicity_score < 0.6:
        action = "warn"
    elif toxicity_score < 0.8:
        action = "hide"
    else:
        action = "delete"

    return {
        "message_id": f"msg_{int(datetime.utcnow().timestamp())}",
        "overall_score": toxicity_score,
        "moderation_action": {
            "recommended_action": action,
            "confidence": 0.85,
            "reason": f"Analysis complete - action: {action}"
        },
        "processing_time_ms": 45,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
=======

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
>>>>>>> compyle/hate-speech-mitigation-agent
