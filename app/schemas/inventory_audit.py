from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class AuditStatusEnum(str, Enum):
    INICIADA = "INICIADA"
    EN_PROCESO = "EN_PROCESO"
    COMPLETADA = "COMPLETADA"
    RECONCILIADA = "RECONCILIADA"

class DiscrepancyTypeEnum(str, Enum):
    FALTANTE = "FALTANTE"
    SOBRANTE = "SOBRANTE"
    UBICACION_INCORRECTA = "UBICACION_INCORRECTA"
    CONDICION_DIFERENTE = "CONDICION_DIFERENTE"

# Schemas para crear auditoría
class InventoryAuditCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    inventarios_ids: List[UUID] = Field(..., min_items=1)

class AuditItemCreate(BaseModel):
    inventory_id: UUID
    incluir_en_audit: bool = True

# Schemas para conteo físico
class ConteoFisicoData(BaseModel):
    cantidad_fisica: int = Field(..., ge=0)
    ubicacion_fisica: Optional[str] = None
    condicion_fisica: Optional[str] = None
    notas_conteo: Optional[str] = None

class ProcesarConteo(BaseModel):
    audit_item_id: UUID
    conteo_data: ConteoFisicoData



# Schemas de respuesta
class InventoryAuditItemResponse(BaseModel):
    id: UUID
    inventory_id: UUID
    product_name: str
    sku: str
    cantidad_sistema: int
    cantidad_fisica: Optional[int] = None
    ubicacion_sistema: Optional[str] = None
    ubicacion_fisica: Optional[str] = None
    tiene_discrepancia: bool
    tipo_discrepancia: Optional[DiscrepancyTypeEnum] = None
    diferencia_cantidad: int
    valor_discrepancia: Optional[float] = None
    conteo_completado: bool
    fecha_conteo: Optional[datetime] = None
    notas_conteo: Optional[str] = None
    
    class Config:
        from_attributes = True

class InventoryAuditResponse(BaseModel):
    id: UUID
    nombre: str
    descripcion: Optional[str] = None
    status: AuditStatusEnum
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    total_items_auditados: int
    discrepancias_encontradas: int
    valor_discrepancias: float
    auditor_nombre: str
    
    class Config:
        from_attributes = True

class InventoryAuditDetailResponse(InventoryAuditResponse):
    audit_items: List[InventoryAuditItemResponse]
    notas: Optional[str] = None

class AuditStatsResponse(BaseModel):
    total_auditorias: int
    auditorias_pendientes: int
    discrepancias_sin_reconciliar: int
    valor_total_discrepancias: float
    ultima_auditoria: Optional[datetime] = None

# Schema para reconciliación
class ReconciliarDiscrepancia(BaseModel):
    audit_item_id: UUID
    accion: str = Field(..., pattern="^(ajustar_sistema|mantener_fisico|investigar)$")
    notas_reconciliacion: Optional[str] = None