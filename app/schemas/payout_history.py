from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PayoutHistoryBase(BaseModel):
    """Schema base para PayoutHistory"""
    payout_request_id: int = Field(..., description="ID del PayoutRequest asociado")
    estado_anterior: Optional[str] = Field(None, description="Estado previo (None para primer registro)")
    estado_nuevo: str = Field(..., description="Nuevo estado del payout")
    observaciones: Optional[str] = Field(None, description="Notas adicionales del cambio")
    usuario_responsable: Optional[int] = Field(None, description="ID del usuario responsable")


class PayoutHistoryCreate(PayoutHistoryBase):
    """Schema para crear registros de historial (uso interno)"""
    pass


class PayoutHistoryRead(PayoutHistoryBase):
    """Schema para lectura de registros de historial"""
    id: int
    fecha_cambio: datetime
    
    class Config:
        from_attributes = True


class PayoutHistoryListResponse(BaseModel):
    """Schema de respuesta para lista de historial por payout"""
    payout_request_id: int
    total_cambios: int
    historial: List[PayoutHistoryRead]
    
    class Config:
        from_attributes = True


class PayoutHistoryByDateRange(BaseModel):
    """Schema para filtrar historial por rango de fechas"""
    fecha_inicio: Optional[datetime] = Field(None, description="Fecha de inicio del filtro")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha fin del filtro")
    estado_filtro: Optional[str] = Field(None, description="Filtrar por estado específico")
    limit: int = Field(50, description="Límite de resultados por página")
    offset: int = Field(0, description="Offset para paginación")
