from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, select
from datetime import datetime, timedelta

from app.core.auth import get_current_user
from app.database import get_async_db as get_db
from app.models import User, Product, Transaction
from app.models.incoming_product_queue import IncomingProductQueue
from app.schemas.admin import AdminDashboardResponse, GlobalKPIs, PeriodMetrics
from app.services.product_verification_workflow import ProductVerificationWorkflow, VerificationStep, StepResult
from app.core.config import settings

router = APIRouter()


@router.get("/dashboard/kpis", response_model=AdminDashboardResponse)
async def get_admin_dashboard_kpis(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
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


async def _calcular_kpis_globales(db: AsyncSession) -> GlobalKPIs:
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


async def _calcular_tendencias(db: AsyncSession, kpis_actuales: GlobalKPIs) -> Optional[PeriodMetrics]:
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


# =============================================================================
# ENDPOINTS PARA WORKFLOW DE VERIFICACIÓN DE PRODUCTOS
# =============================================================================

@router.get("/incoming-products/{queue_id}/verification/current-step")
async def get_current_verification_step(
    queue_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener el paso actual del workflow de verificación"""
    
    # Verificar permisos de administrador
    if not (current_user.is_superuser or 
            (hasattr(current_user, 'user_type') and current_user.user_type in ['ADMIN', 'SUPERUSER'])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta funcionalidad"
        )
    
    # Obtener item de la cola
    query = select(IncomingProductQueue).filter(IncomingProductQueue.id == queue_id)
    result = await db.execute(query)
    queue_item = result.scalar_one_or_none()
    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado en la cola"
        )
    
    try:
        # Para usar ProductVerificationWorkflow necesitamos una sesión síncrona
        # Crear respuesta básica temporalmente
        current_step = "initial_inspection"
        if queue_item.verification_status.value == 'PENDING':
            current_step = "initial_inspection"
        elif queue_item.verification_status.value == 'ASSIGNED':
            current_step = "documentation_check"
        elif queue_item.verification_status.value == 'IN_PROGRESS':
            current_step = "quality_assessment"
        elif queue_item.verification_status.value == 'QUALITY_CHECK':
            current_step = "location_assignment"
        elif queue_item.verification_status.value == 'APPROVED':
            current_step = "final_approval"
        elif queue_item.verification_status.value == 'COMPLETED':
            current_step = "completed"
        
        progress = {
            "queue_id": str(queue_item.id),
            "current_step": current_step,
            "progress_percentage": 20,  # Porcentaje básico
            "steps": [
                {
                    "step": "initial_inspection",
                    "title": "Inspección Inicial",
                    "description": "Revisión visual del producto recibido",
                    "is_current": current_step == "initial_inspection",
                    "is_completed": False,
                    "order": 1
                },
                {
                    "step": "documentation_check",
                    "title": "Verificación de Documentación",
                    "description": "Revisión de documentos y certificados",
                    "is_current": current_step == "documentation_check",
                    "is_completed": False,
                    "order": 2
                },
                {
                    "step": "quality_assessment",
                    "title": "Evaluación de Calidad",
                    "description": "Pruebas de calidad y funcionalidad",
                    "is_current": current_step == "quality_assessment",
                    "is_completed": False,
                    "order": 3
                },
                {
                    "step": "location_assignment",
                    "title": "Asignación de Ubicación",
                    "description": "Determinar ubicación en inventario",
                    "is_current": current_step == "location_assignment",
                    "is_completed": False,
                    "order": 4
                },
                {
                    "step": "final_approval",
                    "title": "Aprobación Final",
                    "description": "Validación final antes de completar",
                    "is_current": current_step == "final_approval",
                    "is_completed": False,
                    "order": 5
                }
            ],
            "can_proceed": True,
            "verification_attempts": queue_item.verification_attempts
        }
        
        return {
            "status": "success",
            "data": progress
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estado de verificación: {str(e)}"
        )


@router.post("/incoming-products/{queue_id}/verification/execute-step")
async def execute_verification_step(
    queue_id: UUID,
    step_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ejecutar un paso específico del workflow de verificación"""
    
    # Verificar permisos de administrador
    if not (current_user.is_superuser or 
            (hasattr(current_user, 'user_type') and current_user.user_type in ['ADMIN', 'SUPERUSER'])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ejecutar verificaciones"
        )
    
    # Obtener item de la cola
    query = select(IncomingProductQueue).filter(IncomingProductQueue.id == queue_id)
    result = await db.execute(query)
    queue_item = result.scalar_one_or_none()
    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado en la cola"
        )
    
    try:
        # Validar datos del paso
        required_fields = ['step', 'passed', 'notes']
        for field in required_fields:
            if field not in step_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo requerido faltante: {field}"
                )
        
        # Crear objetos para el workflow
        step = VerificationStep(step_data['step'])
        result = StepResult(
            passed=step_data['passed'],
            notes=step_data['notes'],
            issues=step_data.get('issues', []),
            metadata=step_data.get('metadata', {})
        )
        
        # Ejecutar paso
        workflow = ProductVerificationWorkflow(db, queue_item)
        success = workflow.execute_step(step, result)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo ejecutar el paso de verificación"
            )
        
        # Obtener estado actualizado
        updated_progress = workflow.get_workflow_progress()
        
        return {
            "status": "success",
            "message": "Paso de verificación ejecutado exitosamente",
            "data": updated_progress
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Valor inválido: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al ejecutar paso de verificación: {str(e)}"
        )


@router.get("/incoming-products/{queue_id}/verification/history")
async def get_verification_history(
    queue_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener historial completo de verificación de un producto"""
    
    # Verificar permisos de administrador
    if not (current_user.is_superuser or 
            (hasattr(current_user, 'user_type') and current_user.user_type in ['ADMIN', 'SUPERUSER'])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder al historial"
        )
    
    # Obtener item de la cola
    query = select(IncomingProductQueue).filter(IncomingProductQueue.id == queue_id)
    result = await db.execute(query)
    queue_item = result.scalar_one_or_none()
    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado en la cola"
        )
    
    try:
        # Construir historial de verificación
        history = {
            "queue_id": queue_id,
            "product_id": queue_item.product_id,
            "verification_status": queue_item.verification_status,
            "verification_attempts": queue_item.verification_attempts or 0,
            "verification_notes": queue_item.verification_notes,
            "quality_score": queue_item.quality_score,
            "quality_issues": queue_item.quality_issues,
            "assigned_to": queue_item.assigned_to,
            "assigned_at": queue_item.assigned_at.isoformat() if queue_item.assigned_at else None,
            "processing_started_at": queue_item.processing_started_at.isoformat() if queue_item.processing_started_at else None,
            "processing_completed_at": queue_item.processing_completed_at.isoformat() if queue_item.processing_completed_at else None,
            "created_at": queue_item.created_at.isoformat(),
            "updated_at": queue_item.updated_at.isoformat() if queue_item.updated_at else None
        }
        
        # Obtener progreso actual del workflow
        workflow = ProductVerificationWorkflow(db, queue_item)
        progress = workflow.get_workflow_progress()
        
        return {
            "status": "success",
            "data": {
                "history": history,
                "current_workflow": progress
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial de verificación: {str(e)}"
        )