"""
TDD Test Suite for Redis Cache Manager
=====================================

Comprehensive Test-Driven Development suite for app.core.redis.cache.py
Following strict RED-GREEN-REFACTOR methodology.

Test Coverage:
- RedisCacheManager: Initialization, connection management, error handling
- Cache-specific connection pool configuration
- Connection resilience and recovery
- Testing mode behavior
- Logging and monitoring

Redis Testing Focus:
- Connection pool management
- Database-specific connections (Cache DB 0)
- Error handling and fallback behaviors
- Connection retry logic
- Performance optimization
- Resource cleanup
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Optional

# Import the modules we're testing
from app.core.redis.cache import RedisCacheManager
from app.core.redis.base import RedisManager
import redis.asyncio as redis


# ========================================
# TEST FIXTURES AND HELPERS
# ========================================

@pytest.fixture
def cache_manager():
    """Create a fresh RedisCacheManager instance for each test"""
    return RedisCacheManager()


@pytest.fixture
def mock_redis_pool():
    """Mock Redis connection pool"""
    pool = Mock()
    pool.from_url = Mock(return_value=pool)
    pool.disconnect = AsyncMock()
    return pool


@pytest.fixture
def mock_redis_client():
    """Mock Redis client with common methods"""
    client = AsyncMock()
    client.ping = AsyncMock(return_value=True)
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.setex = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=1)
    client.exists = AsyncMock(return_value=False)
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_settings():
    """Mock settings for Redis configuration"""
    with patch('app.core.redis.cache.settings') as mock_settings:
        mock_settings.REDIS_CACHE_URL = "redis://localhost:6379/0"
        yield mock_settings


# ========================================
# RED PHASE TESTS - RedisCacheManager Initialization
# ========================================

class TestRedisCacheManagerInitialization:
    """RED Phase: Test RedisCacheManager initialization and inheritance"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_cache_manager_inherits_from_redis_manager(self, cache_manager):
        """RED: Test that RedisCacheManager inherits from RedisManager"""
        assert isinstance(cache_manager, RedisManager)
        assert hasattr(cache_manager, '_redis')
        assert hasattr(cache_manager, '_pool')

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_cache_manager_default_initialization(self, cache_manager):
        """RED: Test default initialization values"""
        assert cache_manager._redis is None
        assert cache_manager._pool is None

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_cache_manager_has_connect_method(self, cache_manager):
        """RED: Test that connect method exists and is callable"""
        assert hasattr(cache_manager, 'connect')
        assert callable(cache_manager.connect)


# ========================================
# RED PHASE TESTS - Connection Management
# ========================================

class TestRedisCacheManagerConnection:
    """RED Phase: Test Redis cache connection establishment"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_creates_cache_connection_pool(self, cache_manager, mock_settings):
        """RED: Test connection pool creation with cache-specific URL"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_pool = Mock()
                mock_from_url.return_value = mock_pool

                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                result = await cache_manager.connect()

                # Test that cache-specific URL is used
                mock_from_url.assert_called_once_with(
                    mock_settings.REDIS_CACHE_URL,
                    max_connections=10,
                    retry_on_timeout=True,
                    decode_responses=True,
                    encoding="utf-8"
                )

                assert result == mock_redis_instance
                assert cache_manager._redis == mock_redis_instance
                assert cache_manager._pool == mock_pool

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_tests_connection_with_ping(self, cache_manager, mock_settings):
        """RED: Test that connection is tested with ping"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await cache_manager.connect()

                # Test that ping was called to verify connection
                mock_redis_instance.ping.assert_called_once()

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_reuses_existing_connection(self, cache_manager, mock_settings):
        """RED: Test that existing connection is reused"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                # First connection
                result1 = await cache_manager.connect()

                # Second connection should reuse existing
                result2 = await cache_manager.connect()

                # Test that pool creation only called once
                assert mock_from_url.call_count == 1
                assert result1 == result2
                assert result1 == mock_redis_instance

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_handles_connection_failure(self, cache_manager, mock_settings):
        """RED: Test connection failure handling"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                # Mock connection failure
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(side_effect=redis.ConnectionError("Connection failed"))
                mock_redis_class.return_value = mock_redis_instance

                with pytest.raises(redis.ConnectionError):
                    await cache_manager.connect()

                # Test that connection creation was attempted but ping failed
                # Note: _redis is set before ping, so it will contain the mock instance
                assert cache_manager._redis == mock_redis_instance
                mock_redis_instance.ping.assert_called_once()

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_logs_success_message(self, cache_manager, mock_settings):
        """RED: Test that successful connection is logged"""
        with patch('redis.ConnectionPool.from_url'):
            with patch('redis.Redis') as mock_redis_class:
                with patch('app.core.redis.cache.logger') as mock_logger:
                    mock_redis_instance = AsyncMock()
                    mock_redis_instance.ping = AsyncMock(return_value=True)
                    mock_redis_class.return_value = mock_redis_instance

                    await cache_manager.connect()

                    # Test that success message is logged
                    mock_logger.info.assert_called_with("✅ Redis Cache (DB 0) connection established")

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_logs_error_message(self, cache_manager, mock_settings):
        """RED: Test that connection errors are logged"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            mock_from_url.side_effect = Exception("Connection pool creation failed")

            with patch('app.core.redis.cache.logger') as mock_logger:
                with pytest.raises(Exception):
                    await cache_manager.connect()

                # Test that error is logged
                mock_logger.error.assert_called()
                error_call = mock_logger.error.call_args[0][0]
                assert "❌ Redis Cache connection failed" in error_call
                assert "Connection pool creation failed" in error_call


# ========================================
# RED PHASE TESTS - Cache-Specific Configuration
# ========================================

class TestRedisCacheManagerConfiguration:
    """RED Phase: Test cache-specific Redis configuration"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_cache_connection_pool_configuration(self, cache_manager, mock_settings):
        """RED: Test cache-specific connection pool parameters"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await cache_manager.connect()

                # Test cache-specific pool configuration
                call_args = mock_from_url.call_args
                assert call_args[1]['max_connections'] == 10  # Cache-specific limit
                assert call_args[1]['retry_on_timeout'] is True
                assert call_args[1]['decode_responses'] is True
                assert call_args[1]['encoding'] == "utf-8"

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_cache_uses_db_0_url(self, cache_manager, mock_settings):
        """RED: Test that cache manager uses DB 0 URL"""
        mock_settings.REDIS_CACHE_URL = "redis://localhost:6379/0"

        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await cache_manager.connect()

                # Test that DB 0 URL is used
                mock_from_url.assert_called_once()
                call_args = mock_from_url.call_args[0]
                assert call_args[0] == "redis://localhost:6379/0"

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_cache_redis_client_creation(self, cache_manager, mock_settings):
        """RED: Test Redis client creation with connection pool"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_pool = Mock()
                mock_from_url.return_value = mock_pool

                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await cache_manager.connect()

                # Test that Redis client is created with the pool
                mock_redis_class.assert_called_once_with(connection_pool=mock_pool)


# ========================================
# RED PHASE TESTS - Error Handling and Resilience
# ========================================

class TestRedisCacheManagerErrorHandling:
    """RED Phase: Test error handling and resilience"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_handles_pool_creation_failure(self, cache_manager, mock_settings):
        """RED: Test handling of connection pool creation failure"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            mock_from_url.side_effect = redis.RedisError("Pool creation failed")

            with pytest.raises(redis.RedisError):
                await cache_manager.connect()

            # Test that state remains clean after failure
            assert cache_manager._redis is None
            assert cache_manager._pool is None

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_handles_redis_client_creation_failure(self, cache_manager, mock_settings):
        """RED: Test handling of Redis client creation failure"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_pool = Mock()
                mock_from_url.return_value = mock_pool
                mock_redis_class.side_effect = Exception("Client creation failed")

                with pytest.raises(Exception):
                    await cache_manager.connect()

                # Test that pool was created but client failed
                assert cache_manager._pool == mock_pool
                assert cache_manager._redis is None

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_handles_ping_timeout(self, cache_manager, mock_settings):
        """RED: Test handling of ping timeout"""
        with patch('redis.ConnectionPool.from_url'):
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(side_effect=redis.TimeoutError("Ping timeout"))
                mock_redis_class.return_value = mock_redis_instance

                with pytest.raises(redis.TimeoutError):
                    await cache_manager.connect()

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connect_handles_authentication_failure(self, cache_manager, mock_settings):
        """RED: Test handling of Redis authentication failure"""
        with patch('redis.ConnectionPool.from_url'):
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(side_effect=redis.AuthenticationError("Auth failed"))
                mock_redis_class.return_value = mock_redis_instance

                with pytest.raises(redis.AuthenticationError):
                    await cache_manager.connect()


# ========================================
# RED PHASE TESTS - Inherited Functionality
# ========================================

class TestRedisCacheManagerInheritedMethods:
    """RED Phase: Test inherited methods from RedisManager"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_disconnect_method_inherited(self, cache_manager):
        """RED: Test that disconnect method is inherited and functional"""
        # Set up a mock connection first
        mock_redis = AsyncMock()
        mock_pool = AsyncMock()
        cache_manager._redis = mock_redis
        cache_manager._pool = mock_pool

        await cache_manager.disconnect()

        # Test that inherited disconnect method works
        mock_redis.close.assert_called_once()
        mock_pool.disconnect.assert_called_once()

        # Test that connections are set to None after disconnect
        assert cache_manager._redis is None
        assert cache_manager._pool is None

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_get_redis_method_inherited(self, cache_manager, mock_settings):
        """RED: Test that get_redis method is inherited and calls connect"""
        with patch.object(cache_manager, 'connect') as mock_connect:
            mock_redis_instance = AsyncMock()

            # Mock connect to also set _redis
            async def mock_connect_side_effect():
                cache_manager._redis = mock_redis_instance
                return mock_redis_instance

            mock_connect.side_effect = mock_connect_side_effect

            result = await cache_manager.get_redis()

            # Test that inherited get_redis method works
            mock_connect.assert_called_once()
            assert result == mock_redis_instance

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_get_redis_reuses_existing_connection(self, cache_manager):
        """RED: Test that get_redis reuses existing connection"""
        mock_redis_instance = AsyncMock()
        cache_manager._redis = mock_redis_instance

        with patch.object(cache_manager, 'connect') as mock_connect:
            result = await cache_manager.get_redis()

            # Test that connect is not called when connection exists
            mock_connect.assert_not_called()
            assert result == mock_redis_instance


# ========================================
# RED PHASE TESTS - Performance and Optimization
# ========================================

class TestRedisCacheManagerPerformance:
    """RED Phase: Test performance characteristics"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connection_pool_performance_settings(self, cache_manager, mock_settings):
        """RED: Test that performance-optimized pool settings are used"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await cache_manager.connect()

                # Test performance settings
                call_kwargs = mock_from_url.call_args[1]
                assert call_kwargs['max_connections'] == 10  # Moderate for cache
                assert call_kwargs['retry_on_timeout'] is True  # Resilience
                assert call_kwargs['decode_responses'] is True  # Performance
                assert call_kwargs['encoding'] == "utf-8"  # Standardized

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connection_reuse_efficiency(self, cache_manager, mock_settings):
        """RED: Test that connection reuse is efficient"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                # Multiple calls should reuse connection
                result1 = await cache_manager.connect()
                result2 = await cache_manager.connect()
                result3 = await cache_manager.connect()

                # Test that pool is only created once
                assert mock_from_url.call_count == 1
                assert result1 == result2 == result3

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_cache_manager_memory_efficiency(self, cache_manager):
        """RED: Test memory-efficient operation"""
        # Test that instance variables are minimal
        expected_attributes = ['_redis', '_pool']
        actual_attributes = [attr for attr in dir(cache_manager) if not attr.startswith('__') and not callable(getattr(cache_manager, attr))]

        # Should only have minimal instance variables
        for attr in expected_attributes:
            assert hasattr(cache_manager, attr)


# ========================================
# RED PHASE TESTS - Integration Points
# ========================================

class TestRedisCacheManagerIntegration:
    """RED Phase: Test integration with other components"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_settings_integration(self, cache_manager):
        """RED: Test integration with settings module"""
        # Test that settings import is correct
        from app.core.redis.cache import settings
        assert hasattr(settings, 'REDIS_CACHE_URL')

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_logger_integration(self, cache_manager):
        """RED: Test integration with logger module"""
        # Test that logger import is correct
        from app.core.redis.cache import logger
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_redis_module_integration(self, cache_manager):
        """RED: Test integration with Redis module"""
        # Test that Redis classes are available
        import redis
        assert hasattr(redis, 'ConnectionPool')
        assert hasattr(redis, 'Redis')

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_base_class_integration(self, cache_manager, mock_settings):
        """RED: Test proper integration with base RedisManager class"""
        # Test that overridden methods work correctly
        with patch('redis.ConnectionPool.from_url'):
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                # Test that cache manager's connect method overrides base correctly
                result = await cache_manager.connect()

                # Should use cache-specific configuration
                assert result == mock_redis_instance
                assert cache_manager._redis == mock_redis_instance


# ========================================
# BENCHMARKING AND COMPLIANCE TESTS
# ========================================

class TestRedisCacheManagerCompliance:
    """RED Phase: Test compliance with Redis best practices"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_connection_pool_best_practices(self, cache_manager, mock_settings):
        """RED: Test that connection pool follows Redis best practices"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            with patch('redis.Redis') as mock_redis_class:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis_class.return_value = mock_redis_instance

                await cache_manager.connect()

                # Test best practices compliance
                call_kwargs = mock_from_url.call_args[1]
                assert call_kwargs['max_connections'] <= 20  # Reasonable limit
                assert call_kwargs['retry_on_timeout'] is True  # Resilience
                assert 'decode_responses' in call_kwargs  # Explicit setting
                assert 'encoding' in call_kwargs  # Explicit encoding

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_error_handling_compliance(self, cache_manager, mock_settings):
        """RED: Test that error handling follows best practices"""
        with patch('redis.ConnectionPool.from_url') as mock_from_url:
            mock_from_url.side_effect = Exception("Test error")

            with patch('app.core.redis.cache.logger') as mock_logger:
                with pytest.raises(Exception):
                    await cache_manager.connect()

                # Test that errors are properly logged
                mock_logger.error.assert_called()

                # Test that exception is re-raised (fail-fast principle)
                assert mock_from_url.call_count == 1

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_class_design_compliance(self, cache_manager):
        """RED: Test that class design follows Python best practices"""
        # Test inheritance
        assert isinstance(cache_manager, RedisManager)

        # Test method presence
        assert hasattr(cache_manager, 'connect')
        assert callable(cache_manager.connect)

        # Test that connect method is async
        import inspect
        assert inspect.iscoroutinefunction(cache_manager.connect)


if __name__ == "__main__":
    # Run the RED phase tests
    pytest.main([__file__, "-v", "-m", "red_test"])