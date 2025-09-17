# Redis Session Manager Module
# Extracted from app/core/redis.py (lines 119-140)

import os
import redis
from unittest.mock import MagicMock
from app.core.config import settings
from app.core.logger import logger
from .base import RedisManager

class RedisSessionManager(RedisManager):
    """Redis manager específico para sesiones (DB 1)"""

    async def connect(self) -> redis.Redis:
        if self._redis is None:
            # In testing mode, return a mock Redis instance
            if os.getenv('TESTING') == '1':
                logger.info("🧪 Using mock Redis Sessions for testing")
                mock_redis = MagicMock()
                # Mock common Redis methods that tests might use
                mock_redis.ping.return_value = True
                mock_redis.setex.return_value = True
                mock_redis.get.return_value = None
                mock_redis.delete.return_value = True
                mock_redis.exists.return_value = False
                self._redis = mock_redis
                return self._redis

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


