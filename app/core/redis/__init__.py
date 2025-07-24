"""
Redis Module - Modular Architecture
Maintains backward compatibility with existing imports
"""

# Import all classes from modules
from .base import RedisManager
from .cache import RedisCacheManager
from .session import RedisSessionManager
from .queue import RedisQueueManager
from .service import RedisService

# Import all dependencies and instances
from .dependencies import (
    redis_manager,
    cache_manager, 
    session_manager,
    queue_manager,
    get_redis,
    get_redis_cache,
    get_redis_sessions,
    get_redis_queues,
    get_redis_service
)

# Export everything for backward compatibility
__all__ = [
    # Classes
    "RedisManager",
    "RedisCacheManager", 
    "RedisSessionManager",
    "RedisQueueManager",
    "RedisService",
    # Instances
    "redis_manager",
    "cache_manager",
    "session_manager", 
    "queue_manager",
    # Dependencies
    "get_redis",
    "get_redis_cache",
    "get_redis_sessions",
    "get_redis_queues",
    "get_redis_service"
]
