# ~/app/schemas/category.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Schemas de Categorías API v1
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: category.py
# Ruta: ~/app/schemas/category.py
# Autor: API Architect AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Schemas Pydantic para sistema de categorías jerárquicas
#            Validación de datos para endpoints de categorías
#
# ---------------------------------------------------------------------------------------------

"""
Schemas Pydantic para el sistema de categorías jerárquicas.

Este módulo contiene:
- CategoryBase: Schema base con campos comunes
- CategoryCreate: Schema para creación de categorías
- CategoryUpdate: Schema para actualización de categorías
- CategoryInDB: Schema para representación en base de datos
- CategoryRead: Schema para respuestas de lectura
- CategoryTree: Schema para estructura jerárquica anidada
- CategoryBreadcrumb: Schema para navegación breadcrumb
- CategoryBulkCreate: Schema para operaciones masivas
- ProductCategoryAssignment: Schema para asignación de categorías a productos
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator


class CategoryBase(BaseModel):
    """Schema base para categorías con campos comunes."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre de la categoría"
    )
    slug: Optional[str] = Field(
        None,
        min_length=1,
        max_length=120,
        pattern=r"^[a-z0-9-]+$",
        description="Slug SEO-friendly (se genera automáticamente si no se proporciona)"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Descripción de la categoría"
    )
    is_active: bool = Field(
        True,
        description="Estado activo de la categoría"
    )
    sort_order: int = Field(
        0,
        ge=0,
        le=9999,
        description="Orden de clasificación (0-9999)"
    )
    meta_title: Optional[str] = Field(
        None,
        max_length=60,
        description="Título meta para SEO"
    )
    meta_description: Optional[str] = Field(
        None,
        max_length=160,
        description="Descripción meta para SEO"
    )
    image_url: Optional[str] = Field(
        None,
        description="URL de imagen representativa de la categoría"
    )


class CategoryCreate(CategoryBase):
    """Schema para creación de categorías."""

    parent_id: Optional[UUID] = Field(
        None,
        description="ID de la categoría padre (None para categoría raíz)"
    )


class CategoryUpdate(BaseModel):
    """Schema para actualización de categorías."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Nombre de la categoría"
    )
    slug: Optional[str] = Field(
        None,
        min_length=1,
        max_length=120,
        pattern=r"^[a-z0-9-]+$",
        description="Slug SEO-friendly"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Descripción de la categoría"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Estado activo de la categoría"
    )
    sort_order: Optional[int] = Field(
        None,
        ge=0,
        le=9999,
        description="Orden de clasificación"
    )
    meta_title: Optional[str] = Field(
        None,
        max_length=60,
        description="Título meta para SEO"
    )
    meta_description: Optional[str] = Field(
        None,
        max_length=160,
        description="Descripción meta para SEO"
    )
    image_url: Optional[str] = Field(
        None,
        description="URL de imagen representativa"
    )


class CategoryInDB(CategoryBase):
    """Schema para representación en base de datos."""

    id: UUID = Field(..., description="ID único de la categoría")
    parent_id: Optional[UUID] = Field(None, description="ID de la categoría padre")
    level: int = Field(..., ge=0, le=10, description="Nivel en la jerarquía (0-10)")
    path: str = Field(..., description="Ruta jerárquica materializada")
    children_count: int = Field(0, ge=0, description="Número de subcategorías directas")
    products_count: int = Field(0, ge=0, description="Número de productos en esta categoría")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    class Config:
        from_attributes = True


class CategoryRead(CategoryInDB):
    """Schema para respuestas de lectura de categorías."""

    parent_name: Optional[str] = Field(None, description="Nombre de la categoría padre")


class CategoryTreeNode(CategoryRead):
    """Schema para nodo en estructura de árbol jerárquico."""

    children: List['CategoryTreeNode'] = Field(
        default_factory=list,
        description="Subcategorías anidadas"
    )

    class Config:
        from_attributes = True


# Actualizar referencias hacia adelante
CategoryTreeNode.model_rebuild()


class CategoryTree(BaseModel):
    """Schema para respuesta de árbol completo de categorías."""

    categories: List[CategoryTreeNode] = Field(
        default_factory=list,
        description="Categorías raíz con subcategorías anidadas"
    )
    total_categories: int = Field(0, ge=0, description="Total de categorías en el árbol")
    max_depth: int = Field(0, ge=0, description="Profundidad máxima del árbol")


class CategoryBreadcrumbItem(BaseModel):
    """Schema para elemento de breadcrumb."""

    id: UUID = Field(..., description="ID de la categoría")
    name: str = Field(..., description="Nombre de la categoría")
    slug: str = Field(..., description="Slug de la categoría")
    level: int = Field(..., ge=0, description="Nivel en la jerarquía")


class CategoryBreadcrumb(BaseModel):
    """Schema para navegación breadcrumb."""

    breadcrumb: List[CategoryBreadcrumbItem] = Field(
        default_factory=list,
        description="Ruta de navegación desde raíz hasta categoría actual"
    )
    current_category: CategoryRead = Field(..., description="Categoría actual")


class CategoryMove(BaseModel):
    """Schema para operación de mover categoría en jerarquía."""

    new_parent_id: Optional[UUID] = Field(
        None,
        description="Nuevo ID de categoría padre (None para mover a raíz)"
    )
    new_sort_order: Optional[int] = Field(
        None,
        ge=0,
        le=9999,
        description="Nuevo orden de clasificación"
    )


class CategoryBulkCreate(BaseModel):
    """Schema para creación masiva de categorías."""

    categories: List[CategoryCreate] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="Lista de categorías a crear (máximo 100)"
    )

    @validator('categories')
    def validate_categories(cls, v):
        """Validar que no hay slugs duplicados en el lote."""
        slugs = [cat.slug for cat in v if cat.slug]
        if len(slugs) != len(set(slugs)):
            raise ValueError("No se permiten slugs duplicados en el lote")
        return v


class ProductCategoryAssignment(BaseModel):
    """Schema para asignación de categorías a producto."""

    category_ids: List[UUID] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="Lista de IDs de categorías a asignar (máximo 10)"
    )
    primary_category_id: Optional[UUID] = Field(
        None,
        description="ID de la categoría principal (debe estar en category_ids)"
    )

    @validator('primary_category_id')
    def validate_primary_category(cls, v, values):
        """Validar que la categoría principal esté en la lista de categorías."""
        if v is not None and 'category_ids' in values:
            if v not in values['category_ids']:
                raise ValueError("La categoría principal debe estar en la lista de categorías")
        return v


class CategoryWithProducts(CategoryRead):
    """Schema para categoría con información de productos."""

    products: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de productos en esta categoría"
    )

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Schema para respuesta paginada de categorías."""

    categories: List[CategoryRead] = Field(
        default_factory=list,
        description="Lista de categorías"
    )
    total: int = Field(0, ge=0, description="Total de categorías")
    page: int = Field(1, ge=1, description="Página actual")
    size: int = Field(20, ge=1, le=100, description="Tamaño de página")
    pages: int = Field(0, ge=0, description="Total de páginas")


class CategorySearchFilters(BaseModel):
    """Schema para filtros de búsqueda de categorías."""

    search: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Término de búsqueda en nombre o descripción"
    )
    parent_id: Optional[UUID] = Field(
        None,
        description="Filtrar por categoría padre"
    )
    level: Optional[int] = Field(
        None,
        ge=0,
        le=10,
        description="Filtrar por nivel jerárquico"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Filtrar por estado activo"
    )
    has_products: Optional[bool] = Field(
        None,
        description="Filtrar categorías que tienen productos"
    )


class CategoryStats(BaseModel):
    """Schema para estadísticas de categorías."""

    total_categories: int = Field(0, ge=0, description="Total de categorías")
    active_categories: int = Field(0, ge=0, description="Categorías activas")
    root_categories: int = Field(0, ge=0, description="Categorías raíz")
    max_depth: int = Field(0, ge=0, description="Profundidad máxima")
    categories_with_products: int = Field(0, ge=0, description="Categorías con productos")
    empty_categories: int = Field(0, ge=0, description="Categorías sin productos")
    most_popular_categories: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Categorías más populares por número de productos"
    )


class CategoryError(BaseModel):
    """Schema para errores específicos de categorías."""

    error_code: str = Field(..., description="Código de error específico")
    message: str = Field(..., description="Mensaje de error")
    category_id: Optional[UUID] = Field(None, description="ID de categoría relacionada")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales del error")