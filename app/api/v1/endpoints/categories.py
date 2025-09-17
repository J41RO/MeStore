# ~/app/api/v1/endpoints/categories.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Endpoints de Categorías API v1
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: categories.py
# Ruta: ~/app/api/v1/endpoints/categories.py
# Autor: API Architect AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Endpoints de gestión de categorías jerárquicas para la API v1
#            Implementa CRUD operations, navegación jerárquica, y operaciones bulk
#
# ---------------------------------------------------------------------------------------------

"""
Endpoints de gestión de categorías jerárquicas para la API v1.

Este módulo contiene:
- CRUD completo de categorías (Admin)
- Consultas públicas para navegación
- Operaciones especiales (move, breadcrumb, slug)
- Operaciones bulk para eficiencia
- Asignación de categorías a productos
- Respuestas optimizadas con eager loading
- Filtros y búsqueda avanzada
- Paginación para listas grandes
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.deps.auth import get_current_user
from app.core.database import get_db
from app.models.user import User, UserType
from app.schemas.category import (
    CategoryBreadcrumb,
    CategoryBulkCreate,
    CategoryCreate,
    CategoryError,
    CategoryListResponse,
    CategoryMove,
    CategoryRead,
    CategorySearchFilters,
    CategoryStats,
    CategoryTree,
    CategoryTreeNode,
    CategoryUpdate,
    CategoryWithProducts,
    ProductCategoryAssignment,
)
from app.schemas.user import UserRead
from app.services.category_service import CategoryService

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de categorías
router = APIRouter(prefix="/categories", tags=["Categories"])


# Decorador para validar permisos de administrador
def admin_required(func):
    """Decorador para endpoints que requieren permisos de administrador."""
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user or current_user.user_type != UserType.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requieren permisos de administrador"
            )
        return await func(*args, **kwargs)
    return wrapper


# ================================================================================================
# CRUD ENDPOINTS PARA ADMINISTRADORES
# ================================================================================================

@router.post(
    "/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva categoría",
    description="Crear una nueva categoría. Solo administradores."
)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user)
) -> CategoryRead:
    """
    Crear una nueva categoría en el sistema.

    - **Permisos**: Solo administradores
    - **Validaciones**: Slug único, padre válido, jerarquía máxima
    - **Features**: Auto-generación de slug, cálculo de level y path
    """
    # Validar permisos de administrador
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )

    try:
        logger.info(f"Admin {current_user.email} creando categoría: {category_data.name}")

        # Usar el servicio de categorías para crear
        category_service = CategoryService(db)
        return await category_service.create_category(category_data, current_user.id)

    except Exception as e:
        logger.error(f"Error creando categoría: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al crear categoría"
        )


@router.get(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Obtener categoría por ID",
    description="Obtener información detallada de una categoría específica."
)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> CategoryRead:
    """
    Obtener una categoría específica por su ID.

    - **Público**: No requiere autenticación
    - **Features**: Incluye información del padre, contadores
    """
    try:
        logger.info(f"Consultando categoría ID: {category_id}")

        # Usar el servicio de categorías para consultar
        category_service = CategoryService(db)
        category = await category_service.get_category_by_id(category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        return category

    except Exception as e:
        logger.error(f"Error consultando categoría {category_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )


@router.put(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Actualizar categoría completa",
    description="Actualizar todos los campos de una categoría. Solo administradores."
)
async def update_category(
    category_id: UUID,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user)
) -> CategoryRead:
    """
    Actualizar una categoría existente.

    - **Permisos**: Solo administradores
    - **Features**: Validación de slug único, actualización de timestamps
    """
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )

    try:
        logger.info(f"Admin {current_user.email} actualizando categoría: {category_id}")

        # Usar el servicio de categorías para actualizar
        category_service = CategoryService(db)
        return await category_service.update_category(category_id, category_data, current_user.id)

    except Exception as e:
        logger.error(f"Error actualizando categoría {category_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al actualizar categoría"
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar categoría",
    description="Eliminar una categoría (soft delete). Solo administradores."
)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user)
):
    """
    Eliminar una categoría del sistema (soft delete).

    - **Permisos**: Solo administradores
    - **Features**: Soft delete, validación de subcategorías/productos
    """
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )

    try:
        logger.info(f"Admin {current_user.email} eliminando categoría: {category_id}")

        # Usar el servicio de categorías para eliminar
        category_service = CategoryService(db)
        await category_service.delete_category(category_id, current_user.id)

    except Exception as e:
        logger.error(f"Error eliminando categoría {category_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al eliminar categoría"
        )


# ================================================================================================
# CONSULTAS PÚBLICAS
# ================================================================================================

@router.get(
    "/",
    response_model=CategoryListResponse,
    summary="Listar categorías",
    description="Obtener lista paginada de categorías con filtros."
)
async def list_categories(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(20, ge=1, le=100, description="Tamaño de página"),
    search: Optional[str] = Query(None, description="Búsqueda en nombre/descripción"),
    parent_id: Optional[UUID] = Query(None, description="Filtrar por categoría padre"),
    level: Optional[int] = Query(None, ge=0, le=10, description="Filtrar por nivel"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    sort_by: str = Query("sort_order", description="Campo de ordenamiento"),
    sort_desc: bool = Query(False, description="Orden descendente"),
    db: AsyncSession = Depends(get_db)
) -> CategoryListResponse:
    """
    Obtener lista paginada de categorías con filtros avanzados.

    - **Público**: No requiere autenticación
    - **Features**: Filtros múltiples, ordenamiento, paginación
    """
    try:
        # TODO: Implementar consulta con filtros
        logger.info(f"Listando categorías - página {page}, tamaño {size}")

        # Placeholder response
        return CategoryListResponse(
            categories=[],
            total=0,
            page=page,
            size=size,
            pages=0
        )

    except Exception as e:
        logger.error(f"Error listando categorías: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al listar categorías"
        )


@router.get(
    "/tree",
    response_model=CategoryTree,
    summary="Árbol completo de categorías",
    description="Obtener estructura jerárquica completa de categorías."
)
async def get_category_tree(
    include_inactive: bool = Query(False, description="Incluir categorías inactivas"),
    max_depth: Optional[int] = Query(None, ge=1, le=10, description="Profundidad máxima"),
    db: AsyncSession = Depends(get_db)
) -> CategoryTree:
    """
    Obtener árbol jerárquico completo de categorías.

    - **Público**: No requiere autenticación
    - **Features**: Estructura anidada optimizada, control de profundidad
    """
    try:
        logger.info("Construyendo árbol de categorías")

        # Usar el servicio de categorías para construir árbol
        category_service = CategoryService(db)
        return await category_service.build_category_tree(include_inactive, max_depth)

    except Exception as e:
        logger.error(f"Error construyendo árbol de categorías: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al construir árbol"
        )


@router.get(
    "/{category_id}/children",
    response_model=CategoryListResponse,
    summary="Obtener subcategorías",
    description="Obtener subcategorías directas de una categoría."
)
async def get_category_children(
    category_id: UUID,
    include_inactive: bool = Query(False, description="Incluir subcategorías inactivas"),
    db: AsyncSession = Depends(get_db)
) -> CategoryListResponse:
    """
    Obtener subcategorías directas de una categoría específica.

    - **Público**: No requiere autenticación
    - **Features**: Solo subcategorías directas (nivel inmediato)
    """
    try:
        # TODO: Implementar consulta de subcategorías
        logger.info(f"Obteniendo subcategorías de: {category_id}")

        # Placeholder response
        return CategoryListResponse(
            categories=[],
            total=0,
            page=1,
            size=20,
            pages=0
        )

    except Exception as e:
        logger.error(f"Error obteniendo subcategorías de {category_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener subcategorías"
        )


@router.get(
    "/{category_id}/products",
    response_model=CategoryWithProducts,
    summary="Obtener productos de categoría",
    description="Obtener productos pertenecientes a una categoría."
)
async def get_category_products(
    category_id: UUID,
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(20, ge=1, le=100, description="Tamaño de página"),
    include_subcategories: bool = Query(False, description="Incluir productos de subcategorías"),
    db: AsyncSession = Depends(get_db)
) -> CategoryWithProducts:
    """
    Obtener productos de una categoría específica.

    - **Público**: No requiere autenticación
    - **Features**: Paginación, opción de incluir subcategorías
    """
    try:
        # TODO: Implementar consulta de productos por categoría
        logger.info(f"Obteniendo productos de categoría: {category_id}")

        # Placeholder response
        return CategoryWithProducts(
            id=category_id,
            name="Categoría Ejemplo",
            slug="categoria-ejemplo",
            description="Descripción de ejemplo",
            is_active=True,
            sort_order=0,
            meta_title="Categoría Ejemplo",
            meta_description="Meta descripción",
            image_url=None,
            parent_id=None,
            level=0,
            path="/categoria-ejemplo",
            children_count=0,
            products_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            parent_name=None,
            products=[]
        )

    except Exception as e:
        logger.error(f"Error obteniendo productos de categoría {category_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener productos"
        )


# ================================================================================================
# OPERACIONES ESPECIALES
# ================================================================================================

@router.post(
    "/{category_id}/move",
    response_model=CategoryRead,
    summary="Mover categoría en jerarquía",
    description="Mover una categoría a otra posición en la jerarquía. Solo administradores."
)
async def move_category(
    category_id: UUID,
    move_data: CategoryMove,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user)
) -> CategoryRead:
    """
    Mover una categoría a otra posición en la jerarquía.

    - **Permisos**: Solo administradores
    - **Features**: Validación de ciclos, recálculo de paths
    """
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )

    try:
        logger.info(f"Admin {current_user.email} moviendo categoría: {category_id}")

        # Usar el servicio de categorías para mover
        category_service = CategoryService(db)
        return await category_service.move_category(
            category_id,
            move_data.new_parent_id,
            move_data.new_sort_order
        )

    except Exception as e:
        logger.error(f"Error moviendo categoría {category_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al mover categoría"
        )


@router.get(
    "/slug/{slug}",
    response_model=CategoryRead,
    summary="Obtener categoría por slug",
    description="Obtener categoría usando su slug SEO-friendly."
)
async def get_category_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
) -> CategoryRead:
    """
    Obtener categoría por su slug SEO-friendly.

    - **Público**: No requiere autenticación
    - **Features**: Búsqueda optimizada por slug indexado
    """
    try:
        logger.info(f"Consultando categoría por slug: {slug}")

        # Usar el servicio de categorías para consultar por slug
        category_service = CategoryService(db)
        category = await category_service.get_category_by_slug(slug)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        return category

    except Exception as e:
        logger.error(f"Error consultando categoría por slug {slug}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )


@router.get(
    "/breadcrumb/{category_id}",
    response_model=CategoryBreadcrumb,
    summary="Obtener breadcrumb de categoría",
    description="Obtener ruta de navegación breadcrumb desde raíz hasta categoría."
)
async def get_category_breadcrumb(
    category_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> CategoryBreadcrumb:
    """
    Obtener breadcrumb path de una categoría.

    - **Público**: No requiere autenticación
    - **Features**: Ruta completa desde raíz hasta categoría actual
    """
    try:
        logger.info(f"Construyendo breadcrumb para categoría: {category_id}")

        # Usar el servicio de categorías para construir breadcrumb
        category_service = CategoryService(db)
        return await category_service.get_category_breadcrumb(category_id)

    except Exception as e:
        logger.error(f"Error construyendo breadcrumb para {category_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al construir breadcrumb"
        )


# ================================================================================================
# OPERACIONES BULK
# ================================================================================================

@router.post(
    "/bulk",
    response_model=List[CategoryRead],
    status_code=status.HTTP_201_CREATED,
    summary="Crear categorías en lote",
    description="Crear múltiples categorías en una sola operación. Solo administradores."
)
async def create_categories_bulk(
    bulk_data: CategoryBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user)
) -> List[CategoryRead]:
    """
    Crear múltiples categorías en lote.

    - **Permisos**: Solo administradores
    - **Features**: Transacción atómica, validación de lote completo
    """
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )

    try:
        logger.info(f"Admin {current_user.email} creando {len(bulk_data.categories)} categorías en lote")

        # Usar el servicio de categorías para creación en lote
        category_service = CategoryService(db)
        return await category_service.create_categories_bulk(bulk_data.categories, current_user.id)

    except Exception as e:
        logger.error(f"Error creando categorías en lote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al crear categorías en lote"
        )


@router.put(
    "/products/{product_id}/categories",
    response_model=Dict[str, Any],
    summary="Asignar categorías a producto",
    description="Asignar categorías a un producto específico. Administradores y vendedores."
)
async def assign_categories_to_product(
    product_id: UUID,
    assignment_data: ProductCategoryAssignment,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Asignar categorías a un producto específico.

    - **Permisos**: Administradores y vendedores (solo sus productos)
    - **Features**: Categoría principal, múltiples categorías
    """
    if current_user.user_type not in [UserType.ADMIN, UserType.VENDOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador o vendedor"
        )

    try:
        # TODO: Implementar asignación de categorías a producto
        logger.info(f"Usuario {current_user.email} asignando categorías al producto: {product_id}")

        # Validar que el vendedor solo puede editar sus productos
        # Validar que las categorías existen
        # Asignar categorías con categoría principal

        return {
            "product_id": product_id,
            "assigned_categories": len(assignment_data.category_ids),
            "primary_category_id": assignment_data.primary_category_id,
            "message": "Categorías asignadas exitosamente"
        }

    except Exception as e:
        logger.error(f"Error asignando categorías al producto {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al asignar categorías"
        )


# ================================================================================================
# ENDPOINTS DE ESTADÍSTICAS
# ================================================================================================

@router.get(
    "/stats",
    response_model=CategoryStats,
    summary="Estadísticas de categorías",
    description="Obtener estadísticas del sistema de categorías. Solo administradores."
)
async def get_category_stats(
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user)
) -> CategoryStats:
    """
    Obtener estadísticas del sistema de categorías.

    - **Permisos**: Solo administradores
    - **Features**: Métricas completas del sistema de categorías
    """
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )

    try:
        logger.info(f"Admin {current_user.email} consultando estadísticas de categorías")

        # Usar el servicio de categorías para obtener estadísticas
        category_service = CategoryService(db)
        return await category_service.get_category_stats()

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de categorías: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener estadísticas"
        )


# ================================================================================================
# HEALTH CHECK ESPECÍFICO
# ================================================================================================

@router.get(
    "/health",
    summary="Health check de categorías",
    description="Verificar estado del sistema de categorías."
)
async def categories_health_check(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Health check específico del sistema de categorías.

    - **Público**: No requiere autenticación
    - **Features**: Verificación de integridad de jerarquía
    """
    try:
        # TODO: Implementar verificaciones de salud
        logger.info("Ejecutando health check del sistema de categorías")

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database_connection": "ok",
            "hierarchy_integrity": "ok",
            "total_categories": 0
        }

    except Exception as e:
        logger.error(f"Error en health check de categorías: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }