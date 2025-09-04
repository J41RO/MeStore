from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from app.api.v1.deps.auth import get_current_active_user
from app.api.v1.deps.database import get_db
from app.models import User, Product, Transaction
from app.schemas.admin import AdminDashboardResponse, GlobalKPIs, PeriodMetrics
from app.core.config import settings

router = APIRouter()


@router.get("/dashboard/kpis", response_model=AdminDashboardResponse)
async def get_admin_dashboard_kpis(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    include_trends: bool = True
) -> AdminDashboardResponse:
    """
    Obtener KPIs globales para dashboard administrativo.
    
    Requiere permisos de SUPERUSER o ADMIN.
    """
    
    # Verificar permisos adicionales (SUPERUSER o ADMIN)
    if not (current_user.is_superuser or 
            (hasattr(current_user, 'user_type') and current_user.user_type in ['ADMIN', 'SUPERUSER'])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )



@router.get("/dashboard/growth-data")
async def get_growth_data(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    months_back: int = 6
):
    """Obtener datos temporales para gráficos de crecimiento."""
    # Verificar permisos
    if not (current_user.is_superuser or
            (hasattr(current_user, 'user_type') and current_user.user_type in ['ADMIN', 'SUPERUSER'])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )
    
    try:
        # Datos de ejemplo para desarrollo
        growth_data = [
            {"month": "Ene", "currentPeriod": 12000, "previousPeriod": 10000, "growthRate": 20},
            {"month": "Feb", "currentPeriod": 15000, "previousPeriod": 12000, "growthRate": 25},
            {"month": "Mar", "currentPeriod": 18000, "previousPeriod": 14000, "growthRate": 28.6},
            {"month": "Abr", "currentPeriod": 22000, "previousPeriod": 16000, "growthRate": 37.5},
            {"month": "May", "currentPeriod": 25000, "previousPeriod": 18000, "growthRate": 38.9},
            {"month": "Jun", "currentPeriod": 28000, "previousPeriod": 20000, "growthRate": 40}
        ]
        
        return {
            "growth_data": growth_data,
            "comparison_data": growth_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo datos de crecimiento: {str(e)}"
        )
    
    try:
        # Calcular KPIs actuales
        kpis_actuales = await _calcular_kpis_globales(db)
        
        # Preparar respuesta
        dashboard_response = AdminDashboardResponse(
            kpis_globales=kpis_actuales,
            metricas_periodo=None if not include_trends else await _calcular_tendencias(db, kpis_actuales)
        )
        
        return dashboard_response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular KPIs administrativos: {str(e)}"
        )


async def _calcular_kpis_globales(db: Session) -> GlobalKPIs:
    """Calcular KPIs globales actuales"""
    
        # QUERIES SQL IMPLEMENTADAS:
    # GMV: SELECT SUM(amount) FROM transactions WHERE status='COMPLETADA'
    gmv_query = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.status == 'COMPLETADA'
    )
    gmv_total = gmv_query.scalar() or 0.0
    
    # Vendedores activos: usuarios tipo VENDEDOR con login reciente (últimos 30 días)
    fecha_limite = datetime.now() - timedelta(days=30)
    vendedores_activos = db.query(func.count(User.id)).filter(
        and_(
            User.user_type == 'VENDEDOR',
            User.is_active == True,
            User.last_login >= fecha_limite
        )
    ).scalar() or 0
    
    # Total productos activos
    total_productos = db.query(func.count(Product.id)).filter(
        Product.status == 'ACTIVE'
    ).scalar() or 0
    
    # Total órdenes/transacciones
    total_ordenes = db.query(func.count(Transaction.id)).scalar() or 0
    
    return GlobalKPIs(
        gmv_total=float(gmv_total),
        vendedores_activos=vendedores_activos,
        total_productos=total_productos,
        total_ordenes=total_ordenes
    )


async def _calcular_tendencias(db: Session, kpis_actuales: GlobalKPIs) -> Optional[PeriodMetrics]:
    """Calcular tendencias y comparación con período anterior"""
    
    try:
        # Calcular KPIs del mes anterior para comparación
        fecha_inicio_anterior = datetime.now() - timedelta(days=60)
        fecha_fin_anterior = datetime.now() - timedelta(days=30)
        
        # GMV período anterior
        gmv_anterior = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            and_(
                Transaction.status == 'COMPLETADA',
                Transaction.created_at >= fecha_inicio_anterior,
                Transaction.created_at <= fecha_fin_anterior
            )
        ).scalar() or 0.0
        
        # Vendedores activos período anterior
        vendedores_anterior = db.query(func.count(User.id)).filter(
            and_(
                User.user_type == 'VENDEDOR',
                User.is_active == True,
                User.last_login >= fecha_inicio_anterior,
                User.last_login <= fecha_fin_anterior
            )
        ).scalar() or 0
        
        kpis_anteriores = GlobalKPIs(
            gmv_total=float(gmv_anterior),
            vendedores_activos=vendedores_anterior,
            total_productos=kpis_actuales.total_productos,  # Asumimos mismos productos
            total_ordenes=kpis_actuales.total_ordenes,  # Simplificación para MVP
            fecha_calculo=fecha_fin_anterior
        )
        
        return PeriodMetrics(
            periodo_actual=kpis_actuales,
            periodo_anterior=kpis_anteriores
        )
        
    except Exception:
        # En caso de error, devolver solo período actual
        return PeriodMetrics(
            periodo_actual=kpis_actuales,
            periodo_anterior=None
        )