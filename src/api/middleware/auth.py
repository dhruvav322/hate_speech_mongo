"""API Key Authentication Middleware"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Set
import secrets
import logging

from src.config.settings import settings

logger = logging.getLogger(__name__)

# API Key Header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyManager:
    """Manage API keys securely"""
    
    def __init__(self):
        # Load valid API keys from environment
        self._valid_keys = self._load_api_keys()
        logger.info(f"Loaded {len(self._valid_keys)} valid API key(s)")
    
    def _load_api_keys(self) -> Set[str]:
        """Load API keys from secure storage"""
        keys = set()
        
        # Primary API key
        if settings.api_key:
            keys.add(settings.api_key)
        
        # Support multiple keys (comma-separated)
        if settings.additional_api_keys:
            additional = settings.additional_api_keys.split(',')
            keys.update(key.strip() for key in additional if key.strip())
        
        if not keys:
            raise ValueError(
                "No API keys configured. Set API_KEY environment variable."
            )
        
        return keys
    
    def verify_key(self, api_key: str) -> bool:
        """
        Verify API key using constant-time comparison.
        
        Args:
            api_key: API key to verify
            
        Returns:
            True if valid, False otherwise
        """
        if not api_key:
            return False
        
        # Use secrets.compare_digest for timing attack prevention
        return any(
            secrets.compare_digest(api_key, valid_key) 
            for valid_key in self._valid_keys
        )
    
    def generate_key(self) -> str:
        """Generate a new secure API key"""
        return secrets.token_urlsafe(32)


# Global instance
api_key_manager = APIKeyManager()


async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Verify API key from request header.
    
    Args:
        api_key: API key from X-API-Key header
        
    Returns:
        Validated API key
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key:
        logger.warning("API request without API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if not api_key_manager.verify_key(api_key):
        logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key


# Public endpoints that don't need authentication
PUBLIC_ENDPOINTS = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
}


def is_public_endpoint(path: str) -> bool:
    """Check if endpoint is public"""
    return path in PUBLIC_ENDPOINTS

