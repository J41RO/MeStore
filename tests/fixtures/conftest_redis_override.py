import pytest
from unittest.mock import AsyncMock
from app.core.redis import RedisManager

@pytest.fixture(autouse=True)
async def mock_redis_for_testing(monkeypatch):
    """Mock Redis para tests sin autenticación"""
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1
    
    async def mock_get_redis():
        return mock_redis
    
    monkeypatch.setattr("app.core.redis.redis_manager.get_redis", mock_get_redis)
    return mock_redis
