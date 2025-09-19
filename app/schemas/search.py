# ~/app/schemas/search.py
# ---------------------------------------------------------------------------------------------
# MeStore - Search Schemas for Advanced Marketplace Search System
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: search.py
# Ruta: ~/app/schemas/search.py
# Autor: API Architect AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Schemas Pydantic para sistema de búsqueda avanzada del marketplace
#            Soporte para búsqueda híbrida PostgreSQL + ChromaDB con filtros complejos
#
# Características:
# - Request/Response schemas para todos los endpoints de búsqueda
# - Validación y serialización optimizada para performance
# - Support para búsqueda semántica y text search
# - Schemas para facetas, filtros y agregaciones
# - Analytics y tracking de búsquedas
# - Paginación y ordenamiento optimizado
#
# ---------------------------------------------------------------------------------------------

"""
Search Schemas para MeStore Marketplace.

Este módulo contiene los schemas Pydantic para el sistema de búsqueda:
- SearchRequest: Request schemas para diferentes tipos de búsqueda
- SearchResponse: Response schemas con productos y metadatos
- FilterSchemas: Schemas para filtros y facetas
- AnalyticsSchemas: Schemas para tracking y analytics
- AutocompleteSchemas: Schemas para sugerencias y autocomplete
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict


class SearchType(str, Enum):
    """Tipos de búsqueda disponibles."""
    TEXT = "text"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class SortBy(str, Enum):
    """Opciones de ordenamiento."""
    RELEVANCE = "relevancia"
    PRICE_ASC = "precio_asc"
    PRICE_DESC = "precio_desc"
    DATE_ASC = "fecha_asc"
    DATE_DESC = "fecha_desc"
    POPULARITY = "popularidad"
    NAME_ASC = "nombre_asc"
    NAME_DESC = "nombre_desc"


class SearchStatus(str, Enum):
    """Estados de productos para filtrar."""
    ALL = "all"
    AVAILABLE = "DISPONIBLE"
    VERIFIED = "VERIFICADO"
    TRANSIT = "TRANSITO"
    SOLD = "VENDIDO"


# ================================
# REQUEST SCHEMAS
# ================================

class BaseSearchRequest(BaseModel):
    """Base schema para requests de búsqueda."""
    q: Optional[str] = Field(None, description="Término de búsqueda", max_length=500)
    page: int = Field(1, ge=1, le=1000, description="Número de página")
    limit: int = Field(20, ge=1, le=100, description="Resultados por página")
    sort_by: SortBy = Field(SortBy.RELEVANCE, description="Criterio de ordenamiento")

    @field_validator('q')
    @classmethod
    def validate_query(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v


class SearchRequest(BaseSearchRequest):
    """Schema para búsqueda general con filtros."""
    category_id: Optional[UUID] = Field(None, description="ID de categoría para filtrar")
    vendor_id: Optional[UUID] = Field(None, description="ID de vendor para filtrar")
    min_price: Optional[float] = Field(None, ge=0, description="Precio mínimo")
    max_price: Optional[float] = Field(None, ge=0, description="Precio máximo")
    in_stock: Optional[bool] = Field(None, description="Solo productos con stock")
    status: Optional[SearchStatus] = Field(SearchStatus.ALL, description="Estado del producto")
    tags: Optional[List[str]] = Field(None, description="Tags para filtrar")
    search_type: SearchType = Field(SearchType.TEXT, description="Tipo de búsqueda")

    @field_validator('max_price')
    @classmethod
    def validate_price_range(cls, v, info):
        if v is not None and 'min_price' in info.data and info.data['min_price'] is not None:
            if v < info.data['min_price']:
                raise ValueError('max_price debe ser mayor que min_price')
        return v


class AdvancedSearchRequest(BaseModel):
    """Schema para búsqueda avanzada multi-criterio."""
    query: Optional[str] = Field(None, description="Término principal de búsqueda")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filtros complejos")
    facets: List[str] = Field(default_factory=list, description="Facetas requeridas en respuesta")
    boost: Dict[str, float] = Field(default_factory=dict, description="Campos con boost de relevancia")
    fuzzy: Dict[str, Any] = Field(default_factory=dict, description="Configuración de fuzzy search")
    page: int = Field(1, ge=1, le=1000)
    limit: int = Field(20, ge=1, le=100)
    sort_by: SortBy = Field(SortBy.RELEVANCE)
    search_type: SearchType = Field(SearchType.HYBRID)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "laptop gaming",
                "filters": {
                    "category_path": "/electronics/computers/",
                    "price_range": {"min": 500, "max": 2000},
                    "vendor_rating": {"min": 4.0},
                    "in_stock": True
                },
                "facets": ["category", "vendor", "price_ranges", "brands"],
                "boost": {"name": 2.0, "description": 1.5},
                "fuzzy": {"enabled": True, "distance": 2},
                "page": 1,
                "limit": 20,
                "sort_by": "relevancia",
                "search_type": "hybrid"
            }
        }
    )


class SemanticSearchRequest(BaseModel):
    """Schema para búsqueda semántica con ChromaDB."""
    query: str = Field(..., description="Query semántica", min_length=3, max_length=500)
    limit: int = Field(10, ge=1, le=50, description="Número máximo de resultados")
    threshold: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Umbral de similitud")
    include_metadata: bool = Field(True, description="Incluir metadatos en respuesta")
    category_filter: Optional[UUID] = Field(None, description="Filtrar por categoría")
    vendor_filter: Optional[UUID] = Field(None, description="Filtrar por vendor")


class AutocompleteRequest(BaseModel):
    """Schema para requests de autocomplete."""
    q: str = Field(..., description="Término parcial", min_length=1, max_length=100)
    limit: int = Field(5, ge=1, le=20, description="Número de sugerencias")
    category_id: Optional[UUID] = Field(None, description="Filtrar por categoría")
    include_categories: bool = Field(True, description="Incluir categorías en sugerencias")
    include_vendors: bool = Field(False, description="Incluir vendors en sugerencias")


class SearchAnalyticsRequest(BaseModel):
    """Schema para tracking de búsquedas."""
    query: str = Field(..., description="Término de búsqueda")
    search_type: SearchType = Field(SearchType.TEXT)
    results_count: int = Field(..., ge=0, description="Número de resultados")
    response_time_ms: int = Field(..., ge=0, description="Tiempo de respuesta en ms")
    user_id: Optional[UUID] = Field(None, description="ID del usuario (opcional)")
    session_id: Optional[str] = Field(None, description="ID de sesión")
    clicked_results: List[UUID] = Field(default_factory=list, description="IDs de productos clickeados")
    filters_used: Dict[str, Any] = Field(default_factory=dict, description="Filtros utilizados")
    page_viewed: int = Field(1, ge=1, description="Página vista")


# ================================
# RESPONSE SCHEMAS
# ================================

class SearchMetadata(BaseModel):
    """Metadatos de la búsqueda."""
    total_results: int = Field(..., description="Total de resultados")
    page: int = Field(..., description="Página actual")
    limit: int = Field(..., description="Resultados por página")
    total_pages: int = Field(..., description="Total de páginas")
    search_time_ms: int = Field(..., description="Tiempo de búsqueda en millisegundos")
    search_type: SearchType = Field(..., description="Tipo de búsqueda utilizada")
    query_processed: Optional[str] = Field(None, description="Query procesada")
    has_next_page: bool = Field(..., description="Hay página siguiente")
    has_prev_page: bool = Field(..., description="Hay página anterior")


class FacetValue(BaseModel):
    """Valor de faceta con conteo."""
    value: str = Field(..., description="Valor de la faceta")
    count: int = Field(..., ge=0, description="Número de productos")
    selected: bool = Field(False, description="Si está seleccionado")


class Facet(BaseModel):
    """Faceta con sus valores."""
    name: str = Field(..., description="Nombre de la faceta")
    display_name: str = Field(..., description="Nombre para mostrar")
    type: str = Field(..., description="Tipo de faceta (category, price_range, etc.)")
    values: List[FacetValue] = Field(..., description="Valores de la faceta")
    multiple: bool = Field(True, description="Permite selección múltiple")


class ProductSearchResult(BaseModel):
    """Resultado de producto en búsqueda."""
    id: UUID = Field(..., description="ID del producto")
    sku: str = Field(..., description="SKU del producto")
    name: str = Field(..., description="Nombre del producto")
    description: Optional[str] = Field(None, description="Descripción")
    precio_venta: Optional[float] = Field(None, description="Precio de venta")
    categoria: Optional[str] = Field(None, description="Categoría")
    tags: List[str] = Field(default_factory=list, description="Tags del producto")
    status: str = Field(..., description="Estado del producto")
    stock_disponible: int = Field(0, description="Stock disponible")
    vendor_id: Optional[UUID] = Field(None, description="ID del vendor")
    vendor_name: Optional[str] = Field(None, description="Nombre del vendor")
    image_url: Optional[str] = Field(None, description="URL de imagen principal")
    score: Optional[float] = Field(None, description="Score de relevancia")
    created_at: datetime = Field(..., description="Fecha de creación")

    # Metadatos de búsqueda
    match_type: Optional[str] = Field(None, description="Tipo de coincidencia")
    highlighted_fields: Dict[str, str] = Field(default_factory=dict, description="Campos destacados")

    model_config = ConfigDict(from_attributes=True)


class SuggestionItem(BaseModel):
    """Item de sugerencia para autocomplete."""
    text: str = Field(..., description="Texto de la sugerencia")
    type: str = Field(..., description="Tipo: product, category, vendor, tag")
    score: float = Field(..., description="Score de relevancia")
    id: Optional[UUID] = Field(None, description="ID del item (si aplica)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales")


class SearchResponse(BaseModel):
    """Respuesta completa de búsqueda."""
    results: List[ProductSearchResult] = Field(..., description="Productos encontrados")
    metadata: SearchMetadata = Field(..., description="Metadatos de búsqueda")
    facets: List[Facet] = Field(default_factory=list, description="Facetas disponibles")
    suggestions: List[str] = Field(default_factory=list, description="Sugerencias de términos")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "results": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "sku": "LAP001",
                        "name": "Laptop Gaming ASUS ROG",
                        "description": "Laptop gaming de alta performance",
                        "precio_venta": 1500.00,
                        "categoria": "Electrónicos",
                        "tags": ["gaming", "laptop", "asus"],
                        "status": "DISPONIBLE",
                        "stock_disponible": 5,
                        "vendor_name": "TechStore",
                        "score": 0.95,
                        "match_type": "exact"
                    }
                ],
                "metadata": {
                    "total_results": 150,
                    "page": 1,
                    "limit": 20,
                    "total_pages": 8,
                    "search_time_ms": 45,
                    "search_type": "text",
                    "has_next_page": True,
                    "has_prev_page": False
                },
                "facets": [
                    {
                        "name": "category",
                        "display_name": "Categoría",
                        "type": "category",
                        "values": [
                            {"value": "Electrónicos", "count": 85, "selected": False},
                            {"value": "Computadoras", "count": 42, "selected": False}
                        ],
                        "multiple": True
                    }
                ],
                "suggestions": ["laptop gaming", "laptop asus", "gaming computer"]
            }
        }
    )


class AutocompleteResponse(BaseModel):
    """Respuesta de autocomplete."""
    suggestions: List[SuggestionItem] = Field(..., description="Lista de sugerencias")
    query: str = Field(..., description="Query original")
    response_time_ms: int = Field(..., description="Tiempo de respuesta")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "suggestions": [
                    {
                        "text": "laptop gaming",
                        "type": "product",
                        "score": 0.95,
                        "metadata": {"category": "Electrónicos", "count": 25}
                    },
                    {
                        "text": "Laptops",
                        "type": "category",
                        "score": 0.88,
                        "id": "cat-123",
                        "metadata": {"product_count": 150}
                    }
                ],
                "query": "lap",
                "response_time_ms": 15
            }
        }
    )


class SemanticSearchResponse(BaseModel):
    """Respuesta de búsqueda semántica."""
    results: List[ProductSearchResult] = Field(..., description="Productos similares")
    query: str = Field(..., description="Query semántica")
    similarity_threshold: float = Field(..., description="Umbral utilizado")
    total_embeddings_searched: int = Field(..., description="Total de embeddings buscados")
    response_time_ms: int = Field(..., description="Tiempo de respuesta")


class SimilarProductsResponse(BaseModel):
    """Respuesta de productos similares."""
    products: List[ProductSearchResult] = Field(..., description="Productos similares")
    base_product_id: UUID = Field(..., description="ID del producto base")
    similarity_method: str = Field(..., description="Método de similitud usado")
    response_time_ms: int = Field(..., description="Tiempo de respuesta")


class TrendingTermsResponse(BaseModel):
    """Respuesta de términos trending."""
    terms: List[Dict[str, Any]] = Field(..., description="Términos trending")
    period: str = Field(..., description="Período analizado")
    updated_at: datetime = Field(..., description="Última actualización")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "terms": [
                    {"term": "laptop gaming", "count": 1250, "growth": "+25%"},
                    {"term": "smartphone", "count": 980, "growth": "+12%"},
                    {"term": "auriculares", "count": 750, "growth": "+8%"}
                ],
                "period": "last_7_days",
                "updated_at": "2025-09-17T10:30:00Z"
            }
        }
    )


class PopularSearchesResponse(BaseModel):
    """Respuesta de búsquedas populares."""
    searches: List[Dict[str, Any]] = Field(..., description="Búsquedas populares")
    category_id: Optional[UUID] = Field(None, description="Categoría filtrada")
    period: str = Field(..., description="Período analizado")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "searches": [
                    {"query": "laptop", "count": 2500, "avg_results": 150},
                    {"query": "celular", "count": 1800, "avg_results": 220},
                    {"query": "audifonos", "count": 1200, "avg_results": 85}
                ],
                "period": "last_30_days"
            }
        }
    )


class FilterOptionsResponse(BaseModel):
    """Respuesta de opciones de filtro."""
    categories: List[Dict[str, Any]] = Field(..., description="Categorías disponibles")
    vendors: List[Dict[str, Any]] = Field(..., description="Vendors disponibles")
    price_ranges: List[Dict[str, Any]] = Field(..., description="Rangos de precio")
    tags: List[str] = Field(..., description="Tags disponibles")
    status_options: List[str] = Field(..., description="Estados disponibles")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "categories": [
                    {"id": "cat-123", "name": "Electrónicos", "product_count": 500},
                    {"id": "cat-456", "name": "Ropa", "product_count": 300}
                ],
                "vendors": [
                    {"id": "ven-123", "name": "TechStore", "product_count": 150},
                    {"id": "ven-456", "name": "FashionHub", "product_count": 200}
                ],
                "price_ranges": [
                    {"min": 0, "max": 100, "count": 250},
                    {"min": 100, "max": 500, "count": 180}
                ],
                "tags": ["gaming", "premium", "sale", "new"],
                "status_options": ["DISPONIBLE", "VERIFICADO", "TRANSITO"]
            }
        }
    )


# ================================
# ANALYTICS SCHEMAS
# ================================

class SearchAnalyticsResponse(BaseModel):
    """Respuesta de analytics de búsqueda."""
    success: bool = Field(True, description="Si se guardó correctamente")
    search_id: Optional[UUID] = Field(None, description="ID del registro de búsqueda")
    message: str = Field("Analytics recorded successfully")


class SearchStatsResponse(BaseModel):
    """Respuesta de estadísticas de búsqueda."""
    total_searches: int = Field(..., description="Total de búsquedas")
    unique_queries: int = Field(..., description="Queries únicos")
    avg_response_time: float = Field(..., description="Tiempo promedio de respuesta")
    top_queries: List[Dict[str, Any]] = Field(..., description="Queries más populares")
    search_types_distribution: Dict[str, int] = Field(..., description="Distribución por tipo")
    period: str = Field(..., description="Período analizado")


# ================================
# ERROR SCHEMAS
# ================================

class SearchError(BaseModel):
    """Schema para errores de búsqueda."""
    error: str = Field(..., description="Tipo de error")
    message: str = Field(..., description="Mensaje de error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales")
    suggestions: List[str] = Field(default_factory=list, description="Sugerencias para resolver")


# ================================
# EXPORT ALL SCHEMAS
# ================================

__all__ = [
    # Enums
    "SearchType",
    "SortBy",
    "SearchStatus",

    # Request Schemas
    "BaseSearchRequest",
    "SearchRequest",
    "AdvancedSearchRequest",
    "SemanticSearchRequest",
    "AutocompleteRequest",
    "SearchAnalyticsRequest",

    # Response Schemas
    "SearchMetadata",
    "FacetValue",
    "Facet",
    "ProductSearchResult",
    "SuggestionItem",
    "SearchResponse",
    "AutocompleteResponse",
    "SemanticSearchResponse",
    "SimilarProductsResponse",
    "TrendingTermsResponse",
    "PopularSearchesResponse",
    "FilterOptionsResponse",

    # Analytics Schemas
    "SearchAnalyticsResponse",
    "SearchStatsResponse",

    # Error Schemas
    "SearchError",
]