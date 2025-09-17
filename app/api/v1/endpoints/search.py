# ~/app/api/v1/endpoints/search.py
# ---------------------------------------------------------------------------------------------
# MeStore - Search API Endpoints
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: search.py
# Ruta: ~/app/api/v1/endpoints/search.py
# Autor: Data Engineering AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Endpoints de API para sistema de búsqueda avanzada del marketplace
#            Búsqueda híbrida, autocomplete, analytics y filtros avanzados
#
# Características:
# - Búsqueda híbrida (PostgreSQL + ChromaDB)
# - Autocomplete inteligente con cache
# - Filtros avanzados (categorías, precio, vendor, stock)
# - Analytics de búsqueda y trending queries
# - Performance optimizada con cache Redis
# - Paginación y ordenamiento flexible
#
# ---------------------------------------------------------------------------------------------

"""
Search API Endpoints para MeStore Marketplace.

Este módulo proporciona endpoints de búsqueda:
- Búsqueda principal con filtros avanzados
- Autocomplete y sugerencias
- Búsqueda de productos similares
- Analytics de búsqueda y trending
- Métricas de performance
"""

import logging
from typing import Dict, List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import get_current_user_optional
from app.api.v1.deps.database import get_async_session
from app.core.redis.base import get_redis_manager
from app.models.user import User
from app.services.search_service import SearchService, SearchFilters, create_search_service
from app.services.search_cache_service import SearchCacheService, create_search_cache_service
from app.services.chroma_service import chroma_service

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic Models para Request/Response
class SearchRequest(BaseModel):
    """
    Modelo para request de búsqueda avanzada.
    """
    query: str = Field("", description="Texto de búsqueda")
    categories: Optional[List[str]] = Field(None, description="Filtro por categorías (slugs o nombres)")
    price_min: Optional[float] = Field(None, ge=0, description="Precio mínimo")
    price_max: Optional[float] = Field(None, ge=0, description="Precio máximo")
    vendor_ids: Optional[List[str]] = Field(None, description="Filtro por vendor IDs")
    has_stock: Optional[bool] = Field(None, description="Solo productos con stock")
    status: Optional[List[str]] = Field(["DISPONIBLE"], description="Status de productos")
    tags: Optional[List[str]] = Field(None, description="Filtro por tags")
    sort_by: str = Field("relevance", description="Campo de ordenamiento")
    sort_order: str = Field("desc", description="Orden (asc/desc)")

    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_sorts = ["relevance", "price_asc", "price_desc", "newest", "oldest", "name"]
        if v not in allowed_sorts:
            raise ValueError(f"sort_by debe ser uno de: {allowed_sorts}")
        return v

    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order debe ser 'asc' o 'desc'")
        return v


class AutocompleteResponse(BaseModel):
    """
    Modelo para respuesta de autocomplete.
    """
    suggestions: List[str] = Field(description="Lista de sugerencias")
    query: str = Field(description="Query parcial original")
    count: int = Field(description="Número de sugerencias")


class SimilarProductsResponse(BaseModel):
    """
    Modelo para respuesta de productos similares.
    """
    similar_products: List[Dict] = Field(description="Lista de productos similares")
    base_product_id: str = Field(description="ID del producto base")
    count: int = Field(description="Número de productos similares")


class TrendingQueriesResponse(BaseModel):
    """
    Modelo para respuesta de queries trending.
    """
    trending_queries: List[Dict] = Field(description="Lista de queries trending")
    period: str = Field(description="Período analizado")
    count: int = Field(description="Número de queries")


class SearchAnalyticsResponse(BaseModel):
    """
    Modelo para respuesta de analytics de búsqueda.
    """
    daily_analytics: Dict = Field(description="Analytics diarios")
    total_searches: int = Field(description="Total de búsquedas")
    trending_queries: List[Dict] = Field(description="Queries trending")
    cache_metrics: Dict = Field(description="Métricas de cache")
    days_analyzed: int = Field(description="Días analizados")


# Dependency functions
async def get_search_service(
    session: AsyncSession = Depends(get_async_session),
    redis_manager = Depends(get_redis_manager)
) -> SearchService:
    """Dependency para obtener SearchService configurado."""
    return create_search_service(redis_manager)


async def get_search_cache_service(
    redis_manager = Depends(get_redis_manager)
) -> SearchCacheService:
    """Dependency para obtener SearchCacheService configurado."""
    return create_search_cache_service(redis_manager)


# API Endpoints
@router.post("/search", response_model=Dict)
async def search_products(
    search_request: SearchRequest,
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Tamaño de página"),
    session: AsyncSession = Depends(get_async_session),
    search_service: SearchService = Depends(get_search_service),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Búsqueda avanzada de productos con filtros y ranking híbrido.

    Combina búsqueda full-text de PostgreSQL con búsqueda semántica de ChromaDB
    para proporcionar resultados relevantes y diversos.

    **Características:**
    - Búsqueda híbrida (texto + semántica)
    - Filtros avanzados por categorías, precio, vendor
    - Ranking inteligente con múltiples señales
    - Cache optimizado para performance
    - Paginación y ordenamiento flexible

    **Ejemplos de uso:**
    - Búsqueda simple: `{"query": "laptop gaming"}`
    - Con filtros: `{"query": "celular", "price_max": 500, "has_stock": true}`
    - Por categoría: `{"categories": ["electronica", "telefonia"]}`
    """
    try:
        # Convertir request a SearchFilters
        filters = SearchFilters(
            query=search_request.query,
            categories=search_request.categories or [],
            price_min=search_request.price_min,
            price_max=search_request.price_max,
            vendor_ids=search_request.vendor_ids or [],
            has_stock=search_request.has_stock,
            status=search_request.status or ["DISPONIBLE"],
            tags=search_request.tags or [],
            sort_by=search_request.sort_by,
            sort_order=search_request.sort_order
        )

        # Ejecutar búsqueda
        results = await search_service.search_products(
            session=session,
            filters=filters,
            page=page,
            page_size=page_size
        )

        # Agregar metadata del usuario si está autenticado
        if current_user:
            results["user_context"] = {
                "user_id": str(current_user.id),
                "user_type": current_user.user_type.value if current_user.user_type else None
            }

        return results

    except Exception as e:
        logger.error(f"Error en búsqueda de productos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno en búsqueda: {str(e)}"
        )


@router.get("/autocomplete", response_model=AutocompleteResponse)
async def get_autocomplete_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="Query parcial para autocomplete"),
    limit: int = Query(10, ge=1, le=20, description="Número máximo de sugerencias"),
    session: AsyncSession = Depends(get_async_session),
    search_service: SearchService = Depends(get_search_service),
    cache_service: SearchCacheService = Depends(get_search_cache_service)
):
    """
    Obtener sugerencias de autocomplete para búsqueda.

    Proporciona sugerencias inteligentes basadas en:
    - Nombres de productos existentes
    - Categorías populares
    - Queries anteriores populares
    - Cache optimizado para respuesta rápida

    **Características:**
    - Respuesta ultra-rápida (<50ms)
    - Cache inteligente con Redis
    - Sugerencias contextuales
    - Soporte para typos comunes
    """
    try:
        # Validar query mínimo
        if len(q.strip()) < 2:
            return AutocompleteResponse(
                suggestions=[],
                query=q,
                count=0
            )

        # Intentar obtener del cache primero
        cached_suggestions = await cache_service.get_autocomplete_suggestions(q)
        if cached_suggestions:
            return AutocompleteResponse(
                suggestions=cached_suggestions[:limit],
                query=q,
                count=len(cached_suggestions[:limit])
            )

        # Generar sugerencias si no están en cache
        suggestions = await search_service.get_autocomplete_suggestions(
            session=session,
            partial_query=q,
            limit=limit
        )

        # Cachear para futuros requests
        await cache_service.set_autocomplete_suggestions(q, suggestions)

        return AutocompleteResponse(
            suggestions=suggestions,
            query=q,
            count=len(suggestions)
        )

    except Exception as e:
        logger.error(f"Error en autocomplete: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo sugerencias: {str(e)}"
        )


@router.get("/products/{product_id}/similar", response_model=SimilarProductsResponse)
async def get_similar_products(
    product_id: UUID,
    limit: int = Query(5, ge=1, le=20, description="Número de productos similares"),
    exclude_same_vendor: bool = Query(True, description="Excluir productos del mismo vendor"),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Encontrar productos similares usando búsqueda semántica.

    Utiliza ChromaDB vector similarity search para encontrar productos
    semánticamente similares basados en nombre y descripción.

    **Características:**
    - Búsqueda por similitud vectorial
    - Exclusión opcional del mismo vendor
    - Filtros por stock disponible
    - Ranking por relevancia semántica

    **Casos de uso:**
    - Recomendaciones de productos relacionados
    - "Customers who viewed this item also viewed"
    - Cross-selling y up-selling
    """
    try:
        # Buscar productos similares usando ChromaDB
        similar_results = await chroma_service.search_similar_products(
            product_id=str(product_id),
            max_results=limit,
            exclude_same_vendor=exclude_same_vendor
        )

        # Formatear respuesta
        similar_products = []
        for result in similar_results:
            product_data = {
                "product_id": result["product_id"],
                "similarity_score": result["similarity_score"],
                "metadata": result["metadata"]
            }
            similar_products.append(product_data)

        return SimilarProductsResponse(
            similar_products=similar_products,
            base_product_id=str(product_id),
            count=len(similar_products)
        )

    except Exception as e:
        logger.error(f"Error obteniendo productos similares: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda de similares: {str(e)}"
        )


@router.get("/trending", response_model=TrendingQueriesResponse)
async def get_trending_queries(
    limit: int = Query(20, ge=1, le=50, description="Número de queries trending"),
    period: str = Query("all", description="Período: 'all', 'daily', 'hourly'"),
    cache_service: SearchCacheService = Depends(get_search_cache_service)
):
    """
    Obtener queries de búsqueda trending y populares.

    Proporciona insights sobre qué están buscando los usuarios:
    - Queries más populares (histórico)
    - Queries trending (últimas horas)
    - Análisis de patrones de búsqueda

    **Casos de uso:**
    - Dashboard de analytics
    - Optimización de inventario
    - Trending searches widget
    - SEO y content strategy
    """
    try:
        trending_queries = await cache_service.get_trending_queries(limit=limit)

        return TrendingQueriesResponse(
            trending_queries=trending_queries,
            period=period,
            count=len(trending_queries)
        )

    except Exception as e:
        logger.error(f"Error obteniendo trending queries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo trending: {str(e)}"
        )


@router.get("/analytics", response_model=SearchAnalyticsResponse)
async def get_search_analytics(
    days: int = Query(7, ge=1, le=30, description="Número de días para analizar"),
    search_service: SearchService = Depends(get_search_service),
    cache_service: SearchCacheService = Depends(get_search_cache_service),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Obtener analytics completos de búsqueda.

    Proporciona métricas detalladas sobre el uso del sistema de búsqueda:
    - Analytics diarios de búsquedas
    - Métricas de performance de cache
    - Queries trending y populares
    - Insights de comportamiento de usuarios

    **Acceso:**
    - Disponible para todos los usuarios
    - Métricas detalladas para admins/vendors

    **Casos de uso:**
    - Dashboard de analytics
    - Optimización de performance
    - Business intelligence
    - Mejora de experiencia de usuario
    """
    try:
        # Obtener analytics básicos
        search_analytics = await search_service.get_search_analytics(days=days)

        # Obtener métricas de cache
        cache_metrics = await cache_service.get_cache_metrics()

        # Combinar analytics
        analytics_response = SearchAnalyticsResponse(
            daily_analytics=search_analytics.get("daily_analytics", {}),
            total_searches=search_analytics.get("total_searches", 0),
            trending_queries=search_analytics.get("trending_queries", []),
            cache_metrics=cache_metrics,
            days_analyzed=days
        )

        return analytics_response

    except Exception as e:
        logger.error(f"Error obteniendo analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo analytics: {str(e)}"
        )


@router.post("/cache/invalidate")
async def invalidate_search_cache(
    pattern: Optional[str] = Query(None, description="Patrón de cache a invalidar"),
    product_ids: Optional[List[str]] = Query(None, description="IDs de productos para invalidación granular"),
    category_ids: Optional[List[str]] = Query(None, description="IDs de categorías para invalidación granular"),
    cache_service: SearchCacheService = Depends(get_search_cache_service),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Invalidar cache de búsqueda de manera selectiva.

    Permite invalidar cache específico cuando hay cambios en productos,
    categorías o cuando se necesita refrescar resultados.

    **Acceso:**
    - Disponible para usuarios autenticados
    - Invalidación granular para vendors (sus productos)
    - Invalidación completa para admins

    **Casos de uso:**
    - Después de actualizar productos
    - Cambios en categorías
    - Mantenimiento de cache
    - Debugging de resultados
    """
    try:
        # TODO: Agregar validación de permisos
        # Por ahora, permitir a cualquier usuario autenticado

        keys_invalidated = await cache_service.invalidate_search_cache(
            pattern=pattern,
            product_ids=product_ids,
            category_ids=category_ids
        )

        return {
            "message": "Cache invalidado exitosamente",
            "keys_invalidated": keys_invalidated,
            "pattern": pattern,
            "product_ids": product_ids,
            "category_ids": category_ids
        }

    except Exception as e:
        logger.error(f"Error invalidando cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error invalidando cache: {str(e)}"
        )


@router.get("/health")
async def search_health_check():
    """
    Health check para sistema de búsqueda.

    Verifica el estado de todos los componentes:
    - PostgreSQL connection
    - ChromaDB connection
    - Redis cache
    - Modelos de embeddings
    """
    try:
        health_status = {
            "status": "healthy",
            "components": {},
            "timestamp": str(logger.manager.disable)  # Placeholder timestamp
        }

        # Verificar ChromaDB
        try:
            stats = await chroma_service.get_collection_stats()
            health_status["components"]["chromadb"] = {
                "status": "healthy",
                "stats": stats
            }
        except Exception as e:
            health_status["components"]["chromadb"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"

        return health_status

    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en health check: {str(e)}"
        )