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

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse

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
