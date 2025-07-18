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


class RedisCacheManager(RedisManager):
    """Redis manager específico para cache (DB 0)"""

    async def connect(self) -> redis.Redis:
        if self._redis is None:
            try:
                self._pool = redis.ConnectionPool.from_url(
                    settings.REDIS_CACHE_URL,
                    max_connections=10,
                    retry_on_timeout=True,
                    decode_responses=True,
                    encoding="utf-8",
                )
                self._redis = redis.Redis(connection_pool=self._pool)
                await self._redis.ping()
                logger.info("✅ Redis Cache (DB 0) connection established")
            except Exception as e:
                logger.error(f"❌ Redis Cache connection failed: {e}")
                raise
        return self._redis


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


# === INSTANCIAS GLOBALES ===
redis_manager = RedisManager()
cache_manager = RedisCacheManager()
session_manager = RedisSessionManager()
queue_manager = RedisQueueManager()

# === DEPENDENCIES GENERALES ===


async def get_redis() -> redis.Redis:
    """
    FastAPI dependency for Redis client

    Usage in endpoints:
        @app.get("/endpoint")
        async def endpoint(redis_client = Depends(get_redis)):
            await redis_client.set("key", "value")
    """
    return await redis_manager.get_redis()


# === DEPENDENCIES ESPECÍFICAS POR DATABASE ===


async def get_redis_cache() -> redis.Redis:
    """
    FastAPI dependency para Redis Cache (DB 0)

    Usage:
        @app.get("/endpoint")
        async def endpoint(cache = Depends(get_redis_cache)):
            await cache.set("key", "value")
    """
    return await cache_manager.get_redis()


async def get_redis_sessions() -> redis.Redis:
    """
    FastAPI dependency para Redis Sessions (DB 1)

    Usage:
        @app.post("/login")
        async def login(sessions = Depends(get_redis_sessions)):
            await sessions.setex("session:uuid", 3600, user_data)
    """
    return await session_manager.get_redis()


async def get_redis_queues() -> redis.Redis:
    """
    FastAPI dependency para Redis Queues (DB 2)

    Usage:
        @app.post("/task")
        async def create_task(queues = Depends(get_redis_queues)):
            await queues.xadd("task_queue", {"data": task_data})
    """
    return await queue_manager.get_redis()


# === REDIS SERVICE ===


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
