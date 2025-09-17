# ~/app/services/cache_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Performance Optimization Cache Service
# Copyright (c) 2025 Performance Optimization AI. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: cache_service.py
# Ruta: ~/app/services/cache_service.py
# Autor: Performance Optimization AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Comprehensive caching strategy for MeStore marketplace performance optimization
#            Redis-based caching for authentication, products, search, and API responses
#
# Características:
# - Multi-layered caching strategy with intelligent TTL management
# - Authentication token caching with smart invalidation
# - Product catalog caching with category-based invalidation
# - Search results caching with faceted invalidation patterns
# - API response caching with ETag and compression support
# - Performance monitoring and cache hit rate tracking
# - Memory-efficient object serialization and compression
#
# ---------------------------------------------------------------------------------------------

"""
Performance Cache Service para MeStore Marketplace.

Este módulo implementa la estrategia integral de caching para optimización de performance:
- Cache de autenticación con invalidación inteligente
- Cache de catálogo de productos con patrones de invalidación por categoría
- Cache de resultados de búsqueda con soporte para facetas
- Cache de respuestas API con soporte ETag y compresión
- Monitoreo de performance y métricas de cache hit rate
- Gestión eficiente de memoria con serialización y compresión
"""

import asyncio
import gzip
import hashlib
import json
import logging
import pickle
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis.base import get_redis_client
from app.models.product import Product, ProductStatus
from app.models.user import User
from app.schemas.product import ProductResponse

logger = logging.getLogger(__name__)


class CacheKeyPatterns:
    """Cache key patterns for consistent naming and invalidation"""

    # Authentication Cache Keys
    AUTH_TOKEN = "auth:token:{token_hash}"
    AUTH_USER = "auth:user:{user_id}"
    AUTH_SESSION = "auth:session:{session_id}"
    AUTH_PERMISSIONS = "auth:permissions:{user_id}"

    # Product Cache Keys
    PRODUCT_DETAIL = "product:detail:{product_id}"
    PRODUCT_LIST = "product:list:{category_id}:{page}:{limit}:{filters_hash}"
    PRODUCT_SEARCH = "product:search:{query_hash}:{filters_hash}"
    PRODUCT_CATEGORY = "product:category:{category_id}:{page}:{limit}"
    PRODUCT_VENDOR = "product:vendor:{vendor_id}:{page}:{limit}"

    # Search Cache Keys
    SEARCH_RESULTS = "search:results:{query_hash}:{filters_hash}"
    SEARCH_SUGGESTIONS = "search:suggestions:{query_prefix}"
    SEARCH_FACETS = "search:facets:{category_id}"
    SEARCH_ANALYTICS = "search:analytics:{period}:{dimension}"

    # API Response Cache Keys
    API_RESPONSE = "api:response:{endpoint_hash}:{params_hash}"
    API_METADATA = "api:metadata:{endpoint}"

    # Performance Metrics
    CACHE_METRICS = "cache:metrics:{service}:{period}"
    PERFORMANCE_STATS = "perf:stats:{endpoint}:{period}"


class CacheService:
    """Comprehensive caching service for MeStore performance optimization"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.compression_threshold = 1024  # Compress objects larger than 1KB
        self.default_ttl = settings.REDIS_CACHE_TTL
        self.metrics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
            "compression_saves": 0
        }

    async def _get_redis(self) -> redis.Redis:
        """Get Redis client with lazy initialization"""
        if self.redis_client is None:
            self.redis_client = await get_redis_client()
        return self.redis_client

    def _generate_hash(self, data: Any) -> str:
        """Generate consistent hash for cache keys"""
        if isinstance(data, (dict, list)):
            data = json.dumps(data, sort_keys=True, default=str)
        elif not isinstance(data, str):
            data = str(data)
        return hashlib.md5(data.encode()).hexdigest()[:16]

    def _serialize_object(self, obj: Any) -> bytes:
        """Serialize object with optional compression"""
        try:
            # Convert SQLAlchemy objects to dict
            if hasattr(obj, '__dict__') and hasattr(obj, '__table__'):
                obj = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            elif hasattr(obj, 'dict') and callable(obj.dict):
                obj = obj.dict()

            # Serialize to bytes
            serialized = pickle.dumps(obj)

            # Compress if above threshold
            if len(serialized) > self.compression_threshold:
                compressed = gzip.compress(serialized)
                if len(compressed) < len(serialized):
                    self.metrics["compression_saves"] += len(serialized) - len(compressed)
                    return b"gzip:" + compressed

            return b"raw:" + serialized
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            raise

    def _deserialize_object(self, data: bytes) -> Any:
        """Deserialize object with compression support"""
        try:
            if data.startswith(b"gzip:"):
                decompressed = gzip.decompress(data[5:])
                return pickle.loads(decompressed)
            elif data.startswith(b"raw:"):
                return pickle.loads(data[4:])
            else:
                # Legacy format
                return pickle.loads(data)
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            raise

    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with performance tracking"""
        try:
            redis_client = await self._get_redis()
            data = await redis_client.get(key)

            if data is None:
                self.metrics["misses"] += 1
                return default

            self.metrics["hits"] += 1
            return self._deserialize_object(data)
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Cache get error for key {key}: {e}")
            return default

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            redis_client = await self._get_redis()
            serialized_value = self._serialize_object(value)
            ttl = ttl or self.default_ttl

            await redis_client.setex(key, ttl, serialized_value)
            self.metrics["sets"] += 1
            return True
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            redis_client = await self._get_redis()
            deleted = await redis_client.delete(key)
            self.metrics["deletes"] += 1
            return bool(deleted)
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern"""
        try:
            redis_client = await self._get_redis()
            keys = await redis_client.keys(pattern)
            if keys:
                deleted = await redis_client.delete(*keys)
                self.metrics["deletes"] += deleted
                return deleted
            return 0
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            redis_client = await self._get_redis()
            return bool(await redis_client.exists(key))
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    async def extend_ttl(self, key: str, ttl: int) -> bool:
        """Extend TTL for existing key"""
        try:
            redis_client = await self._get_redis()
            return bool(await redis_client.expire(key, ttl))
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Cache extend TTL error for key {key}: {e}")
            return False

    # === AUTHENTICATION CACHING ===

    async def cache_auth_token(self, token_hash: str, user_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache authentication token with user data"""
        key = CacheKeyPatterns.AUTH_TOKEN.format(token_hash=token_hash)
        ttl = ttl or settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        return await self.set(key, user_data, ttl)

    async def get_cached_auth_token(self, token_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached authentication token data"""
        key = CacheKeyPatterns.AUTH_TOKEN.format(token_hash=token_hash)
        return await self.get(key)

    async def invalidate_auth_token(self, token_hash: str) -> bool:
        """Invalidate authentication token cache"""
        key = CacheKeyPatterns.AUTH_TOKEN.format(token_hash=token_hash)
        return await self.delete(key)

    async def cache_user_permissions(self, user_id: UUID, permissions: List[str], ttl: Optional[int] = None) -> bool:
        """Cache user permissions"""
        key = CacheKeyPatterns.AUTH_PERMISSIONS.format(user_id=str(user_id))
        ttl = ttl or settings.REDIS_CACHE_TTL
        return await self.set(key, permissions, ttl)

    async def get_cached_user_permissions(self, user_id: UUID) -> Optional[List[str]]:
        """Get cached user permissions"""
        key = CacheKeyPatterns.AUTH_PERMISSIONS.format(user_id=str(user_id))
        return await self.get(key)

    # === PRODUCT CACHING ===

    async def cache_product(self, product: Product, ttl: Optional[int] = None) -> bool:
        """Cache individual product"""
        key = CacheKeyPatterns.PRODUCT_DETAIL.format(product_id=str(product.id))
        ttl = ttl or settings.REDIS_CACHE_TTL
        return await self.set(key, product, ttl)

    async def get_cached_product(self, product_id: UUID) -> Optional[Product]:
        """Get cached product"""
        key = CacheKeyPatterns.PRODUCT_DETAIL.format(product_id=str(product_id))
        return await self.get(key)

    async def cache_product_list(self, cache_key: str, products: List[Product], ttl: Optional[int] = None) -> bool:
        """Cache product list with custom key"""
        ttl = ttl or settings.REDIS_CACHE_TTL // 2  # Shorter TTL for lists
        return await self.set(cache_key, products, ttl)

    async def get_cached_product_list(self, cache_key: str) -> Optional[List[Product]]:
        """Get cached product list"""
        return await self.get(cache_key)

    async def invalidate_product_cache(self, product_id: UUID, category_id: Optional[UUID] = None) -> int:
        """Invalidate all caches related to a product"""
        patterns = [
            CacheKeyPatterns.PRODUCT_DETAIL.format(product_id=str(product_id)),
            f"product:list:*",  # All product lists
            f"product:search:*",  # All search results
        ]

        if category_id:
            patterns.append(f"product:category:{category_id}:*")

        total_deleted = 0
        for pattern in patterns:
            deleted = await self.delete_pattern(pattern)
            total_deleted += deleted

        return total_deleted

    # === SEARCH CACHING ===

    async def cache_search_results(self, query_hash: str, filters_hash: str, results: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache search results"""
        key = CacheKeyPatterns.SEARCH_RESULTS.format(query_hash=query_hash, filters_hash=filters_hash)
        ttl = ttl or settings.REDIS_TEMP_CACHE_TTL  # Shorter TTL for search
        return await self.set(key, results, ttl)

    async def get_cached_search_results(self, query_hash: str, filters_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached search results"""
        key = CacheKeyPatterns.SEARCH_RESULTS.format(query_hash=query_hash, filters_hash=filters_hash)
        return await self.get(key)

    async def cache_search_suggestions(self, query_prefix: str, suggestions: List[str], ttl: Optional[int] = None) -> bool:
        """Cache search suggestions"""
        key = CacheKeyPatterns.SEARCH_SUGGESTIONS.format(query_prefix=query_prefix)
        ttl = ttl or settings.REDIS_LONG_CACHE_TTL  # Longer TTL for suggestions
        return await self.set(key, suggestions, ttl)

    async def get_cached_search_suggestions(self, query_prefix: str) -> Optional[List[str]]:
        """Get cached search suggestions"""
        key = CacheKeyPatterns.SEARCH_SUGGESTIONS.format(query_prefix=query_prefix)
        return await self.get(key)

    async def invalidate_search_cache(self) -> int:
        """Invalidate all search-related caches"""
        patterns = [
            "search:results:*",
            "search:facets:*",
            "search:analytics:*"
        ]

        total_deleted = 0
        for pattern in patterns:
            deleted = await self.delete_pattern(pattern)
            total_deleted += deleted

        return total_deleted

    # === API RESPONSE CACHING ===

    async def cache_api_response(self, endpoint_hash: str, params_hash: str, response: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache API response"""
        key = CacheKeyPatterns.API_RESPONSE.format(endpoint_hash=endpoint_hash, params_hash=params_hash)
        ttl = ttl or settings.REDIS_CACHE_TTL

        # Add cache metadata
        cached_response = {
            "data": response,
            "cached_at": datetime.utcnow().isoformat(),
            "ttl": ttl
        }

        return await self.set(key, cached_response, ttl)

    async def get_cached_api_response(self, endpoint_hash: str, params_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached API response"""
        key = CacheKeyPatterns.API_RESPONSE.format(endpoint_hash=endpoint_hash, params_hash=params_hash)
        cached_response = await self.get(key)

        if cached_response and "data" in cached_response:
            return cached_response["data"]

        return cached_response

    # === PERFORMANCE METRICS ===

    async def record_cache_metrics(self) -> Dict[str, Any]:
        """Record and return current cache metrics"""
        total_operations = sum([
            self.metrics["hits"],
            self.metrics["misses"],
            self.metrics["sets"],
            self.metrics["deletes"]
        ])

        hit_rate = (self.metrics["hits"] / max(self.metrics["hits"] + self.metrics["misses"], 1)) * 100

        metrics_data = {
            **self.metrics,
            "hit_rate": round(hit_rate, 2),
            "total_operations": total_operations,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Cache the metrics themselves for monitoring
        key = CacheKeyPatterns.CACHE_METRICS.format(
            service="cache_service",
            period=datetime.utcnow().strftime("%Y%m%d_%H")
        )
        await self.set(key, metrics_data, ttl=3600)  # 1 hour TTL

        return metrics_data

    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        redis_client = await self._get_redis()

        # Redis info
        redis_info = await redis_client.info()
        memory_usage = redis_info.get('used_memory_human', 'N/A')
        connected_clients = redis_info.get('connected_clients', 0)

        # Cache metrics
        cache_metrics = await self.record_cache_metrics()

        return {
            "cache_metrics": cache_metrics,
            "redis_memory_usage": memory_usage,
            "redis_connected_clients": connected_clients,
            "compression_enabled": True,
            "compression_threshold": self.compression_threshold,
            "default_ttl": self.default_ttl
        }

    async def warmup_cache(self, db: AsyncSession) -> Dict[str, int]:
        """Warm up cache with frequently accessed data"""
        logger.info("Starting cache warmup...")

        warmup_stats = {
            "products_cached": 0,
            "categories_cached": 0,
            "search_suggestions_cached": 0
        }

        try:
            # Warm up popular products (first 100)
            from sqlalchemy import select
            result = await db.execute(
                select(Product)
                .where(Product.status == ProductStatus.ACTIVE)
                .limit(100)
            )
            products = result.scalars().all()

            for product in products:
                await self.cache_product(product, ttl=settings.REDIS_LONG_CACHE_TTL)
                warmup_stats["products_cached"] += 1

            logger.info(f"Cache warmup completed: {warmup_stats}")

        except Exception as e:
            logger.error(f"Cache warmup error: {e}")

        return warmup_stats


# Global cache service instance
cache_service = CacheService()


async def get_cache_service() -> CacheService:
    """Dependency function to get cache service instance"""
    return cache_service