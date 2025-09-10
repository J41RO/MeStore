# ~/app/models/discrepancy_report.py
# ---------------------------------------------------------------------------------------------
# MeStore - Modelo de Reportes de Discrepancias
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: discrepancy_report.py
# Ruta: ~/app/models/discrepancy_report.py
# Autor: Jairo
# Fecha de Creación: 2025-09-10
# Última Actualización: 2025-09-10
# Versión: 1.0.0
# Propósito: Modelo DiscrepancyReport para gestión de reportes de discrepancias y ajustes
#            Se integra con el sistema InventoryAudit existente
#
# ---------------------------------------------------------------------------------------------

"""
Modelo DiscrepancyReport para gestión de reportes de discrepancias.

Este módulo contiene:
- Clase DiscrepancyReport: Modelo principal para reportes de discrepancias
- Enum ReportType: Tipos de reportes generables
- Enum ExportFormat: Formatos de exportación disponibles
- Relaciones con InventoryAudit existente
"""

from sqlalchemy import Column, String, Integer, DateTime, Float, Text, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

from app.models.base import Base


class ReportType(str, Enum):
    """
    Enumeración para tipos de reportes de discrepancias.
    
    Tipos de reportes:
        DISCREPANCIES: Reporte general de discrepancias encontradas
        ADJUSTMENTS: Reporte de ajustes realizados post-auditoría
        ACCURACY: Reporte de precisión del inventario
        FINANCIAL_IMPACT: Reporte de impacto financiero de discrepancias
        LOCATION_ANALYSIS: Análisis por ubicación/almacén
        CATEGORY_ANALYSIS: Análisis por categoría de producto
        TREND_ANALYSIS: Análisis de tendencias históricas
        COMPREHENSIVE: Reporte completo con todos los análisis
    """
    DISCREPANCIES = "DISCREPANCIES"
    ADJUSTMENTS = "ADJUSTMENTS"
    ACCURACY = "ACCURACY"
    FINANCIAL_IMPACT = "FINANCIAL_IMPACT"
    LOCATION_ANALYSIS = "LOCATION_ANALYSIS"
    CATEGORY_ANALYSIS = "CATEGORY_ANALYSIS"
    TREND_ANALYSIS = "TREND_ANALYSIS"
    COMPREHENSIVE = "COMPREHENSIVE"


class ExportFormat(str, Enum):
    """
    Enumeración para formatos de exportación de reportes.
    
    Formatos soportados:
        PDF: Documento PDF con gráficos y análisis visual
        EXCEL: Hoja de cálculo Excel con múltiples pestañas
        CSV: Archivo CSV para análisis en hojas de cálculo
        JSON: Datos estructurados para integración API
    """
    PDF = "PDF"
    EXCEL = "EXCEL"
    CSV = "CSV"
    JSON = "JSON"


class ReportStatus(str, Enum):
    """
    Estado del reporte de discrepancias.
    
    Estados posibles:
        GENERATING: Reporte en proceso de generación
        COMPLETED: Reporte generado exitosamente
        FAILED: Error en la generación del reporte
        EXPIRED: Reporte expirado (archivos eliminados)
    """
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class DiscrepancyReport(Base):
    """
    Modelo DiscrepancyReport para gestión de reportes de discrepancias.
    
    Este modelo se integra con el sistema InventoryAudit existente para generar
    reportes detallados de discrepancias, ajustes y análisis de precisión.
    
    Campos principales:
    - audit_id: Referencia a la auditoría de inventario
    - report_type: Tipo de reporte generado
    - generated_by: Usuario que generó el reporte
    - date_range: Rango de fechas analizado
    - metrics: Métricas y estadísticas calculadas
    - file_info: Información del archivo generado
    """
    
    __tablename__ = "discrepancy_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relación con InventoryAudit existente
    audit_id = Column(
        UUID(as_uuid=True),
        ForeignKey('inventory_audits.id'),
        nullable=False,
        index=True,
        comment="ID de la auditoría de inventario asociada"
    )
    
    # Información básica del reporte
    report_type = Column(
        SQLEnum(ReportType),
        nullable=False,
        index=True,
        comment="Tipo de reporte de discrepancias"
    )
    
    report_name = Column(
        String(200),
        nullable=False,
        comment="Nombre descriptivo del reporte"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Descripción detallada del reporte"
    )
    
    # Usuario que generó el reporte
    generated_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False,
        index=True,
        comment="Usuario que generó el reporte"
    )
    
    generated_by_name = Column(
        String(100),
        nullable=False,
        comment="Nombre del usuario (snapshot)"
    )
    
    # Rango de fechas del análisis
    date_range_start = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Fecha de inicio del análisis"
    )
    
    date_range_end = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Fecha de fin del análisis"
    )
    
    # Métricas principales del reporte
    total_discrepancies = Column(
        Integer,
        default=0,
        comment="Total de discrepancias encontradas"
    )
    
    total_adjustments = Column(
        Integer,
        default=0,
        comment="Total de ajustes realizados"
    )
    
    financial_impact = Column(
        Float,
        default=0.0,
        comment="Impacto financiero total de discrepancias"
    )
    
    accuracy_percentage = Column(
        Float,
        default=0.0,
        comment="Porcentaje de precisión del inventario"
    )
    
    items_analyzed = Column(
        Integer,
        default=0,
        comment="Total de items analizados"
    )
    
    # Información del archivo generado
    file_path = Column(
        String(500),
        nullable=True,
        comment="Ruta del archivo generado"
    )
    
    file_format = Column(
        SQLEnum(ExportFormat),
        nullable=False,
        comment="Formato del archivo exportado"
    )
    
    file_size = Column(
        Integer,
        nullable=True,
        comment="Tamaño del archivo en bytes"
    )
    
    # Estado del reporte
    status = Column(
        SQLEnum(ReportStatus),
        default=ReportStatus.GENERATING,
        nullable=False,
        index=True,
        comment="Estado actual del reporte"
    )
    
    # Datos detallados del análisis (JSON)
    analysis_data = Column(
        JSON,
        nullable=True,
        comment="Datos detallados del análisis (JSON)"
    )
    
    # Configuración del reporte
    report_config = Column(
        JSON,
        nullable=True,
        comment="Configuración utilizada para generar el reporte"
    )
    
    # Metadatos adicionales
    generation_time_seconds = Column(
        Float,
        nullable=True,
        comment="Tiempo de generación en segundos"
    )
    
    expiry_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de expiración del reporte"
    )
    
    download_count = Column(
        Integer,
        default=0,
        comment="Número de descargas del reporte"
    )
    
    notes = Column(
        Text,
        nullable=True,
        comment="Notas adicionales del reporte"
    )
    
    # Campos de auditoría
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Fecha de creación"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
        comment="Fecha de última actualización"
    )
    
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de completado"
    )
    
    # Relationships
    audit = relationship("InventoryAudit", back_populates="discrepancy_reports")
    generated_by = relationship("User", backref="generated_discrepancy_reports")
    
    def __init__(self, **kwargs):
        """Inicializar reporte con defaults automáticos"""
        # Asegurar timestamps si no se proporcionan
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.utcnow()
        
        # Auto-generar nombre si no se proporciona
        if 'report_name' not in kwargs and 'report_type' in kwargs:
            report_type_name = kwargs['report_type'].value if hasattr(kwargs['report_type'], 'value') else str(kwargs['report_type'])
            kwargs['report_name'] = f"Reporte {report_type_name} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        
        super().__init__(**kwargs)
    
    @property
    def is_completed(self) -> bool:
        """Verificar si el reporte está completado"""
        return self.status == ReportStatus.COMPLETED
    
    @property
    def is_expired(self) -> bool:
        """Verificar si el reporte ha expirado"""
        if self.expiry_date is None:
            return False
        return datetime.utcnow() > self.expiry_date
    
    @property
    def file_exists(self) -> bool:
        """Verificar si el archivo del reporte existe"""
        if not self.file_path:
            return False
        import os
        return os.path.exists(self.file_path)
    
    @property
    def days_since_generation(self) -> int:
        """Calcular días desde la generación"""
        if not self.created_at:
            return 0
        delta = datetime.utcnow() - self.created_at
        return delta.days
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Obtener resumen del análisis realizado"""
        if not self.analysis_data:
            return {}
        
        return {
            "total_discrepancies": self.total_discrepancies,
            "total_adjustments": self.total_adjustments,
            "financial_impact": self.financial_impact,
            "accuracy_percentage": self.accuracy_percentage,
            "items_analyzed": self.items_analyzed,
            "analysis_period": {
                "start": self.date_range_start.isoformat() if self.date_range_start else None,
                "end": self.date_range_end.isoformat() if self.date_range_end else None
            },
            "generation_info": {
                "generated_by": self.generated_by_name,
                "generation_time": self.generation_time_seconds,
                "file_format": self.file_format.value if self.file_format else None,
                "download_count": self.download_count
            }
        }
    
    def mark_as_completed(self, file_path: str, file_size: int, generation_time: float):
        """Marcar reporte como completado"""
        self.status = ReportStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.file_path = file_path
        self.file_size = file_size
        self.generation_time_seconds = generation_time
        
        # Establecer fecha de expiración (30 días por defecto)
        from datetime import timedelta
        self.expiry_date = datetime.utcnow() + timedelta(days=30)
    
    def mark_as_failed(self, error_message: str):
        """Marcar reporte como fallido"""
        self.status = ReportStatus.FAILED
        self.notes = f"Error: {error_message}"
        self.completed_at = datetime.utcnow()
    
    def increment_download_count(self):
        """Incrementar contador de descargas"""
        self.download_count = (self.download_count or 0) + 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializar reporte a diccionario."""
        return {
            "id": str(self.id),
            "audit_id": str(self.audit_id),
            "report_type": self.report_type.value if self.report_type else None,
            "report_name": self.report_name,
            "description": self.description,
            "generated_by_id": str(self.generated_by_id),
            "generated_by_name": self.generated_by_name,
            "date_range_start": self.date_range_start.isoformat() if self.date_range_start else None,
            "date_range_end": self.date_range_end.isoformat() if self.date_range_end else None,
            "total_discrepancies": self.total_discrepancies,
            "total_adjustments": self.total_adjustments,
            "financial_impact": self.financial_impact,
            "accuracy_percentage": self.accuracy_percentage,
            "items_analyzed": self.items_analyzed,
            "file_path": self.file_path,
            "file_format": self.file_format.value if self.file_format else None,
            "file_size": self.file_size,
            "status": self.status.value if self.status else None,
            "analysis_data": self.analysis_data,
            "report_config": self.report_config,
            "generation_time_seconds": self.generation_time_seconds,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "download_count": self.download_count,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_completed": self.is_completed,
            "is_expired": self.is_expired,
            "file_exists": self.file_exists,
            "days_since_generation": self.days_since_generation,
            "analysis_summary": self.get_analysis_summary()
        }
    
    def __repr__(self) -> str:
        """Representación string del objeto DiscrepancyReport."""
        return f"<DiscrepancyReport {self.report_type.value}: {self.report_name} ({self.status.value})>"