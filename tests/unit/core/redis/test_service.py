"""
TDD Test Suite for Redis Service
===============================

Comprehensive Test-Driven Development suite for app.core.redis.service.py
Following strict RED-GREEN-REFACTOR methodology.
Target: Improve coverage from 19% to 95%+

Test Coverage:
- RedisService: Initialization, cache operations, session management, queue operations
- Cache operations: set, get, delete with error handling
- Session operations: set, get, delete with JSON serialization
- Message queue operations: push, pop with Redis Streams
- Dependency injection: get_redis_service function
- Error handling and resilience for all operations
- Performance characteristics and optimization

Redis Service Testing Focus:
- High-level service layer operations
- JSON serialization/deserialization
- Error handling and logging
- Redis Streams for message queuing
- Session management with expiration
- Cache operations with TTL
- Dependency injection patterns
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Optional, Dict, List, Any

# Import the modules we're testing
from app.core.redis.service import RedisService, get_redis_service
import redis.asyncio as redis


# ========================================
# TEST FIXTURES AND HELPERS
# ========================================

@pytest.fixture
def mock_redis_client():
    """Mock Redis client with all required methods"""
    client = AsyncMock()
    client.setex = AsyncMock(return_value=True)
    client.get = AsyncMock(return_value=None)
    client.delete = AsyncMock(return_value=1)
    client.xadd = AsyncMock(return_value="1234567890-0")
    client.xgroup_create = AsyncMock(return_value=True)
    client.xreadgroup = AsyncMock(return_value=[])
    client.ping = AsyncMock(return_value=True)
    return client


@pytest.fixture
def redis_service(mock_redis_client):
    """Create RedisService instance with mock client"""
    return RedisService(mock_redis_client)


@pytest.fixture
def sample_cache_data():
    """Sample cache data for testing"""
    return {
        "key": "test_key",
        "value": "test_value",
        "expire": 3600
    }


@pytest.fixture
def sample_session_data():
    """Sample session data for testing"""
    return {
        "session_id": "test_session_123",
        "data": {
            "user_id": "user_456",
            "email": "test@example.com",
            "role": "user"
        },
        "expire": 86400
    }


@pytest.fixture
def sample_queue_data():
    """Sample queue data for testing"""
    return {
        "queue_name": "test_queue",
        "message": {
            "type": "task",
            "payload": {"data": "test"},
            "timestamp": "2025-09-22T12:00:00Z"
        }
    }


# ========================================
# RED PHASE TESTS - RedisService Initialization
# ========================================

class TestRedisServiceInitialization:
    """RED Phase: Test RedisService initialization"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_redis_service_initialization(self, mock_redis_client):
        """RED: Test RedisService initialization with Redis client"""
        service = RedisService(mock_redis_client)

        assert service.redis == mock_redis_client
        assert hasattr(service, 'redis')

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_redis_service_requires_redis_client(self):
        """RED: Test that RedisService requires Redis client parameter"""
        # Should be able to initialize with any Redis client
        mock_client = Mock()
        service = RedisService(mock_client)

        assert service.redis == mock_client

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_redis_service_has_cache_methods(self, redis_service):
        """RED: Test that RedisService has cache operation methods"""
        assert hasattr(redis_service, 'cache_set')
        assert hasattr(redis_service, 'cache_get')
        assert hasattr(redis_service, 'cache_delete')
        assert callable(redis_service.cache_set)
        assert callable(redis_service.cache_get)
        assert callable(redis_service.cache_delete)

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_redis_service_has_session_methods(self, redis_service):
        """RED: Test that RedisService has session operation methods"""
        assert hasattr(redis_service, 'session_set')
        assert hasattr(redis_service, 'session_get')
        assert hasattr(redis_service, 'session_delete')
        assert callable(redis_service.session_set)
        assert callable(redis_service.session_get)
        assert callable(redis_service.session_delete)

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_redis_service_has_queue_methods(self, redis_service):
        """RED: Test that RedisService has queue operation methods"""
        assert hasattr(redis_service, 'queue_push')
        assert hasattr(redis_service, 'queue_pop')
        assert callable(redis_service.queue_push)
        assert callable(redis_service.queue_pop)


# ========================================
# RED PHASE TESTS - Cache Operations
# ========================================

class TestRedisServiceCacheOperations:
    """RED Phase: Test cache operations"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_cache_set_success(self, redis_service, mock_redis_client, sample_cache_data):
        """RED: Test successful cache set operation"""
        mock_redis_client.setex.return_value = True

        result = await redis_service.cache_set(
            sample_cache_data["key"],
            sample_cache_data["value"],
            sample_cache_data["expire"]
        )

        assert result is True
        mock_redis_client.setex.assert_called_once_with(
            sample_cache_data["key"],
            sample_cache_data["expire"],
            sample_cache_data["value"]
        )

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_cache_set_default_expiration(self, redis_service, mock_redis_client):
        """RED: Test cache set with default expiration"""
        mock_redis_client.setex.return_value = True

        result = await redis_service.cache_set("test_key", "test_value")

        assert result is True
        mock_redis_client.setex.assert_called_once_with("test_key", 3600, "test_value")

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_cache_set_error_handling(self, redis_service, mock_redis_client):
        """RED: Test cache set error handling"""
        mock_redis_client.setex.side_effect = Exception("Redis error")

        with patch('app.core.redis.service.logger') as mock_logger:
            result = await redis_service.cache_set("test_key", "test_value")

        assert result is False
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Cache set error" in error_call

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_cache_get_success(self, redis_service, mock_redis_client):
        """RED: Test successful cache get operation"""
        expected_value = "cached_value"
        mock_redis_client.get.return_value = expected_value

        result = await redis_service.cache_get("test_key")

        assert result == expected_value
        mock_redis_client.get.assert_called_once_with("test_key")

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_cache_get_not_found(self, redis_service, mock_redis_client):
        """RED: Test cache get when key not found"""
        mock_redis_client.get.return_value = None

        result = await redis_service.cache_get("nonexistent_key")

        assert result is None
        mock_redis_client.get.assert_called_once_with("nonexistent_key")

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_cache_get_error_handling(self, redis_service, mock_redis_client):
        """RED: Test cache get error handling"""
        mock_redis_client.get.side_effect = Exception("Redis get error")

        with patch('app.core.redis.service.logger') as mock_logger:
            result = await redis_service.cache_get("test_key")

        assert result is None
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Cache get error" in error_call

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_cache_delete_success(self, redis_service, mock_redis_client):
        """RED: Test successful cache delete operation"""
        mock_redis_client.delete.return_value = 1  # 1 key deleted

        result = await redis_service.cache_delete("test_key")

        assert result is True
        mock_redis_client.delete.assert_called_once_with("test_key")

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_cache_delete_key_not_found(self, redis_service, mock_redis_client):
        """RED: Test cache delete when key doesn't exist"""
        mock_redis_client.delete.return_value = 0  # 0 keys deleted

        result = await redis_service.cache_delete("nonexistent_key")

        assert result is False
        mock_redis_client.delete.assert_called_once_with("nonexistent_key")

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_cache_delete_error_handling(self, redis_service, mock_redis_client):
        """RED: Test cache delete error handling"""
        mock_redis_client.delete.side_effect = Exception("Redis delete error")

        with patch('app.core.redis.service.logger') as mock_logger:
            result = await redis_service.cache_delete("test_key")

        assert result is False
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Cache delete error" in error_call


# ========================================
# RED PHASE TESTS - Session Operations
# ========================================

class TestRedisServiceSessionOperations:
    """RED Phase: Test session operations"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_session_set_success(self, redis_service, mock_redis_client, sample_session_data):
        """RED: Test successful session set operation"""
        mock_redis_client.setex.return_value = True

        result = await redis_service.session_set(
            sample_session_data["session_id"],
            sample_session_data["data"],
            sample_session_data["expire"]
        )

        assert result is True
        mock_redis_client.setex.assert_called_once()

        # Verify the call arguments
        call_args = mock_redis_client.setex.call_args[0]
        assert call_args[0] == f"session:{sample_session_data['session_id']}"
        assert call_args[1] == sample_session_data["expire"]
        # Third argument should be JSON serialized data
        stored_data = json.loads(call_args[2])
        assert stored_data == sample_session_data["data"]

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_session_set_default_expiration(self, redis_service, mock_redis_client):
        """RED: Test session set with default expiration (24 hours)"""
        mock_redis_client.setex.return_value = True
        test_data = {"user_id": "123"}

        result = await redis_service.session_set("test_session", test_data)

        assert result is True
        call_args = mock_redis_client.setex.call_args[0]
        assert call_args[1] == 86400  # 24 hours default

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_session_set_json_serialization(self, redis_service, mock_redis_client):
        """RED: Test session set JSON serialization"""
        mock_redis_client.setex.return_value = True
        complex_data = {
            "user_id": "123",
            "permissions": ["read", "write"],
            "metadata": {"last_login": "2025-09-22"}
        }

        result = await redis_service.session_set("test_session", complex_data)

        assert result is True
        call_args = mock_redis_client.setex.call_args[0]
        stored_data = json.loads(call_args[2])
        assert stored_data == complex_data

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_session_set_error_handling(self, redis_service, mock_redis_client):
        """RED: Test session set error handling"""
        mock_redis_client.setex.side_effect = Exception("Session set error")

        with patch('app.core.redis.service.logger') as mock_logger:
            result = await redis_service.session_set("test_session", {"data": "test"})

        assert result is False
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Session set error" in error_call

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_session_get_success(self, redis_service, mock_redis_client, sample_session_data):
        """RED: Test successful session get operation"""
        stored_json = json.dumps(sample_session_data["data"])
        mock_redis_client.get.return_value = stored_json

        result = await redis_service.session_get(sample_session_data["session_id"])

        assert result == sample_session_data["data"]
        mock_redis_client.get.assert_called_once_with(f"session:{sample_session_data['session_id']}")

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_session_get_not_found(self, redis_service, mock_redis_client):
        """RED: Test session get when session doesn't exist"""
        mock_redis_client.get.return_value = None

        result = await redis_service.session_get("nonexistent_session")

        assert result is None
        mock_redis_client.get.assert_called_once_with("session:nonexistent_session")

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_session_get_json_deserialization(self, redis_service, mock_redis_client):
        """RED: Test session get JSON deserialization"""
        complex_data = {
            "user_id": "456",
            "roles": ["admin", "user"],
            "settings": {"theme": "dark", "notifications": True}
        }
        stored_json = json.dumps(complex_data)
        mock_redis_client.get.return_value = stored_json

        result = await redis_service.session_get("test_session")

        assert result == complex_data

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_session_get_error_handling(self, redis_service, mock_redis_client):
        """RED: Test session get error handling"""
        mock_redis_client.get.side_effect = Exception("Session get error")

        with patch('app.core.redis.service.logger') as mock_logger:
            result = await redis_service.session_get("test_session")

        assert result is None
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Session get error" in error_call

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_session_delete_success(self, redis_service, mock_redis_client):
        """RED: Test successful session delete operation"""
        mock_redis_client.delete.return_value = 1

        result = await redis_service.session_delete("test_session")

        assert result is True
        mock_redis_client.delete.assert_called_once_with("session:test_session")

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_session_delete_not_found(self, redis_service, mock_redis_client):
        """RED: Test session delete when session doesn't exist"""
        mock_redis_client.delete.return_value = 0

        result = await redis_service.session_delete("nonexistent_session")

        assert result is False
        mock_redis_client.delete.assert_called_once_with("session:nonexistent_session")

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_session_delete_error_handling(self, redis_service, mock_redis_client):
        """RED: Test session delete error handling"""
        mock_redis_client.delete.side_effect = Exception("Session delete error")

        with patch('app.core.redis.service.logger') as mock_logger:
            result = await redis_service.session_delete("test_session")

        assert result is False
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Session delete error" in error_call


# ========================================
# RED PHASE TESTS - Queue Operations
# ========================================

class TestRedisServiceQueueOperations:
    """RED Phase: Test message queue operations using Redis Streams"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_push_success(self, redis_service, mock_redis_client, sample_queue_data):
        """RED: Test successful queue push operation"""
        mock_redis_client.xadd.return_value = "1234567890-0"

        result = await redis_service.queue_push(
            sample_queue_data["queue_name"],
            sample_queue_data["message"]
        )

        assert result is True
        mock_redis_client.xadd.assert_called_once()

        # Verify the call arguments
        call_args = mock_redis_client.xadd.call_args[0]
        assert call_args[0] == f"queue:{sample_queue_data['queue_name']}"

        # Second argument should be the message fields
        message_fields = call_args[1]
        assert "data" in message_fields
        stored_data = json.loads(message_fields["data"])
        assert stored_data == sample_queue_data["message"]

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_push_complex_message(self, redis_service, mock_redis_client):
        """RED: Test queue push with complex message structure"""
        mock_redis_client.xadd.return_value = "1234567890-1"
        complex_message = {
            "type": "email",
            "recipient": "user@example.com",
            "template": "welcome",
            "data": {
                "user_name": "John Doe",
                "activation_link": "https://example.com/activate"
            },
            "priority": "high"
        }

        result = await redis_service.queue_push("email_queue", complex_message)

        assert result is True
        call_args = mock_redis_client.xadd.call_args[0]
        message_fields = call_args[1]
        stored_data = json.loads(message_fields["data"])
        assert stored_data == complex_message

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_push_error_handling(self, redis_service, mock_redis_client):
        """RED: Test queue push error handling"""
        mock_redis_client.xadd.side_effect = Exception("Queue push error")

        with patch('app.core.redis.service.logger') as mock_logger:
            result = await redis_service.queue_push("test_queue", {"data": "test"})

        assert result is False
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Queue push error" in error_call

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_pop_success(self, redis_service, mock_redis_client):
        """RED: Test successful queue pop operation"""
        # Mock successful queue pop with message
        test_message = {"type": "task", "data": "test_data"}
        mock_redis_client.xgroup_create.return_value = True
        mock_redis_client.xreadgroup.return_value = [
            ("queue:test_queue", [("1234567890-0", {"data": json.dumps(test_message)})])
        ]

        result = await redis_service.queue_pop("test_queue")

        assert len(result) == 1
        assert result[0]["id"] == "1234567890-0"
        assert result[0]["data"] == test_message

        # Verify Redis Streams operations
        mock_redis_client.xgroup_create.assert_called_once_with(
            "queue:test_queue", "workers", id="0", mkstream=True
        )
        mock_redis_client.xreadgroup.assert_called_once_with(
            "workers",
            "worker-1",
            {"queue:test_queue": ">"},
            count=1,
            block=1000
        )

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_pop_custom_consumer(self, redis_service, mock_redis_client):
        """RED: Test queue pop with custom consumer group and name"""
        mock_redis_client.xgroup_create.return_value = True
        mock_redis_client.xreadgroup.return_value = []

        result = await redis_service.queue_pop(
            "test_queue",
            consumer_group="custom_group",
            consumer_name="custom_worker",
            count=5
        )

        assert result == []
        mock_redis_client.xgroup_create.assert_called_once_with(
            "queue:test_queue", "custom_group", id="0", mkstream=True
        )
        mock_redis_client.xreadgroup.assert_called_once_with(
            "custom_group",
            "custom_worker",
            {"queue:test_queue": ">"},
            count=5,
            block=1000
        )

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_pop_group_already_exists(self, redis_service, mock_redis_client):
        """RED: Test queue pop when consumer group already exists"""
        # Mock group creation failure (group exists)
        mock_redis_client.xgroup_create.side_effect = Exception("Group already exists")
        mock_redis_client.xreadgroup.return_value = []

        result = await redis_service.queue_pop("test_queue")

        assert result == []
        # Should still attempt to read even if group creation fails
        mock_redis_client.xreadgroup.assert_called_once()

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_pop_multiple_messages(self, redis_service, mock_redis_client):
        """RED: Test queue pop with multiple messages"""
        messages = [
            {"type": "task1", "data": "data1"},
            {"type": "task2", "data": "data2"}
        ]
        mock_redis_client.xgroup_create.return_value = True
        mock_redis_client.xreadgroup.return_value = [
            ("queue:test_queue", [
                ("1234567890-0", {"data": json.dumps(messages[0])}),
                ("1234567890-1", {"data": json.dumps(messages[1])})
            ])
        ]

        result = await redis_service.queue_pop("test_queue", count=2)

        assert len(result) == 2
        assert result[0]["data"] == messages[0]
        assert result[1]["data"] == messages[1]

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_pop_no_messages(self, redis_service, mock_redis_client):
        """RED: Test queue pop when no messages available"""
        mock_redis_client.xgroup_create.return_value = True
        mock_redis_client.xreadgroup.return_value = []

        result = await redis_service.queue_pop("empty_queue")

        assert result == []

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_pop_error_handling(self, redis_service, mock_redis_client):
        """RED: Test queue pop error handling"""
        mock_redis_client.xreadgroup.side_effect = Exception("Queue pop error")

        with patch('app.core.redis.service.logger') as mock_logger:
            result = await redis_service.queue_pop("test_queue")

        assert result == []
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Queue pop error" in error_call


# ========================================
# RED PHASE TESTS - Dependency Injection
# ========================================

class TestRedisServiceDependencyInjection:
    """RED Phase: Test get_redis_service dependency function"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_get_redis_service_function_exists(self):
        """RED: Test that get_redis_service function exists and is callable"""
        assert callable(get_redis_service)

        # Should be an async function
        import inspect
        assert inspect.iscoroutinefunction(get_redis_service)

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_get_redis_service_returns_service_instance(self):
        """RED: Test that get_redis_service returns RedisService instance"""
        mock_redis_client = AsyncMock()

        with patch('app.core.redis.service.get_redis', return_value=mock_redis_client):
            service = await get_redis_service()

        assert isinstance(service, RedisService)
        assert service.redis == mock_redis_client

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_get_redis_service_calls_get_redis_dependency(self):
        """RED: Test that get_redis_service calls get_redis dependency"""
        mock_redis_client = AsyncMock()

        with patch('app.core.redis.service.get_redis', return_value=mock_redis_client) as mock_get_redis:
            service = await get_redis_service()

        mock_get_redis.assert_called_once()
        assert service.redis == mock_redis_client

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_get_redis_service_creates_new_instance_each_call(self):
        """RED: Test that get_redis_service creates new instance on each call"""
        mock_redis_client = AsyncMock()

        with patch('app.core.redis.service.get_redis', return_value=mock_redis_client):
            service1 = await get_redis_service()
            service2 = await get_redis_service()

        # Should be different instances but same Redis client
        assert service1 is not service2
        assert service1.redis == service2.redis == mock_redis_client


# ========================================
# RED PHASE TESTS - Integration and Error Scenarios
# ========================================

class TestRedisServiceIntegration:
    """RED Phase: Test integration scenarios and edge cases"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_service_operations_with_real_redis_calls(self, redis_service, mock_redis_client):
        """RED: Test service operations sequence"""
        # Setup mock responses for a complete workflow
        mock_redis_client.setex.return_value = True
        mock_redis_client.get.return_value = json.dumps({"user_id": "123"})
        mock_redis_client.xadd.return_value = "1234567890-0"

        # Test cache operation
        cache_result = await redis_service.cache_set("test_key", "test_value")
        assert cache_result is True

        # Test session operation
        session_result = await redis_service.session_get("test_session")
        assert session_result == {"user_id": "123"}

        # Test queue operation
        queue_result = await redis_service.queue_push("test_queue", {"task": "process"})
        assert queue_result is True

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_json_serialization_edge_cases(self, redis_service, mock_redis_client):
        """RED: Test JSON serialization with edge cases"""
        mock_redis_client.setex.return_value = True

        # Test with None values
        data_with_none = {"key": None, "valid": "value"}
        result = await redis_service.session_set("test", data_with_none)
        assert result is True

        # Test with empty dict
        empty_data = {}
        result = await redis_service.session_set("test", empty_data)
        assert result is True

        # Test with nested structures
        nested_data = {
            "level1": {
                "level2": {
                    "level3": ["item1", "item2", {"nested": True}]
                }
            }
        }
        result = await redis_service.session_set("test", nested_data)
        assert result is True

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_redis_connection_failure_resilience(self, redis_service, mock_redis_client):
        """RED: Test service resilience to Redis connection failures"""
        # All operations should return appropriate defaults when Redis fails
        mock_redis_client.setex.side_effect = redis.ConnectionError("Connection lost")
        mock_redis_client.get.side_effect = redis.ConnectionError("Connection lost")
        mock_redis_client.delete.side_effect = redis.ConnectionError("Connection lost")
        mock_redis_client.xadd.side_effect = redis.ConnectionError("Connection lost")
        mock_redis_client.xreadgroup.side_effect = redis.ConnectionError("Connection lost")

        with patch('app.core.redis.service.logger'):
            # All operations should handle connection failures gracefully
            assert await redis_service.cache_set("key", "value") is False
            assert await redis_service.cache_get("key") is None
            assert await redis_service.cache_delete("key") is False
            assert await redis_service.session_set("session", {}) is False
            assert await redis_service.session_get("session") is None
            assert await redis_service.session_delete("session") is False
            assert await redis_service.queue_push("queue", {}) is False
            assert await redis_service.queue_pop("queue") == []

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_service_logger_integration(self, redis_service):
        """RED: Test integration with logger module"""
        # Test that logger import is correct in service module
        from app.core.redis.service import logger
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'info')

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_service_imports_and_dependencies(self, redis_service):
        """RED: Test that all required imports are available"""
        # Test Redis import
        import redis
        assert hasattr(redis, 'Redis')

        # Test json import works in module
        import json
        assert hasattr(json, 'dumps')
        assert hasattr(json, 'loads')

        # Test typing imports
        from typing import Optional, Dict, List, Any
        assert Optional is not None


# ========================================
# PERFORMANCE AND BENCHMARKING TESTS
# ========================================

class TestRedisServicePerformance:
    """RED Phase: Test performance characteristics"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_service_method_call_overhead(self, redis_service, mock_redis_client):
        """RED: Test that service methods have minimal overhead"""
        import time

        # Mock quick Redis responses
        mock_redis_client.setex.return_value = True
        mock_redis_client.get.return_value = "test_value"

        # Test cache operations performance
        start_time = time.time()
        await redis_service.cache_set("key", "value")
        await redis_service.cache_get("key")
        end_time = time.time()

        # Service overhead should be minimal (< 1ms)
        total_time = (end_time - start_time) * 1000
        assert total_time < 1.0  # Should complete in less than 1ms

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_json_serialization_performance(self, redis_service, mock_redis_client):
        """RED: Test JSON serialization performance"""
        import time

        mock_redis_client.setex.return_value = True

        # Large data structure for performance test
        large_data = {
            f"key_{i}": f"value_{i}" for i in range(1000)
        }

        start_time = time.time()
        await redis_service.session_set("large_session", large_data)
        end_time = time.time()

        # JSON serialization should be efficient
        total_time = (end_time - start_time) * 1000
        assert total_time < 10.0  # Should complete in less than 10ms


if __name__ == "__main__":
    # Run the RED phase tests
    pytest.main([__file__, "-v", "-m", "red_test"])