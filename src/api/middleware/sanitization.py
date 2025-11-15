"""Input Sanitization Middleware"""

import re
from fastapi import HTTPException
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Sanitize user input to prevent injection attacks"""
    
    # Dangerous patterns for NoSQL injection
    NOSQL_INJECTION_PATTERNS = [
        r'\$where',
        r'\$regex',
        r'\$gt',
        r'\$lt',
        r'\$ne',
        r'\$or',
        r'\$and',
        r'\$nin',
        r'\$in',
        r'javascript:',
        r'<script',
        r'\.\.',  # Path traversal
    ]
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 10000, field_name: str = "text") -> str:
        """
        Sanitize text input.
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            field_name: Name of field for error messages
            
        Returns:
            Sanitized text
            
        Raises:
            HTTPException: If input is invalid
        """
        if not isinstance(text, str):
            raise HTTPException(400, f"{field_name} must be a string")
        
        # Check length
        if len(text) > max_length:
            raise HTTPException(
                400,
                f"{field_name} exceeds maximum length of {max_length} characters"
            )
        
        # Check for NoSQL injection patterns
        text_lower = text.lower()
        for pattern in InputSanitizer.NOSQL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Blocked potentially dangerous input pattern: {pattern}")
                raise HTTPException(
                    400,
                    f"{field_name} contains potentially dangerous patterns"
                )
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if char == '\n' or char == '\t' or ord(char) >= 32)
        
        return text.strip()
    
    @staticmethod
    def sanitize_identifier(identifier: str, field_name: str = "identifier", max_length: int = 100) -> str:
        """
        Sanitize user ID, conversation ID, etc.
        
        Args:
            identifier: Identifier to sanitize
            field_name: Name of field for error messages
            max_length: Maximum length
            
        Returns:
            Sanitized identifier
            
        Raises:
            HTTPException: If identifier is invalid
        """
        if not identifier or not isinstance(identifier, str):
            raise HTTPException(400, f"Invalid {field_name}")
        
        # Only allow alphanumeric, underscore, hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', identifier):
            raise HTTPException(
                400,
                f"{field_name} can only contain letters, numbers, underscore, and hyphen"
            )
        
        if len(identifier) > max_length:
            raise HTTPException(400, f"{field_name} too long (max {max_length} characters)")
        
        return identifier
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], max_depth: int = 5, current_depth: int = 0) -> Dict[str, Any]:
        """
        Recursively sanitize dictionary.
        
        Args:
            data: Dictionary to sanitize
            max_depth: Maximum nesting depth
            current_depth: Current nesting level
            
        Returns:
            Sanitized dictionary
            
        Raises:
            HTTPException: If data is invalid
        """
        if current_depth > max_depth:
            raise HTTPException(400, "Data structure too deeply nested")
        
        sanitized = {}
        for key, value in data.items():
            # Sanitize keys
            if not isinstance(key, str) or not re.match(r'^[a-zA-Z0-9_]+$', key):
                raise HTTPException(400, f"Invalid key: {key}")
            
            # Sanitize values
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_text(value, field_name=key)
            elif isinstance(value, dict):
                sanitized[key] = InputSanitizer.sanitize_dict(
                    value, max_depth, current_depth + 1
                )
            elif isinstance(value, list):
                sanitized[key] = [
                    InputSanitizer.sanitize_text(item, field_name=f"{key}[{i}]") 
                    if isinstance(item, str) else item
                    for i, item in enumerate(value)
                ]
            else:
                sanitized[key] = value
        
        return sanitized

