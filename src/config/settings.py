"""Configuration management for the hate speech moderation system."""

import os
from typing import Optional, List

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Database
    mongodb_url: str = Field(default="mongodb://localhost:27017", env="MONGODB_URL")
    mongodb_db_name: str = Field(default="hate_speech_mitigation", env="MONGODB_DB_NAME")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_secret_key: str = Field(default="your-secret-key-here", env="API_SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # API Key Authentication (REQUIRED in production)
    api_key: str = Field(..., env="API_KEY")
    additional_api_keys: Optional[str] = Field(None, env="ADDITIONAL_API_KEYS")
    
    # CORS Configuration
    allowed_origins: str = Field(
        default="http://localhost:3000",
        env="ALLOWED_ORIGINS"
    )
    
    @validator('api_key')
    def validate_api_key(cls, v, values):
        """Ensure API key is secure in production"""
        environment = values.get('environment', 'development')
        
        if not v:
            raise ValueError("API_KEY is required")
        
        # Prevent weak keys in production
        if environment == "production":
            if v in ["your-secret-key-here", "industry-demo-key-12345", "test-key"]:
                raise ValueError("Default/demo API key not allowed in production!")
            
            if len(v) < 32:
                raise ValueError("Production API key must be at least 32 characters")
        
        return v
    
    @validator('allowed_origins', pre=True)
    def parse_origins(cls, v):
        """Parse comma-separated origins"""
        if isinstance(v, str):
            return v
        return ",".join(v) if isinstance(v, list) else v
    
    def get_allowed_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.allowed_origins.split(',')]

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
    
    # Request Limits
    max_request_size: int = Field(default=1_000_000, env="MAX_REQUEST_SIZE")  # 1MB

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