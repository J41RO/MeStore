# ~/app/schemas/commission_dispute.py
"""
Schemas Pydantic para disputas de comisiones.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.commission_dispute import EstadoDispute


class DisputeCreate(BaseModel):
    """Schema para crear una nueva disputa de comisión"""

    transaction_id: UUID = Field(..., description="ID de la transacción a disputar")
    motivo: str = Field(..., max_length=100, description="Motivo de la disputa")
    descripcion: str = Field(..., min_length=10, description="Descripción detallada de la discrepancia")


class DisputeRead(BaseModel):
    """Schema para leer datos de una disputa"""

    id: UUID = Field(..., description="ID único de la disputa")
    transaction_id: UUID = Field(..., description="ID de la transacción disputada")
    usuario_id: UUID = Field(..., description="ID del usuario que reporta")
    motivo: str = Field(..., description="Motivo de la disputa")
    descripcion: str = Field(..., description="Descripción de la discrepancia")
    estado: EstadoDispute = Field(..., description="Estado actual de la disputa")
    respuesta_admin: Optional[str] = Field(None, description="Respuesta del administrador")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")


class DisputeUpdate(BaseModel):
    """Schema para actualizar una disputa (uso administrativo)"""

    estado: Optional[EstadoDispute] = Field(None, description="Nuevo estado de la disputa")
    respuesta_admin: Optional[str] = Field(None, description="Respuesta del administrador")


class DisputeResponse(BaseModel):
    """Schema de respuesta exitosa al crear disputa"""

    success: bool = Field(True, description="Indicador de éxito")
    message: str = Field(..., description="Mensaje de confirmación")
    dispute_id: UUID = Field(..., description="ID de la disputa creada")
    estado: EstadoDispute = Field(..., description="Estado inicial de la disputa")