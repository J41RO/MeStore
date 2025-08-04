# ~/app/api/v1/endpoints/productos.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Endpoints de Productos API v1
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: productos.py
# Ruta: ~/app/api/v1/endpoints/productos.py
# Autor: Jairo
# Fecha de Creación: 2025-01-14
# Última Actualización: 2025-01-14
# Versión: 1.0.0
# Propósito: Endpoints de gestión de productos para la API v1
#            Implementa CRUD operations con validaciones empresariales
#
# Modificaciones:
# 2025-01-14 - Implementación inicial del endpoint POST /productos
#
# ---------------------------------------------------------------------------------------------

"""
Endpoints de gestión de productos para la API v1.

Este módulo contiene:
- POST /productos: Crear nuevos productos con validaciones
- Validaciones empresariales (SKU único, datos requeridos)
- Manejo de errores específicos del dominio
- Logging estructurado para auditoría
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, or_, and_

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter()


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
    description="Crear un nuevo producto con validaciones empresariales",
    tags=["productos"],
)
async def create_producto(
    producto_data: ProductCreate, db: AsyncSession = Depends(get_db)
) -> ProductResponse:
    """
    Crear un nuevo producto en el marketplace.

    Args:
        producto_data: Datos del producto con validaciones
        db: Sesión de base de datos async

    Returns:
        ProductResponse: Producto creado con información completa

    Raises:
        HTTPException 400: Datos inválidos o SKU duplicado
        HTTPException 500: Error interno del servidor
    """
    try:
        from sqlalchemy import select

        logger.info(f"Creando producto con SKU: {producto_data.sku}")

        # Verificar que SKU no existe
        stmt = select(Product).where(Product.sku == producto_data.sku)
        result = await db.execute(stmt)
        existing_product = result.scalar_one_or_none()

        if existing_product:
            logger.warning(
                f"Intento de crear producto con SKU duplicado: {producto_data.sku}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Producto con SKU {producto_data.sku} ya existe",
            )

        # Crear nuevo producto
        db_product = Product(**producto_data.model_dump())
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)

        logger.info(
            f"Producto creado exitosamente: SKU={db_product.sku}, ID={db_product.id}"
        )

        # Convertir a ProductResponse
        return ProductResponse.model_validate(db_product)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando producto: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )



@router.get(
    "/",
    response_model=List[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar productos",
    description="Obtener lista de productos con filtros avanzados y paginación",
    tags=["productos"]
)
async def get_productos(
    # Filtros de búsqueda
    search: Optional[str] = Query(None, description="Búsqueda por nombre, descripción o SKU"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filtrar por estado"),

    # Filtros de precio
    precio_min: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    precio_max: Optional[float] = Query(None, ge=0, description="Precio máximo"),

    # Ordenamiento
    sort_by: Optional[str] = Query("created_at", description="Campo para ordenar"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Orden de clasificación"),

    # Paginación básica
    skip: int = Query(0, ge=0, description="Elementos a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Límite de elementos"),
    db: AsyncSession = Depends(get_db)
) -> List[ProductResponse]:
    """
    Obtener lista de productos con paginación básica.
    """
    try:
        # Query básica con paginación
        # Construir query base
        stmt = select(Product)

        # Lista para condiciones WHERE
        where_conditions = []

        # Aplicar filtro de búsqueda
        if search:
            search_filter = or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%")
            )
            where_conditions.append(search_filter)

        # Filtros específicos
        if categoria:
            where_conditions.append(Product.categoria.ilike(f"%{categoria}%"))

        if status_filter:
            where_conditions.append(Product.status == status_filter)

        # Filtros de precio
        if precio_min is not None:
            where_conditions.append(Product.precio_venta >= precio_min)
        if precio_max is not None:
            where_conditions.append(Product.precio_venta <= precio_max)

        # Aplicar condiciones WHERE si existen
        if where_conditions:
            stmt = stmt.where(and_(*where_conditions))

        # Aplicar ordenamiento
        if sort_by == "precio_venta":
            order_field = Product.precio_venta
        elif sort_by == "name":
            order_field = Product.name
        elif sort_by == "created_at":
            order_field = Product.created_at
        else:
            order_field = Product.created_at

        if sort_order == "desc":
            stmt = stmt.order_by(desc(order_field))
        else:
            stmt = stmt.order_by(asc(order_field))

        # Aplicar paginación
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        productos = result.scalars().all()

        logger.info(f"Obtenidos {len(productos)} productos con filtros aplicados")

        return [ProductResponse.model_validate(producto) for producto in productos]

    except Exception as e:
        logger.error(f"Error al obtener productos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener productos"
        )
@router.get(
    "/{producto_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener producto por ID",
    description="Obtener detalles específicos de un producto por su ID único",
    tags=["productos"]
)
async def get_producto_by_id(
    producto_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ProductResponse:
    """
    Obtener un producto específico por su ID.

    Args:
        producto_id: UUID del producto a obtener
        db: Sesión de base de datos async

    Returns:
        ProductResponse: Producto con información completa

    Raises:
        HTTPException 404: Producto no encontrado
        HTTPException 500: Error interno del servidor
    """
    try:
        from sqlalchemy import select

        logger.info(f"Buscando producto con ID: {producto_id}")

        # Buscar producto por ID
        stmt = select(Product).where(Product.id == producto_id)
        result = await db.execute(stmt)
        producto = result.scalar_one_or_none()

        if not producto:
            logger.warning(f"Producto no encontrado: ID={producto_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {producto_id} no encontrado"
            )

        logger.info(f"Producto encontrado: SKU={producto.sku}, ID={producto.id}")

        # Convertir a ProductResponse
        return ProductResponse.model_validate(producto)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener producto por ID {producto_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )



@router.put(
    "/{producto_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar producto",
    description="Actualizar un producto existente por su ID con datos parciales o completos",
    tags=["productos"]
)
async def update_producto(
    producto_id: UUID,
    producto_data: ProductUpdate,
    db: AsyncSession = Depends(get_db)
) -> ProductResponse:
    """
    Actualizar un producto existente.

    Args:
        producto_id: ID único del producto a actualizar
        producto_data: Datos del producto a actualizar (campos opcionales)
        db: Sesión de base de datos

    Returns:
        ProductResponse: Producto actualizado

    Raises:
        HTTPException: 404 si el producto no existe,
                      400 si hay errores de validación,
                      500 si hay error interno
    """
    try:
        logger.info(f"Actualizando producto con ID: {producto_id}")

        # Buscar producto existente
        from sqlalchemy import select
        result = await db.execute(
            select(Product).where(Product.id == producto_id)
        )
        producto = result.scalar_one_or_none()

        if not producto:
            logger.warning(f"Producto no encontrado: {producto_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {producto_id} no encontrado"
            )

        # Actualizar solo campos proporcionados (no None)
        update_data = producto_data.model_dump(exclude_unset=True, exclude_none=True)

        if not update_data:
            logger.warning(f"No se proporcionaron datos para actualizar: {producto_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron datos para actualizar"
            )

        # Validar SKU único si se está actualizando
        if "sku" in update_data and update_data["sku"] != producto.sku:
            existing_sku = await db.execute(
                select(Product).where(
                    Product.sku == update_data["sku"],
                    Product.id != producto_id
                )
            )
            if existing_sku.scalar_one_or_none():
                logger.warning(f"SKU ya existe: {update_data['sku']}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El SKU {update_data['sku']} ya está en uso"
                )

        # Aplicar actualizaciones
        for field, value in update_data.items():
            setattr(producto, field, value)

        # Actualizar metadatos de tracking si el método existe
        if hasattr(producto, 'update_tracking'):
            producto.update_tracking(user_id=None)  # TODO: Obtener user_id del token

        # Guardar cambios
        await db.commit()
        await db.refresh(producto)

        logger.info(f"Producto actualizado exitosamente: {producto_id}")
        return ProductResponse.model_validate(producto)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error al actualizar producto {producto_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )