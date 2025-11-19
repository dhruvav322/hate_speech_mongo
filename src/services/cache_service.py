"""Redis-based caching service for improved performance and scalability."""

import json
import hashlib
from typing import Optional, Any, Dict
from datetime import timedelta

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from src.config.settings import settings

logger = None
try:
    import logging
    logger = logging.getLogger(__name__)
except:
    pass


class CacheService:
    """Redis-based caching service with fallback to in-memory cache."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.use_redis = False
        
    async def connect(self) -> None:
        """Initialize Redis connection if available."""
        if not REDIS_AVAILABLE:
            if logger:
                logger.warning("Redis not available, using in-memory cache")
            return
            
        if settings.redis_url:
            try:
                self.redis_client = await redis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=50
                )
                # Test connection
                await self.redis_client.ping()
                self.use_redis = True
                if logger:
                    logger.info("✅ Redis cache connected")
            except Exception as e:
                if logger:
                    logger.warning(f"Redis connection failed, using in-memory cache: {e}")
                self.use_redis = False
        else:
            if logger:
                logger.info("Redis URL not configured, using in-memory cache")
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    def _generate_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments."""
        key_parts = [prefix] + [str(arg) for arg in args]
        key_string = ":".join(key_parts)
        # Hash long keys to keep them manageable
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:hash:{key_hash}"
        return key_string
    
    async def get(self, prefix: str, *args) -> Optional[Any]:
        """Get value from cache."""
        key = self._generate_key(prefix, *args)
        
        if self.use_redis and self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                if logger:
                    logger.error(f"Redis get error: {e}")
        else:
            # Fallback to memory cache
            if key in self.memory_cache:
                cached = self.memory_cache[key]
                # Check TTL (simple implementation)
                import time
                if time.time() - cached.get("timestamp", 0) < cached.get("ttl", 3600):
                    return cached["value"]
                else:
                    del self.memory_cache[key]
        
        return None
    
    async def set(self, prefix: str, value: Any, ttl_seconds: int = 3600, *args) -> bool:
        """Set value in cache with TTL."""
        key = self._generate_key(prefix, *args)
        
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.setex(
                    key,
                    ttl_seconds,
                    json.dumps(value, default=str)
                )
                return True
            except Exception as e:
                if logger:
                    logger.error(f"Redis set error: {e}")
                return False
        else:
            # Fallback to memory cache
            import time
            self.memory_cache[key] = {
                "value": value,
                "timestamp": time.time(),
                "ttl": ttl_seconds
            }
            # Limit memory cache size
            if len(self.memory_cache) > 1000:
                # Remove oldest entries
                sorted_items = sorted(
                    self.memory_cache.items(),
                    key=lambda x: x[1].get("timestamp", 0)
                )
                for old_key, _ in sorted_items[:100]:
                    del self.memory_cache[old_key]
            return True
    
    async def delete(self, prefix: str, *args) -> bool:
        """Delete value from cache."""
        key = self._generate_key(prefix, *args)
        
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.delete(key)
                return True
            except Exception as e:
                if logger:
                    logger.error(f"Redis delete error: {e}")
                return False
        else:
            if key in self.memory_cache:
                del self.memory_cache[key]
            return True
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if self.use_redis and self.redis_client:
            try:
                keys = []
                async for key in self.redis_client.scan_iter(match=pattern):
                    keys.append(key)
                if keys:
                    return await self.redis_client.delete(*keys)
                return 0
            except Exception as e:
                if logger:
                    logger.error(f"Redis clear pattern error: {e}")
                return 0
        else:
            # Memory cache pattern matching
            count = 0
            keys_to_delete = [k for k in self.memory_cache.keys() if pattern.replace("*", "") in k]
            for key in keys_to_delete:
                del self.memory_cache[key]
                count += 1
            return count
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if self.use_redis and self.redis_client:
            try:
                info = await self.redis_client.info("stats")
                return {
                    "type": "redis",
                    "keys": await self.redis_client.dbsize(),
                    "hits": info.get("keyspace_hits", 0),
                    "misses": info.get("keyspace_misses", 0),
                }
            except:
                pass
        
        return {
            "type": "memory",
            "keys": len(self.memory_cache),
            "hits": 0,
            "misses": 0,
        }


# Global cache service instance
cache_service = CacheService()

