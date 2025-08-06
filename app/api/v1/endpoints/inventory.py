from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryResponse
import logging

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter()


@router.get(
    "/",
    response_model=List[InventoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar inventario por vendedor",
    description="Obtener stock por vendedor con filtros opcionales",
    tags=["inventory"]
)
async def get_inventario(
    vendedor_id: Optional[UUID] = Query(None, description="ID del vendedor (updated_by_id)"),
    product_id: Optional[UUID] = Query(None, description="Filtrar por producto específico"),
    limit: int = Query(50, ge=1, le=100, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    db: AsyncSession = Depends(get_db)
) -> List[InventoryResponse]:
    """
    Consultar stock de inventario por vendedor.

    Args:
        vendedor_id: ID del vendedor para filtrar
        product_id: Filtro opcional por producto
        limit: Límite de resultados (1-100)
        offset: Offset para paginación
        db: Sesión de base de datos

    Returns:
        List[InventoryResponse]: Lista de inventario con stock
    """
    try:
        logger.info(f"Consultando inventario - vendedor: {vendedor_id}, producto: {product_id}")

        # Construir query base
        stmt = select(Inventory)

        # Filtros
        if vendedor_id:
            stmt = stmt.where(Inventory.updated_by_id == vendedor_id)
        if product_id:
            stmt = stmt.where(Inventory.product_id == product_id)

        # Solo mostrar inventario con stock disponible
        stmt = stmt.where(Inventory.cantidad > 0)

        # Paginación y orden
        stmt = stmt.order_by(Inventory.updated_at.desc()).offset(offset).limit(limit)

        # Ejecutar query
        result = await db.execute(stmt)
        inventario = result.scalars().all()

        logger.info(f"Inventario encontrado: {len(inventario)} registros")

        # Convertir a schema response
        return [InventoryResponse.model_validate(item) for item in inventario]

    except Exception as e:
        logger.error(f"Error consultando inventario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno consultando inventario"
        )