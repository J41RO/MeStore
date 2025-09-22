# app/core/performance_middleware.py
# PERFORMANCE_MIDDLEWARE: Enterprise-grade performance optimization for FastAPI
# Target: API responses <200ms, Memory usage optimized, Caching implemented

import time
import logging
import asyncio
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import json
import hashlib
from contextlib import asynccontextmanager
import tracemalloc
import psutil
import os

# Performance monitoring logger
perf_logger = logging.getLogger("performance")

class PerformanceMiddleware:
    """
    High-performance middleware for API optimization
    - Response time monitoring
    - Automatic caching
    - Memory usage tracking
    - Database query optimization
    """

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.cache_ttl = 300  # 5 minutes default
        self.response_time_threshold = 200  # 200ms threshold
        self.memory_threshold = 100 * 1024 * 1024  # 100MB

    async def init_redis(self):
        """Initialize Redis connection for caching"""
        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                decode_responses=True,
                socket_connect_timeout=1.0,
                socket_timeout=1.0,
                retry_on_timeout=True,
                health_check_interval=30
            )
            await self.redis_client.ping()
            perf_logger.info("Redis connection established for performance caching")
        except Exception as e:
            perf_logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None

    def generate_cache_key(self, request: Request) -> str:
        """Generate cache key from request"""
        # Create key from method, path, and query parameters
        key_data = f"{request.method}:{request.url.path}:{str(request.query_params)}"

        # Add user context for personalized responses
        user_id = getattr(request.state, 'user_id', 'anonymous')
        key_data += f":{user_id}"

        # Hash for consistent key length
        return hashlib.md5(key_data.encode()).hexdigest()

    async def get_cached_response(self, cache_key: str) -> Optional[Dict[Any, Any]]:
        """Retrieve cached response"""
        if not self.redis_client:
            return None

        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            perf_logger.warning(f"Cache retrieval failed: {e}")

        return None

    async def set_cached_response(self, cache_key: str, response_data: Dict[Any, Any], ttl: int = None):
        """Store response in cache"""
        if not self.redis_client:
            return

        try:
            cache_ttl = ttl or self.cache_ttl
            await self.redis_client.setex(
                cache_key,
                cache_ttl,
                json.dumps(response_data, default=str)
            )
        except Exception as e:
            perf_logger.warning(f"Cache storage failed: {e}")

    def should_cache_response(self, request: Request, response: Response) -> bool:
        """Determine if response should be cached"""
        # Only cache GET requests
        if request.method != "GET":
            return False

        # Don't cache error responses
        if response.status_code >= 400:
            return False

        # Don't cache real-time endpoints
        no_cache_paths = ['/ws/', '/sse/', '/api/v1/auth/me', '/api/v1/analytics/realtime']
        if any(path in str(request.url.path) for path in no_cache_paths):
            return False

        return True

    @asynccontextmanager
    async def track_memory_usage(self):
        """Context manager for memory usage tracking"""
        tracemalloc.start()
        process = psutil.Process(os.getpid())

        # Initial memory snapshot
        initial_memory = process.memory_info().rss

        try:
            yield
        finally:
            # Final memory measurement
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory

            if memory_increase > self.memory_threshold:
                perf_logger.warning(f"High memory usage detected: {memory_increase / 1024 / 1024:.2f}MB increase")

            # Get tracemalloc snapshot
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')

            # Log top memory consumers in development
            if os.getenv('ENVIRONMENT') == 'development' and top_stats:
                perf_logger.debug("Top memory consumers:")
                for stat in top_stats[:3]:
                    perf_logger.debug(f"  {stat}")

            tracemalloc.stop()

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Main middleware function"""
        start_time = time.time()

        # Generate cache key for GET requests
        cache_key = None
        if request.method == "GET":
            cache_key = self.generate_cache_key(request)

            # Try to get cached response
            cached_response = await self.get_cached_response(cache_key)
            if cached_response:
                response = JSONResponse(
                    content=cached_response['content'],
                    status_code=cached_response['status_code'],
                    headers=cached_response.get('headers', {})
                )
                response.headers["X-Cache"] = "HIT"
                return response

        # Track memory usage during request processing
        async with self.track_memory_usage():
            try:
                # Process request
                response = await call_next(request)

            except Exception as e:
                # Log exception and return error response
                perf_logger.error(f"Request processing failed: {e}")
                response = JSONResponse(
                    content={"error": "Internal server error"},
                    status_code=500
                )

        # Calculate response time
        process_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Add performance headers
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        response.headers["X-Cache"] = "MISS"

        # Log slow responses
        if process_time > self.response_time_threshold:
            perf_logger.warning(
                f"Slow response detected: {request.method} {request.url.path} "
                f"took {process_time:.2f}ms (threshold: {self.response_time_threshold}ms)"
            )

        # Cache successful GET responses
        if cache_key and self.should_cache_response(request, response):
            try:
                # Prepare response for caching
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk

                response_data = {
                    "content": json.loads(response_body.decode()) if response_body else {},
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }

                # Cache with dynamic TTL based on endpoint
                ttl = self.get_cache_ttl(request.url.path)
                await self.set_cached_response(cache_key, response_data, ttl)

                # Recreate response since body_iterator was consumed
                response = JSONResponse(
                    content=response_data['content'],
                    status_code=response_data['status_code'],
                    headers=response_data['headers']
                )
                response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
                response.headers["X-Cache"] = "MISS"

            except Exception as e:
                perf_logger.warning(f"Response caching failed: {e}")

        return response

    def get_cache_ttl(self, path: str) -> int:
        """Get cache TTL based on endpoint"""
        cache_config = {
            '/api/v1/products/': 600,      # 10 minutes for products
            '/api/v1/categories/': 1800,   # 30 minutes for categories
            '/api/v1/vendors/': 300,       # 5 minutes for vendors
            '/api/v1/analytics/': 60,      # 1 minute for analytics
            '/api/v1/reports/': 900,       # 15 minutes for reports
        }

        for pattern, ttl in cache_config.items():
            if pattern in path:
                return ttl

        return self.cache_ttl  # Default TTL

class DatabaseOptimizationMiddleware:
    """
    Middleware for database query optimization
    """

    def __init__(self):
        self.query_threshold = 50  # 50ms for database queries

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Track database query performance"""

        # Add database query monitoring context
        request.state.db_queries = []
        request.state.db_query_start_time = time.time()

        response = await call_next(request)

        # Calculate total database time
        total_db_time = getattr(request.state, 'total_db_time', 0)

        if total_db_time > self.query_threshold:
            perf_logger.warning(
                f"Slow database queries detected: {request.method} {request.url.path} "
                f"spent {total_db_time:.2f}ms in database queries"
            )

        response.headers["X-DB-Time"] = f"{total_db_time:.2f}ms"

        return response

class CompressionMiddleware:
    """
    Response compression middleware for bandwidth optimization
    """

    def __init__(self):
        self.min_size = 1024  # Only compress responses > 1KB

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Apply compression to responses"""
        response = await call_next(request)

        # Check if client accepts compression
        accept_encoding = request.headers.get('accept-encoding', '')

        if 'gzip' in accept_encoding and hasattr(response, 'body'):
            try:
                import gzip

                # Get response body
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk

                # Compress if body is large enough
                if len(body) > self.min_size:
                    compressed_body = gzip.compress(body)

                    # Only use compression if it reduces size
                    if len(compressed_body) < len(body):
                        response.headers["content-encoding"] = "gzip"
                        response.headers["content-length"] = str(len(compressed_body))

                        # Create new response with compressed body
                        response = Response(
                            content=compressed_body,
                            status_code=response.status_code,
                            headers=dict(response.headers),
                            media_type=response.media_type
                        )

            except Exception as e:
                perf_logger.warning(f"Compression failed: {e}")

        return response

# Global instances
performance_middleware = PerformanceMiddleware()
db_optimization_middleware = DatabaseOptimizationMiddleware()
compression_middleware = CompressionMiddleware()

# Initialization function
async def init_performance_middleware():
    """Initialize performance middleware with Redis connection"""
    await performance_middleware.init_redis()

# Performance monitoring utilities
def track_db_query(request: Request, query_time: float):
    """Track database query performance"""
    if hasattr(request.state, 'db_queries'):
        request.state.db_queries.append(query_time)

        # Update total database time
        total_time = getattr(request.state, 'total_db_time', 0)
        request.state.total_db_time = total_time + query_time

async def optimize_db_query(query_func, *args, **kwargs):
    """Wrapper for database queries with performance tracking"""
    start_time = time.time()

    try:
        result = await query_func(*args, **kwargs)
        return result
    finally:
        query_time = (time.time() - start_time) * 1000

        if query_time > 50:  # Log slow queries
            perf_logger.warning(f"Slow database query: {query_time:.2f}ms")

# Export middleware stack
performance_middleware_stack = [
    performance_middleware,
    db_optimization_middleware,
    compression_middleware
]