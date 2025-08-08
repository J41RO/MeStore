# ~/app/api/v1/endpoints/pagos.py
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.transaction import TransactionRead
from sqlalchemy import select, desc
from app.models.transaction import Transaction
from pydantic import BaseModel
from datetime import datetime

class HistorialPagosResponse(BaseModel):
    """Respuesta del endpoint de historial de pagos."""
    transacciones: List[TransactionRead]
    total: int

router = APIRouter()


@router.get("/historial", response_model=HistorialPagosResponse)
async def get_historial_pagos(
    db: AsyncSession = Depends(get_db)
) -> HistorialPagosResponse:
    """Obtener historial de transferencias."""
    query = select(Transaction).order_by(desc(Transaction.created_at))
    result = await db.execute(query)
    transacciones = result.scalars().all()

    return HistorialPagosResponse(
        transacciones=transacciones,
        total=len(transacciones)
    )