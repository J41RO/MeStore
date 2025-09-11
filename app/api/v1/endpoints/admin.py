from typing import List, Optional
from uuid import UUID
import uuid
import os
import aiofiles
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, select
from datetime import datetime, timedelta, date
from PIL import Image
import io

from app.core.auth import get_current_user
from app.database import get_async_db as get_db, get_db as get_sync_db
from app.models import User, Product, Transaction
from app.models.incoming_product_queue import IncomingProductQueue
from app.schemas.admin import AdminDashboardResponse, GlobalKPIs, PeriodMetrics
from app.schemas.product_verification import QualityPhoto, PhotoUploadResponse, QualityChecklist, QualityChecklistRequest
from app.services.product_verification_workflow import ProductVerificationWorkflow, VerificationStep, StepResult, ProductRejection, RejectionReason
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


# =============================================================================
# ENDPOINTS PARA UPLOAD DE FOTOS Y CHECKLIST DE CALIDAD
# =============================================================================

@router.post("/incoming-products/{queue_id}/verification/upload-photos", response_model=PhotoUploadResponse)
async def upload_verification_photos(
    queue_id: UUID,
    files: List[UploadFile] = File(...),
    photo_types: List[str] = Form(...),
    descriptions: List[str] = Form(default=[]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload de fotos para verificación de calidad"""
    
    # Verificar permisos de administrador
    if not (current_user.is_superuser or 
            (hasattr(current_user, 'user_type') and current_user.user_type in ['ADMIN', 'SUPERUSER'])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para subir fotos"
        )
    
    # Verificar que el producto existe
    query = select(IncomingProductQueue).filter(IncomingProductQueue.id == queue_id)
    result = await db.execute(query)
    queue_item = result.scalar_one_or_none()
    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado en la cola"
        )
    
    # Validar tipos de archivo permitidos
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    max_file_size = 10 * 1024 * 1024  # 10MB máximo
    
    uploaded_photos = []
    failed_uploads = []
    
    # Crear directorio si no existe
    upload_dir = Path("uploads/verification_photos")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        for i, file in enumerate(files):
            try:
                # Validar tipo de archivo
                if file.content_type not in allowed_types:
                    failed_uploads.append(f"{file.filename}: Tipo de archivo no permitido")
                    continue
                
                # Leer contenido del archivo
                content = await file.read()
                
                # Validar tamaño
                if len(content) > max_file_size:
                    failed_uploads.append(f"{file.filename}: Archivo demasiado grande (máximo 10MB)")
                    continue
                
                # Generar nombre único
                file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
                unique_filename = f"verification_{queue_id}_{uuid.uuid4().hex}.{file_extension}"
                file_path = upload_dir / unique_filename
                
                # Procesar y comprimir imagen
                try:
                    with Image.open(io.BytesIO(content)) as img:
                        # Convertir a RGB si es necesario
                        if img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')
                        
                        # Redimensionar si es muy grande
                        img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                        
                        # Guardar archivo comprimido
                        img.save(file_path, optimize=True, quality=85)
                    
                    # Crear objeto QualityPhoto
                    photo_type = photo_types[i] if i < len(photo_types) else "general"
                    description = descriptions[i] if i < len(descriptions) else None
                    
                    quality_photo = QualityPhoto(
                        photo_type=photo_type,
                        filename=unique_filename,
                        url=f"/uploads/verification_photos/{unique_filename}",
                        description=description,
                        is_required=photo_type in ["general", "damage", "label"],
                        uploaded_at=datetime.now()
                    )
                    
                    uploaded_photos.append(quality_photo)
                    
                except Exception as img_error:
                    failed_uploads.append(f"{file.filename}: Error procesando imagen - {str(img_error)}")
                    # Limpiar archivo si se creó
                    if file_path.exists():
                        file_path.unlink()
                    continue
                    
            except Exception as file_error:
                failed_uploads.append(f"{file.filename}: Error procesando archivo - {str(file_error)}")
                continue
        
        return PhotoUploadResponse(
            uploaded_photos=uploaded_photos,
            total_uploaded=len(uploaded_photos),
            failed_uploads=failed_uploads
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error subiendo fotos: {str(e)}"
        )


@router.delete("/verification-photos/{filename}")
async def delete_verification_photo(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Eliminar foto de verificación"""
    
    # Verificar permisos de administrador
    if not (current_user.is_superuser or 
            (hasattr(current_user, 'user_type') and current_user.user_type in ['ADMIN', 'SUPERUSER'])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar fotos"
        )
    
    try:
        # Validar nombre de archivo (seguridad)
        if not filename.startswith("verification_") or ".." in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre de archivo inválido"
            )
        
        file_path = Path("uploads/verification_photos") / filename
        
        if file_path.exists():
            file_path.unlink()
            return {"message": "Foto eliminada exitosamente", "filename": filename}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Foto no encontrada"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando foto: {str(e)}"
        )


@router.post("/incoming-products/{queue_id}/verification/quality-checklist")
async def submit_quality_checklist(
    queue_id: UUID,
    checklist_request: QualityChecklistRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enviar checklist de calidad completado"""
    
    # Verificar permisos de administrador
    if not (current_user.is_superuser or 
            (hasattr(current_user, 'user_type') and current_user.user_type in ['ADMIN', 'SUPERUSER'])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para enviar checklists"
        )
    
    # Verificar que el queue_id coincida
    if checklist_request.queue_id != queue_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de cola no coincide"
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
        checklist = checklist_request.checklist
        
        # Actualizar campos de calidad en el queue_item
        queue_item.quality_score = checklist.quality_score
        queue_item.verification_notes = checklist.inspector_notes
        queue_item.quality_issues = f"Daños: {checklist.has_damage}, Faltantes: {checklist.has_missing_parts}, Defectos: {checklist.has_defects}"
        
        # Añadir metadatos del inspector
        if checklist.inspector_id:
            queue_item.assigned_to = UUID(checklist.inspector_id) if isinstance(checklist.inspector_id, str) else checklist.inspector_id
        
        # Ejecutar paso de quality_assessment con los resultados del checklist
        step_data = {
            "step": "quality_assessment",
            "passed": checklist.approved,
            "notes": checklist.inspector_notes,
            "metadata": {
                "quality_checklist": checklist.dict(),
                "quality_score": checklist.quality_score,
                "inspector_id": checklist.inspector_id or str(current_user.id),
                "inspection_duration_minutes": checklist.inspection_duration_minutes,
                "overall_condition": checklist.overall_condition,
                "approved": checklist.approved
            }
        }
        
        # Crear objetos para el workflow
        step = VerificationStep(step_data['step'])
        step_result = StepResult(
            passed=step_data['passed'],
            notes=step_data['notes'],
            issues=[],
            metadata=step_data.get('metadata', {})
        )
        
        # Ejecutar paso en el workflow
        workflow = ProductVerificationWorkflow(db, queue_item)
        success = workflow.execute_step(step, step_result)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo procesar el checklist de calidad"
            )
        
        # Commitear cambios
        await db.commit()
        
        # Obtener estado actualizado del workflow
        updated_progress = workflow.get_workflow_progress()
        
        return {
            "status": "success",
            "message": "Checklist de calidad procesado exitosamente",
            "data": {
                "checklist": checklist.dict(),
                "workflow_progress": updated_progress
            }
        }
        
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Valor inválido en checklist: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando checklist de calidad: {str(e)}"
        )


# ENDPOINTS PARA SISTEMA DE RECHAZO
def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """Validar que el usuario tenga permisos de administrador"""
    if not (current_user.is_superuser or 
            (hasattr(current_user, 'user_type') and current_user.user_type in ['ADMIN', 'SUPERUSER'])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador"
        )
    return current_user


@router.post("/incoming-products/{queue_id}/verification/reject")
async def reject_product(
    queue_id: int,
    rejection_data: ProductRejection,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Rechazar producto y enviar notificaciones al vendedor"""
    
    # Obtener producto de la cola
    queue_item = db.query(IncomingProductQueue).filter(
        IncomingProductQueue.id == queue_id
    ).first()
    
    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado en cola"
        )
    
    # Verificar que el producto no esté ya procesado
    if queue_item.verification_status in ["APPROVED", "COMPLETED", "REJECTED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El producto ya está en estado: {queue_item.verification_status}"
        )
    
    try:
        # Crear workflow y rechazar
        workflow = ProductVerificationWorkflow(db, queue_item)
        success = await workflow.reject_product(rejection_data, str(current_user.id))
        
        if success:
            return {
                "status": "success",
                "message": "Producto rechazado exitosamente",
                "data": {
                    "queue_id": queue_id,
                    "tracking_number": queue_item.tracking_number,
                    "rejection_reason": rejection_data.reason.value,
                    "notification_sent": True,
                    "can_appeal": rejection_data.can_appeal,
                    "appeal_deadline": rejection_data.appeal_deadline.isoformat() if rejection_data.appeal_deadline else None
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al rechazar producto"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando rechazo: {str(e)}"
        )


@router.get("/incoming-products/{queue_id}/rejection-history")
async def get_rejection_history(
    queue_id: int,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Obtener historial de rechazos de un producto"""
    
    queue_item = db.query(IncomingProductQueue).filter(
        IncomingProductQueue.id == queue_id
    ).first()
    
    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    return {
        "status": "success",
        "data": {
            "queue_id": queue_id,
            "tracking_number": queue_item.tracking_number,
            "current_status": queue_item.verification_status,
            "quality_issues": queue_item.quality_issues,
            "verification_notes": queue_item.verification_notes,
            "quality_score": queue_item.quality_score,
            "rejection_count": queue_item.verification_attempts or 0,
            "vendor_info": {
                "id": queue_item.vendor_id,
                "email": queue_item.vendor.email if queue_item.vendor else None,
                "phone": getattr(queue_item.vendor, 'telefono', None) if queue_item.vendor else None
            },
            "timeline": {
                "created_at": queue_item.created_at.isoformat() if queue_item.created_at else None,
                "updated_at": queue_item.updated_at.isoformat() if queue_item.updated_at else None,
                "assigned_at": queue_item.assigned_at.isoformat() if queue_item.assigned_at else None,
                "processing_started_at": queue_item.processing_started_at.isoformat() if queue_item.processing_started_at else None,
                "processing_completed_at": queue_item.processing_completed_at.isoformat() if queue_item.processing_completed_at else None
            }
        }
    }


@router.get("/rejections/summary")
async def get_rejections_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Obtener resumen de rechazos por período"""
    
    query = db.query(IncomingProductQueue).filter(
        IncomingProductQueue.verification_status == "REJECTED"
    )
    
    if start_date:
        query = query.filter(IncomingProductQueue.created_at >= start_date)
    if end_date:
        query = query.filter(IncomingProductQueue.created_at <= end_date)
    
    rejected_products = query.all()
    
    # Agrupar por razón de rechazo
    rejection_summary = {}
    rejection_reasons_count = {}
    
    for product in rejected_products:
        reason = product.quality_issues or "unknown"
        
        # Contar por razón
        if reason not in rejection_reasons_count:
            rejection_reasons_count[reason] = 0
        rejection_reasons_count[reason] += 1
        
        # Detalles por razón
        if reason not in rejection_summary:
            rejection_summary[reason] = []
        rejection_summary[reason].append({
            "queue_id": product.id,
            "tracking_number": product.tracking_number,
            "rejected_at": product.updated_at.isoformat() if product.updated_at else None,
            "quality_score": product.quality_score,
            "vendor_id": product.vendor_id,
            "verification_attempts": product.verification_attempts
        })
    
    # Estadísticas generales
    total_rejected = len(rejected_products)
    average_quality_score = 0
    if rejected_products:
        scores = [p.quality_score for p in rejected_products if p.quality_score is not None]
        if scores:
            average_quality_score = sum(scores) / len(scores)
    
    return {
        "status": "success",
        "data": {
            "summary": {
                "total_rejected": total_rejected,
                "period": f"{start_date} to {end_date}" if start_date and end_date else "All time",
                "average_quality_score": round(average_quality_score, 2),
                "rejection_rate": round((total_rejected / max(1, total_rejected)) * 100, 2)
            },
            "rejection_reasons_count": rejection_reasons_count,
            "rejection_details": rejection_summary,
            "available_reasons": [reason.value for reason in RejectionReason]
        }
    }


@router.post("/incoming-products/{queue_id}/verification/approve")
async def approve_product(
    queue_id: int,
    quality_score: Optional[int] = None,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Aprobar producto y enviar notificación al vendedor"""
    
    # Obtener producto de la cola
    queue_item = db.query(IncomingProductQueue).filter(
        IncomingProductQueue.id == queue_id
    ).first()
    
    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado en cola"
        )
    
    # Verificar que el producto no esté ya procesado
    if queue_item.verification_status in ["APPROVED", "COMPLETED", "REJECTED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El producto ya está en estado: {queue_item.verification_status}"
        )
    
    try:
        # Crear workflow y aprobar
        workflow = ProductVerificationWorkflow(db, queue_item)
        success = await workflow.approve_product(str(current_user.id), quality_score)
        
        if success:
            return {
                "status": "success",
                "message": "Producto aprobado exitosamente",
                "data": {
                    "queue_id": queue_id,
                    "tracking_number": queue_item.tracking_number,
                    "quality_score": quality_score,
                    "notification_sent": True,
                    "new_status": "APPROVED"
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al aprobar producto"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando aprobación: {str(e)}"
        )