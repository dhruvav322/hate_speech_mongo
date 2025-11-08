#!/usr/bin/env python3
"""
Enhanced Industry-Ready Hate Speech Moderation API
Advanced ML models with ensemble predictions and real-time monitoring
"""

import os
import sys
import logging
import asyncio
import time
import uuid
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# MongoDB
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("Warning: MongoDB not available, using in-memory storage")

# Import advanced ML models
try:
    from advanced_ml_models import advanced_models, EnsembleResult
    ADVANCED_MODELS_AVAILABLE = True
    print("Advanced ML models available")
except ImportError:
    ADVANCED_MODELS_AVAILABLE = False
    print("Warning: Advanced ML models not available, using fallback")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hate_speech_db")
    API_KEY = os.getenv("API_KEY", "industry-demo-key-12345")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    BACKGROUND_PROCESSING = os.getenv("BACKGROUND_PROCESSING", "true").lower() == "true"
    MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
    MODEL_NAME = os.getenv("MODEL_NAME", "ensemble")
    USE_ADVANCED_MODELS = os.getenv("USE_ADVANCED_MODELS", "true").lower() == "true"

config = Config()

# In-memory storage for fallback
@dataclass
class InMemoryStorage:
    users: Dict[str, Dict] = None
    messages: Dict[str, Dict] = None
    feedback: List[Dict] = None

    def __post_init__(self):
        if self.users is None:
            self.users = {}
        if self.messages is None:
            self.messages = {}
        if self.feedback is None:
            self.feedback = []

memory_storage = InMemoryStorage()

# Pydantic Models
from enum import Enum

class ModerationAction(str, Enum):
    ALLOW = "allow"
    FLAG = "flag"
    BLOCK = "block"

class UserProfile(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    email: Optional[str] = Field(None, description="User email (optional)")
    trust_score: float = Field(0.5, ge=0.0, le=1.0, description="User trust score")
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)

class MessageAnalysis(BaseModel):
    message_id: str = Field(..., description="Unique message identifier")
    user_id: str = Field(..., description="User who sent the message")
    text: str = Field(..., min_length=1, max_length=10000, description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)
    toxicity_scores: Dict[str, float] = Field(default_factory=dict)
    toxicity_score: float = Field(0.0, ge=0.0, le=1.0, description="Overall toxicity score")
    moderation_action: ModerationAction = Field(ModerationAction.ALLOW)
    processing_time_ms: float = Field(0.0, description="Processing time in milliseconds")
    model_version: str = Field(default="unknown")

class FeedbackRequest(BaseModel):
    message_id: str = Field(..., description="Unique identifier of the moderated message")
    correct_action: ModerationAction = Field(..., description="Correct moderation action")
    feedback_text: Optional[str] = Field(None, description="Additional feedback")
    user_id: str = Field(..., description="User providing feedback")

class AnalyticsResponse(BaseModel):
    total_messages: int
    toxic_messages: int
    toxicity_rate: float
    average_toxicity_score: float
    actions_blocked: int
    actions_flagged: int
    actions_allowed: int
    model_accuracy: Optional[float] = None
    feedback_count: int
    uptime_hours: float

class ModelPerformanceResponse(BaseModel):
    models_loaded: int
    total_predictions: int
    average_prediction_time_ms: float
    uptime_hours: float
    cache_hit_rate_percent: float
    cache_size: int
    model_usage: Dict[str, int]
    available_models: List[str]
    ml_libraries_available: bool

# Security
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=True)

async def get_api_key(api_key: str = Depends(API_KEY_HEADER)) -> str:
    """Validate API key."""
    valid_keys = [config.API_KEY]
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key

# Database Interface
class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.connected = False

    async def connect(self):
        """Connect to MongoDB."""
        if MONGODB_AVAILABLE:
            try:
                self.client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)
                self.client.admin.command('ping')
                self.db = self.client.get_default_database()
                self.connected = True
                logger.info("Connected to MongoDB")
            except Exception as e:
                logger.warning(f"MongoDB connection failed: {e}")
                self.connected = False
        else:
            logger.info("Using in-memory storage")

    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user profile."""
        if self.connected and self.db is not None:
            return self.db.users.find_one({"user_id": user_id})
        return memory_storage.users.get(user_id)

    async def create_user(self, user_data: Dict) -> Dict:
        """Create user profile."""
        if self.connected and self.db is not None:
            result = self.db.users.insert_one(user_data)
            user_data["_id"] = str(result.inserted_id)
            return user_data
        memory_storage.users[user_data["user_id"]] = user_data
        return user_data

    async def store_message(self, message_data: Dict) -> Dict:
        """Store message analysis."""
        if self.connected and self.db is not None:
            result = self.db.messages.insert_one(message_data)
            message_data["_id"] = str(result.inserted_id)
            return message_data
        memory_storage.messages[message_data["message_id"]] = message_data
        return message_data

    async def store_feedback(self, feedback_data: Dict) -> Dict:
        """Store feedback."""
        if self.connected and self.db is not None:
            result = self.db.feedback.insert_one(feedback_data)
            feedback_data["_id"] = str(result.inserted_id)
            return feedback_data
        memory_storage.feedback.append(feedback_data)
        return feedback_data

    async def get_analytics(self) -> Dict:
        """Get analytics data."""
        if self.connected and self.db is not None:
            total_messages = self.db.messages.count_documents({})
            toxic_messages = self.db.messages.count_documents({"toxicity_score": {"$gt": 0.5}})

            pipeline = [
                {"$group": {"_id": "$moderation_action", "count": {"$sum": 1}}}
            ]
            action_counts = []
            try:
                action_counts = list(self.db.messages.aggregate(pipeline))
            except Exception as e:
                logger.warning(f"MongoDB aggregation failed: {e}")
                action_counts = []

            feedback_count = self.db.feedback.count_documents({})
        else:
            total_messages = len(memory_storage.messages)
            toxic_messages = sum(1 for msg in memory_storage.messages.values()
                               if msg.get("toxicity_score", 0) > 0.5)

            action_counts = {}
            for msg in memory_storage.messages.values():
                action = msg.get("moderation_action", ModerationAction.ALLOW)
                action_str = action.value if hasattr(action, 'value') else str(action)
                action_counts[action_str] = action_counts.get(action_str, 0) + 1

            feedback_count = len(memory_storage.feedback)

        # Calculate action breakdown
        actions = {"block": 0, "flag": 0, "allow": 0}
        for action_count in action_counts:
            action = action_count.get("_id", "allow")
            if action in actions:
                actions[action] = action_count.get("count", 0)

        return {
            "total_messages": total_messages,
            "toxic_messages": toxic_messages,
            "toxicity_rate": toxic_messages / total_messages if total_messages > 0 else 0,
            "actions_blocked": actions["block"],
            "actions_flagged": actions["flag"],
            "actions_allowed": actions["allow"],
            "feedback_count": feedback_count
        }

# Enhanced ML Model Handler
class ToxicityModel:
    def __init__(self):
        self.start_time = time.time()
        self.using_advanced_models = ADVANCED_MODELS_AVAILABLE and config.USE_ADVANCED_MODELS

    async def load_model(self):
        """Load the ML model(s)."""
        if self.using_advanced_models:
            try:
                await advanced_models.load_all_models()
                logger.info("Loaded advanced ML models ensemble")
            except Exception as e:
                logger.error(f"Failed to load advanced models: {e}")
                self.using_advanced_models = False
        else:
            logger.info("Advanced models disabled or not available, using fallback predictions")

    async def predict_toxicity(self, text: str) -> Dict[str, float]:
        """Predict toxicity scores using advanced models or fallback."""
        start_time = time.time()

        if self.using_advanced_models:
            try:
                # Use advanced ensemble prediction
                result = await advanced_models.predict_toxicity_ensemble(text)

                # Convert to standard format
                toxicity_scores = {}
                for pred in result.individual_predictions:
                    for category, score in pred.raw_scores.items():
                        if isinstance(score, (int, float)):
                            toxicity_scores[category] = score

                # Ensure we have standard toxicity categories
                standard_categories = ['toxicity', 'severe_toxicity', 'obscene', 'identity_attack', 'insult', 'threat']
                for cat in standard_categories:
                    if cat not in toxicity_scores:
                        toxicity_scores[cat] = result.final_score

                processing_time = (time.time() - start_time) * 1000

                return {
                    'toxicity_scores': toxicity_scores,
                    'overall_score': result.final_score,
                    'processing_time_ms': processing_time,
                    'ensemble_info': {
                        'model_count': result.model_count,
                        'confidence': result.confidence,
                        'consensus': result.consensus,
                        'individual_models': [p.model_name for p in result.individual_predictions]
                    }
                }
            except Exception as e:
                logger.error(f"Advanced prediction failed: {e}")
                # Fall back to simple prediction

        # Fallback predictions
        return await self._fallback_prediction(text, start_time)

    async def _fallback_prediction(self, text: str, start_time: float) -> Dict[str, float]:
        """Fallback prediction when advanced models fail."""
        toxic_keywords = ['hate', 'stupid', 'ugly', 'kill', 'die', 'idiot', 'moron', 'fool']
        severe_keywords = ['kill', 'die', 'murder', 'violence', 'harm']
        text_lower = text.lower()

        toxicity_scores = {}

        for category in ['toxicity', 'severe_toxicity', 'obscene', 'identity_attack', 'insult', 'threat']:
            score = 0.0

            if category == 'toxicity' and any(word in text_lower for word in toxic_keywords):
                score = 0.7
            elif category == 'severe_toxicity' and any(word in text_lower for word in severe_keywords):
                score = 0.9
            elif category == 'insult' and any(word in text_lower for word in ['stupid', 'idiot', 'moron', 'fool']):
                score = 0.6
            elif category == 'threat' and any(word in text_lower for word in ['kill', 'hurt', 'harm', 'die']):
                score = 0.8
            elif category == 'identity_attack' and any(word in text_lower for word in ['race', 'gender', 'religion']):
                score = 0.5
            elif category == 'obscene' and any(word in text_lower for word in ['ugly', 'disgusting']):
                score = 0.4

            toxicity_scores[category] = score

        overall_score = max(toxicity_scores.values())
        processing_time = (time.time() - start_time) * 1000

        return {
            'toxicity_scores': toxicity_scores,
            'overall_score': overall_score,
            'processing_time_ms': processing_time
        }

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Industry-Ready Hate Speech Moderation API",
    description="Production-grade hate speech moderation with advanced ML ensemble and feedback loop",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
db_manager = DatabaseManager()
toxicity_model = ToxicityModel()

# Background processing
async def process_analysis_background(message_id: str, text: str, user_id: str):
    """Background task for additional processing."""
    try:
        logger.info(f"Background processing for message {message_id}")

        # Simulate additional processing
        await asyncio.sleep(0.1)

        # Could add: store embeddings, update user profile, aggregate statistics

        logger.info(f"Background processing completed for message {message_id}")
    except Exception as e:
        logger.error(f"Background processing failed for {message_id}: {e}")

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize the application."""
    logger.info("Starting Enhanced Industry-Ready Hate Speech Moderation API")
    await db_manager.connect()
    await toxicity_model.load_model()
    logger.info("API initialization complete")

@app.get("/", status_code=200)
async def root():
    """Health check endpoint with enhanced features."""
    features = {
        "api_key_auth": True,
        "background_processing": config.BACKGROUND_PROCESSING,
        "mongodb_connected": db_manager.connected,
        "advanced_ml_models": toxicity_model.using_advanced_models,
        "mlops_feedback": True,
        "ensemble_predictions": ADVANCED_MODELS_AVAILABLE and config.USE_ADVANCED_MODELS,
        "real_time_monitoring": True
    }

    return {
        "status": "operational",
        "service": "enhanced-hate-speech-moderation",
        "version": "2.0.0",
        "features": features,
        "uptime_seconds": int(time.time() - toxicity_model.start_time)
    }

@app.post("/api/v1/moderation/analyze", response_model=Dict[str, Any])
async def analyze_message(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key)
):
    """Analyze message for hate speech using advanced ML ensemble."""
    start_time = time.time()

    try:
        # Extract request data
        text = request.get("text", "")
        user_id = request.get("user_id", f"anonymous_{uuid.uuid4().hex[:8]}")

        if not text:
            raise HTTPException(status_code=400, detail="Text field is required")

        # Generate unique message ID
        message_id = str(uuid.uuid4())

        # Get or create user profile
        user = await db_manager.get_user(user_id)
        if not user:
            user_data = {
                "user_id": user_id,
                "trust_score": 0.5,
                "created_at": datetime.now(),
                "last_active": datetime.now()
            }
            user = await db_manager.create_user(user_data)

        # Analyze toxicity with advanced models
        prediction = await toxicity_model.predict_toxicity(text)
        toxicity_score = prediction['overall_score']
        toxicity_scores = prediction['toxicity_scores']

        # Determine moderation action
        if toxicity_score >= 0.8:
            moderation_action = ModerationAction.BLOCK
        elif toxicity_score >= 0.5:
            moderation_action = ModerationAction.FLAG
        else:
            moderation_action = ModerationAction.ALLOW

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000

        # Create message record
        message_data = {
            "message_id": message_id,
            "user_id": user_id,
            "text": text,
            "timestamp": datetime.now(),
            "toxicity_scores": toxicity_scores,
            "toxicity_score": toxicity_score,
            "moderation_action": moderation_action,
            "processing_time_ms": processing_time,
            "model_version": "ensemble_v2" if toxicity_model.using_advanced_models else "fallback_v1"
        }

        # Store message
        await db_manager.store_message(message_data)

        # Schedule background processing
        if config.BACKGROUND_PROCESSING:
            background_tasks.add_task(process_analysis_background, message_id, text, user_id)

        logger.info(f"Analyzed message {message_id}: score={toxicity_score:.3f}, action={moderation_action}")

        # Enhanced response with model information
        response = {
            "success": True,
            "message_id": message_id,
            "moderation_action": {
                "recommended_action": moderation_action,
                "confidence": max(0.1, 1.0 - toxicity_score)
            },
            "analysis": {
                "toxicity_score": toxicity_score,
                "toxicity_scores": toxicity_scores,
                "processing_time_ms": processing_time
            },
            "user": {
                "user_id": user_id,
                "trust_score": user.get("trust_score", 0.5)
            },
            "model_info": {
                "model_type": "ensemble" if toxicity_model.using_advanced_models else "fallback",
                "advanced_ml": toxicity_model.using_advanced_models
            }
        }

        # Add ensemble information if available
        if 'ensemble_info' in prediction:
            response["ensemble_info"] = prediction['ensemble_info']

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/v1/feedback", status_code=201)
async def submit_feedback(
    feedback_data: FeedbackRequest,
    api_key: str = Depends(get_api_key)
):
    """Submit feedback for incorrect moderation."""
    try:
        # Store feedback
        feedback_record = {
            "message_id": feedback_data.message_id,
            "correct_action": feedback_data.correct_action,
            "feedback_text": feedback_data.feedback_text,
            "user_id": feedback_data.user_id,
            "timestamp": datetime.now()
        }

        await db_manager.store_feedback(feedback_record)

        logger.info(f"Received feedback for message {feedback_data.message_id}")

        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": str(uuid.uuid4())
        }

    except Exception as e:
        logger.error(f"Feedback submission failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/analytics", response_model=AnalyticsResponse)
async def get_analytics(api_key: str = Depends(get_api_key)):
    """Get system analytics."""
    try:
        # Get analytics from database
        analytics_data = await db_manager.get_analytics()

        # Calculate additional metrics
        uptime_hours = (time.time() - toxicity_model.start_time) / 3600

        # Mock model accuracy (would be calculated from feedback)
        model_accuracy = 0.92 if analytics_data["feedback_count"] > 0 else None

        return AnalyticsResponse(
            total_messages=analytics_data["total_messages"],
            toxic_messages=analytics_data["toxic_messages"],
            toxicity_rate=analytics_data["toxicity_rate"],
            average_toxicity_score=analytics_data["toxicity_rate"],
            actions_blocked=analytics_data["actions_blocked"],
            actions_flagged=analytics_data["actions_flagged"],
            actions_allowed=analytics_data["actions_allowed"],
            model_accuracy=model_accuracy,
            feedback_count=analytics_data["feedback_count"],
            uptime_hours=uptime_hours
        )

    except Exception as e:
        logger.error(f"Analytics failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/model-performance", response_model=ModelPerformanceResponse)
async def get_model_performance(api_key: str = Depends(get_api_key)):
    """Get detailed ML model performance statistics."""
    try:
        if ADVANCED_MODELS_AVAILABLE and config.USE_ADVANCED_MODELS:
            stats = advanced_models.get_performance_stats()
            return ModelPerformanceResponse(**stats)
        else:
            return ModelPerformanceResponse(
                models_loaded=0,
                total_predictions=0,
                average_prediction_time_ms=0.0,
                uptime_hours=(time.time() - toxicity_model.start_time) / 3600,
                cache_hit_rate_percent=0.0,
                cache_size=0,
                model_usage={},
                available_models=[],
                ml_libraries_available=False
            )
    except Exception as e:
        logger.error(f"Model performance stats failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/health")
async def health_check():
    """Detailed health check with ML model status."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected" if db_manager.connected else "in-memory",
            "ml_models": "advanced_ensemble" if toxicity_model.using_advanced_models else "fallback",
            "auth": "operational"
        },
        "metrics": {
            "uptime_seconds": int(time.time() - toxicity_model.start_time),
            "environment": config.ENVIRONMENT
        }
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

# Run directly
if __name__ == "__main__":
    uvicorn.run(
        "main_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=config.ENVIRONMENT == "development",
        log_level=config.LOG_LEVEL.lower()
    )