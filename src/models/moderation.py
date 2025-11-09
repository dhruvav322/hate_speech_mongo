"""Moderation and analytics data models."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class ModerationLog(BaseModel):
    """Log entry for moderation actions."""
    log_id: str = Field(..., alias="_id")
    message_id: str
    user_id: str
    conversation_id: str
    action: str
    original_score: float
    adjusted_threshold: float
    context_factors: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: int

    class Config:
        populate_by_name = True


class ModerationMetrics(BaseModel):
    """Moderation performance metrics."""
    total_messages: int
    flagged_messages: int
    false_positives: int
    false_negatives: int
    accuracy_rate: float
    precision: float
    recall: float
    f1_score: float
    avg_processing_time_ms: float


class FeedbackAppeal(BaseModel):
    """User appeal against moderation decision."""
    appeal_id: str = Field(..., alias="_id")
    message_id: str
    user_id: str
    original_action: str
    appeal_reason: str
    user_explanation: str
    status: str
    reviewer_id: Optional[str] = None
    review_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class ModeratorReview(BaseModel):
    """Moderator review of automated decision."""
    review_id: str = Field(..., alias="_id")
    message_id: str
    reviewer_id: str
    original_action: str
    final_action: str
    review_notes: str
    confidence_score: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class AnalyticsOverview(BaseModel):
    """System-wide analytics overview."""
    total_messages: int
    messages_last_24h: int
    messages_last_7d: int
    flagged_rate: float
    false_positive_rate: float
    active_users: int
    active_conversations: int


class ToxicityCategoryStats(BaseModel):
    """Statistics for toxicity categories."""
    category: str
    count: int
    percentage: float
    avg_score: float


class UserRiskDistribution(BaseModel):
    """Distribution of users by risk level."""
    low: int
    medium: int
    high: int


class PerformanceMetrics(BaseModel):
    """System performance metrics."""
    avg_processing_time_ms: float
    api_uptime: float
    model_accuracy: float
    memory_usage_mb: float
    cpu_usage_percent: float


class AnalyticsDashboard(BaseModel):
    """Complete analytics dashboard data."""
    overview: AnalyticsOverview
    top_toxicity_categories: List[ToxicityCategoryStats]
    user_risk_distribution: UserRiskDistribution
    performance_metrics: PerformanceMetrics
    recent_trends: Dict[str, List[float]]


class SystemHealth(BaseModel):
    """System health check response."""
    status: str
    version: str
    models_loaded: List[str]
    database_connection: str
    memory_usage_mb: float
    uptime_seconds: int
    last_error: Optional[str] = None


class ContextEmbedding(BaseModel):
    """Context embedding model."""
    embedding_id: str = Field(..., alias="_id")
    conversation_id: str
    message_window: List[str]
    embedding_vector: List[float]
    embedding_model: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    context_type: str

    class Config:
        populate_by_name = True


class LearningUpdate(BaseModel):
    """Model for learning system updates."""
    update_id: str = Field(..., alias="_id")
    update_type: str
    parameters: Dict[str, Any]
    performance_impact: Dict[str, float]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    applied: bool = False

    class Config:
        populate_by_name = True