# ~/app/api/v1/endpoints/comisiones.py
from fastapi import APIRouter, Depends, Query, HTTPException
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
from app.models.payout_request import PayoutRequest, EstadoPayout
from app.schemas.payout_request import PayoutRequestCreate, PayoutRequestRead
from app.core.auth import get_current_user
from app.models.user import User


@router.get("/", summary="Consultar comisiones por período")
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


@router.post("/solicitar-pago", response_model=PayoutRequestRead)
async def solicitar_pago_comisiones(
    payout_data: PayoutRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Solicitar pago de comisiones acumuladas.

    Permite a los vendedores solicitar el pago de sus comisiones
    proporcionando datos bancarios temporales para el payout.
    """

    # Verificar que el usuario es vendedor o superior
    if current_user.user_type not in ['VENDEDOR', 'ADMIN', 'SUPERUSER']:
        raise HTTPException(
            status_code=403,
            detail="Solo los vendedores pueden solicitar pagos de comisiones"
        )

    # TODO: Verificar que tiene comisiones pendientes
    # comisiones_pendientes = await calcular_comisiones_pendientes(current_user.id, db)
    # if comisiones_pendientes < payout_data.monto_solicitado:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Comisiones disponibles insuficientes. Disponible: {comisiones_pendientes}"
    #     )

    # Crear solicitud de payout
    payout_request = PayoutRequest(
        vendedor_id=current_user.id,
        **payout_data.dict()
    )

    db.add(payout_request)
    await db.commit()
    await db.refresh(payout_request)

    return PayoutRequestRead(
        id=str(payout_request.id),
        vendedor_id=str(payout_request.vendedor_id),
        monto_solicitado=payout_request.monto_solicitado,
        estado=payout_request.estado,
        tipo_cuenta=payout_request.tipo_cuenta,
        banco=payout_request.banco,
        created_at=payout_request.created_at,
        fecha_procesamiento=payout_request.fecha_procesamiento,
        referencia_pago=payout_request.referencia_pago,
        observaciones=payout_request.observaciones
    )