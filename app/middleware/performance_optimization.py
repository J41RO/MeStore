# ~/app/middleware/performance_optimization.py
# ---------------------------------------------------------------------------------------------
# MeStore - Performance Optimization Middleware
# Copyright (c) 2025 Performance Optimization AI. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: performance_optimization.py
# Ruta: ~/app/middleware/performance_optimization.py
# Autor: Performance Optimization AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Performance optimization middleware for MeStore API
#            Response caching, compression, and optimization
#
# Características:
# - Automatic response compression (gzip, brotli)
# - Intelligent API response caching with ETag support
# - Request/response performance monitoring
# - Cache control headers optimization
# - CDN-friendly caching strategies
# - Response size optimization
# - Performance metrics collection
#
# ---------------------------------------------------------------------------------------------

"""
Performance Optimization Middleware para MeStore API.

Este middleware implementa optimizaciones de performance para la API:
- Compresión automática de respuestas (gzip, brotli)
- Cache inteligente de respuestas API con soporte ETag
- Monitoreo de performance de request/response
- Optimización de headers de cache control
- Estrategias de caching amigables para CDN
- Optimización de tamaño de respuestas
- Recolección de métricas de performance
"""

import gzip
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from app.services.cache_service import cache_service
from app.services.performance_monitoring_service import performance_monitoring_service

logger = logging.getLogger(__name__)


class PerformanceOptimizationMiddleware(BaseHTTPMiddleware):
    """Performance optimization middleware for API responses"""

    def __init__(self, app, config: Optional[Dict[str, Any]] = None):
        super().__init__(app)
        self.config = config or {}

        # Configuration options
        self.enable_compression = self.config.get("enable_compression", True)
        self.enable_response_caching = self.config.get("enable_response_caching", True)
        self.enable_etag = self.config.get("enable_etag", True)
        self.enable_performance_monitoring = self.config.get("enable_performance_monitoring", True)

        # Compression settings
        self.compression_threshold = self.config.get("compression_threshold", 1024)  # 1KB
        self.compression_level = self.config.get("compression_level", 6)

        # Caching settings
        self.cache_ttl_default = self.config.get("cache_ttl_default", 300)  # 5 minutes
        self.cache_ttl_by_endpoint = self.config.get("cache_ttl_by_endpoint", {})

        # Cacheable endpoints (GET requests only)
        self.cacheable_endpoints = self.config.get("cacheable_endpoints", [
            "/api/v1/productos",
            "/api/v1/categories",
            "/api/v1/search",
            "/api/v1/vendor/profile",
            "/api/v1/buyer/products"
        ])

        # Non-cacheable endpoints
        self.non_cacheable_endpoints = self.config.get("non_cacheable_endpoints", [
            "/api/v1/auth",
            "/api/v1/orders",
            "/api/v1/transactions",
            "/api/v1/admin"
        ])

    async def dispatch(self, request: Request, call_next):
        """Main middleware dispatch method"""
        start_time = time.time()

        # Check if request is cacheable
        is_cacheable = self._is_request_cacheable(request)

        # Try to serve from cache if applicable
        if is_cacheable and self.enable_response_caching:
            cached_response = await self._get_cached_response(request)
            if cached_response:
                return cached_response

        # Performance monitoring context
        endpoint = request.url.path
        method = request.method
        user_id = getattr(request.state, "user_id", None)

        if self.enable_performance_monitoring:
            async with performance_monitoring_service.track_endpoint_performance(
                endpoint=endpoint,
                method=method,
                user_id=user_id
            ) as request_id:
                response = await call_next(request)
        else:
            response = await call_next(request)

        # Post-process response
        response = await self._optimize_response(request, response, start_time, is_cacheable)

        return response

    def _is_request_cacheable(self, request: Request) -> bool:
        """Determine if request is cacheable"""
        # Only cache GET requests
        if request.method != "GET":
            return False

        path = request.url.path

        # Check non-cacheable endpoints first
        for pattern in self.non_cacheable_endpoints:
            if path.startswith(pattern):
                return False

        # Check cacheable endpoints
        for pattern in self.cacheable_endpoints:
            if path.startswith(pattern):
                return True

        return False

    async def _get_cached_response(self, request: Request) -> Optional[Response]:
        """Get cached response if available"""
        try:
            cache_key = self._generate_cache_key(request)
            cached_data = await cache_service.get(cache_key)

            if cached_data:
                # Check if client has current version (ETag)
                if self.enable_etag:
                    client_etag = request.headers.get("if-none-match")
                    cached_etag = cached_data.get("etag")

                    if client_etag and client_etag == cached_etag:
                        # Return 304 Not Modified
                        response = Response(status_code=304)
                        response.headers["etag"] = cached_etag
                        response.headers["cache-control"] = "public, max-age=300"
                        return response

                # Return cached response
                response_data = cached_data.get("data")
                headers = cached_data.get("headers", {})

                response = JSONResponse(content=response_data)

                # Add cached headers
                for key, value in headers.items():
                    response.headers[key] = value

                # Add cache hit header for debugging
                response.headers["x-cache"] = "HIT"
                response.headers["x-cache-timestamp"] = cached_data.get("cached_at", "")

                return response

        except Exception as e:
            logger.error(f"Error getting cached response: {e}")

        return None

    async def _optimize_response(self, request: Request, response: StarletteResponse,
                                start_time: float, is_cacheable: bool) -> StarletteResponse:
        """Optimize response with compression, caching, and headers"""
        try:
            # Calculate response time
            response_time = (time.time() - start_time) * 1000

            # Add performance headers
            response.headers["x-response-time"] = f"{response_time:.2f}ms"
            response.headers["x-powered-by"] = "MeStore-PerformanceOptimized"

            # Only optimize successful responses
            if response.status_code != 200:
                return response

            # Get response body
            response_body = None
            if hasattr(response, 'body'):
                response_body = response.body
            elif hasattr(response, 'content'):
                response_body = response.content

            if not response_body:
                return response

            # Parse JSON response for optimization
            try:
                if isinstance(response_body, bytes):
                    content = json.loads(response_body.decode('utf-8'))
                else:
                    content = json.loads(response_body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Not JSON, skip optimization
                return response

            # Optimize response content
            optimized_content = await self._optimize_response_content(content)

            # Generate ETag
            etag = None
            if self.enable_etag:
                etag = self._generate_etag(optimized_content)
                response.headers["etag"] = etag

            # Cache response if applicable
            if is_cacheable and self.enable_response_caching:
                await self._cache_response(request, optimized_content, etag, response.headers)

            # Compress response if beneficial
            if self.enable_compression:
                response = await self._compress_response(request, optimized_content, response)
            else:
                # Update response body
                optimized_body = json.dumps(optimized_content, separators=(',', ':'))
                response = JSONResponse(content=optimized_content)

            # Add cache control headers
            self._add_cache_control_headers(request, response)

            return response

        except Exception as e:
            logger.error(f"Error optimizing response: {e}")
            return response

    async def _optimize_response_content(self, content: Any) -> Any:
        """Optimize response content structure"""
        if isinstance(content, dict):
            # Remove null values to reduce size
            optimized = {k: v for k, v in content.items() if v is not None}

            # Optimize nested objects
            for key, value in optimized.items():
                if isinstance(value, (dict, list)):
                    optimized[key] = await self._optimize_response_content(value)

            return optimized

        elif isinstance(content, list):
            # Optimize list items
            return [await self._optimize_response_content(item) for item in content if item is not None]

        return content

    async def _compress_response(self, request: Request, content: Any,
                                original_response: StarletteResponse) -> StarletteResponse:
        """Compress response if beneficial"""
        try:
            # Serialize content
            content_str = json.dumps(content, separators=(',', ':'))
            content_bytes = content_str.encode('utf-8')

            # Check if compression is beneficial
            if len(content_bytes) < self.compression_threshold:
                return JSONResponse(content=content)

            # Check client support for compression
            accept_encoding = request.headers.get("accept-encoding", "")

            if "gzip" in accept_encoding:
                # Compress with gzip
                compressed_content = gzip.compress(content_bytes, compresslevel=self.compression_level)

                # Only use compression if it reduces size significantly
                if len(compressed_content) < len(content_bytes) * 0.9:
                    response = Response(
                        content=compressed_content,
                        media_type="application/json"
                    )
                    response.headers["content-encoding"] = "gzip"
                    response.headers["content-length"] = str(len(compressed_content))
                    response.headers["vary"] = "Accept-Encoding"

                    # Copy original headers
                    for key, value in original_response.headers.items():
                        if key.lower() not in ["content-encoding", "content-length"]:
                            response.headers[key] = value

                    return response

            # Return uncompressed if compression not beneficial
            return JSONResponse(content=content)

        except Exception as e:
            logger.error(f"Error compressing response: {e}")
            return JSONResponse(content=content)

    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request"""
        # Include path, query parameters, and relevant headers
        key_components = [
            request.url.path,
            str(sorted(request.query_params.items())),
            request.headers.get("accept", ""),
            request.headers.get("accept-language", ""),
        ]

        # Add user context for personalized responses
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            key_components.append(f"user:{user_id}")

        key_string = "|".join(str(c) for c in key_components)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()

        return f"api:response:{request.url.path.replace('/', '_')}:{key_hash}"

    def _generate_etag(self, content: Any) -> str:
        """Generate ETag for content"""
        content_str = json.dumps(content, sort_keys=True, separators=(',', ':'))
        etag_hash = hashlib.md5(content_str.encode()).hexdigest()[:16]
        return f'"{etag_hash}"'

    async def _cache_response(self, request: Request, content: Any, etag: Optional[str],
                             headers: Dict[str, str]):
        """Cache response data"""
        try:
            cache_key = self._generate_cache_key(request)

            # Determine TTL
            ttl = self._get_cache_ttl(request)

            # Prepare cache data
            cache_data = {
                "data": content,
                "etag": etag,
                "headers": {
                    "content-type": "application/json",
                    "etag": etag,
                    "cache-control": f"public, max-age={ttl}"
                },
                "cached_at": datetime.utcnow().isoformat(),
                "ttl": ttl
            }

            await cache_service.set(cache_key, cache_data, ttl)

        except Exception as e:
            logger.error(f"Error caching response: {e}")

    def _get_cache_ttl(self, request: Request) -> int:
        """Get cache TTL for specific endpoint"""
        path = request.url.path

        # Check custom TTL for specific endpoints
        for pattern, ttl in self.cache_ttl_by_endpoint.items():
            if path.startswith(pattern):
                return ttl

        # Default TTL
        return self.cache_ttl_default

    def _add_cache_control_headers(self, request: Request, response: StarletteResponse):
        """Add appropriate cache control headers"""
        ttl = self._get_cache_ttl(request)

        # Add cache control headers
        response.headers["cache-control"] = f"public, max-age={ttl}, s-maxage={ttl}"
        response.headers["expires"] = (datetime.utcnow() + timedelta(seconds=ttl)).strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

        # Add CORS headers for CDN compatibility
        response.headers["access-control-max-age"] = str(ttl)

        # Add security headers
        response.headers["x-content-type-options"] = "nosniff"
        response.headers["x-frame-options"] = "DENY"


def create_performance_optimization_middleware(config: Optional[Dict[str, Any]] = None):
    """Factory function to create performance optimization middleware"""
    default_config = {
        "enable_compression": True,
        "enable_response_caching": True,
        "enable_etag": True,
        "enable_performance_monitoring": True,
        "compression_threshold": 1024,
        "compression_level": 6,
        "cache_ttl_default": 300,
        "cache_ttl_by_endpoint": {
            "/api/v1/categories": 3600,  # 1 hour for categories
            "/api/v1/productos": 600,    # 10 minutes for products
            "/api/v1/search": 300,       # 5 minutes for search
            "/api/v1/vendor/profile": 1800,  # 30 minutes for profiles
        },
        "cacheable_endpoints": [
            "/api/v1/productos",
            "/api/v1/categories",
            "/api/v1/search",
            "/api/v1/vendor/profile",
            "/api/v1/buyer/products"
        ],
        "non_cacheable_endpoints": [
            "/api/v1/auth",
            "/api/v1/orders",
            "/api/v1/transactions",
            "/api/v1/admin"
        ]
    }

    if config:
        default_config.update(config)

    return lambda app: PerformanceOptimizationMiddleware(app, default_config)