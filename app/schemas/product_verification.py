from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from app.services.product_verification_workflow import VerificationStep, StepResult

class StepExecutionRequest(BaseModel):
    """Request para ejecutar un paso del workflow de verificación"""
    step: VerificationStep
    passed: bool
    notes: str = Field(..., min_length=1, max_length=1000, description="Notas del paso de verificación")
    issues: List[str] = Field(default_factory=list, description="Lista de problemas encontrados")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Datos adicionales específicos del paso")
    
    class Config:
        schema_extra = {
            "example": {
                "step": "initial_inspection",
                "passed": True,
                "notes": "Producto en buenas condiciones, documentación completa",
                "issues": [],
                "metadata": {
                    "inspector_id": "admin-001",
                    "inspection_duration_minutes": 15
                }
            }
        }

class VerificationStepResponse(BaseModel):
    """Response detallada de un paso del workflow"""
    step: VerificationStep
    title: str = Field(..., description="Título legible del paso")
    description: str = Field(..., description="Descripción detallada del paso")
    is_current: bool = Field(..., description="Si es el paso actual")
    is_completed: bool = Field(..., description="Si el paso ya fue completado")
    order: int = Field(..., description="Orden del paso en el workflow")
    result: Optional[StepResult] = Field(None, description="Resultado del paso si ya fue ejecutado")
    
    class Config:
        schema_extra = {
            "example": {
                "step": "initial_inspection",
                "title": "Inspección Inicial",
                "description": "Revisar condición física y documentación básica del producto",
                "is_current": True,
                "is_completed": False,
                "order": 1,
                "result": None
            }
        }

class WorkflowStatusResponse(BaseModel):
    """Response completa del estado del workflow de verificación"""
    queue_id: int = Field(..., description="ID del item en la cola")
    current_step: VerificationStep = Field(..., description="Paso actual del workflow")
    progress_percentage: float = Field(..., ge=0, le=100, description="Porcentaje de progreso")
    steps: List[VerificationStepResponse] = Field(..., description="Lista de todos los pasos del workflow")
    can_proceed: bool = Field(..., description="Si puede proceder al siguiente paso")
    verification_attempts: int = Field(default=0, description="Número de intentos de verificación")
    estimated_completion: Optional[datetime] = Field(None, description="Tiempo estimado de finalización")
    
    class Config:
        schema_extra = {
            "example": {
                "queue_id": 123,
                "current_step": "quality_assessment",
                "progress_percentage": 60.0,
                "steps": [
                    {
                        "step": "initial_inspection",
                        "title": "Inspección Inicial",
                        "description": "Revisar condición física y documentación básica",
                        "is_current": False,
                        "is_completed": True,
                        "order": 1
                    }
                ],
                "can_proceed": True,
                "verification_attempts": 2,
                "estimated_completion": None
            }
        }

class VerificationHistoryResponse(BaseModel):
    """Response del historial completo de verificación"""
    queue_id: int = Field(..., description="ID del item en la cola")
    product_id: Optional[str] = Field(None, description="ID del producto")
    verification_status: str = Field(..., description="Estado actual de verificación")
    verification_attempts: int = Field(default=0, description="Intentos de verificación")
    verification_notes: Optional[str] = Field(None, description="Notas de verificación acumuladas")
    quality_score: Optional[float] = Field(None, ge=0, le=10, description="Puntuación de calidad")
    quality_issues: Optional[str] = Field(None, description="Problemas de calidad encontrados")
    assigned_to: Optional[str] = Field(None, description="Usuario asignado")
    assigned_at: Optional[datetime] = Field(None, description="Fecha de asignación")
    processing_started_at: Optional[datetime] = Field(None, description="Inicio del procesamiento")
    processing_completed_at: Optional[datetime] = Field(None, description="Finalización del procesamiento")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Última actualización")
    current_workflow: WorkflowStatusResponse = Field(..., description="Estado actual del workflow")
    
    class Config:
        schema_extra = {
            "example": {
                "queue_id": 123,
                "product_id": "PROD-001",
                "verification_status": "QUALITY_CHECK",
                "verification_attempts": 3,
                "verification_notes": "[INITIAL_INSPECTION] Producto recibido en buenas condiciones...",
                "quality_score": 8.5,
                "quality_issues": None,
                "assigned_to": "admin-001",
                "assigned_at": "2024-09-10T10:00:00Z",
                "processing_started_at": "2024-09-10T10:15:00Z",
                "processing_completed_at": None,
                "created_at": "2024-09-10T09:30:00Z",
                "updated_at": "2024-09-10T11:45:00Z"
            }
        }

# Schemas adicionales para operaciones específicas
class BulkStepExecutionRequest(BaseModel):
    """Request para ejecutar pasos en múltiples productos"""
    queue_ids: List[int] = Field(..., min_items=1, max_items=50, description="Lista de IDs de productos")
    step_data: StepExecutionRequest = Field(..., description="Datos del paso a ejecutar")
    
    class Config:
        schema_extra = {
            "example": {
                "queue_ids": [123, 124, 125],
                "step_data": {
                    "step": "initial_inspection",
                    "passed": True,
                    "notes": "Inspección masiva - productos en condiciones aceptables",
                    "issues": [],
                    "metadata": {
                        "bulk_operation": True,
                        "inspector_id": "admin-001"
                    }
                }
            }
        }

class WorkflowSummaryResponse(BaseModel):
    """Response resumido para dashboards y listados"""
    queue_id: int
    product_id: Optional[str]
    current_step: VerificationStep
    progress_percentage: float
    verification_status: str
    can_proceed: bool
    priority: Optional[str] = None
    days_in_queue: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "queue_id": 123,
                "product_id": "PROD-001",
                "current_step": "quality_assessment",
                "progress_percentage": 60.0,
                "verification_status": "IN_PROGRESS",
                "can_proceed": True,
                "priority": "HIGH",
                "days_in_queue": 3
            }
        }


# =============================================================================
# SCHEMAS PARA CHECKLIST DE CALIDAD CON FOTOS Y DIMENSIONES
# =============================================================================

class ProductCondition(str, Enum):
    """Enumeración para condiciones del producto"""
    NEW = "new"
    LIKE_NEW = "like_new" 
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    DAMAGED = "damaged"

class QualityPhoto(BaseModel):
    """Schema para fotos de verificación de calidad"""
    photo_type: str = Field(..., description="Tipo de foto: general, damage, label, packaging, etc.")
    filename: str = Field(..., description="Nombre del archivo")
    url: str = Field(..., description="URL de acceso a la foto")
    description: Optional[str] = Field(None, description="Descripción opcional de la foto")
    is_required: bool = Field(True, description="Si la foto es obligatoria")
    uploaded_at: Optional[datetime] = Field(None, description="Fecha de subida")
    
    class Config:
        schema_extra = {
            "example": {
                "photo_type": "general",
                "filename": "verification_123_abc123.jpg",
                "url": "/uploads/verification_photos/verification_123_abc123.jpg",
                "description": "Vista general del producto",
                "is_required": True,
                "uploaded_at": "2024-09-10T14:30:00Z"
            }
        }

class DimensionCheck(BaseModel):
    """Schema para verificación de dimensiones físicas"""
    length_cm: float = Field(..., gt=0, description="Largo en centímetros")
    width_cm: float = Field(..., gt=0, description="Ancho en centímetros") 
    height_cm: float = Field(..., gt=0, description="Alto en centímetros")
    weight_kg: float = Field(..., gt=0, description="Peso en kilogramos")
    matches_declared: bool = Field(..., description="Si las dimensiones coinciden con las declaradas")
    variance_percentage: Optional[float] = Field(None, ge=0, le=100, description="Porcentaje de variación respecto a lo declarado")
    measurement_notes: Optional[str] = Field(None, description="Notas sobre las mediciones")
    
    class Config:
        schema_extra = {
            "example": {
                "length_cm": 25.5,
                "width_cm": 15.2,
                "height_cm": 8.0,
                "weight_kg": 1.25,
                "matches_declared": True,
                "variance_percentage": 2.5,
                "measurement_notes": "Medición realizada con empaque incluido"
            }
        }

class QualityChecklist(BaseModel):
    """Schema completo para checklist de calidad"""
    
    # Inspección visual general
    overall_condition: ProductCondition = Field(..., description="Condición general del producto")
    has_original_packaging: bool = Field(..., description="Tiene empaque original")
    packaging_condition: Optional[ProductCondition] = Field(None, description="Condición del empaque")
    
    # Fotos de verificación
    photos: List[QualityPhoto] = Field(default_factory=list, description="Lista de fotos de verificación")
    
    # Verificación de dimensiones físicas
    dimensions: DimensionCheck = Field(..., description="Verificación de dimensiones y peso")
    
    # Checklist de problemas específicos
    has_damage: bool = Field(..., description="Producto tiene daños visibles")
    damage_description: Optional[str] = Field(None, description="Descripción detallada de daños")
    has_missing_parts: bool = Field(..., description="Faltan partes o accesorios")
    missing_parts_description: Optional[str] = Field(None, description="Descripción de partes faltantes")
    has_defects: bool = Field(default=False, description="Producto tiene defectos de fabricación")
    defects_description: Optional[str] = Field(None, description="Descripción de defectos")
    
    # Verificación funcional
    is_functional: bool = Field(..., description="Producto funciona correctamente")
    functionality_notes: Optional[str] = Field(None, description="Notas sobre funcionalidad")
    
    # Documentación y etiquetado
    has_required_labels: bool = Field(..., description="Tiene etiquetas requeridas")
    labels_condition: Optional[ProductCondition] = Field(None, description="Condición de etiquetas")
    has_documentation: bool = Field(..., description="Tiene documentación/manual")
    documentation_condition: Optional[ProductCondition] = Field(None, description="Condición de documentación")
    
    # Calificación final
    quality_score: int = Field(..., ge=1, le=10, description="Puntuación de calidad (1-10)")
    inspector_notes: str = Field(..., min_length=1, max_length=2000, description="Notas detalladas del inspector")
    approved: bool = Field(..., description="Producto aprobado para inventario")
    requires_additional_review: bool = Field(default=False, description="Requiere revisión adicional")
    
    # Metadatos
    inspector_id: Optional[str] = Field(None, description="ID del inspector")
    inspection_duration_minutes: Optional[int] = Field(None, gt=0, description="Duración de la inspección en minutos")
    inspection_completed_at: Optional[datetime] = Field(None, description="Fecha de finalización de inspección")
    
    class Config:
        schema_extra = {
            "example": {
                "overall_condition": "like_new",
                "has_original_packaging": True,
                "packaging_condition": "good",
                "photos": [
                    {
                        "photo_type": "general",
                        "filename": "verification_123_general.jpg",
                        "url": "/uploads/verification_photos/verification_123_general.jpg",
                        "description": "Vista general del producto",
                        "is_required": True
                    }
                ],
                "dimensions": {
                    "length_cm": 25.5,
                    "width_cm": 15.2,
                    "height_cm": 8.0,
                    "weight_kg": 1.25,
                    "matches_declared": True,
                    "variance_percentage": 2.5
                },
                "has_damage": False,
                "damage_description": None,
                "has_missing_parts": False,
                "missing_parts_description": None,
                "has_defects": False,
                "defects_description": None,
                "is_functional": True,
                "functionality_notes": "Todas las funciones operan correctamente",
                "has_required_labels": True,
                "labels_condition": "good",
                "has_documentation": True,
                "documentation_condition": "new",
                "quality_score": 8,
                "inspector_notes": "Producto en excelentes condiciones, listo para inventario",
                "approved": True,
                "requires_additional_review": False,
                "inspector_id": "admin-001",
                "inspection_duration_minutes": 25,
                "inspection_completed_at": "2024-09-10T15:30:00Z"
            }
        }

class QualityChecklistRequest(BaseModel):
    """Request para enviar checklist de calidad completado"""
    queue_id: int = Field(..., description="ID del item en cola")
    checklist: QualityChecklist = Field(..., description="Datos completos del checklist")
    
    class Config:
        schema_extra = {
            "example": {
                "queue_id": 123,
                "checklist": {
                    "overall_condition": "like_new",
                    "has_original_packaging": True,
                    "quality_score": 8,
                    "inspector_notes": "Producto verificado exitosamente",
                    "approved": True
                }
            }
        }

class PhotoUploadResponse(BaseModel):
    """Response para upload de fotos"""
    uploaded_photos: List[QualityPhoto] = Field(..., description="Lista de fotos subidas exitosamente")
    total_uploaded: int = Field(..., description="Total de fotos subidas")
    failed_uploads: List[str] = Field(default_factory=list, description="Lista de archivos que fallaron")
    
    class Config:
        schema_extra = {
            "example": {
                "uploaded_photos": [
                    {
                        "photo_type": "general",
                        "filename": "verification_123_general.jpg",
                        "url": "/uploads/verification_photos/verification_123_general.jpg",
                        "description": "Vista general",
                        "is_required": True
                    }
                ],
                "total_uploaded": 1,
                "failed_uploads": []
            }
        }