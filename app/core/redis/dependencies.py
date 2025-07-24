# Redis Dependencies Module
# Extracted from app/core/redis.py (lines 162-225)

import redis

# Import managers from modules
from .base import RedisManager
from .cache import RedisCacheManager
from .session import RedisSessionManager
from .queue import RedisQueueManager


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



# Import RedisService for dependency
from .service import RedisService

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
