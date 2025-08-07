# ~/app/api/v1/endpoints/comisiones.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from app.core.database import get_db

router = APIRouter()

from sqlalchemy import select, func, and_
from decimal import Decimal
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionRead
from typing import List, Dict, Any


@router.get("/comisiones", summary="Consultar comisiones por período")
async def get_comisiones(
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
# Construir query base
    query = select(Transaction).where(
        Transaction.porcentaje_mestocker.is_not(None)
    )
    
    # Aplicar filtros de fecha si se proporcionan
    if fecha_inicio:
        query = query.where(Transaction.fecha_transaccion >= fecha_inicio)
    if fecha_fin:
        query = query.where(Transaction.fecha_transaccion <= fecha_fin)

    # Ejecutar query
    result = await db.execute(query)
    transactions = result.scalars().all()

    # Formatear respuesta
    comisiones_data = []
    for tx in transactions:
        if tx.porcentaje_mestocker and tx.monto:
            comision_monto = (tx.monto * tx.porcentaje_mestocker) / 100
            comisiones_data.append({
                "transaction_id": str(tx.id),
                "fecha": tx.fecha_transaccion.isoformat(),
                "monto_total": float(tx.monto),
                "porcentaje_comision": float(tx.porcentaje_mestocker),
                "monto_comision": float(comision_monto),
                "monto_vendedor": float(tx.monto_vendedor) if tx.monto_vendedor else float(tx.monto - comision_monto)
            })

    return {"comisiones": comisiones_data, "total_registros": len(comisiones_data)}