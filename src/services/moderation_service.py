"""Adaptive moderation service with context-aware scoring and user behavior adaptation."""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from src.config.settings import (
    settings, MODERATION_THRESHOLDS, USER_RISK_MULTIPLIERS
)
from src.config.database import db_manager, COLLECTIONS
from src.models.conversation import ConversationTrend
from src.models.message import (
    Message, ModerationAction, ModerationActionData,
    ToxicityAnalysis, ModerationRequest, ModerationResponse
)
from src.models.user import RiskLevel, BehaviorProfile
from src.models.moderation import ModerationLog
from src.services.toxicity_detector import toxicity_detector
from src.services.embedding_service import embedding_service
from src.services.cache_service import cache_service


class ModerationService:
    """Service for adaptive content moderation with context awareness."""

    def __init__(self):
        """Initialize the moderation service."""
        self._models_loaded = False

    async def _ensure_models_loaded(self) -> None:
        """Ensure ML models are loaded."""
        if not self._models_loaded:
            # This will trigger model loading
            await toxicity_detector.health_check()
            await embedding_service.health_check()
            self._models_loaded = True

    async def analyze_message(
        self,
        request: ModerationRequest,
        generate_message_id: bool = True
    ) -> ModerationResponse:
        """
        Analyze a message for moderation with adaptive scoring.

        Args:
            request: Moderation request with message details
            generate_message_id: Whether to generate a new message ID

        Returns:
            Detailed moderation response with recommendations
        """
        await self._ensure_models_loaded()

        start_time = time.time()

        # Generate message ID if needed
        message_id = f"msg_{int(time.time() * 1000)}" if generate_message_id else None

        try:
            # Step 1: Base toxicity detection
            toxicity_analysis = await toxicity_detector.analyze_toxicity(request.text)
            base_score = toxicity_analysis.overall_score

            # Step 2: Get context information (with caching)
            context_info = None
            if request.conversation_id:
                cached = await cache_service.get("context", request.conversation_id)
                if cached:
                    # Reconstruct from dict if cached
                    from src.models.moderation import ContextAnalysis
                    context_info = ContextAnalysis(**cached) if isinstance(cached, dict) else cached
            
            if not context_info:
                context_info = await self._get_context_analysis(
                    request.conversation_id,
                    request.user_id,
                    request.text
                )
                # Cache context for 10 minutes (store as dict)
                if request.conversation_id and hasattr(context_info, 'dict'):
                    await cache_service.set("context", context_info.dict(), ttl_seconds=600, *[request.conversation_id])

            # Step 3: Get user behavior profile (with caching)
            user_profile = None
            if request.user_id:
                cached = await cache_service.get("user_profile", request.user_id)
                if cached:
                    # Reconstruct from dict if cached
                    from src.models.user import BehaviorProfile
                    user_profile = BehaviorProfile(**cached) if isinstance(cached, dict) else cached
            
            if not user_profile:
                user_profile = await self._get_user_profile(request.user_id)
                # Cache user profile for 5 minutes (store as dict)
                if request.user_id and hasattr(user_profile, 'dict'):
                    await cache_service.set("user_profile", user_profile.dict(), ttl_seconds=300, *[request.user_id])

            # Step 4: Calculate adaptive threshold
            adjusted_threshold = self._calculate_adaptive_threshold(
                base_score,
                user_profile,
                context_info
            )

            # Step 5: Determine moderation action
            moderation_action = self._determine_moderation_action(
                base_score,
                adjusted_threshold,
                toxicity_analysis,
                user_profile,
                context_info
            )

            # Step 6: Create response
            processing_time = int((time.time() - start_time) * 1000)

            response = ModerationResponse(
                message_id=message_id or "",
                toxicity_scores=toxicity_analysis.predictions,
                overall_score=base_score,
                moderation_action=moderation_action,
                context_analysis=context_info,
                processing_time_ms=processing_time,
                timestamp=datetime.utcnow()
            )

            # Step 7: Log the moderation decision (async, don't wait)
            asyncio.create_task(self._log_moderation_decision(
                message_id or "unknown",
                request.user_id or "unknown",
                request.conversation_id or "unknown",
                base_score,
                adjusted_threshold,
                moderation_action,
                context_info
            ))

            return response

        except Exception as e:
            raise RuntimeError(f"Error in message analysis: {e}")

    async def analyze_batch(self, requests: List[ModerationRequest]) -> List[ModerationResponse]:
        """
        Analyze multiple messages in batch.

        Args:
            requests: List of moderation requests

        Returns:
            List of moderation responses
        """
        if not requests:
            return []

        await self._ensure_models_loaded()

        responses = []
        start_time = time.time()

        # Process each request
        for request in requests:
            try:
                response = await self.analyze_message(request)
                responses.append(response)
            except Exception as e:
                # Create error response for failed analysis
                error_response = ModerationResponse(
                    message_id=f"error_{int(time.time() * 1000)}",
                    toxicity_scores=None,
                    overall_score=0.0,
                    moderation_action=ModerationActionData(
                        action=ModerationAction.NONE,
                        confidence=0.0,
                        reason=f"Analysis failed: {str(e)}",
                        adjusted_threshold=0.5
                    ),
                    context_analysis={"error": str(e)},
                    processing_time_ms=0,
                    timestamp=datetime.utcnow()
                )
                responses.append(error_response)

        return responses

    async def _get_context_analysis(
        self,
        conversation_id: Optional[str],
        user_id: Optional[str],
        current_text: str
    ) -> Dict[str, Any]:
        """Get context analysis for the message."""
        context_info = {
            "similarity_to_context": 0.0,
            "user_risk_level": "medium",
            "conversation_trend": "neutral",
            "context_available": False
        }

        if not conversation_id:
            return context_info

        try:
            # Get recent messages from conversation
            messages_collection = db_manager.async_db[COLLECTIONS["messages"]]
            recent_messages = await messages_collection.find(
                {"conversation_id": conversation_id},
                {"content": 1, "toxicity_analysis.overall_score": 1, "timestamp": 1}
            ).sort("timestamp", -1).limit(settings.context_window_size).to_list(None)

            if not recent_messages:
                return context_info

            context_info["context_available"] = True

            # Generate embedding for current message
            current_embedding = await embedding_service.generate_embedding(current_text)

            # Calculate similarity to recent messages
            if len(recent_messages) > 0:
                # Get embeddings for recent messages (would need to be stored)
                # For now, simulate similarity calculation
                similarities = []
                for msg in recent_messages:
                    if "text_embedding" in msg and msg["text_embedding"]:
                        similarity = await embedding_service.calculate_similarity(
                            current_embedding,
                            msg["text_embedding"]
                        )
                        similarities.append(similarity)

                if similarities:
                    context_info["similarity_to_context"] = sum(similarities) / len(similarities)

            # Analyze conversation trend
            if len(recent_messages) >= 2:
                recent_scores = [
                    msg.get("toxicity_analysis", {}).get("overall_score", 0.0)
                    for msg in recent_messages
                ]
                trend = self._analyze_trend(recent_scores)
                context_info["conversation_trend"] = trend.value

            # Get conversation metadata
            conversations_collection = db_manager.async_db[COLLECTIONS["conversations"]]
            conversation = await conversations_collection.find_one(
                {"conversation_id": conversation_id},
                {"context_embedding": 1, "moderation_level": 1}
            )

            if conversation and "context_embedding" in conversation:
                context_embedding_similarity = await embedding_service.calculate_similarity(
                    current_embedding,
                    conversation["context_embedding"]
                )
                context_info["context_embedding_similarity"] = context_embedding_similarity

        except Exception as e:
            # Log error but don't fail the analysis
            context_info["context_error"] = str(e)

        return context_info

    async def _get_user_profile(self, user_id: Optional[str]) -> BehaviorProfile:
        """Get user behavior profile."""
        if not user_id:
            return BehaviorProfile()

        try:
            users_collection = db_manager.async_db[COLLECTIONS["users"]]
            user = await users_collection.find_one(
                {"user_id": user_id},
                {"behavior_profile": 1}
            )

            if user and "behavior_profile" in user:
                return BehaviorProfile(**user["behavior_profile"])

        except Exception as e:
            # Log error but don't fail the analysis
            pass

        return BehaviorProfile()

    def _calculate_adaptive_threshold(
        self,
        base_score: float,
        user_profile: BehaviorProfile,
        context_info: Dict[str, Any]
    ) -> float:
        """Calculate adaptive threshold based on user behavior and context."""
        base_threshold = settings.default_toxicity_threshold

        # User risk multiplier
        user_multiplier = USER_RISK_MULTIPLIERS.get(user_profile.risk_level.value, 1.0)

        # Context multiplier
        context_multiplier = 1.0
        if context_info.get("conversation_trend") == "escalating":
            context_multiplier = 1.2  # More strict in escalating conversations
        elif context_info.get("conversation_trend") == "deescalating":
            context_multiplier = 0.9  # More lenient in deescalating conversations

        # Similarity to toxic context
        similarity = context_info.get("similarity_to_context", 0.0)
        if similarity > 0.7:
            context_multiplier *= 1.1  # Increase sensitivity if similar to toxic context

        # User trust score adjustment
        trust_multiplier = 1.0 + (0.5 - user_profile.trust_score)  # Higher score = lower threshold

        # Calculate final threshold
        adjusted_threshold = base_threshold * user_multiplier * context_multiplier * trust_multiplier

        # Clamp between 0.1 and 0.9
        return max(0.1, min(0.9, adjusted_threshold))

    def _determine_moderation_action(
        self,
        base_score: float,
        adjusted_threshold: float,
        toxicity_analysis: ToxicityAnalysis,
        user_profile: BehaviorProfile,
        context_info: Dict[str, Any]
    ) -> ModerationActionData:
        """Determine the appropriate moderation action."""
        # Adjust score based on context
        final_score = base_score

        # Consider quoted content (reduces severity)
        # This would need to be detected in the text analysis
        # For now, just use base score

        # Determine action based on thresholds
        if final_score < MODERATION_THRESHOLDS["allow"]:
            action = ModerationAction.NONE
            reason = "Content appears to be within acceptable limits"
        elif final_score < MODERATION_THRESHOLDS["warn"]:
            action = ModerationAction.WARN
            reason = "Content may be inappropriate, user warning issued"
        elif final_score < MODERATION_THRESHOLDS["hide"]:
            action = ModerationAction.HIDE
            reason = "Content violates community guidelines, hidden from view"
        elif final_score < MODERATION_THRESHOLDS["delete"]:
            action = ModerationAction.DELETE
            reason = "Content severely violates community guidelines, deleted"
        else:
            action = ModerationAction.BAN
            reason = "Content represents severe violation, user ban recommended"

        # Add context-specific reasoning
        if context_info.get("conversation_trend") == "escalating":
            reason += " (escalating conversation context)"

        if user_profile.risk_level == RiskLevel.HIGH:
            reason += " (high-risk user profile)"

        return ModerationActionData(
            action=action,
            confidence=toxicity_analysis.confidence,
            reason=reason,
            adjusted_threshold=adjusted_threshold,
            applied_by="system"
        )

    def _analyze_trend(self, scores: List[float]) -> ConversationTrend:
        """Analyze trend in toxicity scores."""
        if len(scores) < 2:
            return ConversationTrend.NEUTRAL

        # Simple trend analysis
        recent_avg = sum(scores[-3:]) / min(3, len(scores))
        older_avg = sum(scores[:-3]) / max(1, len(scores) - 3) if len(scores) > 3 else scores[0]

        if recent_avg > older_avg + 0.1:
            return ConversationTrend.ESCALATING
        elif recent_avg < older_avg - 0.1:
            return ConversationTrend.DEESCALATING
        else:
            return ConversationTrend.NEUTRAL

    async def _log_moderation_decision(
        self,
        message_id: str,
        user_id: str,
        conversation_id: str,
        score: float,
        threshold: float,
        action: ModerationActionData,
        context_info: Dict[str, Any]
    ) -> None:
        """Log moderation decision for analytics."""
        try:
            log_entry = ModerationLog(
                log_id=f"log_{int(time.time() * 1000)}",
                message_id=message_id,
                user_id=user_id,
                conversation_id=conversation_id,
                action=action.action.value,
                original_score=score,
                adjusted_threshold=threshold,
                context_factors=context_info,
                timestamp=datetime.utcnow(),
                processing_time_ms=0  # Would be passed from caller
            )

            logs_collection = db_manager.async_db[COLLECTIONS["moderation_logs"]]
            await logs_collection.insert_one(log_entry.dict(by_alias=True))

        except Exception as e:
            # Log error but don't fail the moderation process
            print(f"Error logging moderation decision: {e}")

    async def get_moderation_statistics(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get moderation statistics for the specified period."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            logs_collection = db_manager.async_db[COLLECTIONS["moderation_logs"]]

            # Aggregate statistics
            pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": "$action",
                    "count": {"$sum": 1},
                    "avg_score": {"$avg": "$original_score"}
                }}
            ]

            results = await logs_collection.aggregate(pipeline).to_list(None)

            total_actions = sum(r["count"] for r in results)
            action_stats = {
                r["_id"]: {
                    "count": r["count"],
                    "percentage": (r["count"] / total_actions * 100) if total_actions > 0 else 0,
                    "avg_score": r["avg_score"]
                }
                for r in results
            }

            return {
                "period_days": days,
                "total_actions": total_actions,
                "action_breakdown": action_stats,
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {"error": str(e), "period_days": days}

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the moderation service."""
        health_info = {
            "status": "healthy",
            "components": {},
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            # Check toxicity detector
            toxicity_health = await toxicity_detector.health_check()
            health_info["components"]["toxicity_detector"] = toxicity_health

            # Check embedding service
            embedding_health = await embedding_service.health_check()
            health_info["components"]["embedding_service"] = embedding_health

            # Check database connection
            try:
                await db_manager.async_db.command('ping')
                health_info["components"]["database"] = {"status": "connected"}
            except Exception as e:
                health_info["components"]["database"] = {"status": "error", "error": str(e)}
                health_info["status"] = "degraded"

        except Exception as e:
            health_info["status"] = "unhealthy"
            health_info["error"] = str(e)

        return health_info


# Global moderation service instance
moderation_service = ModerationService()