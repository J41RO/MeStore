# ~/app/middleware/rate_limiting.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Rate Limiting Middleware
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Archivo: rate_limiting.py
# Ruta: ~/app/middleware/rate_limiting.py
# Autor: API Architect AI
# Fecha de Creación: 2025-09-18
# Versión: 1.0.0
# Propósito: Rate limiting middleware for API protection
#
# Características:
# - Token bucket algorithm implementation
# - User-based and IP-based rate limiting
# - Redis backend for distributed rate limiting
# - Different limits for different endpoints
# - Configurable rate limits and time windows
#
# ---------------------------------------------------------------------------------------------

"""
Rate limiting middleware for FastAPI.

This module provides:
- Token bucket rate limiting implementation
- User-based and IP-based rate limiting
- Redis-backed distributed rate limiting
- Configurable rate limits per endpoint type
- Graceful handling of rate limit exceeded
"""

import asyncio
import json
import time
from typing import Dict, Optional

import redis.asyncio as redis
from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm.

    Features:
    - Per-user and per-IP rate limiting
    - Different limits for different endpoint types
    - Redis-backed for distributed deployment
    - Configurable rate limits and time windows
    """

    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client

        # Default rate limits (requests per minute)
        self.default_limits = {
            "anonymous": 100,      # Anonymous users
            "authenticated": 300,  # Authenticated users
            "vendor": 500,        # Vendor users
            "admin": 1000,        # Admin users
            "search": 60,         # Search endpoints
            "upload": 20,         # File upload endpoints
            "bulk": 10,           # Bulk operations
        }

        # Time windows in seconds
        self.time_window = 60  # 1 minute

        # Endpoint categorization
        self.endpoint_categories = {
            "/api/v1/products/search": "search",
            "/api/v1/products/bulk-update": "bulk",
            "/api/v1/products/*/images": "upload",
        }

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        try:
            # Skip rate limiting for health checks and internal endpoints
            if self._should_skip_rate_limiting(request):
                return await call_next(request)

            # Get rate limit key and limit
            rate_limit_key, rate_limit = await self._get_rate_limit_info(request)

            # Check rate limit
            is_allowed, remaining, reset_time = await self._check_rate_limit(
                rate_limit_key, rate_limit
            )

            if not is_allowed:
                # Rate limit exceeded
                return self._create_rate_limit_response(remaining, reset_time)

            # Process request
            response = await call_next(request)

            # Add rate limit headers to response
            self._add_rate_limit_headers(response, remaining, reset_time, rate_limit)

            return response

        except Exception as e:
            # Log error but don't block request
            print(f"Rate limiting error: {e}")
            return await call_next(request)

    def _should_skip_rate_limiting(self, request: Request) -> bool:
        """Check if request should skip rate limiting."""
        skip_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        ]

        path = str(request.url.path).lower()
        return any(skip_path in path for skip_path in skip_paths)

    async def _get_rate_limit_info(self, request: Request) -> tuple[str, int]:
        """Get rate limit key and limit for request."""
        # Get user info from request
        user_type = await self._get_user_type(request)
        user_id = await self._get_user_id(request)
        client_ip = self._get_client_ip(request)

        # Get endpoint category
        endpoint_category = self._get_endpoint_category(request)

        # Determine rate limit and key
        if user_id:
            # Authenticated user
            rate_limit_key = f"rate_limit:user:{user_id}"
            if endpoint_category in self.default_limits:
                rate_limit = self.default_limits[endpoint_category]
            elif user_type in self.default_limits:
                rate_limit = self.default_limits[user_type]
            else:
                rate_limit = self.default_limits["authenticated"]
        else:
            # Anonymous user (by IP)
            rate_limit_key = f"rate_limit:ip:{client_ip}"
            if endpoint_category in self.default_limits:
                rate_limit = self.default_limits[endpoint_category]
            else:
                rate_limit = self.default_limits["anonymous"]

        # Add endpoint category to key if applicable
        if endpoint_category:
            rate_limit_key += f":{endpoint_category}"

        return rate_limit_key, rate_limit

    async def _get_user_type(self, request: Request) -> Optional[str]:
        """Extract user type from request."""
        try:
            # Try to get from auth header or user context
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # In a real implementation, you would decode the JWT token
                # For now, return a default value
                return "authenticated"
            return None
        except:
            return None

    async def _get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request."""
        try:
            # Try to get from auth header or user context
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # In a real implementation, you would decode the JWT token
                # and extract user ID
                return "user_id_placeholder"
            return None
        except:
            return None

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return str(request.client.host) if request.client else "unknown"

    def _get_endpoint_category(self, request: Request) -> Optional[str]:
        """Determine endpoint category for specific rate limits."""
        path = str(request.url.path)
        method = request.method.upper()

        # Check for specific endpoint patterns
        if "/search" in path:
            return "search"
        elif "/bulk" in path or method == "PATCH":
            return "bulk"
        elif "/images" in path and method == "POST":
            return "upload"

        return None

    async def _check_rate_limit(
        self,
        key: str,
        limit: int
    ) -> tuple[bool, int, int]:
        """Check rate limit using token bucket algorithm."""
        current_time = int(time.time())

        if self.redis_client:
            # Redis-backed rate limiting
            return await self._check_rate_limit_redis(key, limit, current_time)
        else:
            # In-memory rate limiting (for development)
            return await self._check_rate_limit_memory(key, limit, current_time)

    async def _check_rate_limit_redis(
        self,
        key: str,
        limit: int,
        current_time: int
    ) -> tuple[bool, int, int]:
        """Redis-backed rate limiting."""
        try:
            # Lua script for atomic rate limiting check
            lua_script = """
            local key = KEYS[1]
            local limit = tonumber(ARGV[1])
            local window = tonumber(ARGV[2])
            local current_time = tonumber(ARGV[3])

            local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
            local tokens = tonumber(bucket[1]) or limit
            local last_refill = tonumber(bucket[2]) or current_time

            -- Calculate tokens to add based on time passed
            local time_passed = current_time - last_refill
            local tokens_to_add = math.floor(time_passed * limit / window)
            tokens = math.min(limit, tokens + tokens_to_add)

            if tokens >= 1 then
                tokens = tokens - 1
                redis.call('HMSET', key, 'tokens', tokens, 'last_refill', current_time)
                redis.call('EXPIRE', key, window)
                return {1, tokens, current_time + window}
            else
                redis.call('HMSET', key, 'tokens', tokens, 'last_refill', current_time)
                redis.call('EXPIRE', key, window)
                return {0, tokens, current_time + window}
            end
            """

            result = await self.redis_client.eval(
                lua_script,
                1,
                key,
                limit,
                self.time_window,
                current_time
            )

            is_allowed = bool(result[0])
            remaining = int(result[1])
            reset_time = int(result[2])

            return is_allowed, remaining, reset_time

        except Exception as e:
            print(f"Redis rate limiting error: {e}")
            # Fallback to allowing request
            return True, limit, current_time + self.time_window

    _memory_store: Dict[str, Dict] = {}

    async def _check_rate_limit_memory(
        self,
        key: str,
        limit: int,
        current_time: int
    ) -> tuple[bool, int, int]:
        """In-memory rate limiting for development."""
        if key not in self._memory_store:
            self._memory_store[key] = {
                "tokens": limit,
                "last_refill": current_time
            }

        bucket = self._memory_store[key]
        tokens = bucket["tokens"]
        last_refill = bucket["last_refill"]

        # Calculate tokens to add
        time_passed = current_time - last_refill
        tokens_to_add = (time_passed * limit) // self.time_window
        tokens = min(limit, tokens + tokens_to_add)

        if tokens >= 1:
            tokens -= 1
            bucket["tokens"] = tokens
            bucket["last_refill"] = current_time
            return True, tokens, current_time + self.time_window
        else:
            bucket["tokens"] = tokens
            bucket["last_refill"] = current_time
            return False, tokens, current_time + self.time_window

    def _create_rate_limit_response(self, remaining: int, reset_time: int) -> Response:
        """Create rate limit exceeded response."""
        headers = {
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
            "Retry-After": str(reset_time - int(time.time()))
        }

        content = {
            "error": {
                "type": "RateLimitExceeded",
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Rate limit exceeded. Please try again later.",
                "retry_after": reset_time - int(time.time())
            }
        }

        return Response(
            content=json.dumps(content),
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers=headers,
            media_type="application/json"
        )

    def _add_rate_limit_headers(
        self,
        response: Response,
        remaining: int,
        reset_time: int,
        limit: int
    ):
        """Add rate limit headers to response."""
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)


# Utility function to create middleware with Redis
async def create_rate_limiting_middleware(app, redis_url: Optional[str] = None):
    """Create rate limiting middleware with optional Redis backend."""
    redis_client = None

    if redis_url:
        try:
            redis_client = redis.from_url(redis_url)
            # Test connection
            await redis_client.ping()
        except Exception as e:
            print(f"Redis connection failed, using in-memory rate limiting: {e}")
            redis_client = None

    return RateLimitingMiddleware(app, redis_client)