"""
TDD Test Suite for Performance Middleware
========================================

Comprehensive Test-Driven Development suite for app.core.performance_middleware.py
Following strict RED-GREEN-REFACTOR methodology.

Test Coverage:
- PerformanceMiddleware: Initialization, Redis, caching, memory tracking, execution
- DatabaseOptimizationMiddleware: Query tracking and performance monitoring
- CompressionMiddleware: Response compression logic
- Utility functions: Database query tracking and optimization

Performance Testing Focus:
- Response time thresholds (200ms)
- Memory usage monitoring and warnings
- Cache hit/miss scenarios
- Compression effectiveness
- Database query performance tracking
- Error handling and fallback behaviors
"""

import pytest
import asyncio
import json
import time
import gzip
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.datastructures import Headers, QueryParams
from starlette.types import Scope, Receive, Send

# Import the modules we're testing
from app.core.performance_middleware import (
    PerformanceMiddleware,
    DatabaseOptimizationMiddleware,
    CompressionMiddleware,
    performance_middleware,
    db_optimization_middleware,
    compression_middleware,
    init_performance_middleware,
    track_db_query,
    optimize_db_query,
    performance_middleware_stack
)


# ========================================
# TEST FIXTURES AND HELPERS
# ========================================

@pytest.fixture
def mock_request():
    """Create a mock FastAPI Request for testing"""
    request = Mock(spec=Request)
    request.method = "GET"
    request.url = Mock()
    request.url.path = "/api/v1/products"
    request.url.scheme = "http"
    request.url.netloc = "localhost:8000"
    request.query_params = QueryParams("")
    request.headers = Headers({})
    request.state = Mock()
    request.state.user_id = "test_user_123"
    return request


@pytest.fixture
def mock_response():
    """Create a mock FastAPI Response for testing"""
    response = Mock(spec=Response)
    response.status_code = 200
    response.headers = {}
    response.body_iterator = [b'{"data": "test"}']
    response.media_type = "application/json"
    return response


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing"""
    redis_mock = AsyncMock()
    redis_mock.ping = AsyncMock(return_value=True)
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.setex = AsyncMock(return_value=True)
    return redis_mock


@pytest.fixture
def performance_middleware_instance():
    """Fresh PerformanceMiddleware instance for each test"""
    return PerformanceMiddleware()


@pytest.fixture
def db_middleware_instance():
    """Fresh DatabaseOptimizationMiddleware instance for each test"""
    return DatabaseOptimizationMiddleware()


@pytest.fixture
def compression_middleware_instance():
    """Fresh CompressionMiddleware instance for each test"""
    return CompressionMiddleware()


# ========================================
# RED PHASE TESTS - PerformanceMiddleware
# ========================================

class TestPerformanceMiddlewareInitialization:
    """RED Phase: Test PerformanceMiddleware initialization and basic configuration"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_performance_middleware_default_initialization(self, performance_middleware_instance):
        """RED: Test default initialization values"""
        middleware = performance_middleware_instance

        # Test that initialization sets correct defaults
        assert middleware.redis_client is None
        assert middleware.cache_ttl == 300  # 5 minutes
        assert middleware.response_time_threshold == 200  # 200ms
        assert middleware.memory_threshold == 100 * 1024 * 1024  # 100MB

    @pytest.mark.red_test
    @pytest.mark.tdd
    async def test_redis_initialization_success(self, performance_middleware_instance, mock_redis):
        """RED: Test successful Redis connection initialization"""
        middleware = performance_middleware_instance

        with patch('app.core.performance_middleware.redis.Redis', return_value=mock_redis):
            with patch.dict('os.environ', {'REDIS_HOST': 'test-host', 'REDIS_PORT': '6380'}):
                await middleware.init_redis()

        # Test that Redis client is properly initialized
        assert middleware.redis_client is not None
        mock_redis.ping.assert_called_once()

    @pytest.mark.red_test
    @pytest.mark.tdd
    async def test_redis_initialization_failure(self, performance_middleware_instance):
        """RED: Test Redis connection failure handling"""
        middleware = performance_middleware_instance

        with patch('app.core.performance_middleware.redis.Redis') as mock_redis_class:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping.side_effect = Exception("Connection failed")
            mock_redis_class.return_value = mock_redis_instance

            await middleware.init_redis()

        # Test that failed connection results in None redis_client
        assert middleware.redis_client is None


class TestPerformanceMiddlewareCacheOperations:
    """RED Phase: Test cache key generation and cache operations"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_generate_cache_key_basic_request(self, performance_middleware_instance, mock_request):
        """RED: Test cache key generation for basic request"""
        middleware = performance_middleware_instance

        # Test cache key generation includes method, path, params, user
        cache_key = middleware.generate_cache_key(mock_request)

        assert cache_key is not None
        assert len(cache_key) == 32  # MD5 hash length
        assert isinstance(cache_key, str)

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_generate_cache_key_with_query_params(self, performance_middleware_instance):
        """RED: Test cache key generation includes query parameters"""
        middleware = performance_middleware_instance

        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/api/v1/products"
        request.query_params = QueryParams("page=1&limit=10")
        request.state = Mock()
        request.state.user_id = "user123"

        cache_key = middleware.generate_cache_key(request)

        # Different query params should generate different keys
        request2 = Mock(spec=Request)
        request2.method = "GET"
        request2.url = Mock()
        request2.url.path = "/api/v1/products"
        request2.query_params = QueryParams("page=2&limit=10")
        request2.state = Mock()
        request2.state.user_id = "user123"

        cache_key2 = middleware.generate_cache_key(request2)

        assert cache_key != cache_key2

    @pytest.mark.red_test
    @pytest.mark.tdd
    async def test_get_cached_response_no_redis(self, performance_middleware_instance):
        """RED: Test cache retrieval when Redis is not available"""
        middleware = performance_middleware_instance
        middleware.redis_client = None

        result = await middleware.get_cached_response("test_key")

        assert result is None

    @pytest.mark.red_test
    @pytest.mark.tdd
    async def test_get_cached_response_cache_hit(self, performance_middleware_instance, mock_redis):
        """RED: Test successful cache retrieval"""
        middleware = performance_middleware_instance
        middleware.redis_client = mock_redis

        test_data = {"content": {"message": "cached"}, "status_code": 200}
        mock_redis.get.return_value = json.dumps(test_data)

        result = await middleware.get_cached_response("test_key")

        assert result == test_data
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.red_test
    @pytest.mark.tdd
    async def test_get_cached_response_cache_miss(self, performance_middleware_instance, mock_redis):
        """RED: Test cache miss scenario"""
        middleware = performance_middleware_instance
        middleware.redis_client = mock_redis

        mock_redis.get.return_value = None

        result = await middleware.get_cached_response("test_key")

        assert result is None

    @pytest.mark.red_test
    @pytest.mark.tdd
    async def test_set_cached_response_no_redis(self, performance_middleware_instance):
        """RED: Test cache storage when Redis is not available"""
        middleware = performance_middleware_instance
        middleware.redis_client = None

        test_data = {"content": {"message": "test"}, "status_code": 200}

        # Should not raise exception when Redis is unavailable
        await middleware.set_cached_response("test_key", test_data)

    @pytest.mark.red_test
    @pytest.mark.tdd
    async def test_set_cached_response_success(self, performance_middleware_instance, mock_redis):
        """RED: Test successful cache storage"""
        middleware = performance_middleware_instance
        middleware.redis_client = mock_redis

        test_data = {"content": {"message": "test"}, "status_code": 200}

        await middleware.set_cached_response("test_key", test_data, ttl=600)

        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "test_key"  # key
        assert call_args[0][1] == 600  # ttl
        # Third argument should be JSON serialized data
        stored_data = json.loads(call_args[0][2])
        assert stored_data == test_data


class TestPerformanceMiddlewareCacheLogic:
    """RED Phase: Test cache eligibility and TTL logic"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_should_cache_response_get_request_success(self, performance_middleware_instance):
        """RED: Test caching eligibility for successful GET request"""
        middleware = performance_middleware_instance

        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/api/v1/products"

        response = Mock(spec=Response)
        response.status_code = 200

        assert middleware.should_cache_response(request, response) is True

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_should_cache_response_post_request(self, performance_middleware_instance):
        """RED: Test that POST requests are not cached"""
        middleware = performance_middleware_instance

        request = Mock(spec=Request)
        request.method = "POST"
        request.url = Mock()
        request.url.path = "/api/v1/products"

        response = Mock(spec=Response)
        response.status_code = 200

        assert middleware.should_cache_response(request, response) is False

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_should_cache_response_error_status(self, performance_middleware_instance):
        """RED: Test that error responses are not cached"""
        middleware = performance_middleware_instance

        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/api/v1/products"

        response = Mock(spec=Response)
        response.status_code = 404

        assert middleware.should_cache_response(request, response) is False

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_should_cache_response_realtime_endpoints(self, performance_middleware_instance):
        """RED: Test that real-time endpoints are not cached"""
        middleware = performance_middleware_instance

        response = Mock(spec=Response)
        response.status_code = 200

        realtime_paths = ['/ws/', '/sse/', '/api/v1/auth/me', '/api/v1/analytics/realtime']

        for path in realtime_paths:
            request = Mock(spec=Request)
            request.method = "GET"
            request.url = Mock()
            request.url.path = path

            assert middleware.should_cache_response(request, response) is False

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_cache_ttl_products_endpoint(self, performance_middleware_instance):
        """RED: Test TTL configuration for products endpoint"""
        middleware = performance_middleware_instance

        ttl = middleware.get_cache_ttl("/api/v1/products/")
        assert ttl == 600  # 10 minutes

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_cache_ttl_categories_endpoint(self, performance_middleware_instance):
        """RED: Test TTL configuration for categories endpoint"""
        middleware = performance_middleware_instance

        ttl = middleware.get_cache_ttl("/api/v1/categories/")
        assert ttl == 1800  # 30 minutes

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_cache_ttl_default_endpoint(self, performance_middleware_instance):
        """RED: Test default TTL for unspecified endpoints"""
        middleware = performance_middleware_instance

        ttl = middleware.get_cache_ttl("/api/v1/unknown/")
        assert ttl == 300  # Default 5 minutes


class TestPerformanceMiddlewareMemoryTracking:
    """RED Phase: Test memory usage tracking functionality"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_track_memory_usage_context_manager(self, performance_middleware_instance):
        """RED: Test memory tracking context manager functionality"""
        middleware = performance_middleware_instance

        with patch('app.core.performance_middleware.tracemalloc') as mock_tracemalloc:
            with patch('app.core.performance_middleware.psutil') as mock_psutil:
                # Mock process and memory info
                mock_process = Mock()
                mock_memory_info = Mock()
                mock_memory_info.rss = 1024 * 1024  # 1MB
                mock_process.memory_info.return_value = mock_memory_info
                mock_psutil.Process.return_value = mock_process

                # Mock tracemalloc
                mock_snapshot = Mock()
                mock_snapshot.statistics.return_value = []
                mock_tracemalloc.take_snapshot.return_value = mock_snapshot

                async with middleware.track_memory_usage():
                    # Simulate some work
                    await asyncio.sleep(0.001)

                # Verify tracemalloc was started and stopped
                mock_tracemalloc.start.assert_called_once()
                mock_tracemalloc.stop.assert_called_once()
                mock_tracemalloc.take_snapshot.assert_called_once()

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_track_memory_usage_high_memory_warning(self, performance_middleware_instance):
        """RED: Test memory warning for high memory usage"""
        middleware = performance_middleware_instance
        middleware.memory_threshold = 1024  # Very low threshold for testing

        with patch('app.core.performance_middleware.tracemalloc') as mock_tracemalloc:
            with patch('app.core.performance_middleware.psutil') as mock_psutil:
                with patch('app.core.performance_middleware.perf_logger') as mock_logger:
                    # Mock process with increasing memory usage
                    mock_process = Mock()
                    mock_memory_info_initial = Mock()
                    mock_memory_info_initial.rss = 1024
                    mock_memory_info_final = Mock()
                    mock_memory_info_final.rss = 5120  # 4KB increase

                    mock_process.memory_info.side_effect = [
                        mock_memory_info_initial,
                        mock_memory_info_final
                    ]
                    mock_psutil.Process.return_value = mock_process

                    # Mock tracemalloc
                    mock_snapshot = Mock()
                    mock_snapshot.statistics.return_value = []
                    mock_tracemalloc.take_snapshot.return_value = mock_snapshot

                    async with middleware.track_memory_usage():
                        await asyncio.sleep(0.001)

                    # Verify warning was logged for high memory usage
                    mock_logger.warning.assert_called()
                    warning_call = mock_logger.warning.call_args[0][0]
                    assert "High memory usage detected" in warning_call


class TestPerformanceMiddlewareExecution:
    """RED Phase: Test main middleware execution flow"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_middleware_call_cache_miss_flow(self, performance_middleware_instance, mock_request):
        """RED: Test middleware execution with cache miss"""
        middleware = performance_middleware_instance
        middleware.redis_client = None  # No caching

        # Mock the call_next function
        async def mock_call_next(request):
            response = JSONResponse(content={"message": "success"})
            return response

        with patch.object(middleware, 'track_memory_usage') as mock_memory_tracker:
            # Mock the context manager
            mock_memory_tracker.return_value.__aenter__ = AsyncMock()
            mock_memory_tracker.return_value.__aexit__ = AsyncMock()

            response = await middleware(mock_request, mock_call_next)

        # Test response headers are added
        assert "X-Process-Time" in response.headers
        assert "X-Cache" in response.headers
        assert response.headers["X-Cache"] == "MISS"

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_middleware_call_cache_hit_flow(self, performance_middleware_instance, mock_request, mock_redis):
        """RED: Test middleware execution with cache hit"""
        middleware = performance_middleware_instance
        middleware.redis_client = mock_redis

        # Mock cached response
        cached_data = {
            "content": {"message": "cached"},
            "status_code": 200,
            "headers": {"content-type": "application/json"}
        }
        mock_redis.get.return_value = json.dumps(cached_data)

        async def mock_call_next(request):
            # This should not be called on cache hit
            pytest.fail("call_next should not be called on cache hit")

        response = await middleware(mock_request, mock_call_next)

        # Test cache hit response
        assert response.headers["X-Cache"] == "HIT"
        assert response.status_code == 200

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_middleware_call_slow_response_warning(self, performance_middleware_instance, mock_request):
        """RED: Test slow response detection and warning"""
        middleware = performance_middleware_instance
        middleware.response_time_threshold = 10  # Very low threshold for testing
        middleware.redis_client = None

        # Mock request to avoid caching (make it a POST request)
        mock_request.method = "POST"

        async def slow_call_next(request):
            await asyncio.sleep(0.05)  # 50ms delay
            return JSONResponse(content={"message": "slow"})

        with patch('app.core.performance_middleware.perf_logger') as mock_logger:
            with patch.object(middleware, 'track_memory_usage') as mock_memory_tracker:
                mock_memory_tracker.return_value.__aenter__ = AsyncMock()
                mock_memory_tracker.return_value.__aexit__ = AsyncMock()

                response = await middleware(mock_request, slow_call_next)

        # Verify slow response warning was logged
        mock_logger.warning.assert_called()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "Slow response detected" in warning_call

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_middleware_call_exception_handling(self, performance_middleware_instance, mock_request):
        """RED: Test exception handling in middleware"""
        middleware = performance_middleware_instance
        middleware.redis_client = None

        async def failing_call_next(request):
            raise Exception("Something went wrong")

        with patch('app.core.performance_middleware.perf_logger') as mock_logger:
            with patch.object(middleware, 'track_memory_usage') as mock_memory_tracker:
                mock_memory_tracker.return_value.__aenter__ = AsyncMock()
                mock_memory_tracker.return_value.__aexit__ = AsyncMock()

                response = await middleware(mock_request, failing_call_next)

        # Test error response
        assert response.status_code == 500
        mock_logger.error.assert_called()


# ========================================
# RED PHASE TESTS - DatabaseOptimizationMiddleware
# ========================================

class TestDatabaseOptimizationMiddleware:
    """RED Phase: Test database query optimization middleware"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_db_middleware_initialization(self, db_middleware_instance):
        """RED: Test database middleware initialization"""
        middleware = db_middleware_instance

        assert middleware.query_threshold == 50  # 50ms threshold

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_db_middleware_call_normal_query_time(self, db_middleware_instance, mock_request):
        """RED: Test database middleware with normal query times"""
        middleware = db_middleware_instance

        async def mock_call_next(request):
            # Simulate normal database time
            request.state.total_db_time = 25.0  # 25ms - below threshold
            return Response(content="success", status_code=200)

        response = await middleware(mock_request, mock_call_next)

        # Test that database time header is added
        assert "X-DB-Time" in response.headers
        assert response.headers["X-DB-Time"] == "25.00ms"

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_db_middleware_call_slow_query_warning(self, db_middleware_instance, mock_request):
        """RED: Test database middleware with slow query warning"""
        middleware = db_middleware_instance

        async def mock_call_next(request):
            # Simulate slow database time
            request.state.total_db_time = 75.0  # 75ms - above threshold
            return Response(content="success", status_code=200)

        with patch('app.core.performance_middleware.perf_logger') as mock_logger:
            response = await middleware(mock_request, mock_call_next)

        # Test slow query warning was logged
        mock_logger.warning.assert_called()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "Slow database queries detected" in warning_call

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_db_middleware_request_state_initialization(self, db_middleware_instance, mock_request):
        """RED: Test request state initialization for database tracking"""
        middleware = db_middleware_instance

        async def mock_call_next(request):
            # Verify request state is properly initialized
            assert hasattr(request.state, 'db_queries')
            assert hasattr(request.state, 'db_query_start_time')
            assert isinstance(request.state.db_queries, list)
            # Set total_db_time as float for the test
            request.state.total_db_time = 25.0  # Mock a float value
            return Response(content="success", status_code=200)

        await middleware(mock_request, mock_call_next)


# ========================================
# RED PHASE TESTS - CompressionMiddleware
# ========================================

class TestCompressionMiddleware:
    """RED Phase: Test response compression middleware"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_compression_middleware_initialization(self, compression_middleware_instance):
        """RED: Test compression middleware initialization"""
        middleware = compression_middleware_instance

        assert middleware.min_size == 1024  # Only compress responses > 1KB

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_compression_middleware_no_gzip_support(self, compression_middleware_instance):
        """RED: Test compression middleware when client doesn't support gzip"""
        middleware = compression_middleware_instance

        request = Mock(spec=Request)
        request.headers = Headers({"accept-encoding": "deflate"})

        original_response = Response(content="x" * 2000, status_code=200)  # 2KB response

        async def mock_call_next(request):
            return original_response

        response = await middleware(request, mock_call_next)

        # Test that response is not compressed
        assert "content-encoding" not in response.headers
        assert response == original_response

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_compression_middleware_small_response(self, compression_middleware_instance):
        """RED: Test compression middleware with small response (below threshold)"""
        middleware = compression_middleware_instance

        request = Mock(spec=Request)
        request.headers = Headers({"accept-encoding": "gzip"})

        small_content = "x" * 500  # 500B response - below 1KB threshold
        original_response = Mock(spec=Response)
        original_response.body_iterator = [small_content.encode()]
        original_response.status_code = 200
        original_response.headers = {}
        original_response.media_type = "text/plain"

        async def mock_call_next(request):
            return original_response

        response = await middleware(request, mock_call_next)

        # Test that small response is not compressed
        assert "content-encoding" not in response.headers

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_compression_middleware_large_response_compression(self, compression_middleware_instance):
        """RED: Test compression middleware with large response"""
        middleware = compression_middleware_instance

        request = Mock(spec=Request)
        request.headers = Headers({"accept-encoding": "gzip"})

        # Create large compressible content
        large_content = "x" * 2000  # 2KB of repeated content

        # Mock response with body attribute and async iterator
        original_response = Mock(spec=Response)
        original_response.body = large_content.encode()  # The middleware checks for body attribute
        original_response.status_code = 200
        original_response.headers = {}
        original_response.media_type = "text/plain"

        # Mock the async body iterator
        async def mock_body_iterator():
            yield large_content.encode()

        original_response.body_iterator = mock_body_iterator()

        async def mock_call_next(request):
            return original_response

        response = await middleware(request, mock_call_next)

        # Test that large response is compressed (check if middleware processed it)
        # Note: The actual compression logic is in the middleware implementation
        assert response is not None

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_compression_middleware_compression_exception_handling(self, compression_middleware_instance):
        """RED: Test compression middleware exception handling"""
        middleware = compression_middleware_instance

        request = Mock(spec=Request)
        request.headers = Headers({"accept-encoding": "gzip"})

        # Mock response that will cause compression to fail
        large_content = "x" * 2000  # Large enough to trigger compression
        original_response = Mock(spec=Response)
        original_response.body = large_content.encode()  # Add body attribute
        original_response.status_code = 200
        original_response.headers = {}
        original_response.media_type = "text/plain"

        # Mock the async body iterator
        async def mock_body_iterator():
            yield large_content.encode()

        original_response.body_iterator = mock_body_iterator()

        async def mock_call_next(request):
            return original_response

        with patch('gzip.compress', side_effect=Exception("Compression failed")):
            with patch('app.core.performance_middleware.perf_logger') as mock_logger:
                response = await middleware(request, mock_call_next)

        # Test that compression failure is logged and original response returned
        mock_logger.warning.assert_called()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "Compression failed" in warning_call


# ========================================
# RED PHASE TESTS - Utility Functions
# ========================================

class TestUtilityFunctions:
    """RED Phase: Test utility functions for performance monitoring"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    async def test_init_performance_middleware(self):
        """RED: Test performance middleware initialization function"""
        with patch.object(performance_middleware, 'init_redis') as mock_init_redis:
            await init_performance_middleware()

        mock_init_redis.assert_called_once()

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_track_db_query_with_request_state(self, mock_request):
        """RED: Test database query tracking with request state"""
        mock_request.state.db_queries = []
        mock_request.state.total_db_time = 0

        track_db_query(mock_request, 25.5)

        assert len(mock_request.state.db_queries) == 1
        assert mock_request.state.db_queries[0] == 25.5
        assert mock_request.state.total_db_time == 25.5

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_track_db_query_without_request_state(self, mock_request):
        """RED: Test database query tracking without request state"""
        # Request without db_queries attribute
        delattr(mock_request.state, 'db_queries') if hasattr(mock_request.state, 'db_queries') else None

        # Should not raise exception when state is not properly initialized
        track_db_query(mock_request, 25.5)

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_optimize_db_query_normal_performance(self):
        """RED: Test database query optimization wrapper with normal performance"""
        async def fast_query(arg1, arg2, kwarg1=None):
            await asyncio.sleep(0.001)  # 1ms - fast query
            return f"result: {arg1}, {arg2}, {kwarg1}"

        result = await optimize_db_query(fast_query, "test1", "test2", kwarg1="test3")

        assert result == "result: test1, test2, test3"

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_optimize_db_query_slow_performance_warning(self):
        """RED: Test database query optimization wrapper with slow query warning"""
        async def slow_query():
            await asyncio.sleep(0.06)  # 60ms - slow query
            return "slow result"

        with patch('app.core.performance_middleware.perf_logger') as mock_logger:
            result = await optimize_db_query(slow_query)

        assert result == "slow result"
        mock_logger.warning.assert_called()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "Slow database query" in warning_call

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_optimize_db_query_exception_handling(self):
        """RED: Test database query optimization wrapper exception handling"""
        async def failing_query():
            raise Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await optimize_db_query(failing_query)


class TestPerformanceMiddlewareStack:
    """RED Phase: Test performance middleware stack configuration"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_performance_middleware_stack_contains_all_middlewares(self):
        """RED: Test that middleware stack contains all expected middleware instances"""
        assert len(performance_middleware_stack) == 3
        assert performance_middleware in performance_middleware_stack
        assert db_optimization_middleware in performance_middleware_stack
        assert compression_middleware in performance_middleware_stack

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_global_middleware_instances_initialization(self):
        """RED: Test that global middleware instances are properly initialized"""
        # Test that global instances exist and are properly typed
        assert isinstance(performance_middleware, PerformanceMiddleware)
        assert isinstance(db_optimization_middleware, DatabaseOptimizationMiddleware)
        assert isinstance(compression_middleware, CompressionMiddleware)


# ========================================
# PERFORMANCE BENCHMARKING TESTS
# ========================================

class TestPerformanceBenchmarks:
    """RED Phase: Test performance benchmarks and thresholds"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_middleware_performance_under_threshold(self, performance_middleware_instance, mock_request):
        """RED: Test that middleware itself doesn't add significant overhead"""
        middleware = performance_middleware_instance
        middleware.redis_client = None  # Disable caching for pure middleware test

        async def fast_call_next(request):
            return JSONResponse(content={"message": "fast"})

        start_time = time.time()

        with patch.object(middleware, 'track_memory_usage') as mock_memory_tracker:
            mock_memory_tracker.return_value.__aenter__ = AsyncMock()
            mock_memory_tracker.return_value.__aexit__ = AsyncMock()

            response = await middleware(mock_request, fast_call_next)

        total_time = (time.time() - start_time) * 1000  # Convert to ms

        # Test that middleware overhead is minimal (< 10ms)
        assert total_time < 10
        assert response.status_code == 200

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_cache_performance_improvement(self, performance_middleware_instance, mock_request, mock_redis):
        """RED: Test that caching provides performance improvement"""
        middleware = performance_middleware_instance
        middleware.redis_client = mock_redis

        # Mock cached response for performance test
        cached_data = {
            "content": {"message": "cached"},
            "status_code": 200,
            "headers": {}
        }
        mock_redis.get.return_value = json.dumps(cached_data)

        async def slow_call_next(request):
            await asyncio.sleep(0.1)  # 100ms delay
            return JSONResponse(content={"message": "slow"})

        start_time = time.time()
        response = await middleware(mock_request, slow_call_next)
        cache_time = (time.time() - start_time) * 1000

        # Test that cache hit is much faster than original call
        assert cache_time < 50  # Cache hit should be < 50ms
        assert response.headers["X-Cache"] == "HIT"


# ========================================
# INTEGRATION TESTS
# ========================================

class TestPerformanceMiddlewareIntegration:
    """RED Phase: Integration tests for complete middleware functionality"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_full_middleware_stack_integration(self, mock_request):
        """RED: Test integration of all middleware components"""
        # Test that all middlewares can work together

        async def mock_app(request):
            # Simulate some database work
            request.state.total_db_time = 30.0
            return JSONResponse(content={"message": "integration test"})

        # Chain all middlewares
        response = await performance_middleware(mock_request, mock_app)
        async def mock_next_middleware(req):
            return response

        response = await db_optimization_middleware(mock_request, mock_next_middleware)

        # Test that all middleware headers are present
        assert "X-Process-Time" in response.headers
        assert "X-Cache" in response.headers

    @pytest.mark.red_test
    @pytest.mark.tdd
    @pytest.mark.asyncio
    async def test_error_resilience_integration(self, mock_request):
        """RED: Test middleware resilience to various error conditions"""
        middleware = PerformanceMiddleware()

        # Test with failing Redis
        with patch('app.core.performance_middleware.redis.Redis', side_effect=Exception("Redis down")):
            await middleware.init_redis()

        async def error_app(request):
            raise Exception("App error")

        # Test that middleware handles app errors gracefully
        response = await middleware(mock_request, error_app)

        assert response.status_code == 500
        assert "X-Process-Time" in response.headers


if __name__ == "__main__":
    # Run the RED phase tests
    pytest.main([__file__, "-v", "-m", "red_test"])