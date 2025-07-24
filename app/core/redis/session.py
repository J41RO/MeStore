# Redis Session Manager Module
# Extracted from app/core/redis.py (lines 119-140)

import redis
from app.core.config import settings
from app.core.logger import logger
from .base import RedisManager

class RedisSessionManager(RedisManager):
    """Redis manager específico para sesiones (DB 1)"""

    async def connect(self) -> redis.Redis:
        if self._redis is None:
            try:
                self._pool = redis.ConnectionPool.from_url(
                    settings.REDIS_SESSION_URL,
                    max_connections=10,
                    retry_on_timeout=True,
                    decode_responses=True,
                    encoding="utf-8",
                )
                self._redis = redis.Redis(connection_pool=self._pool)
                await self._redis.ping()
                logger.info("✅ Redis Sessions (DB 1) connection established")
            except Exception as e:
                logger.error(f"❌ Redis Sessions connection failed: {e}")
                raise
        return self._redis


