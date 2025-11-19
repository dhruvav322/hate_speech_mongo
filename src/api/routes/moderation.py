"""Moderation API routes."""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request, Query
from fastapi.responses import JSONResponse
from starlette.requests import Request as StarletteRequest

from src.config.database import get_database
from src.models.message import (
    ModerationRequest, ModerationResponse, BatchModerationRequest,
    BatchModerationResponse, MessageCreate
)
from src.models.moderation import ModerationLog
from src.services.moderation_service import moderation_service
from src.services.user_service import user_service
from src.services.toxicity_detector import toxicity_detector
from src.services.embedding_service import embedding_service
from src.models.user import UserBehaviorUpdate
from src.api.middleware.rate_limit import limiter
from src.api.middleware.sanitization import InputSanitizer

router = APIRouter()


@router.post("/analyze", response_model=ModerationResponse)
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute
async def analyze_message(
    request: StarletteRequest,  # Required for rate limiting - slowapi expects 'request'
    body: ModerationRequest,  # Renamed from 'request' to avoid conflict
    background_tasks: BackgroundTasks,
    db=Depends(get_database)
):
    """
    Analyze a single message for hate speech toxicity.

    This endpoint performs comprehensive toxicity analysis including:
    - Base toxicity detection using ML models
    - Context-aware scoring based on conversation history
    - User behavior adaptation
    - Adaptive threshold calculation

    Rate Limit: 10 requests per minute per API key
    
    Args:
        http_request: HTTP request (for rate limiting)
        request: Message analysis request
        background_tasks: FastAPI background tasks
        db: Database connection

    Returns:
        Detailed moderation analysis with recommendations
    """
    try:
        # Sanitize input
        body.text = InputSanitizer.sanitize_text(body.text)
        if body.user_id:
            body.user_id = InputSanitizer.sanitize_identifier(body.user_id, "user_id")
        if body.conversation_id:
            body.conversation_id = InputSanitizer.sanitize_identifier(body.conversation_id, "conversation_id")
        
        # Perform analysis
        response = await moderation_service.analyze_message(body)

        # Update user behavior in background
        if body.user_id:
            background_tasks.add_task(
                update_user_behavior_async,
                body.user_id,
                response
            )

        # Store message and analysis in background
        background_tasks.add_task(
            store_message_async,
            body,
            response
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing message: {e}")


@router.post("/batch", response_model=BatchModerationResponse)
@limiter.limit("2/minute")  # Stricter rate limit for batch: 2 requests per minute
async def analyze_batch(
    http_request: Request,  # Required for rate limiting
    request: BatchModerationRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_database)
):
    """
    Analyze multiple messages in batch for efficiency.

    This endpoint processes multiple messages simultaneously,
    providing better performance for bulk operations.

    Rate Limit: 2 requests per minute per API key
    Max Batch Size: 100 messages

    Args:
        http_request: HTTP request (for rate limiting)
        request: Batch analysis request
        background_tasks: FastAPI background tasks
        db: Database connection

    Returns:
        Batch moderation results
    """
    try:
        if len(request.messages) > 100:
            raise HTTPException(
                status_code=400,
                detail="Batch size cannot exceed 100 messages"
            )
        
        # Sanitize all messages in batch
        for msg in request.messages:
            msg.content = InputSanitizer.sanitize_text(msg.content)
            if msg.user_id:
                msg.user_id = InputSanitizer.sanitize_identifier(msg.user_id, "user_id")
            if msg.conversation_id:
                msg.conversation_id = InputSanitizer.sanitize_identifier(msg.conversation_id, "conversation_id")

        # Convert to moderation requests
        moderation_requests = []
        for msg in request.messages:
            moderation_request = ModerationRequest(
                text=msg.content,
                conversation_id=msg.conversation_id,
                user_id=msg.user_id,
                context=msg.context
            )
            moderation_requests.append(moderation_request)

        # Perform batch analysis
        responses = await moderation_service.analyze_batch(moderation_requests)

        # Generate batch ID
        batch_id = f"batch_{uuid.uuid4().hex[:8]}"

        # Create batch response
        batch_response = BatchModerationResponse(
            results=responses,
            total_processed=len(responses),
            processing_time_ms=sum(r.processing_time_ms for r in responses),
            batch_id=batch_id
        )

        # Update user behaviors and store messages in background
        for i, (msg, response) in enumerate(zip(request.messages, responses)):
            if msg.user_id:
                background_tasks.add_task(
                    update_user_behavior_async,
                    msg.user_id,
                    response
                )
            background_tasks.add_task(
                store_message_async,
                ModerationRequest(
                    text=msg.content,
                    conversation_id=msg.conversation_id,
                    user_id=msg.user_id,
                    context=msg.context
                ),
                response
            )

        return batch_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch analysis: {e}")


@router.get("/statistics")
@limiter.limit("20/minute")  # Rate limit: 20 requests per minute
async def get_moderation_statistics(
    request: Request,  # Required for rate limiting
    days: int = Query(default=7, ge=1, le=365),
    limit: int = Query(default=10, ge=1, le=100),
    db=Depends(get_database)
):
    """
    Get moderation statistics for the specified period.

    Rate Limit: 20 requests per minute per API key

    Args:
        request: HTTP request (for rate limiting)
        days: Number of days to look back (default: 7)
        limit: Number of recent events to return (default: 10)
        db: Database connection

    Returns:
        Moderation statistics and analytics with recent events
    """
    try:
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=400,
                detail="Days must be between 1 and 365"
            )

        stats = await moderation_service.get_moderation_statistics(days)
        
        # Get recent events
        from src.config.database import COLLECTIONS
        from datetime import datetime, timedelta
        
        messages_collection = db[COLLECTIONS["messages"]]
        cutoff_date = datetime.utcnow() - timedelta(days=1)
        
        recent_messages = await messages_collection.find(
            {"timestamp": {"$gte": cutoff_date}},
            sort=[("timestamp", -1)],
            limit=limit
        ).to_list(limit)
        
        recent_events = []
        for msg in recent_messages:
            recent_events.append({
                "message_id": msg.get("message_id", ""),
                "content": msg.get("content", "")[:100],  # Truncate for display
                "user_id": msg.get("user_id", ""),
                "score": msg.get("toxicity_analysis", {}).get("overall_score", 0.0),
                "action": msg.get("moderation_action", {}).get("action", "none"),
                "timestamp": msg.get("timestamp", datetime.utcnow()).isoformat() if isinstance(msg.get("timestamp"), datetime) else str(msg.get("timestamp", ""))
            })
        
        stats["recent_events"] = recent_events
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {e}")


@router.get("/health")
async def moderation_health_check(db=Depends(get_database)):
    """
    Check the health of the moderation service components.

    Returns:
        Health status of all moderation components
    """
    try:
        health = await moderation_service.health_check()
        return health

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {e}")


@router.post("/webhook/message-event")
async def message_webhook(
    webhook_data: dict,
    background_tasks: BackgroundTasks,
    db=Depends(get_database)
):
    """
    Webhook endpoint for real-time message processing from external platforms.

    This endpoint allows external platforms (Discord, Slack, etc.) to send
    messages for real-time moderation analysis.

    Expected webhook format:
    {
        "event": "message_created",
        "platform": "discord|slack|telegram|custom",
        "data": {
            "message_id": "string",
            "text": "string",
            "author_id": "string",
            "channel_id": "string",
            "timestamp": "ISO datetime"
        }
    }

    Args:
        webhook_data: Webhook payload
        background_tasks: FastAPI background tasks
        db: Database connection

    Returns:
        Confirmation of message processing
    """
    try:
        # Validate webhook format
        if "event" not in webhook_data or "data" not in webhook_data:
            raise HTTPException(
                status_code=400,
                detail="Invalid webhook format"
            )

        event = webhook_data["event"]
        data = webhook_data["data"]

        if event != "message_created":
            return {"status": "ignored", "reason": "Only message_created events are processed"}

        # Extract required fields
        text = data.get("text", "")
        if not text:
            raise HTTPException(
                status_code=400,
                detail="Message text is required"
            )

        # Create moderation request
        request = ModerationRequest(
            text=text,
            user_id=data.get("author_id"),
            conversation_id=data.get("channel_id"),
            context={
                "platform": webhook_data.get("platform", "custom"),
                "message_type": "chat"
            }
        )

        # Process message
        response = await moderation_service.analyze_message(request)

        # Update user behavior in background
        if data.get("author_id"):
            background_tasks.add_task(
                update_user_behavior_async,
                data["author_id"],
                response
            )

        # Store message in background
        background_tasks.add_task(
            store_message_async,
            request,
            response
        )

        return {
            "status": "processed",
            "message_id": data.get("message_id"),
            "moderation_action": response.moderation_action.action.value,
            "overall_score": response.overall_score,
            "processed_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {e}")


@router.get("/models/status")
async def get_models_status(db=Depends(get_database)):
    """
    Get the status of ML models used in moderation.

    Returns:
        Status information for all ML models
    """
    try:
        # Ensure models are loaded
        if not moderation_service._models_loaded:
            # Trigger health check to load models
            await moderation_service.health_check()

        return {
            "toxicity_detector": toxicity_detector.get_model_info(),
            "embedding_service": embedding_service.get_model_info(),
            "models_loaded": moderation_service._models_loaded,
            "last_updated": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model status: {e}")


# Background task functions
async def update_user_behavior_async(user_id: str, response: ModerationResponse):
    """Update user behavior statistics in background."""
    try:
        from src.services.user_service import user_service
        from src.models.user import UserBehaviorUpdate
        from src.services.queue_service import queue_service

        # Use queue service if available, otherwise execute directly
        if queue_service.use_redis:
            await queue_service.enqueue(
                "user_updates",
                "update_user_behavior",
                user_id,
                response.overall_score,
                response.moderation_action.action.value
            )
        else:
            # Direct execution (fallback)
            behavior_update = UserBehaviorUpdate(
                message_toxicity_score=response.overall_score,
                moderation_action_taken=response.moderation_action.action.value,
                was_false_positive=False
            )
            await user_service.update_user_behavior(user_id, behavior_update)
    except Exception as e:
        # Log error but don't fail the main process
        print(f"Error updating user behavior: {e}")


async def store_message_async(request: ModerationRequest, response: ModerationResponse):
    """Store message and analysis results in background."""
    try:
        from src.config.database import db_manager, COLLECTIONS
        from src.services.queue_service import queue_service

        # Use queue service if available, otherwise execute directly
        if queue_service.use_redis:
            await queue_service.enqueue(
                "message_storage",
                "store_message",
                response.message_id,
                request.conversation_id,
                request.user_id,
                request.text,
                response.dict()
            )
        else:
            # Direct execution (fallback)
            message_doc = {
                "message_id": response.message_id,
                "conversation_id": request.conversation_id,
                "user_id": request.user_id,
                "content": request.text,
                "timestamp": response.timestamp,
                "toxicity_analysis": {
                    "overall_score": response.overall_score,
                    "predictions": response.toxicity_scores.dict(),
                    "confidence": response.moderation_action.confidence,
                    "processing_time_ms": response.processing_time_ms
                },
                "moderation_action": response.moderation_action.dict(),
                "context": request.context.dict() if request.context else {}
            }
            messages_collection = db_manager.async_db[COLLECTIONS["messages"]]
            await messages_collection.insert_one(message_doc)

    except Exception as e:
        # Log error but don't fail the main process
        print(f"Error storing message: {e}")