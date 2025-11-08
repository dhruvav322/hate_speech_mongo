"""User data models for the hate speech moderation system."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field, EmailStr


class RiskLevel(str, Enum):
    """User risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ModerationSensitivity(str, Enum):
    """Moderation sensitivity preferences."""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


class ModerationHistory(BaseModel):
    """User moderation history statistics."""
    total_messages: int = Field(default=0)
    flagged_messages: int = Field(default=0)
    false_positives: int = Field(default=0)
    corrected_moderations: int = Field(default=0)


class BehaviorProfile(BaseModel):
    """User behavior profile and statistics."""
    average_toxicity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    message_frequency: int = Field(default=0)  # Messages per day
    moderation_history: ModerationHistory = Field(default_factory=ModerationHistory)
    risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)
    trust_score: float = Field(default=0.5, ge=0.0, le=1.0)


class NotificationSettings(BaseModel):
    """User notification preferences."""
    email_notifications: bool = Field(default=True)
    moderation_warnings: bool = Field(default=True)
    account_status_changes: bool = Field(default=True)


class UserPreferences(BaseModel):
    """User preferences and settings."""
    moderation_sensitivity: ModerationSensitivity = Field(default=ModerationSensitivity.MODERATE)
    notification_settings: NotificationSettings = Field(default_factory=NotificationSettings)


class UserBase(BaseModel):
    """Base user model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(...)


class UserCreate(UserBase):
    """Model for creating new users."""
    platform: str = Field(..., min_length=1, max_length=50)
    preferences: Optional[UserPreferences] = Field(default=None)


class UserUpdate(BaseModel):
    """Model for updating user information."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(None)
    preferences: Optional[UserPreferences] = Field(None)


class User(UserBase):
    """Complete user model."""
    user_id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    behavior_profile: BehaviorProfile = Field(default_factory=BehaviorProfile)
    preferences: UserPreferences = Field(default_factory=UserPreferences)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserInDB(User):
    """User model as stored in database."""
    pass


class UserStats(BaseModel):
    """User statistics for API responses."""
    messages_last_24h: int = Field(default=0)
    messages_last_7d: int = Field(default=0)
    most_active_hours: List[int] = Field(default_factory=list)
    average_response_time_ms: float = Field(default=0.0)


class UserPublic(BaseModel):
    """Public user information (safe to share)."""
    user_id: str
    username: str
    created_at: datetime
    behavior_profile: BehaviorProfile


class UserBehaviorUpdate(BaseModel):
    """Model for updating user behavior statistics."""
    message_toxicity_score: float = Field(..., ge=0.0, le=1.0)
    moderation_action_taken: str = Field(...)
    was_false_positive: bool = Field(default=False)
    response_time_ms: Optional[int] = Field(None)


class UserTrustAdjustment(BaseModel):
    """Model for adjusting user trust scores."""
    adjustment_amount: float = Field(..., ge=-1.0, le=1.0)
    reason: str = Field(..., min_length=1, max_length=200)
    moderator_notes: Optional[str] = Field(None)


class UserListResponse(BaseModel):
    """Response model for user lists."""
    users: List[UserPublic]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool