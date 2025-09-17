# ~/app/api/v1/endpoints/commissions.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Commission API Endpoints (PRODUCTION_READY)
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: commissions.py
# Ruta: ~/app/api/v1/endpoints/commissions.py
# Autor: Jairo
# Fecha de Creación: 2025-09-12
# Última Actualización: 2025-09-12
# Versión: 1.0.0
# Propósito: Endpoints REST para gestión de comisiones con autenticación enterprise
#            APIs para vendors, admins con rate limiting y validación
#
# Modificaciones:
# 2025-09-12 - Creación inicial con preparación hosting enterprise
#
# ---------------------------------------------------------------------------------------------

"""
PRODUCTION_READY: Endpoints REST para sistema de comisiones

Este módulo contiene:
- GET /commissions - Lista comisiones por vendor con filtros
- GET /commissions/{id} - Detalle de comisión específica
- GET /commissions/earnings - Reporte de earnings para vendor
- POST /commissions/calculate - Recálculo manual (admin only)
- PATCH /commissions/{id}/approve - Aprobación de comisión (admin only)
- Autenticación JWT y autorización por rol
- Rate limiting dinámico por ambiente
- Documentación OpenAPI completa
"""

import os
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.api.v1.deps.database import get_db
from app.api.v1.deps.auth import get_current_user
from app.models.user import User, UserType
from app.models.commission import Commission, CommissionStatus, CommissionType
from app.models.order import Order
from app.services.commission_service import CommissionService, CommissionCalculationError
from app.services.transaction_service import TransactionService
from app.schemas.commission import (
    VendorEarnings,
    CommissionReport,
    CommissionRead,
    CommissionFilters,
    CommissionListResponse
)

# Initialize router with tags and metadata
router = APIRouter(
    tags=["commissions"],
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Commission not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

# Rate limiting configuration
RATE_LIMITS = {
    'development': {'requests': 1000, 'window': 60},  # 1000 req/min for dev
    'production': {'requests': 100, 'window': 60},    # 100 req/min for prod
    'testing': {'requests': 10000, 'window': 60}      # No limits for tests
}

current_env = os.getenv('ENVIRONMENT', 'development')
current_rate_limit = RATE_LIMITS.get(current_env, RATE_LIMITS['development'])


# Pydantic schemas for request/response
class CommissionListFilters(BaseModel):
    """Filtros para listado de comisiones"""
    status: Optional[CommissionStatus] = None
    commission_type: Optional[CommissionType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=20, ge=1, le=100, description="Número de resultados por página")
    offset: int = Field(default=0, ge=0, description="Número de resultados a omitir")


class CommissionResponse(BaseModel):
    """Respuesta de comisión individual"""
    id: str
    commission_number: str
    order_id: int
    vendor_id: str
    order_amount: float
    commission_rate: float
    commission_amount: float
    vendor_amount: float
    platform_amount: float
    commission_type: str
    status: str
    currency: str
    calculated_at: datetime
    approved_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CommissionListResponse(BaseModel):
    """Respuesta de lista de comisiones con paginación"""
    commissions: List[CommissionResponse]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool


class EarningsResponse(BaseModel):
    """Respuesta de earnings del vendor"""
    vendor_id: str
    period: Dict[str, Optional[str]]
    summary: Dict[str, float]
    breakdown_by_status: Dict[str, Dict[str, Any]]
    currency: str


class ApproveCommissionRequest(BaseModel):
    """Request para aprobación de comisión"""
    notes: Optional[str] = Field(None, max_length=500, description="Notas de aprobación")


class CalculateCommissionRequest(BaseModel):
    """Request para cálculo de comisión"""
    order_id: int = Field(..., gt=0, description="ID de la orden")
    commission_type: CommissionType = Field(default=CommissionType.STANDARD)
    custom_rate: Optional[float] = Field(None, ge=0, le=1, description="Tasa personalizada (0-1)")


# Helper functions
def check_admin_permission(current_user: User) -> None:
    """Verifica permisos de administrador"""
    if current_user.user_type not in [UserType.ADMIN, UserType.SUPERUSER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required"
        )


def check_vendor_or_admin_permission(current_user: User, vendor_id: UUID) -> None:
    """Verifica permisos de vendor o admin"""
    is_admin = current_user.user_type in [UserType.ADMIN, UserType.SUPERUSER]
    is_owner = current_user.id == vendor_id
    
    if not (is_admin or is_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied - can only access own commissions"
        )


# API Endpoints
@router.get(
    "/",
    response_model=CommissionListResponse,
    summary="List commissions",
    description="Get list of commissions with filters. Vendors see only their commissions, admins see all.",
    response_description="List of commissions with pagination metadata"
)
async def list_commissions(
    status: Optional[CommissionStatus] = Query(None, description="Filter by status"),
    commission_type: Optional[CommissionType] = Query(None, description="Filter by commission type"),
    date_from: Optional[datetime] = Query(None, description="Start date filter"),
    date_to: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CommissionListResponse:
    """
    Lista comisiones con filtros y paginación
    
    - **Vendors**: Solo ven sus propias comisiones
    - **Admins**: Ven todas las comisiones del sistema
    - Filtros disponibles: status, tipo, fechas
    - Paginación automática con límites por ambiente
    """
    try:
        service = CommissionService(db)

        # Determine vendor filter based on user role
        vendor_id = None
        if current_user.user_type not in [UserType.ADMIN, UserType.SUPERUSER]:
            vendor_id = current_user.id

        # Use service method with proper parameters
        status_filter = [status] if status else None

        result = service.list_commissions(
            vendor_id=vendor_id,
            status_filter=status_filter,
            start_date=date_from,
            end_date=date_to,
            limit=limit,
            offset=offset,
            db=db
        )

        # Convert service response to API schema
        commission_responses = []
        for commission_data in result['commissions']:
            commission_responses.append(CommissionResponse(
                id=commission_data['id'],
                commission_number=commission_data['commission_number'],
                order_id=commission_data['order_id'],
                vendor_id=commission_data['vendor_id'],
                order_amount=commission_data['order_amount'],
                commission_rate=commission_data['commission_rate'],
                commission_amount=commission_data['commission_amount'],
                vendor_amount=commission_data['vendor_amount'],
                platform_amount=commission_data['platform_amount'],
                commission_type=commission_data['commission_type'],
                status=commission_data['status'],
                currency=commission_data['currency'],
                calculated_at=datetime.fromisoformat(commission_data['created_at']),  # Use created_at as calculated_at
                approved_at=datetime.fromisoformat(commission_data['approved_at']) if commission_data.get('approved_at') else None,
                paid_at=datetime.fromisoformat(commission_data['paid_at']) if commission_data.get('paid_at') else None,
                notes=commission_data.get('notes'),
                created_at=datetime.fromisoformat(commission_data['created_at']),
                updated_at=datetime.fromisoformat(commission_data['updated_at']) if commission_data.get('updated_at') else None
            ))

        return CommissionListResponse(
            commissions=commission_responses,
            total=result.get('total', len(commission_responses)),
            limit=limit,
            offset=offset,
            has_next=result.get('has_next', False),
            has_prev=result.get('has_prev', False)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving commissions: {str(e)}"
        )


@router.get(
    "/{commission_id}",
    response_model=CommissionResponse,
    summary="Get commission details",
    description="Get detailed information about a specific commission",
    response_description="Commission details"
)
async def get_commission(
    commission_id: UUID = Path(..., description="Commission ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CommissionResponse:
    """
    Obtiene detalles de una comisión específica
    
    - **Vendors**: Solo pueden ver sus propias comisiones
    - **Admins**: Pueden ver cualquier comisión
    - Incluye información completa de cálculos y estados
    """
    try:
        commission = db.query(Commission).filter(Commission.id == commission_id).first()
        
        if not commission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Commission not found"
            )
        
        # Check permissions
        check_vendor_or_admin_permission(current_user, commission.vendor_id)
        
        return CommissionResponse(
            id=str(commission.id),
            commission_number=commission.commission_number,
            order_id=commission.order_id,
            vendor_id=str(commission.vendor_id),
            order_amount=float(commission.order_amount),
            commission_rate=float(commission.commission_rate),
            commission_amount=float(commission.commission_amount),
            vendor_amount=float(commission.vendor_amount),
            platform_amount=float(commission.platform_amount),
            commission_type=commission.commission_type.value,
            status=commission.status.value,
            currency=commission.currency,
            calculated_at=commission.calculated_at,
            approved_at=commission.approved_at,
            paid_at=commission.paid_at,
            notes=commission.notes,
            created_at=commission.created_at,
            updated_at=commission.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving commission: {str(e)}"
        )


@router.get(
    "/earnings/summary",
    response_model=EarningsResponse,
    summary="Get vendor earnings",
    description="Get earnings summary for current vendor or specified vendor (admin only)",
    response_description="Earnings summary with breakdowns"
)
async def get_earnings(
    vendor_id: Optional[UUID] = Query(None, description="Vendor ID (admin only)"),
    start_date: Optional[datetime] = Query(None, description="Start date for report"),
    end_date: Optional[datetime] = Query(None, description="End date for report"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> EarningsResponse:
    """
    Obtiene reporte de earnings para un vendor
    
    - **Vendors**: Solo pueden ver sus propios earnings
    - **Admins**: Pueden especificar vendor_id para ver earnings de cualquier vendor
    - Filtros por fechas opcionales
    - Breakdown por status de comisión
    """
    try:
        service = CommissionService(db)
        
        # Determine target vendor
        target_vendor_id = vendor_id
        if target_vendor_id:
            # Only admins can query other vendors' earnings
            check_admin_permission(current_user)
        else:
            # Default to current user if vendor
            if current_user.user_type == UserType.VENDOR:
                target_vendor_id = current_user.id
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="vendor_id required for non-vendor users"
                )
        
        # Get earnings report
        earnings_data = service.get_vendor_earnings(
            vendor_id=target_vendor_id,
            start_date=start_date,
            end_date=end_date,
            db=db
        )
        
        return EarningsResponse(**earnings_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating earnings report: {str(e)}"
        )


@router.post(
    "/calculate",
    response_model=CommissionResponse,
    summary="Calculate commission for order",
    description="Manually calculate commission for an order (admin only)",
    response_description="Newly calculated commission"
)
async def calculate_commission(
    request: CalculateCommissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CommissionResponse:
    """
    Calcula manualmente comisión para una orden
    
    - **Solo Admins**: Funcionalidad restringida a administradores
    - Permite recálculo con tasa personalizada
    - Útil para correcciones o casos especiales
    """
    try:
        check_admin_permission(current_user)
        
        service = CommissionService(db)
        
        # Get the order
        order = db.query(Order).filter(Order.id == request.order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Calculate commission
        from decimal import Decimal
        custom_rate = Decimal(str(request.custom_rate)) if request.custom_rate else None
        
        commission = service.calculate_commission_for_order(
            order=order,
            commission_type=request.commission_type,
            custom_rate=custom_rate,
            db=db
        )
        
        return CommissionResponse(
            id=str(commission.id),
            commission_number=commission.commission_number,
            order_id=commission.order_id,
            vendor_id=str(commission.vendor_id),
            order_amount=float(commission.order_amount),
            commission_rate=float(commission.commission_rate),
            commission_amount=float(commission.commission_amount),
            vendor_amount=float(commission.vendor_amount),
            platform_amount=float(commission.platform_amount),
            commission_type=commission.commission_type.value,
            status=commission.status.value,
            currency=commission.currency,
            calculated_at=commission.calculated_at,
            approved_at=commission.approved_at,
            paid_at=commission.paid_at,
            notes=commission.notes,
            created_at=commission.created_at,
            updated_at=commission.updated_at
        )
        
    except CommissionCalculationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating commission: {str(e)}"
        )


@router.patch(
    "/{commission_id}/approve",
    response_model=CommissionResponse,
    summary="Approve commission",
    description="Approve a commission for payment (admin only)",
    response_description="Approved commission"
)
async def approve_commission(
    commission_id: UUID = Path(..., description="Commission ID"),
    request: ApproveCommissionRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CommissionResponse:
    """
    Aprueba una comisión para pago
    
    - **Solo Admins**: Funcionalidad restringida a administradores
    - Marca la comisión como APPROVED
    - Registra quien aprobó y cuándo
    - Opcional: agregar notas de aprobación
    """
    try:
        check_admin_permission(current_user)
        
        service = CommissionService(db)
        
        commission = service.approve_commission(
            commission_id=commission_id,
            approver_user_id=current_user.id,
            notes=request.notes,
            db=db
        )
        
        return CommissionResponse(
            id=str(commission.id),
            commission_number=commission.commission_number,
            order_id=commission.order_id,
            vendor_id=str(commission.vendor_id),
            order_amount=float(commission.order_amount),
            commission_rate=float(commission.commission_rate),
            commission_amount=float(commission.commission_amount),
            vendor_amount=float(commission.vendor_amount),
            platform_amount=float(commission.platform_amount),
            commission_type=commission.commission_type.value,
            status=commission.status.value,
            currency=commission.currency,
            calculated_at=commission.calculated_at,
            approved_at=commission.approved_at,
            paid_at=commission.paid_at,
            notes=commission.notes,
            created_at=commission.created_at,
            updated_at=commission.updated_at
        )
        
    except CommissionCalculationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error approving commission: {str(e)}"
        )


@router.get(
    "/transactions/history",
    summary="Get transaction history",
    description="Get transaction history for commissions",
    response_description="Transaction history with pagination"
)
async def get_transaction_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene historial de transacciones de comisiones
    
    - **Vendors**: Solo ven sus transacciones
    - **Admins**: Ven todas las transacciones
    - Filtros por fechas opcionales
    """
    try:
        service = TransactionService(db)
        
        # Determine user filter
        user_filter = None if current_user.user_type in [UserType.ADMIN, UserType.SUPERUSER] else current_user.id
        
        history = service.get_transaction_history(
            user_id=user_filter,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            db=db
        )
        
        return history
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving transaction history: {str(e)}"
        )


# ===================================================================
# ENDPOINTS CRÍTICOS REQUERIDOS POR EL MANAGER - MVP MESTORE
# ===================================================================

@router.get(
    "/vendors/earnings",
    response_model=VendorEarnings,
    summary="Get vendor earnings report",
    description="Get comprehensive earnings report for authenticated vendor",
    response_description="Vendor earnings with totals and metrics"
)
async def get_vendor_earnings(
    period: Optional[str] = Query("current_month", description="Período: 'current_month', 'last_month', 'last_3_months', 'ytd', 'all_time'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> VendorEarnings:
    """
    ENDPOINT CRÍTICO MVP: Obtiene reporte de earnings del vendor autenticado

    - **Solo Vendors**: Cada vendor ve únicamente sus propias ganancias
    - **Métricas incluidas**: Total earned, órdenes, comisiones, promedios
    - **Período configurable**: mes actual, último mes, últimos 3 meses, YTD, total
    - **Performance optimizada**: < 200ms response time requerido

    **Caso de uso:** Dashboard principal del vendor para ver sus ganancias
    """
    try:
        # Verificar que sea vendor
        if current_user.user_type != UserType.VENDOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only vendors can access earnings reports"
            )

        service = CommissionService(db)

        # Obtener reporte de earnings
        earnings = await service.get_vendor_earnings(
            vendor_id=current_user.id,
            period=period,
            db=db
        )

        if not earnings:
            # Retornar earnings vacío si no hay datos
            return VendorEarnings(
                vendor_id=current_user.id,
                vendor_name=current_user.first_name + " " + current_user.last_name,
                vendor_email=current_user.email,
                total_earned=Decimal('0.00'),
                total_orders=0,
                total_commission_paid=Decimal('0.00'),
                earnings_this_month=Decimal('0.00'),
                orders_this_month=0,
                commission_this_month=Decimal('0.00'),
                pending_commissions=Decimal('0.00'),
                average_commission_rate=Decimal('0.05'),
                report_period=period or "current_month",
                generated_at=datetime.utcnow(),
                currency="COP"
            )

        return earnings

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating vendor earnings report: {str(e)}"
        )


@router.get(
    "/admin/commissions",
    response_model=List[CommissionReport],
    summary="Get admin commissions report",
    description="Get comprehensive commissions report for administrators",
    response_description="List of commission reports by vendor"
)
async def get_admin_commissions(
    vendor_id: Optional[UUID] = Query(None, description="Filtrar por vendor específico"),
    date_from: Optional[datetime] = Query(None, description="Fecha inicio del reporte"),
    date_to: Optional[datetime] = Query(None, description="Fecha fin del reporte"),
    status_filter: Optional[CommissionStatus] = Query(None, description="Filtrar por estado"),
    limit: int = Query(50, ge=1, le=200, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[CommissionReport]:
    """
    ENDPOINT CRÍTICO MVP: Obtiene reporte completo de comisiones para administradores

    - **Solo Admins**: Acceso restringido a administradores
    - **Filtros avanzados**: Por vendor, fechas, estado de comisión
    - **Agregaciones**: Totales por vendor, métricas de performance
    - **Paginación**: Soporte para grandes volúmenes de datos

    **Caso de uso:** Dashboard administrativo para gestionar comisiones de todos los vendors
    """
    try:
        # Verificar permisos de admin
        if current_user.user_type not in [UserType.ADMIN, UserType.SUPER_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrator permissions required"
            )

        service = CommissionService(db)

        # Crear filtros
        filters = CommissionFilters(
            vendor_id=vendor_id,
            status=status_filter,
            date_from=date_from.date() if date_from else None,
            date_to=date_to.date() if date_to else None,
            limit=limit,
            offset=offset
        )

        # Obtener reporte de comisiones
        reports = await service.get_admin_commission_reports(
            filters=filters,
            db=db
        )

        return reports

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating admin commission reports: {str(e)}"
        )


@router.post(
    "/orders/{order_id}/process-commission",
    response_model=CommissionRead,
    summary="Process commission for order",
    description="Process commission calculation for a specific order (webhook/internal use)",
    response_description="Calculated commission"
)
async def process_order_commission(
    order_id: int = Path(..., gt=0, description="Order ID"),
    force_recalculate: bool = Query(False, description="Force recalculation if commission exists"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CommissionRead:
    """
    ENDPOINT CRÍTICO MVP: Procesa comisión para una orden específica

    - **Uso interno/webhook**: Llamado automáticamente al confirmar pago
    - **Cálculo automático**: Basado en configuración de comisiones
    - **Validación**: Verifica integridad de datos y cálculos
    - **Idempotente**: No duplica comisiones existentes (salvo force_recalculate)

    **Caso de uso:** Webhook de payment confirmation para generar comisiones automáticamente
    """
    try:
        # Verificar permisos (admin o sistema interno)
        if current_user.user_type not in [UserType.ADMIN, UserType.SUPER_ADMIN, UserType.SYSTEM]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrator or system permissions required"
            )

        service = CommissionService(db)

        # Procesar comisión para la orden
        commission = await service.process_commission_for_order(
            order_id=order_id,
            force_recalculate=force_recalculate,
            db=db
        )

        # Convertir a schema de respuesta
        return CommissionRead.model_validate(commission)

    except CommissionCalculationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing commission for order {order_id}: {str(e)}"
        )