# ~/app/api/v1/endpoints/products_bulk.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Endpoints de Operaciones Bulk de Productos API v1
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: products_bulk.py
# Ruta: ~/app/api/v1/endpoints/products_bulk.py
# Autor: Jairo
# Fecha de Creación: 2025-08-18
# Última Actualización: 2025-08-18
# Versión: 1.0.0
# Propósito: Endpoints para operaciones bulk (masivas) de productos
#            Implementa DELETE y PATCH en lote con validaciones
#            Diseñado para integración con frontend bulk actions
#
# Modificaciones:
# 2025-08-18 - Implementación inicial con DELETE y PATCH bulk endpoints
#
# ---------------------------------------------------------------------------------------------

"""
Endpoints para operaciones bulk de productos.

Este módulo contiene:
- DELETE /products/bulk: Eliminación masiva de productos
- PATCH /products/bulk/status: Cambio de estado masivo de productos
- Validaciones de seguridad y permisos
- Manejo de errores estructurado
"""

import logging
from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.product import Product
from app.api.v1.deps.auth import get_current_user
from sqlalchemy.orm import Session

# Configurar logger específico para este módulo
logger = logging.getLogger(__name__)

# Crear router para endpoints bulk
router = APIRouter()

# Schemas para requests bulk
class BulkDeleteRequest(BaseModel):
    """Schema para request de eliminación bulk"""
    product_ids: List[str] = Field(..., description="Lista de IDs de productos a eliminar", min_items=1, max_items=100)

class BulkStatusUpdateRequest(BaseModel):
    """Schema para request de actualización de estado bulk"""
    product_ids: List[str] = Field(..., description="Lista de IDs de productos a actualizar", min_items=1, max_items=100)
    status: str = Field(..., description="Nuevo estado para los productos", pattern="^(active|inactive|pending|archived)$")

class BulkOperationResponse(BaseModel):
    """Schema para respuesta de operaciones bulk"""
    success: bool
    message: str
    affected_count: int
    errors: List[Dict[str, Any]] = []

# Utility function para validar IDs
def validate_product_ids(product_ids: List[str]) -> List[UUID]:
    """
    Valida y convierte string IDs a UUIDs
    
    Args:
        product_ids: Lista de IDs como strings
        
    Returns:
        Lista de UUIDs válidos
        
    Raises:
        HTTPException: Si algún ID no es válido
    """
    valid_uuids = []
    invalid_ids = []
    
    for pid in product_ids:
        try:
            valid_uuids.append(UUID(pid))
        except ValueError:
            invalid_ids.append(pid)
    
    if invalid_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"IDs de producto inválidos: {invalid_ids}"
        )
    
    return valid_uuids

@router.delete("/bulk", response_model=BulkOperationResponse)
async def bulk_delete_products(
    request: BulkDeleteRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Eliminar múltiples productos en una sola operación.
    
    - **product_ids**: Lista de IDs de productos a eliminar (máximo 100)
    - Requiere autenticación de usuario
    - Valida existencia de productos antes de eliminar
    - Retorna conteo de productos eliminados y errores si los hay
    """
    logger.info(f"Usuario {current_user.id} iniciando eliminación bulk de {len(request.product_ids)} productos")
    
    try:
        # Validar formato de IDs
        valid_uuids = validate_product_ids(request.product_ids)
        
        # Verificar cuáles productos existen
        existing_products = db.query(Product).filter(Product.id.in_(valid_uuids)).all()
        existing_ids = {str(p.id) for p in existing_products}
        missing_ids = set(request.product_ids) - existing_ids
        
        errors = []
        if missing_ids:
            errors.append({
                "type": "not_found",
                "message": f"Productos no encontrados: {list(missing_ids)}",
                "product_ids": list(missing_ids)
            })
        
        # Eliminar productos existentes
        deleted_count = 0
        if existing_products:
            for product in existing_products:
                db.delete(product)
            db.commit()
            deleted_count = len(existing_products)
            
        logger.info(f"Eliminación bulk completada: {deleted_count} productos eliminados, {len(missing_ids)} no encontrados")
        
        return BulkOperationResponse(
            success=True,
            message=f"Eliminación bulk completada: {deleted_count} productos eliminados",
            affected_count=deleted_count,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"Error en eliminación bulk: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante eliminación bulk: {str(e)}"
        )

@router.patch("/bulk/status", response_model=BulkOperationResponse)
async def bulk_update_product_status(
    request: BulkStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Actualizar estado de múltiples productos en una sola operación.
    
    - **product_ids**: Lista de IDs de productos a actualizar (máximo 100)
    - **status**: Nuevo estado (active, inactive, pending, archived)
    - Requiere autenticación de usuario
    - Valida existencia de productos antes de actualizar
    - Retorna conteo de productos actualizados y errores si los hay
    """
    logger.info(f"Usuario {current_user.id} iniciando actualización bulk de estado '{request.status}' para {len(request.product_ids)} productos")
    
    try:
        # Validar formato de IDs
        valid_uuids = validate_product_ids(request.product_ids)
        
        # Verificar cuáles productos existen
        existing_products = db.query(Product).filter(Product.id.in_(valid_uuids)).all()
        existing_ids = {str(p.id) for p in existing_products}
        missing_ids = set(request.product_ids) - existing_ids
        
        errors = []
        if missing_ids:
            errors.append({
                "type": "not_found",
                "message": f"Productos no encontrados: {list(missing_ids)}",
                "product_ids": list(missing_ids)
            })
        
        # Actualizar estado de productos existentes
        updated_count = 0
        if existing_products:
            for product in existing_products:
                product.status = request.status
            db.commit()
            updated_count = len(existing_products)
            
        logger.info(f"Actualización bulk de estado completada: {updated_count} productos actualizados a '{request.status}', {len(missing_ids)} no encontrados")
        
        return BulkOperationResponse(
            success=True,
            message=f"Actualización bulk completada: {updated_count} productos actualizados a '{request.status}'",
            affected_count=updated_count,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"Error en actualización bulk de estado: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante actualización bulk: {str(e)}"
        )
