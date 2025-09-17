# Redis Base Manager Module
# Extracted from app/core/redis.py (lines 42-96)

# ~/app/core/redis.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Redis Async Configuration
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: redis.py
# Ruta: ~/app/core/redis.py
# Autor: Jairo
# Fecha de Creación: 2025-07-17
# Última Actualización: 2025-07-17
# Versión: 1.0.0
# Propósito: Cliente Redis async para cache, sesiones y message queuing
#            Configuración singleton con pool de conexiones optimizado
#
# Modificaciones:
# 2025-07-17 - Implementación inicial con soporte async completo
#
# ---------------------------------------------------------------------------------------------

"""
Redis Async Configuration for MeStock

Provides async Redis client with connection pooling for:
- Application caching
- User sessions storage
- Message queuing system
- Rate limiting
"""

import logging
import os
from typing import Optional
from unittest.mock import MagicMock

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)



class RedisManager:
    """Redis connection manager with singleton pattern"""

    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._pool: Optional[redis.ConnectionPool] = None

    async def connect(self) -> redis.Redis:
        """Initialize Redis connection with pool"""
        if self._redis is None:
            # In testing mode, return a mock Redis instance
            if os.getenv('TESTING') == '1':
                logger.info("🧪 Using mock Redis for testing")
                mock_redis = MagicMock()
                # Mock common Redis methods that tests might use
                mock_redis.ping.return_value = True
                mock_redis.setex.return_value = True
                mock_redis.get.return_value = None
                mock_redis.delete.return_value = True
                mock_redis.exists.return_value = False
                mock_redis.close.return_value = None
                self._redis = mock_redis
                return self._redis

            try:
                # Create connection pool for better performance
                self._pool = redis.ConnectionPool.from_url(
                    settings.REDIS_URL,
                    max_connections=20,
                    retry_on_timeout=True,
                    decode_responses=True,
                    encoding="utf-8",
                )

                # Create Redis client with pool
                self._redis = redis.Redis(connection_pool=self._pool)

                # Test connection
                await self._redis.ping()
                logger.info("✅ Redis connection established successfully")

            except Exception as e:
                logger.error(f"❌ Redis connection failed: {e}")
                raise

        return self._redis

    async def disconnect(self):
        """Close Redis connection and pool"""
        if self._redis:
            await self._redis.close()
            self._redis = None

        if self._pool:
            await self._pool.disconnect()
            self._pool = None

        logger.info("🔌 Redis connection closed")

    async def get_redis(self) -> redis.Redis:
        """Get active Redis connection"""
        if self._redis is None:
            await self.connect()
        return self._redis


# === MANAGERS ESPECÍFICOS POR DATABASE ===

# Global Redis Manager instance
_redis_manager = RedisManager()


async def get_redis_manager() -> RedisManager:
    """
    Dependency function to get the Redis manager instance.

    Returns:
        RedisManager: The global Redis manager instance
    """
    return _redis_manager


async def get_redis() -> redis.Redis:
    """
    Dependency function to get Redis connection.

    Returns:
        redis.Redis: Active Redis connection
    """
    return await _redis_manager.get_redis()


async def get_redis_client() -> redis.Redis:
    """
    Alias for get_redis() for backwards compatibility.

    Returns:
        redis.Redis: Active Redis connection
    """
    return await _redis_manager.get_redis()


