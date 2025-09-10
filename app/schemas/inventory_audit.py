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


# ============================================================================
# SCHEMAS PARA REPORTES DE DISCREPANCIAS
# ============================================================================

from typing import Dict, Any

class ReportTypeEnum(str, Enum):
    DISCREPANCIES = "DISCREPANCIES"
    ADJUSTMENTS = "ADJUSTMENTS"
    ACCURACY = "ACCURACY"
    FINANCIAL_IMPACT = "FINANCIAL_IMPACT"
    LOCATION_ANALYSIS = "LOCATION_ANALYSIS"
    CATEGORY_ANALYSIS = "CATEGORY_ANALYSIS"
    TREND_ANALYSIS = "TREND_ANALYSIS"
    COMPREHENSIVE = "COMPREHENSIVE"

class ExportFormatEnum(str, Enum):
    PDF = "PDF"
    EXCEL = "EXCEL"
    CSV = "CSV"
    JSON = "JSON"

class ReportStatusEnum(str, Enum):
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"

# Schema para crear reporte de discrepancias
class DiscrepancyReportCreate(BaseModel):
    audit_id: UUID
    report_type: ReportTypeEnum
    report_name: Optional[str] = None
    description: Optional[str] = None
    file_format: ExportFormatEnum = ExportFormatEnum.PDF
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    include_charts: bool = True
    include_recommendations: bool = True
    group_by_location: bool = False
    group_by_category: bool = False
    
    class Config:
        from_attributes = True

# Schema para configuración de reporte
class ReportConfig(BaseModel):
    include_charts: bool = True
    include_recommendations: bool = True
    group_by_location: bool = False
    group_by_category: bool = False
    chart_types: List[str] = Field(default=["bar", "pie", "trend"])
    export_options: Dict[str, Any] = Field(default_factory=dict)

# Schema de respuesta para reporte de discrepancias
class DiscrepancyReportResponse(BaseModel):
    id: UUID
    audit_id: UUID
    report_type: ReportTypeEnum
    report_name: str
    description: Optional[str] = None
    generated_by_id: UUID
    generated_by_name: str
    date_range_start: datetime
    date_range_end: datetime
    total_discrepancies: int
    total_adjustments: int
    financial_impact: float
    accuracy_percentage: float
    items_analyzed: int
    file_path: Optional[str] = None
    file_format: ExportFormatEnum
    file_size: Optional[int] = None
    status: ReportStatusEnum
    generation_time_seconds: Optional[float] = None
    expiry_date: Optional[datetime] = None
    download_count: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_completed: bool
    is_expired: bool
    file_exists: bool
    days_since_generation: int
    
    class Config:
        from_attributes = True

# Schema para análisis detallado
class DiscrepancyAnalysis(BaseModel):
    total_discrepancies: int
    discrepancies_by_type: Dict[str, int]
    discrepancies_by_location: Dict[str, int] 
    discrepancies_by_category: Dict[str, int]
    financial_impact_by_type: Dict[str, float]
    accuracy_metrics: Dict[str, float]
    trend_analysis: Optional[Dict[str, Any]] = None
    recommendations: List[str] = Field(default_factory=list)

# Schema para respuesta con análisis completo
class DiscrepancyReportWithAnalysis(DiscrepancyReportResponse):
    analysis_data: Optional[DiscrepancyAnalysis] = None
    report_config: Optional[Dict[str, Any]] = None
    
# Schema para listado de reportes
class DiscrepancyReportListResponse(BaseModel):
    reports: List[DiscrepancyReportResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool

# Schema para estadísticas de reportes
class ReportStatsResponse(BaseModel):
    total_reports: int
    reports_by_type: Dict[str, int]
    reports_by_status: Dict[str, int]
    avg_generation_time: float
    total_downloads: int
    disk_space_used: int  # en bytes
    reports_this_month: int