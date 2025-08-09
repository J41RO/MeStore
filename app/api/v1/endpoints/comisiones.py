# ~/app/api/v1/endpoints/comisiones.py
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.financial_reports import ComisionBreakdown
from app.models.commission_dispute import ComissionDispute
from app.schemas.commission_dispute import DisputeCreate, DisputeResponse

router = APIRouter()

from decimal import Decimal
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import and_, func, select

from app.core.auth import get_current_user
from app.models.payout_request import EstadoPayout, PayoutRequest
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.payout_request import PayoutRequestCreate, PayoutRequestRead
from app.schemas.transaction import TransactionRead


@router.get("/", summary="Consultar comisiones por período")
async def get_comisiones(
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    # Construir query base
    query = select(Transaction).where(Transaction.porcentaje_mestocker.is_not(None))

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
            comisiones_data.append(
                {
                    "transaction_id": str(tx.id),
                    "fecha": tx.fecha_transaccion.isoformat(),
                    "monto_total": float(tx.monto),
                    "porcentaje_comision": float(tx.porcentaje_mestocker),
                    "monto_comision": float(comision_monto),
                    "monto_vendedor": (
                        float(tx.monto_vendedor)
                        if tx.monto_vendedor
                        else float(tx.monto - comision_monto)
                    ),
                }
            )

    return {"comisiones": comisiones_data, "total_registros": len(comisiones_data)}


@router.post("/solicitar-pago", response_model=PayoutRequestRead)
async def solicitar_pago_comisiones(
    payout_data: PayoutRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Solicitar pago de comisiones acumuladas.

    Permite a los vendedores solicitar el pago de sus comisiones
    proporcionando datos bancarios temporales para el payout.
    """

    # Verificar que el usuario es vendedor o superior
    if current_user.user_type not in ["VENDEDOR", "ADMIN", "SUPERUSER"]:
        raise HTTPException(
            status_code=403,
            detail="Solo los vendedores pueden solicitar pagos de comisiones",
        )

    # TODO: Verificar que tiene comisiones pendientes
    # comisiones_pendientes = await calcular_comisiones_pendientes(current_user.id, db)
    # if comisiones_pendientes < payout_data.monto_solicitado:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Comisiones disponibles insuficientes. Disponible: {comisiones_pendientes}"
    #     )

    # Crear solicitud de payout
    payout_request = PayoutRequest(vendedor_id=current_user.id, **payout_data.dict())

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
        observaciones=payout_request.observaciones,
    )


@router.get(
    "/detalle/{transaction_id}",
    response_model=ComisionBreakdown,
    summary="Obtener breakdown de comisión",
)
async def get_comision_detalle(
    transaction_id: UUID, db: AsyncSession = Depends(get_db)
) -> ComisionBreakdown:
    """Obtener breakdown detallado de comisiones para una transacción."""
    # Buscar transacción por ID
    query = select(Transaction).where(Transaction.id == transaction_id)
    result = await db.execute(query)
    transaction = result.scalars().first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    if not transaction.porcentaje_mestocker:
        raise HTTPException(status_code=400, detail="Transacción sin datos de comisión")

    # Calcular breakdown
    monto_comision = (transaction.monto * transaction.porcentaje_mestocker) / 100
    monto_vendedor = transaction.monto_vendedor or (transaction.monto - monto_comision)

    return ComisionBreakdown(
        transaction_id=transaction.id,
        monto_total=transaction.monto,
        porcentaje_comision=transaction.porcentaje_mestocker,
        monto_comision=monto_comision,
        monto_vendedor=monto_vendedor,
        fecha_transaccion=transaction.created_at,
    )



@router.post("/dispute", response_model=DisputeResponse, status_code=status.HTTP_201_CREATED)
async def reportar_disputa_comision(
    dispute_data: DisputeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Reportar discrepancia en comisión de transacción.

    Permite a vendedores reportar cuando consideran que
    la comisión cobrada no es correcta.
    """

    # Verificar que el usuario puede reportar disputas
    if current_user.user_type not in ["VENDEDOR", "ADMIN", "SUPERUSER"]:
        raise HTTPException(
            status_code=403,
            detail="Solo vendedores pueden reportar disputas de comisiones"
        )

    # Verificar que la transacción existe
    query = select(Transaction).where(Transaction.id == dispute_data.transaction_id)
    result = await db.execute(query)
    transaction = result.scalars().first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transacción no encontrada"
        )

    # Verificar que la transacción tiene datos de comisión
    if not transaction.porcentaje_mestocker:
        raise HTTPException(
            status_code=400,
            detail="La transacción no tiene información de comisiones para disputar"
        )

    # Verificar que el usuario es el vendedor de la transacción (excepto admins)
    if current_user.user_type == "VENDEDOR" and str(transaction.vendedor_id) != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Solo puedes disputar tus propias transacciones"
        )

    # Verificar que no existe una disputa activa para esta transacción
    existing_dispute_query = select(ComissionDispute).where(
        and_(
            ComissionDispute.transaction_id == dispute_data.transaction_id,
            ComissionDispute.estado.in_(["ABIERTO", "EN_REVISION"])
        )
    )
    existing_result = await db.execute(existing_dispute_query)
    existing_dispute = existing_result.scalars().first()

    if existing_dispute:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una disputa activa para esta transacción"
        )

    # Crear la disputa
    new_dispute = ComissionDispute(
        transaction_id=dispute_data.transaction_id,
        usuario_id=UUID(current_user.id),
        motivo=dispute_data.motivo,
        descripcion=dispute_data.descripcion
    )

    db.add(new_dispute)
    await db.commit()
    await db.refresh(new_dispute)

    return DisputeResponse(
        message="Disputa de comisión reportada exitosamente",
        dispute_id=new_dispute.id,
        estado=new_dispute.estado
    )