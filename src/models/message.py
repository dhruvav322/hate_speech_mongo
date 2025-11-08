"""Message data models for the hate speech moderation system."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field, validator


class ModerationAction(str, Enum):
    """Moderation action types."""
    NONE = "none"
    WARN = "warn"
    HIDE = "hide"
    DELETE = "delete"
    BAN = "ban"


class AppealStatus(str, Enum):
    """Appeal status enumeration."""
    NONE = "none"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AppliedBy(str, Enum):
    """Who applied the moderation action."""
    SYSTEM = "system"
    HUMAN = "human"


class MessageType(str, Enum):
    """Message types."""
    CHAT = "chat"
    COMMENT = "comment"
    POST = "post"


class ToxicityPredictions(BaseModel):
    """Toxicity predictions from the model."""
    toxic: float = Field(..., ge=0.0, le=1.0)
    severe_toxic: float = Field(..., ge=0.0, le=1.0)
    obscene: float = Field(..., ge=0.0, le=1.0)
    threat: float = Field(..., ge=0.0, le=1.0)
    insult: float = Field(..., ge=0.0, le=1.0)
    identity_hate: float = Field(..., ge=0.0, le=1.0)


class ToxicityAnalysis(BaseModel):
    """Complete toxicity analysis results."""
    overall_score: float = Field(..., ge=0.0, le=1.0)
    predictions: ToxicityPredictions = Field(...)
    confidence: float = Field(..., ge=0.0, le=1.0)
    processing_time_ms: int = Field(..., ge=0)


class ModerationActionData(BaseModel):
    """Moderation action details."""
    action: ModerationAction = Field(...)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str = Field(..., min_length=1, max_length=500)
    adjusted_threshold: float = Field(..., ge=0.0, le=1.0)
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    applied_by: AppliedBy = Field(default=AppliedBy.SYSTEM)


class Feedback(BaseModel):
    """User and community feedback on messages."""
    user_reported: bool = Field(default=False)
    community_flags: int = Field(default=0, ge=0)
    moderator_review: Optional[Dict[str, Any]] = Field(None)
    appeal_status: AppealStatus = Field(default=AppealStatus.NONE)


class MessageContext(BaseModel):
    """Message context information."""
    platform: str = Field(..., max_length=50)
    language: str = Field(default="en", max_length=10)
    message_type: MessageType = Field(default=MessageType.CHAT)
    reply_to_message_id: Optional[str] = Field(None)
    quoted_content: Optional[str] = Field(None, max_length=500)


class MessageBase(BaseModel):
    """Base message model."""
    content: str = Field(..., min_length=1, max_length=10000)
    conversation_id: str = Field(...)
    user_id: str = Field(...)
    context: Optional[MessageContext] = Field(None)


class MessageCreate(MessageBase):
    """Model for creating new messages."""
    pass


class Message(MessageBase):
    """Complete message model."""
    message_id: str = Field(..., alias="_id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    text_embedding: Optional[List[float]] = Field(None)
    toxicity_analysis: Optional[ToxicityAnalysis] = Field(None)
    moderation_action: Optional[ModerationActionData] = Field(None)
    feedback: Feedback = Field(default_factory=Feedback)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @validator('content')
    def validate_content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty or whitespace only')
        return v.strip()


class MessageInDB(Message):
    """Message model as stored in database."""
    pass


class ModerationRequest(BaseModel):
    """Request model for message moderation."""
    text: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = Field(None)
    user_id: Optional[str] = Field(None)
    context: Optional[MessageContext] = Field(None)


class ModerationResponse(BaseModel):
    """Response model for message moderation."""
    message_id: str
    toxicity_scores: ToxicityPredictions
    overall_score: float
    moderation_action: ModerationActionData
    context_analysis: Dict[str, Any]
    processing_time_ms: int
    timestamp: datetime


class BatchModerationRequest(BaseModel):
    """Request model for batch message moderation."""
    messages: List[MessageCreate] = Field(..., min_items=1, max_items=100)
    priority: str = Field(default="normal", regex="^(low|normal|high)$")


class BatchModerationResponse(BaseModel):
    """Response model for batch message moderation."""
    results: List[ModerationResponse]
    total_processed: int
    processing_time_ms: int
    batch_id: str


class MessageUpdate(BaseModel):
    """Model for updating messages."""
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    moderation_action: Optional[ModerationActionData] = Field(None)
    feedback: Optional[Feedback] = Field(None)


class MessageListResponse(BaseModel):
    """Response model for message lists."""
    messages: List[Message]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool


class MessageSearchFilters(BaseModel):
    """Filters for message search."""
    conversation_id: Optional[str] = Field(None)
    user_id: Optional[str] = Field(None)
    min_toxicity: Optional[float] = Field(None, ge=0.0)
    max_toxicity: Optional[float] = Field(None, le=1.0)
    moderation_action: Optional[ModerationAction] = Field(None)
    message_type: Optional[MessageType] = Field(None)
    created_after: Optional[datetime] = Field(None)
    created_before: Optional[datetime] = Field(None)
    has_appeal: Optional[bool] = Field(None)