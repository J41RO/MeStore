from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SQLEnum
# UUID import removed for SQLite compatibility
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from enum import Enum

class TipoIncidente(str, Enum):
    PERDIDO = "PERDIDO"
    DAÑADO = "DAÑADO"

class EstadoIncidente(str, Enum):
    REPORTADO = "REPORTADO"
    EN_INVESTIGACION = "EN_INVESTIGACION"
    RESUELTO = "RESUELTO"
    CERRADO = "CERRADO"

class IncidenteInventario(BaseModel):
    __tablename__ = "incidentes_inventario"
    
    inventory_id = Column(String(36), ForeignKey("inventory.id"), nullable=False)
    tipo_incidente = Column(SQLEnum(TipoIncidente), nullable=False)
    estado = Column(SQLEnum(EstadoIncidente), default=EstadoIncidente.REPORTADO)
    descripcion = Column(Text, nullable=False)
    reportado_por = Column(String, nullable=False)
    fecha_incidente = Column(DateTime, nullable=True)
    
    # Relationship
    inventory = relationship("Inventory", back_populates="incidentes")