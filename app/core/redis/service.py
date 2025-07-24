# Redis Service Class Module
# Extracted from app/core/redis.py (lines 226-end)

import redis
from typing import Optional, Dict, List, Any
from app.core.logger import logger

class RedisService:
    """High-level Redis operations for application use"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    # === CACHE OPERATIONS ===
    async def cache_set(self, key: str, value: str, expire: int = 3600) -> bool:
        """Set cache value with expiration (default 1 hour)"""
        try:
            return await self.redis.setex(key, expire, value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def cache_get(self, key: str) -> Optional[str]:
        """Get cache value"""
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def cache_delete(self, key: str) -> bool:
        """Delete cache key"""
        try:
            return bool(await self.redis.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    # === SESSION OPERATIONS ===
    async def session_set(
        self, session_id: str, data: dict, expire: int = 86400
    ) -> bool:
        """Store session data (default 24 hours)"""
        try:
            import json

            session_key = f"session:{session_id}"
            return await self.redis.setex(session_key, expire, json.dumps(data))
        except Exception as e:
            logger.error(f"Session set error: {e}")
            return False

    async def session_get(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        try:
            import json

            session_key = f"session:{session_id}"
            data = await self.redis.get(session_key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Session get error: {e}")
            return None

    async def session_delete(self, session_id: str) -> bool:
        """Delete session"""
        try:
            session_key = f"session:{session_id}"
            return bool(await self.redis.delete(session_key))
        except Exception as e:
            logger.error(f"Session delete error: {e}")
            return False

    # === MESSAGE QUEUE OPERATIONS ===
    async def queue_push(self, queue_name: str, message: dict) -> bool:
        """Push message to queue using Redis Streams"""
        try:
            import json

            stream_key = f"queue:{queue_name}"
            message_id = await self.redis.xadd(
                stream_key, {"data": json.dumps(message)}
            )
            return bool(message_id)
        except Exception as e:
            logger.error(f"Queue push error: {e}")
            return False

    async def queue_pop(
        self,
        queue_name: str,
        consumer_group: str = "workers",
        consumer_name: str = "worker-1",
        count: int = 1,
    ) -> list:
        """Pop messages from queue using Redis Streams"""
        try:
            import json

            stream_key = f"queue:{queue_name}"

            # Ensure consumer group exists
            try:
                await self.redis.xgroup_create(
                    stream_key, consumer_group, id="0", mkstream=True
                )
            except Exception:
                pass  # Group already exists

            # Read messages
            messages = await self.redis.xreadgroup(
                consumer_group,
                consumer_name,
                {stream_key: ">"},
                count=count,
                block=1000,
            )

            result = []
            for stream, msgs in messages:
                for msg_id, fields in msgs:
                    data = json.loads(fields["data"])
                    result.append({"id": msg_id, "data": data})

            return result
        except Exception as e:
            logger.error(f"Queue pop error: {e}")
            return []


async def get_redis_service() -> RedisService:
    """
    FastAPI dependency for Redis service

    Usage in endpoints:
        @app.get("/endpoint")
        async def endpoint(redis_svc = Depends(get_redis_service)):
            await redis_svc.cache_set("key", "value")
    """
    redis_client = await get_redis()
    return RedisService(redis_client)
