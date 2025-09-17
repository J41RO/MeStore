# ~/app/services/search_cache_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Search Cache Service for Performance Optimization
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: search_cache_service.py
# Ruta: ~/app/services/search_cache_service.py
# Autor: API Architect AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Service especializado para caching de búsquedas y optimización de performance
#            Sistema de cache inteligente con invalidación selectiva y warm-up automático
#
# Características:
# - Cache jerárquico con múltiples TTLs
# - Invalidación inteligente por categorías
# - Warm-up automático de queries populares
# - Compresión de respuestas grandes
# - Metrics y monitoring de cache hit ratio
# - Fallback graceful en caso de falla
#
# ---------------------------------------------------------------------------------------------

"""
Search Cache Service para MeStore Marketplace.

Este módulo implementa un sistema de cache avanzado para búsquedas:
- Cache multi-nivel con diferentes TTLs
- Invalidación selectiva e inteligente
- Warm-up automático de contenido popular
- Compresión automática para optimizar memoria
- Monitoring y métricas de performance
"""

import gzip
import hashlib
import json
import logging
import pickle
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import redis
from pydantic import BaseModel

from app.core.config import settings
from app.core.redis.base import get_redis_client
from app.schemas.search import SearchResponse, AutocompleteResponse

logger = logging.getLogger(__name__)


class CacheMetrics(BaseModel):
    """Métricas de performance del cache."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    memory_usage_mb: float = 0.0
    avg_response_time_ms: float = 0.0
    hit_ratio: float = 0.0


class SearchCacheService:
    """
    Service para cache avanzado de búsquedas.

    Implementa un sistema de cache multi-nivel:
    - L1: Cache de queries exactas (TTL corto, alta frecuencia)
    - L2: Cache de resultados procesados (TTL medio)
    - L3: Cache de facetas y agregaciones (TTL largo)
    - L4: Cache de autocomplete (TTL muy largo)
    """

    def __init__(self):
        """Inicializar SearchCacheService."""
        self.redis_client = None  # Lazy initialization
        self.compression_threshold = 1024  # Comprimir si > 1KB
        self.max_cache_size_mb = 100  # Límite de memoria para cache

        # TTL configurations por tipo de cache
        self.ttl_config = {
            "search_exact": 300,      # 5 minutos - queries exactas
            "search_processed": 1800,  # 30 minutos - resultados procesados
            "facets": 3600,           # 1 hora - facetas y agregaciones
            "autocomplete": 7200,     # 2 horas - autocomplete
            "popular_queries": 86400,  # 24 horas - queries populares
            "trending": 1800,         # 30 minutos - trending terms
            "analytics": 3600         # 1 hora - analytics
        }

        # Prefijos para organizar el cache
        self.cache_prefixes = {
            "search": "search_cache:",
            "autocomplete": "autocomplete_cache:",
            "facets": "facets_cache:",
            "trending": "trending_cache:",
            "popular": "popular_cache:",
            "similar": "similar_cache:",
            "metrics": "cache_metrics:"
        }

    async def _get_redis_client(self):
        """Get Redis client with lazy initialization."""
        if self.redis_client is None:
            self.redis_client = await get_redis_client()
        return self.redis_client

    # ================================
    # SEARCH RESULT CACHING
    # ================================

    async def get_search_cache(
        self,
        cache_key: str,
        cache_type: str = "search_exact"
    ) -> Optional[SearchResponse]:
        """
        Obtener resultado de búsqueda desde cache.

        Args:
            cache_key: Clave del cache
            cache_type: Tipo de cache para TTL apropiado

        Returns:
            SearchResponse o None si no existe
        """
        try:
            full_key = f"{self.cache_prefixes['search']}{cache_key}"

            # Increment cache request counter
            await self._increment_metric("cache_requests")

            cached_data = await self.redis_client.get(full_key)

            if cached_data:
                await self._increment_metric("cache_hits")

                # Check if data is compressed
                if cached_data.startswith(b'\x1f\x8b'):  # gzip magic number
                    cached_data = gzip.decompress(cached_data)

                # Deserialize
                data = json.loads(cached_data.decode('utf-8'))
                return SearchResponse(**data)
            else:
                await self._increment_metric("cache_misses")
                return None

        except Exception as e:
            logger.error(f"Cache get failed: {e}")
            await self._increment_metric("cache_errors")
            return None

    async def set_search_cache(
        self,
        cache_key: str,
        response: SearchResponse,
        cache_type: str = "search_exact"
    ) -> bool:
        """
        Guardar resultado de búsqueda en cache.

        Args:
            cache_key: Clave del cache
            response: Respuesta a cachear
            cache_type: Tipo de cache para TTL apropiado

        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            full_key = f"{self.cache_prefixes['search']}{cache_key}"
            ttl = self.ttl_config.get(cache_type, 300)

            # Serialize response
            data = response.dict()
            serialized_data = json.dumps(data, default=str).encode('utf-8')

            # Compress if larger than threshold
            if len(serialized_data) > self.compression_threshold:
                serialized_data = gzip.compress(serialized_data)
                await self._increment_metric("cache_compressions")

            # Store with TTL
            await self.redis_client.setex(full_key, ttl, serialized_data)
            await self._increment_metric("cache_sets")

            # Track cache size
            await self._track_cache_size(len(serialized_data))

            return True

        except Exception as e:
            logger.error(f"Cache set failed: {e}")
            await self._increment_metric("cache_errors")
            return False

    def generate_search_cache_key(
        self,
        query: Optional[str],
        filters: Dict[str, Any],
        page: int,
        limit: int,
        sort_by: str
    ) -> str:
        """
        Generar clave de cache para búsqueda.

        Args:
            query: Término de búsqueda
            filters: Filtros aplicados
            page: Página
            limit: Límite de resultados
            sort_by: Ordenamiento

        Returns:
            str: Clave de cache única
        """
        # Create consistent key from parameters
        key_data = {
            "q": query or "",
            "filters": sorted(filters.items()) if filters else [],
            "page": page,
            "limit": limit,
            "sort_by": sort_by
        }

        # Generate hash
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()

        return f"search_{key_hash}"

    # ================================
    # AUTOCOMPLETE CACHING
    # ================================

    async def get_autocomplete_cache(
        self,
        query: str,
        category_id: Optional[UUID] = None,
        limit: int = 5
    ) -> Optional[AutocompleteResponse]:
        """Obtener autocomplete desde cache."""
        try:
            cache_key = self._generate_autocomplete_key(query, category_id, limit)
            full_key = f"{self.cache_prefixes['autocomplete']}{cache_key}"

            cached_data = await self.redis_client.get(full_key)
            if cached_data:
                data = json.loads(cached_data.decode('utf-8'))
                return AutocompleteResponse(**data)

            return None

        except Exception as e:
            logger.error(f"Autocomplete cache get failed: {e}")
            return None

    async def set_autocomplete_cache(
        self,
        query: str,
        response: AutocompleteResponse,
        category_id: Optional[UUID] = None,
        limit: int = 5
    ) -> bool:
        """Guardar autocomplete en cache."""
        try:
            cache_key = self._generate_autocomplete_key(query, category_id, limit)
            full_key = f"{self.cache_prefixes['autocomplete']}{cache_key}"
            ttl = self.ttl_config["autocomplete"]

            data = response.dict()
            serialized_data = json.dumps(data, default=str)

            await self.redis_client.setex(full_key, ttl, serialized_data)
            return True

        except Exception as e:
            logger.error(f"Autocomplete cache set failed: {e}")
            return False

    def _generate_autocomplete_key(
        self,
        query: str,
        category_id: Optional[UUID],
        limit: int
    ) -> str:
        """Generar clave para autocomplete cache."""
        key_data = f"autocomplete_{query.lower()}_{category_id}_{limit}"
        return hashlib.md5(key_data.encode()).hexdigest()

    # ================================
    # FACETS AND AGGREGATIONS CACHING
    # ================================

    async def get_facets_cache(
        self,
        base_query_hash: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Obtener facetas desde cache."""
        try:
            cache_key = f"facets_{base_query_hash}"
            full_key = f"{self.cache_prefixes['facets']}{cache_key}"

            cached_data = await self.redis_client.get(full_key)
            if cached_data:
                return json.loads(cached_data.decode('utf-8'))

            return None

        except Exception as e:
            logger.error(f"Facets cache get failed: {e}")
            return None

    async def set_facets_cache(
        self,
        base_query_hash: str,
        facets: List[Dict[str, Any]]
    ) -> bool:
        """Guardar facetas en cache."""
        try:
            cache_key = f"facets_{base_query_hash}"
            full_key = f"{self.cache_prefixes['facets']}{cache_key}"
            ttl = self.ttl_config["facets"]

            serialized_data = json.dumps(facets, default=str)
            await self.redis_client.setex(full_key, ttl, serialized_data)
            return True

        except Exception as e:
            logger.error(f"Facets cache set failed: {e}")
            return False

    # ================================
    # TRENDING AND POPULAR CACHING
    # ================================

    async def get_trending_cache(self, period: str) -> Optional[List[Dict[str, Any]]]:
        """Obtener trending terms desde cache."""
        try:
            cache_key = f"trending_{period}"
            full_key = f"{self.cache_prefixes['trending']}{cache_key}"

            cached_data = await self.redis_client.get(full_key)
            if cached_data:
                return json.loads(cached_data.decode('utf-8'))

            return None

        except Exception as e:
            logger.error(f"Trending cache get failed: {e}")
            return None

    async def set_trending_cache(
        self,
        period: str,
        trending_data: List[Dict[str, Any]]
    ) -> bool:
        """Guardar trending terms en cache."""
        try:
            cache_key = f"trending_{period}"
            full_key = f"{self.cache_prefixes['trending']}{cache_key}"
            ttl = self.ttl_config["trending"]

            serialized_data = json.dumps(trending_data, default=str)
            await self.redis_client.setex(full_key, ttl, serialized_data)
            return True

        except Exception as e:
            logger.error(f"Trending cache set failed: {e}")
            return False

    async def get_popular_cache(self, period: str) -> Optional[List[Dict[str, Any]]]:
        """Obtener popular searches desde cache."""
        try:
            cache_key = f"popular_{period}"
            full_key = f"{self.cache_prefixes['popular']}{cache_key}"

            cached_data = await self.redis_client.get(full_key)
            if cached_data:
                return json.loads(cached_data.decode('utf-8'))

            return None

        except Exception as e:
            logger.error(f"Popular cache get failed: {e}")
            return None

    async def set_popular_cache(
        self,
        period: str,
        popular_data: List[Dict[str, Any]]
    ) -> bool:
        """Guardar popular searches en cache."""
        try:
            cache_key = f"popular_{period}"
            full_key = f"{self.cache_prefixes['popular']}{cache_key}"
            ttl = self.ttl_config["popular_queries"]

            serialized_data = json.dumps(popular_data, default=str)
            await self.redis_client.setex(full_key, ttl, serialized_data)
            return True

        except Exception as e:
            logger.error(f"Popular cache set failed: {e}")
            return False

    # ================================
    # CACHE INVALIDATION
    # ================================

    async def invalidate_search_cache(
        self,
        pattern: Optional[str] = None,
        category_id: Optional[UUID] = None,
        vendor_id: Optional[UUID] = None
    ) -> int:
        """
        Invalidar cache de búsquedas selectivamente.

        Args:
            pattern: Patrón de claves a invalidar
            category_id: Invalidar por categoría
            vendor_id: Invalidar por vendor

        Returns:
            int: Número de claves invalidadas
        """
        try:
            invalidated_count = 0

            if pattern:
                # Invalidate by pattern
                pattern_key = f"{self.cache_prefixes['search']}*{pattern}*"
                keys = await self.redis_client.keys(pattern_key)
                if keys:
                    await self.redis_client.delete(*keys)
                    invalidated_count += len(keys)

            if category_id:
                # Invalidate by category
                category_pattern = f"{self.cache_prefixes['search']}*category_{category_id}*"
                keys = await self.redis_client.keys(category_pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    invalidated_count += len(keys)

                # Also invalidate facets
                facets_pattern = f"{self.cache_prefixes['facets']}*"
                facets_keys = await self.redis_client.keys(facets_pattern)
                if facets_keys:
                    await self.redis_client.delete(*facets_keys)
                    invalidated_count += len(facets_keys)

            if vendor_id:
                # Invalidate by vendor
                vendor_pattern = f"{self.cache_prefixes['search']}*vendor_{vendor_id}*"
                keys = await self.redis_client.keys(vendor_pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    invalidated_count += len(keys)

            await self._increment_metric("cache_invalidations", invalidated_count)
            logger.info(f"Invalidated {invalidated_count} cache entries")

            return invalidated_count

        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")
            return 0

    async def invalidate_all_search_cache(self) -> int:
        """Invalidar todo el cache de búsquedas."""
        try:
            invalidated_count = 0

            for prefix in self.cache_prefixes.values():
                pattern = f"{prefix}*"
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    invalidated_count += len(keys)

            await self._increment_metric("cache_full_invalidations")
            logger.info(f"Invalidated all search cache: {invalidated_count} entries")

            return invalidated_count

        except Exception as e:
            logger.error(f"Full cache invalidation failed: {e}")
            return 0

    # ================================
    # CACHE WARM-UP
    # ================================

    async def warmup_popular_searches(
        self,
        popular_queries: List[str],
        session
    ) -> int:
        """
        Pre-calentar cache con búsquedas populares.

        Args:
            popular_queries: Lista de queries populares
            session: Database session

        Returns:
            int: Número de queries pre-cacheadas
        """
        try:
            from app.services.search_service import search_service
            from app.schemas.search import SearchRequest, SearchType, SortBy

            warmed_count = 0

            for query in popular_queries:
                try:
                    # Generate cache key
                    cache_key = self.generate_search_cache_key(
                        query=query,
                        filters={},
                        page=1,
                        limit=20,
                        sort_by=SortBy.RELEVANCE.value
                    )

                    # Check if already cached
                    cached = await self.get_search_cache(cache_key)
                    if cached:
                        continue  # Already warmed

                    # Perform search
                    search_request = SearchRequest(
                        q=query,
                        page=1,
                        limit=20,
                        sort_by=SortBy.RELEVANCE,
                        search_type=SearchType.TEXT
                    )

                    result = await search_service.search(session, search_request)

                    # Cache result
                    await self.set_search_cache(
                        cache_key, result, "search_processed"
                    )

                    warmed_count += 1

                except Exception as e:
                    logger.error(f"Warmup failed for query '{query}': {e}")
                    continue

            logger.info(f"Warmed up {warmed_count} popular searches")
            return warmed_count

        except Exception as e:
            logger.error(f"Cache warmup failed: {e}")
            return 0

    # ================================
    # METRICS AND MONITORING
    # ================================

    async def get_cache_metrics(self) -> CacheMetrics:
        """Obtener métricas del cache."""
        try:
            metrics_key = f"{self.cache_prefixes['metrics']}stats"

            # Get basic counters
            hits = await self._get_metric("cache_hits") or 0
            misses = await self._get_metric("cache_misses") or 0
            total_requests = hits + misses

            # Calculate hit ratio
            hit_ratio = (hits / total_requests) if total_requests > 0 else 0.0

            # Get memory usage (approximate)
            memory_usage = await self._estimate_cache_memory_usage()

            # Get average response time (simplified)
            avg_response_time = await self._get_metric("avg_response_time") or 0.0

            return CacheMetrics(
                hits=hits,
                misses=misses,
                evictions=await self._get_metric("cache_evictions") or 0,
                memory_usage_mb=memory_usage,
                avg_response_time_ms=avg_response_time,
                hit_ratio=hit_ratio
            )

        except Exception as e:
            logger.error(f"Get cache metrics failed: {e}")
            return CacheMetrics()

    async def _increment_metric(self, metric_name: str, amount: int = 1):
        """Incrementar contador de métrica."""
        try:
            key = f"{self.cache_prefixes['metrics']}{metric_name}"
            await self.redis_client.incrby(key, amount)
            await self.redis_client.expire(key, 86400)  # 24 hours
        except Exception:
            pass  # Don't fail on metrics

    async def _get_metric(self, metric_name: str) -> Optional[int]:
        """Obtener valor de métrica."""
        try:
            key = f"{self.cache_prefixes['metrics']}{metric_name}"
            value = await self.redis_client.get(key)
            return int(value) if value else None
        except Exception:
            return None

    async def _track_cache_size(self, size_bytes: int):
        """Track del tamaño de cache."""
        try:
            key = f"{self.cache_prefixes['metrics']}total_size"
            await self.redis_client.incrby(key, size_bytes)
            await self.redis_client.expire(key, 86400)
        except Exception:
            pass

    async def _estimate_cache_memory_usage(self) -> float:
        """Estimar uso de memoria del cache (en MB)."""
        try:
            total_size = await self._get_metric("total_size") or 0
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0.0

    # ================================
    # CLEANUP AND MAINTENANCE
    # ================================

    async def cleanup_expired_cache(self) -> int:
        """Limpiar entradas de cache expiradas."""
        try:
            # Redis handles TTL automatically, but we can clean up metrics
            cleaned_count = 0

            # Clean old metrics
            metrics_pattern = f"{self.cache_prefixes['metrics']}*"
            old_metrics = await self.redis_client.keys(metrics_pattern)

            for key in old_metrics:
                ttl = await self.redis_client.ttl(key)
                if ttl <= 0:  # Expired or no TTL
                    await self.redis_client.delete(key)
                    cleaned_count += 1

            logger.info(f"Cleaned up {cleaned_count} expired cache entries")
            return cleaned_count

        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
            return 0

    async def optimize_cache_memory(self) -> bool:
        """Optimizar memoria del cache."""
        try:
            # Check current memory usage
            memory_mb = await self._estimate_cache_memory_usage()

            if memory_mb > self.max_cache_size_mb:
                logger.warning(f"Cache memory usage ({memory_mb:.2f}MB) exceeds limit")

                # Implement LRU-style cleanup (simplified)
                # In production, this would be more sophisticated
                await self.invalidate_search_cache(pattern="old_")

                await self._increment_metric("cache_memory_optimizations")
                return True

            return False

        except Exception as e:
            logger.error(f"Cache memory optimization failed: {e}")
            return False


# ================================
# SERVICE INSTANCE
# ================================

search_cache_service = SearchCacheService()


def create_search_cache_service() -> SearchCacheService:
    """
    Factory function to create SearchCacheService instance.

    Returns:
        SearchCacheService: Instance of search cache service
    """
    return SearchCacheService()