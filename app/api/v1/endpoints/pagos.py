# ~/app/api/v1/endpoints/pagos.py
# ⚠️ DEPRECATED: This endpoint will be removed in v2.0.0
# Please migrate to /api/v1/payments/ instead

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_async_db as get_db
from app.schemas.transaction import TransactionRead
from sqlalchemy import select, desc
from app.models.transaction import Transaction
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

class HistorialPagosResponse(BaseModel):
    """Respuesta del endpoint de historial de pagos."""
    transacciones: List[TransactionRead]
    total: int

router = APIRouter()


@router.get("/historial", response_model=HistorialPagosResponse)
async def get_historial_pagos(
    db: AsyncSession = Depends(get_db)
) -> HistorialPagosResponse:
    """
    Obtener historial de transferencias.

    ⚠️ DEPRECATED: This endpoint is deprecated and will be removed in v2.0.0
    Please migrate to: GET /api/v1/payments/history

    Migration guide: See SAFE_API_MIGRATION_STRATEGY.md
    """
    logger.warning(
        "⚠️ DEPRECATED: /api/v1/pagos/historial called. "
        "Migrate to /api/v1/payments/history"
    )

    query = select(Transaction).order_by(desc(Transaction.created_at))
    result = await db.execute(query)
    transacciones = result.scalars().all()

    return HistorialPagosResponse(
        transacciones=transacciones,
        total=len(transacciones)
    )