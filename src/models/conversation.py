"""Conversation data models for the hate speech moderation system."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class ModerationLevel(str, Enum):
    """Conversation moderation levels."""
    NONE = "none"
    BASIC = "basic"
    STRICT = "strict"


class ConversationStatus(str, Enum):
    """Conversation status enumeration."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    MODERATED = "moderated"


class ConversationTrend(str, Enum):
    """Conversation trend analysis."""
    NEUTRAL = "neutral"
    ESCALATING = "escalating"
    DEESCALATING = "deescalating"


class ConversationMetadata(BaseModel):
    """Conversation metadata and context."""
    topic: Optional[str] = Field(None, max_length=100)
    language: str = Field(default="en", max_length=10)
    platform: str = Field(..., max_length=50)
    moderation_level: ModerationLevel = Field(default=ModerationLevel.BASIC)


class ConversationBase(BaseModel):
    """Base conversation model."""
    participants: List[str] = Field(..., min_items=1)
    metadata: ConversationMetadata = Field(...)


class ConversationCreate(ConversationBase):
    """Model for creating new conversations."""
    pass


class ConversationUpdate(BaseModel):
    """Model for updating conversations."""
    participants: Optional[List[str]] = Field(None, min_items=1)
    metadata: Optional[ConversationMetadata] = Field(None)
    status: Optional[ConversationStatus] = Field(None)


class Conversation(ConversationBase):
    """Complete conversation model."""
    conversation_id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    context_embedding: Optional[List[float]] = Field(None)
    status: ConversationStatus = Field(default=ConversationStatus.ACTIVE)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationInDB(Conversation):
    """Conversation model as stored in database."""
    pass


class MessageSummary(BaseModel):
    """Summary of a message for context."""
    message_id: str
    text: str = Field(..., max_length=200)  # Truncated for context
    toxicity_score: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime


class ConversationContext(BaseModel):
    """Conversation context for moderation."""
    conversation_id: str
    context_embedding: List[float]
    recent_messages: List[MessageSummary]
    conversation_trend: ConversationTrend
    average_toxicity: float = Field(..., ge=0.0, le=1.0)
    message_count: int = Field(..., ge=0)
    participant_count: int = Field(..., ge=1)


class ConversationStats(BaseModel):
    """Conversation statistics."""
    total_messages: int = Field(default=0)
    average_toxicity: float = Field(default=0.0)
    flagged_messages: int = Field(default=0)
    unique_participants: int = Field(default=0)
    duration_minutes: int = Field(default=0)
    peak_activity_hour: Optional[int] = Field(None)


class ConversationAnalytics(BaseModel):
    """Detailed conversation analytics."""
    conversation_id: str
    stats: ConversationStats
    toxicity_over_time: List[Dict[str, Any]]
    participant_activity: Dict[str, int]
    topic_keywords: List[str]
    moderation_actions: List[Dict[str, Any]]


class ConversationListResponse(BaseModel):
    """Response model for conversation lists."""
    conversations: List[Conversation]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool


class ConversationSearchFilters(BaseModel):
    """Filters for conversation search."""
    platform: Optional[str] = Field(None)
    language: Optional[str] = Field(None)
    moderation_level: Optional[ModerationLevel] = Field(None)
    status: Optional[ConversationStatus] = Field(None)
    participant_id: Optional[str] = Field(None)
    created_after: Optional[datetime] = Field(None)
    created_before: Optional[datetime] = Field(None)
    min_toxicity: Optional[float] = Field(None, ge=0.0)
    max_toxicity: Optional[float] = Field(None, le=1.0)