from sqlalchemy import Column, String, Integer, DateTime, Float, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid
from app.models.base import Base

class AuditStatus(str, Enum):
    INICIADA = "INICIADA"
    EN_PROCESO = "EN_PROCESO"
    COMPLETADA = "COMPLETADA"
    RECONCILIADA = "RECONCILIADA"

class DiscrepancyType(str, Enum):
    FALTANTE = "FALTANTE"  # Menos físico que digital
    SOBRANTE = "SOBRANTE"  # Más físico que digital
    UBICACION_INCORRECTA = "UBICACION_INCORRECTA"
    CONDICION_DIFERENTE = "CONDICION_DIFERENTE"

class InventoryAudit(Base):
    __tablename__ = "inventory_audits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    status = Column(SQLEnum(AuditStatus), default=AuditStatus.INICIADA)
    
    # Fechas de auditoría
    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now())
    fecha_fin = Column(DateTime(timezone=True), nullable=True)
    
    # Usuario que realiza la auditoría
    auditor_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    auditor = relationship("User", back_populates="auditorias_realizadas")
    # Tipo de auditoría y métricas
    audit_type = Column(String(50), default="physical")  # physical, system, cycle_count
    discrepancies_found = Column(Integer, default=0)  # Contador de discrepancias
    
    # Estadísticas de la auditoría
    total_items_auditados = Column(Integer, default=0)
    discrepancias_encontradas = Column(Integer, default=0)
    valor_discrepancias = Column(Float, default=0.0)
    
    # Metadatos
    notas = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    audit_items = relationship("InventoryAuditItem", back_populates="audit", cascade="all, delete-orphan")
    discrepancy_reports = relationship("DiscrepancyReport", back_populates="audit", cascade="all, delete-orphan")
    
    def calcular_estadisticas(self):
        """Calcular estadísticas de la auditoría"""
        if not self.audit_items:
            return
            
        self.total_items_auditados = len(self.audit_items)
        self.discrepancias_encontradas = sum(1 for item in self.audit_items if item.tiene_discrepancia)
        self.valor_discrepancias = sum(item.valor_discrepancia or 0 for item in self.audit_items)
    
    def puede_finalizar(self) -> bool:
        """Verificar si la auditoría puede finalizarse"""
        return self.status == AuditStatus.EN_PROCESO and all(
            item.conteo_completado for item in self.audit_items
        )



class InventoryAuditItem(Base):
    __tablename__ = "inventory_audit_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id = Column(UUID(as_uuid=True), ForeignKey('inventory_audits.id'), nullable=False)
    inventory_id = Column(UUID(as_uuid=True), ForeignKey('inventory.id'), nullable=False)
    
    # Datos del sistema (antes del conteo)
    cantidad_sistema = Column(Integer, nullable=False)
    ubicacion_sistema = Column(String(100))
    condicion_sistema = Column(String(50))
    
    # Datos del conteo físico
    cantidad_fisica = Column(Integer, nullable=True)
    ubicacion_fisica = Column(String(100), nullable=True)
    condicion_fisica = Column(String(50), nullable=True)
    conteo_completado = Column(Boolean, default=False)
    
    # Análisis de discrepancia
    tiene_discrepancia = Column(Boolean, default=False)
    tipo_discrepancia = Column(SQLEnum(DiscrepancyType), nullable=True)
    diferencia_cantidad = Column(Integer, default=0)
    valor_discrepancia = Column(Float, nullable=True)
    
    # Metadatos del conteo
    fecha_conteo = Column(DateTime(timezone=True), nullable=True)
    notas_conteo = Column(Text)
    reconciliado = Column(Boolean, default=False)
    
    # Relaciones
    audit = relationship("InventoryAudit", back_populates="audit_items")
    inventory = relationship("Inventory")
    
    def procesar_conteo(self, cantidad_fisica: int, ubicacion_fisica: str = None, 
                       condicion_fisica: str = None, notas: str = None):
        """Procesar el conteo físico y detectar discrepancias"""
        self.cantidad_fisica = cantidad_fisica
        self.ubicacion_fisica = ubicacion_fisica or self.ubicacion_sistema
        self.condicion_fisica = condicion_fisica or self.condicion_sistema
        self.notas_conteo = notas
        self.fecha_conteo = func.now()
        self.conteo_completado = True
        
        # Detectar discrepancias
        self._detectar_discrepancias()
    
    def _detectar_discrepancias(self):
        """Detectar y clasificar discrepancias"""
        self.diferencia_cantidad = self.cantidad_fisica - self.cantidad_sistema
        
        if self.diferencia_cantidad != 0:
            self.tiene_discrepancia = True
            self.tipo_discrepancia = (
                DiscrepancyType.SOBRANTE if self.diferencia_cantidad > 0 
                else DiscrepancyType.FALTANTE
            )
        elif self.ubicacion_fisica != self.ubicacion_sistema:
            self.tiene_discrepancia = True
            self.tipo_discrepancia = DiscrepancyType.UBICACION_INCORRECTA
        elif self.condicion_fisica != self.condicion_sistema:
            self.tiene_discrepancia = True
            self.tipo_discrepancia = DiscrepancyType.CONDICION_DIFERENTE
        else:
            self.tiene_discrepancia = False
            self.tipo_discrepancia = None