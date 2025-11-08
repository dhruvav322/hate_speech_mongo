"""Configuration management for the hate speech moderation system."""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    mongodb_url: str = Field(default="mongodb://localhost:27017", env="MONGODB_URL")
    mongodb_db_name: str = Field(default="hate_speech_mitigation", env="MONGODB_DB_NAME")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_secret_key: str = Field(default="your-secret-key-here", env="API_SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Model Configuration
    detoxify_model: str = Field(default="original", env="DETOXIFY_MODEL")
    sentence_transformer_model: str = Field(default="all-MiniLM-L6-v2", env="SENTENCE_TRANSFORMER_MODEL")
    embedding_dimension: int = Field(default=384, env="EMBEDDING_DIMENSION")

    # Moderation Settings
    default_toxicity_threshold: float = Field(default=0.5, env="DEFAULT_TOXICITY_THRESHOLD")
    context_window_size: int = Field(default=5, env="CONTEXT_WINDOW_SIZE")
    user_history_limit: int = Field(default=50, env="USER_HISTORY_LIMIT")
    batch_size: int = Field(default=32, env="BATCH_SIZE")

    # Monitoring
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")

    # Performance
    max_concurrent_requests: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Moderation thresholds configuration
MODERATION_THRESHOLDS = {
    "allow": 0.3,
    "warn": 0.6,
    "hide": 0.8,
    "delete": 0.95,
    "ban": 1.0,
}

# User risk level multipliers
USER_RISK_MULTIPLIERS = {
    "low": 0.8,    # More lenient for trusted users
    "medium": 1.0,  # Standard moderation
    "high": 1.2,    # Stricter moderation for risky users
}

# Toxicity category weights
TOXICITY_WEIGHTS = {
    "toxic": 1.0,
    "severe_toxic": 2.0,
    "obscene": 1.5,
    "threat": 2.5,
    "insult": 1.2,
    "identity_hate": 3.0,
}