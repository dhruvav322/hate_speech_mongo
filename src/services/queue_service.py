"""Message queue service for background task processing."""

import asyncio
from typing import Callable, Any, Dict, Optional
from datetime import datetime
import json

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


class QueueService:
    """Simple Redis-based queue service for background tasks."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.use_redis = False
        self.task_registry: Dict[str, Callable] = {}
        self.is_processing = False
        
    async def connect(self) -> None:
        """Initialize Redis connection."""
        if not REDIS_AVAILABLE:
            if logger:
                logger.warning("Redis not available, queue will use in-memory fallback")
            return
            
        if settings.redis_url:
            try:
                self.redis_client = await redis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self.redis_client.ping()
                self.use_redis = True
                if logger:
                    logger.info("✅ Queue service connected to Redis")
            except Exception as e:
                if logger:
                    logger.warning(f"Redis queue connection failed: {e}")
                self.use_redis = False
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    async def enqueue(self, queue_name: str, task_name: str, *args, **kwargs) -> str:
        """Add task to queue."""
        task_id = f"{task_name}_{datetime.utcnow().timestamp()}"
        task_data = {
            "task_id": task_id,
            "task_name": task_name,
            "args": args,
            "kwargs": kwargs,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.lpush(
                    f"queue:{queue_name}",
                    json.dumps(task_data, default=str)
                )
                return task_id
            except Exception as e:
                if logger:
                    logger.error(f"Failed to enqueue task: {e}")
                # Fallback to immediate execution
                await self._execute_task(task_name, *args, **kwargs)
                return task_id
        else:
            # Fallback: execute immediately
            if logger:
                logger.warning("Queue not available, executing task immediately")
            await self._execute_task(task_name, *args, **kwargs)
            return task_id
    
    async def _execute_task(self, task_name: str, *args, **kwargs) -> None:
        """Execute a task function."""
        if task_name in self.task_registry:
            try:
                task_func = self.task_registry[task_name]
                if asyncio.iscoroutinefunction(task_func):
                    await task_func(*args, **kwargs)
                else:
                    task_func(*args, **kwargs)
            except Exception as e:
                if logger:
                    logger.error(f"Task execution failed: {e}")
    
    def register_task(self, task_name: str, task_func: Callable) -> None:
        """Register a task function."""
        self.task_registry[task_name] = task_func
    
    async def process_queue(self, queue_name: str, max_tasks: int = 10) -> int:
        """Process tasks from queue (for worker processes)."""
        if not self.use_redis or not self.redis_client:
            return 0
        
        processed = 0
        try:
            for _ in range(max_tasks):
                # Blocking pop with timeout
                result = await self.redis_client.brpop(
                    f"queue:{queue_name}",
                    timeout=1
                )
                
                if result:
                    _, task_json = result
                    task_data = json.loads(task_json)
                    await self._execute_task(
                        task_data["task_name"],
                        *task_data.get("args", []),
                        **task_data.get("kwargs", {})
                    )
                    processed += 1
                else:
                    break
        except Exception as e:
            if logger:
                logger.error(f"Queue processing error: {e}")
        
        return processed


# Global queue service instance
queue_service = QueueService()

