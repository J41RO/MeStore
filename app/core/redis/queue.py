# Redis Queue Manager Module
# Extracted from app/core/redis.py (lines 141-160)

import redis
from app.core.config import settings
from app.core.logger import logger
from .base import RedisManager

class RedisQueueManager(RedisManager):
    """Redis manager específico para message queues (DB 2)"""

    async def connect(self) -> redis.Redis:
        if self._redis is None:
            try:
                self._pool = redis.ConnectionPool.from_url(
                    settings.REDIS_QUEUE_URL,
                    max_connections=15,  # Más conexiones para queues
                    retry_on_timeout=True,
                    decode_responses=True,
                    encoding="utf-8",
                )
                self._redis = redis.Redis(connection_pool=self._pool)
                await self._redis.ping()
                logger.info("✅ Redis Queues (DB 2) connection established")
            except Exception as e:
                logger.error(f"❌ Redis Queues connection failed: {e}")
                raise
        return self._redis
