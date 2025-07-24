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
from typing import Optional

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


