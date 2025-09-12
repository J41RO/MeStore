from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List
from datetime import datetime, timedelta
import logging

from app.database import get_db as get_sync_db
from app.api.v1.endpoints.admin import get_current_admin_user
from app.schemas.leads import (
    LeadCreateSchema, 
    LeadResponseSchema, 
    LeadStatsSchema,
    LeadUpdateSchema,
    LeadBulkActionSchema
)
from app.models.user import User
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)
router = APIRouter()

# Simulación de modelo Lead - En producción debería estar en app/models/
class Lead:
    """Modelo simulado para leads. En producción usar SQLAlchemy."""
    
    _leads_storage = []
    _next_id = 1
    
    @classmethod
    def create(cls, lead_data: dict):
        lead = {
            'id': cls._next_id,
            'created_at': datetime.utcnow(),
            'status': 'active',
            **lead_data
        }
        cls._leads_storage.append(lead)
        cls._next_id += 1
        return lead
    
    @classmethod
    def get_by_email(cls, email: str):
        for lead in cls._leads_storage:
            if lead['email'].lower() == email.lower():
                return lead
        return None
    
    @classmethod
    def get_all(cls):
        return cls._leads_storage.copy()
    
    @classmethod
    def get_stats(cls):
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        total = len(cls._leads_storage)
        today_count = len([l for l in cls._leads_storage if l['created_at'] >= today])
        week_count = len([l for l in cls._leads_storage if l['created_at'] >= week_ago])
        month_count = len([l for l in cls._leads_storage if l['created_at'] >= month_ago])
        
        # Agrupar por tipo de negocio
        business_types = {}
        sources = {}
        for lead in cls._leads_storage:
            tipo = lead.get('tipo_negocio', 'unknown')
            source = lead.get('source', 'unknown')
            business_types[tipo] = business_types.get(tipo, 0) + 1
            sources[source] = sources.get(source, 0) + 1
        
        return {
            'total_leads': total,
            'leads_today': today_count,
            'leads_this_week': week_count,
            'leads_this_month': month_count,
            'conversion_rate': 0.0,  # Placeholder
            'top_sources': [{'source': k, 'count': v} for k, v in sources.items()],
            'business_type_breakdown': business_types
        }

def send_welcome_email_task(email: str, nombre: str, tipo_negocio: str):
    """Tarea en background para enviar email de bienvenida."""
    try:
        email_service = EmailService()
        success = email_service.send_lead_welcome_email(
            email=email,
            nombre=nombre,
            tipo_negocio=tipo_negocio
        )
        if success:
            logger.info(f"Email de bienvenida enviado exitosamente a {email}")
        else:
            logger.error(f"Error enviando email de bienvenida a {email}")
    except Exception as e:
        logger.error(f"Excepción enviando email de bienvenida: {str(e)}")

@router.post("/", response_model=dict)
async def create_lead(
    lead_data: LeadCreateSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_sync_db)
):
    """
    Crear nuevo lead desde formulario de landing page.
    
    Este endpoint:
    - Valida los datos del formulario
    - Previene duplicados por email
    - Almacena el lead
    - Envía email de bienvenida automáticamente
    """
    try:
        # Verificar si el email ya existe
        existing_lead = Lead.get_by_email(lead_data.email)
        if existing_lead:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este email ya está registrado en nuestra lista de espera"
            )
        
        # Crear nuevo lead
        lead_dict = lead_data.model_dump()
        new_lead = Lead.create(lead_dict)
        
        # Programar envío de email de bienvenida
        background_tasks.add_task(
            send_welcome_email_task,
            email=lead_data.email,
            nombre=lead_data.nombre,
            tipo_negocio=lead_data.tipo_negocio
        )
        
        logger.info(f"Nuevo lead creado: {lead_data.email} - {lead_data.tipo_negocio}")
        
        return {
            "message": "¡Registro exitoso! Te contactaremos pronto con acceso prioritario.",
            "lead_id": new_lead['id'],
            "email_sent": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando lead: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor. Inténtalo de nuevo."
        )

@router.get("/", response_model=List[dict])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Obtener lista de leads (solo admins).
    """
    leads = Lead.get_all()
    
    # Aplicar paginación
    paginated_leads = leads[skip:skip + limit]
    
    return paginated_leads

@router.get("/stats", response_model=LeadStatsSchema)
async def get_lead_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Obtener estadísticas de leads (solo admins).
    """
    stats = Lead.get_stats()
    return stats

@router.put("/{lead_id}", response_model=dict)
async def update_lead(
    lead_id: int,
    update_data: LeadUpdateSchema,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Actualizar información de un lead (solo admins).
    """
    # En una implementación real, buscarías y actualizarías el lead en la BD
    return {
        "message": f"Lead {lead_id} actualizado exitosamente",
        "updated_fields": update_data.model_dump(exclude_unset=True)
    }

@router.post("/bulk-action", response_model=dict)
async def bulk_action_leads(
    action_data: LeadBulkActionSchema,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Ejecutar acciones masivas en leads (solo admins).
    """
    action_results = {
        'processed': len(action_data.lead_ids),
        'successful': len(action_data.lead_ids),
        'failed': 0,
        'action': action_data.action
    }
    
    if action_data.action == 'send_email':
        # Programar envío masivo de emails
        for lead_id in action_data.lead_ids:
            # En implementación real, obtener datos del lead por ID
            background_tasks.add_task(
                send_welcome_email_task,
                email=f"lead{lead_id}@example.com",
                nombre=f"Lead {lead_id}",
                tipo_negocio="vendedor"
            )
    
    logger.info(f"Acción masiva ejecutada: {action_data.action} en {len(action_data.lead_ids)} leads")
    
    return action_results

@router.delete("/{lead_id}", response_model=dict)
async def delete_lead(
    lead_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Eliminar un lead (solo admins).
    """
    # En implementación real, eliminar de la base de datos
    logger.info(f"Lead {lead_id} eliminado por admin {current_user.email}")
    
    return {"message": f"Lead {lead_id} eliminado exitosamente"}

@router.post("/test-email", response_model=dict)
async def test_welcome_email(
    email: str,
    nombre: str = "Usuario Test",
    tipo_negocio: str = "vendedor",
    current_user: User = Depends(get_current_admin_user)
):
    """
    Endpoint de prueba para enviar email de bienvenida (solo admins).
    """
    try:
        email_service = EmailService()
        success = email_service.send_lead_welcome_email(
            email=email,
            nombre=nombre,
            tipo_negocio=tipo_negocio
        )
        
        return {
            "message": "Email de prueba enviado",
            "success": success,
            "email": email,
            "simulation_mode": email_service.simulation_mode
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando email de prueba: {str(e)}"
        )