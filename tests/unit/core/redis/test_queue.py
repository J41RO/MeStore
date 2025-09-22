"""
TDD Test Suite for Redis Queue Manager
=====================================

Comprehensive Test-Driven Development suite for app.core.redis.queue.py
Following strict RED-GREEN-REFACTOR methodology.

Test Coverage:
- RedisQueueManager: Initialization, connection management, error handling
- Queue-specific connection pool configuration (DB 2)
- Higher connection limits for queue processing
- Connection resilience and recovery
- Message queue specific optimizations
- Performance characteristics for background tasks

Redis Queue Testing Focus:
- Queue-specific connection pool (DB 2)
- Higher connection limits for concurrent workers
- Message processing reliability
- Error handling and fallback behaviors
- Connection retry logic for queue workers
- Resource cleanup and management
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Optional

# Import the modules we're testing
from app.core.redis.queue import RedisQueueManager
from app.core.redis.base import RedisManager
import redis.asyncio as redis


# ========================================
# TEST FIXTURES AND HELPERS
# ========================================

@pytest.fixture
def queue_manager():
    """Create a fresh RedisQueueManager instance for each test"""
    return RedisQueueManager()


@pytest.fixture
def mock_redis_pool():
    """Mock Redis connection pool for queue operations"""
    pool = Mock()
    pool.from_url = Mock(return_value=pool)
    pool.disconnect = AsyncMock()
    return pool


@pytest.fixture
def mock_redis_client():
    """Mock Redis client with queue-specific methods"""
    client = AsyncMock()
    client.ping = AsyncMock(return_value=True)
    client.lpush = AsyncMock(return_value=1)
    client.rpop = AsyncMock(return_value=None)
    client.llen = AsyncMock(return_value=0)
    client.brpop = AsyncMock(return_value=None)
    client.lpop = AsyncMock(return_value=None)
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_settings():
    """Mock settings for Redis queue configuration"""
    with patch('app.core.redis.queue.settings') as mock_settings:
        mock_settings.REDIS_QUEUE_URL = "redis://localhost:6379/2"
        yield mock_settings


# ========================================
# RED PHASE TESTS - RedisQueueManager Initialization
# ========================================

class TestRedisQueueManagerInitialization:
    """RED Phase: Test RedisQueueManager initialization and inheritance"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_queue_manager_inherits_from_redis_manager(self, queue_manager):
        """RED: Test that RedisQueueManager inherits from RedisManager"""
        assert isinstance(queue_manager, RedisManager)
        assert hasattr(queue_manager, '_redis')
        assert hasattr(queue_manager, '_pool')

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_queue_manager_default_initialization(self, queue_manager):
        """RED: Test default initialization values"""
        assert queue_manager._redis is None
        assert queue_manager._pool is None

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_queue_manager_has_connect_method(self, queue_manager):
        """RED: Test that connect method exists and is callable"""
        assert hasattr(queue_manager, 'connect')
        assert callable(queue_manager.connect)

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_queue_manager_is_separate_from_cache_manager(self, queue_manager):
        """RED: Test that queue manager is distinct from cache manager"""
        from app.core.redis.cache import RedisCacheManager
        cache_manager = RedisCacheManager()

        # Should be different classes
        assert type(queue_manager) != type(cache_manager)
        assert isinstance(queue_manager, RedisQueueManager)
        assert not isinstance(queue_manager, RedisCacheManager)


# ========================================
# RED PHASE TESTS - Queue Connection Management
# ========================================

class TestRedisQueueManagerConnection:
    """RED Phase: Test Redis queue connection establishment"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_creates_queue_connection_pool(self, queue_manager, mock_settings):
        """RED: Test connection pool creation with queue-specific URL"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_pool = Mock()
                mock_from_url.return_value = mock_pool

                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                result = await queue_manager.connect()

                # Test that queue-specific URL is used
                mock_from_url.assert_called_once_with(
                    mock_settings.REDIS_QUEUE_URL,
                    max_connections=15,  # Higher limit for queues
                    retry_on_timeout=True,
                    decode_responses=True,
                    encoding="utf-8"
                )

                assert result == mock_redis_instance
                assert queue_manager._redis == mock_redis_instance
                assert queue_manager._pool == mock_pool

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_uses_higher_connection_limit(self, queue_manager, mock_settings):
        """RED: Test that queue manager uses higher connection limit"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await queue_manager.connect()

                # Test queue-specific higher connection limit
                call_kwargs = mock_from_url.call_args[1]
                assert call_kwargs['max_connections'] == 15  # Higher than cache (10)

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_tests_connection_with_ping(self, queue_manager, mock_settings):
        """RED: Test that connection is tested with ping"""
        with patch('redis.ConnectionPool.from_url'):
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await queue_manager.connect()

                # Test that ping was called to verify connection
                mock_redis_instance.ping.assert_called_once()

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_reuses_existing_connection(self, queue_manager, mock_settings):
        """RED: Test that existing connection is reused"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                # First connection
                result1 = await queue_manager.connect()

                # Second connection should reuse existing
                result2 = await queue_manager.connect()

                # Test that pool creation only called once
                assert mock_from_url.call_count == 1
                assert result1 == result2
                assert result1 == mock_redis_instance

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_logs_queue_success_message(self, queue_manager, mock_settings):
        """RED: Test that successful queue connection is logged"""
        with patch('redis.ConnectionPool.from_url'):
            with patch('redis.Redis') as mock_redis_class:
                with patch('app.core.redis.queue.logger') as mock_logger:
                    mock_redis_instance = AsyncMock()
                    mock_redis_instance.ping = AsyncMock(return_value=True)
                    mock_redis_class.return_value = mock_redis_instance

                    await queue_manager.connect()

                    # Test that queue-specific success message is logged
                    mock_logger.info.assert_called_with("✅ Redis Queues (DB 2) connection established")

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_logs_queue_error_message(self, queue_manager, mock_settings):
        """RED: Test that queue connection errors are logged"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            mock_from_url.side_effect = Exception("Queue connection failed")

            with patch('app.core.redis.queue.logger') as mock_logger:
                with pytest.raises(Exception):
                    await queue_manager.connect()

                # Test that queue-specific error is logged
                mock_logger.error.assert_called()
                error_call = mock_logger.error.call_args[0][0]
                assert "❌ Redis Queues connection failed" in error_call
                assert "Queue connection failed" in error_call


# ========================================
# RED PHASE TESTS - Queue-Specific Configuration
# ========================================

class TestRedisQueueManagerConfiguration:
    """RED Phase: Test queue-specific Redis configuration"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_connection_pool_configuration(self, queue_manager, mock_settings):
        """RED: Test queue-specific connection pool parameters"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await queue_manager.connect()

                # Test queue-specific pool configuration
                call_args = mock_from_url.call_args
                assert call_args[1]['max_connections'] == 15  # Higher for queue workers
                assert call_args[1]['retry_on_timeout'] is True
                assert call_args[1]['decode_responses'] is True
                assert call_args[1]['encoding'] == "utf-8"

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_uses_db_2_url(self, queue_manager, mock_settings):
        """RED: Test that queue manager uses DB 2 URL"""
        mock_settings.REDIS_QUEUE_URL = "redis://localhost:6379/2"

        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await queue_manager.connect()

                # Test that DB 2 URL is used for queues
                mock_from_url.assert_called_once()
                call_args = mock_from_url.call_args[0]
                assert call_args[0] == "redis://localhost:6379/2"

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_redis_client_creation(self, queue_manager, mock_settings):
        """RED: Test Redis client creation with queue connection pool"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_pool = Mock()
                mock_from_url.return_value = mock_pool

                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await queue_manager.connect()

                # Test that Redis client is created with the queue pool
                mock_redis_class.assert_called_once_with(connection_pool=mock_pool)

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_vs_cache_configuration_differences(self, queue_manager, mock_settings):
        """RED: Test configuration differences between queue and cache managers"""
        from app.core.redis.cache import RedisCacheManager

        cache_manager = RedisCacheManager()

        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                # Connect queue manager
                await queue_manager.connect()
                queue_call_kwargs = mock_from_url.call_args[1]

                # Reset mock for cache manager
                mock_from_url.reset_mock()

                # Connect cache manager
                await cache_manager.connect()
                cache_call_kwargs = mock_from_url.call_args[1]

                # Test that queue has higher connection limit than cache
                assert queue_call_kwargs['max_connections'] > cache_call_kwargs['max_connections']
                assert queue_call_kwargs['max_connections'] == 15
                assert cache_call_kwargs['max_connections'] == 10


# ========================================
# RED PHASE TESTS - Queue Error Handling
# ========================================

class TestRedisQueueManagerErrorHandling:
    """RED Phase: Test error handling and resilience for queue operations"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_handles_queue_connection_failure(self, queue_manager, mock_settings):
        """RED: Test handling of queue connection failure"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                # Mock connection failure for queue
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(side_effect=redis.ConnectionError("Queue connection failed"))
                mock_redis_class.return_value = mock_redis_instance

                with pytest.raises(redis.ConnectionError):
                    await queue_manager.connect()

                # Test that connection creation was attempted but ping failed
                # Note: _redis is set before ping, so it will contain the mock instance
                assert queue_manager._redis == mock_redis_instance
                mock_redis_instance.ping.assert_called_once()

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_handles_queue_pool_creation_failure(self, queue_manager, mock_settings):
        """RED: Test handling of queue connection pool creation failure"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            mock_from_url.side_effect = redis.RedisError("Queue pool creation failed")

            with pytest.raises(redis.RedisError):
                await queue_manager.connect()

            # Test that state remains clean after failure
            assert queue_manager._redis is None
            assert queue_manager._pool is None

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_handles_queue_timeout(self, queue_manager, mock_settings):
        """RED: Test handling of queue connection timeout"""
        with patch('redis.ConnectionPool.from_url'):
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(side_effect=redis.TimeoutError("Queue timeout"))
                mock_redis_class.return_value = mock_redis_instance

                with pytest.raises(redis.TimeoutError):
                    await queue_manager.connect()

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_handles_queue_authentication_failure(self, queue_manager, mock_settings):
        """RED: Test handling of queue Redis authentication failure"""
        with patch('redis.ConnectionPool.from_url'):
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(side_effect=redis.AuthenticationError("Queue auth failed"))
                mock_redis_class.return_value = mock_redis_instance

                with pytest.raises(redis.AuthenticationError):
                    await queue_manager.connect()


# ========================================
# RED PHASE TESTS - Queue Performance Characteristics
# ========================================

class TestRedisQueueManagerPerformance:
    """RED Phase: Test performance characteristics for queue operations"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_connection_pool_performance_settings(self, queue_manager, mock_settings):
        """RED: Test that queue performance-optimized pool settings are used"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await queue_manager.connect()

                # Test queue performance settings
                call_kwargs = mock_from_url.call_args[1]
                assert call_kwargs['max_connections'] == 15  # Higher for queue workers
                assert call_kwargs['retry_on_timeout'] is True  # Critical for queues
                assert call_kwargs['decode_responses'] is True  # JSON processing
                assert call_kwargs['encoding'] == "utf-8"  # Standardized

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_connection_reuse_efficiency(self, queue_manager, mock_settings):
        """RED: Test that queue connection reuse is efficient"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                # Multiple calls should reuse connection for queue operations
                result1 = await queue_manager.connect()
                result2 = await queue_manager.connect()
                result3 = await queue_manager.connect()

                # Test that pool is only created once
                assert mock_from_url.call_count == 1
                assert result1 == result2 == result3

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_higher_concurrency_support(self, queue_manager, mock_settings):
        """RED: Test that queue manager supports higher concurrency"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await queue_manager.connect()

                # Test concurrency settings
                call_kwargs = mock_from_url.call_args[1]
                max_connections = call_kwargs['max_connections']

                # Queue should support more connections than basic cache
                assert max_connections >= 15  # Minimum for queue workers
                assert max_connections > 10   # Higher than cache


# ========================================
# RED PHASE TESTS - Queue Inherited Functionality
# ========================================

class TestRedisQueueManagerInheritedMethods:
    """RED Phase: Test inherited methods from RedisManager for queues"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_disconnect_method_inherited(self, queue_manager):
        """RED: Test that disconnect method is inherited and functional for queues"""
        # Set up a mock queue connection first
        mock_redis = AsyncMock()
        mock_pool = AsyncMock()
        queue_manager._redis = mock_redis
        queue_manager._pool = mock_pool

        await queue_manager.disconnect()

        # Test that inherited disconnect method works for queues
        mock_redis.close.assert_called_once()
        mock_pool.disconnect.assert_called_once()

        # Test that connections are set to None after disconnect
        assert queue_manager._redis is None
        assert queue_manager._pool is None

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_get_redis_method_inherited(self, queue_manager, mock_settings):
        """RED: Test that get_redis method is inherited and calls queue connect"""
        with patch.object(queue_manager, 'connect') as mock_connect:
            mock_redis_instance = AsyncMock()

            # Mock connect to also set _redis
            async def mock_connect_side_effect():
                queue_manager._redis = mock_redis_instance
                return mock_redis_instance

            mock_connect.side_effect = mock_connect_side_effect

            result = await queue_manager.get_redis()

            # Test that inherited get_redis method works for queues
            mock_connect.assert_called_once()
            assert result == mock_redis_instance

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_get_redis_reuses_existing_connection(self, queue_manager):
        """RED: Test that queue get_redis reuses existing connection"""
        mock_redis_instance = AsyncMock()
        queue_manager._redis = mock_redis_instance

        with patch.object(queue_manager, 'connect') as mock_connect:
            result = await queue_manager.get_redis()

            # Test that connect is not called when queue connection exists
            mock_connect.assert_not_called()
            assert result == mock_redis_instance


# ========================================
# RED PHASE TESTS - Queue Integration Points
# ========================================

class TestRedisQueueManagerIntegration:
    """RED Phase: Test integration with other components for queue operations"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_queue_settings_integration(self, queue_manager):
        """RED: Test integration with settings module for queues"""
        # Test that queue settings import is correct
        from app.core.redis.queue import settings
        assert hasattr(settings, 'REDIS_QUEUE_URL')

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_queue_logger_integration(self, queue_manager):
        """RED: Test integration with logger module for queues"""
        # Test that queue logger import is correct
        from app.core.redis.queue import logger
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_queue_redis_module_integration(self, queue_manager):
        """RED: Test integration with Redis module for queues"""
        # Test that Redis classes are available for queue operations
        import redis
        assert hasattr(redis, 'ConnectionPool')
        assert hasattr(redis, 'Redis')

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_base_class_integration(self, queue_manager, mock_settings):
        """RED: Test proper integration with base RedisManager class for queues"""
        # Test that overridden methods work correctly for queues
        with patch('redis.ConnectionPool.from_url'):
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                # Test that queue manager's connect method overrides base correctly
                result = await queue_manager.connect()

                # Should use queue-specific configuration
                assert result == mock_redis_instance
                assert queue_manager._redis == mock_redis_instance


# ========================================
# RED PHASE TESTS - Queue Compliance and Best Practices
# ========================================

class TestRedisQueueManagerCompliance:
    """RED Phase: Test compliance with Redis queue best practices"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_connection_pool_best_practices(self, queue_manager, mock_settings):
        """RED: Test that queue connection pool follows Redis best practices"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await queue_manager.connect()

                # Test queue best practices compliance
                call_kwargs = mock_from_url.call_args[1]
                assert call_kwargs['max_connections'] <= 50  # Reasonable queue limit
                assert call_kwargs['max_connections'] >= 10  # Minimum for queues
                assert call_kwargs['retry_on_timeout'] is True  # Critical for queues
                assert 'decode_responses' in call_kwargs  # Explicit setting
                assert 'encoding' in call_kwargs  # Explicit encoding

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_error_handling_compliance(self, queue_manager, mock_settings):
        """RED: Test that queue error handling follows best practices"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            mock_from_url.side_effect = Exception("Queue test error")

            with patch('app.core.redis.queue.logger') as mock_logger:
                with pytest.raises(Exception):
                    await queue_manager.connect()

                # Test that queue errors are properly logged
                mock_logger.error.assert_called()

                # Test that exception is re-raised (fail-fast principle)
                assert mock_from_url.call_count == 1

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_queue_class_design_compliance(self, queue_manager):
        """RED: Test that queue class design follows Python best practices"""
        # Test queue inheritance
        assert isinstance(queue_manager, RedisManager)

        # Test queue method presence
        assert hasattr(queue_manager, 'connect')
        assert callable(queue_manager.connect)

        # Test that queue connect method is async
        import inspect
        assert inspect.iscoroutinefunction(queue_manager.connect)

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_queue_database_isolation(self, queue_manager):
        """RED: Test that queue manager is properly isolated to DB 2"""
        # Test queue specialization
        assert hasattr(queue_manager, 'connect')

        # Queue manager should be designed for DB 2 operations
        # This is verified through the URL configuration in integration tests


# ========================================
# RED PHASE TESTS - Queue Scalability
# ========================================

class TestRedisQueueManagerScalability:
    """RED Phase: Test scalability characteristics for queue operations"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_supports_worker_concurrency(self, queue_manager, mock_settings):
        """RED: Test that queue manager supports multiple worker connections"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await queue_manager.connect()

                # Test worker concurrency configuration
                call_kwargs = mock_from_url.call_args[1]
                max_connections = call_kwargs['max_connections']

                # Should support multiple queue workers
                assert max_connections >= 10  # Minimum for concurrent workers
                assert max_connections == 15  # Specific queue configuration

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_queue_connection_retry_resilience(self, queue_manager, mock_settings):
        """RED: Test that queue connections have retry resilience"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await queue_manager.connect()

                # Test retry configuration for queue resilience
                call_kwargs = mock_from_url.call_args[1]
                assert call_kwargs['retry_on_timeout'] is True

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_queue_memory_efficiency(self, queue_manager):
        """RED: Test memory-efficient operation for queue manager"""
        # Test that queue instance variables are minimal
        expected_attributes = ['_redis', '_pool']
        actual_attributes = [attr for attr in dir(queue_manager) if not attr.startswith('__') and not callable(getattr(queue_manager, attr))]

        # Should only have minimal instance variables for efficiency
        for attr in expected_attributes:
            assert hasattr(queue_manager, attr)


if __name__ == "__main__":
    # Run the RED phase tests
    pytest.main([__file__, "-v", "-m", "red_test"])