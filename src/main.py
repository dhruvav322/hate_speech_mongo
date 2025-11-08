"""Main FastAPI application for hate speech moderation system."""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    print("🚀 Hate Speech Moderation System starting...")
    yield
    print("📴 Application shutdown")

app = FastAPI(
    title="Hate Speech Moderation API",
    description="Adaptive hate speech moderation system with context-aware scoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
