# ~/app/models/payout_request.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Sistema de Solicitud de Pagos de Comisiones
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: payout_request.py
# Ruta: ~/app/models/payout_request.py
# Autor: Jairo
# Fecha de Creación: 2025-08-07
# Última Actualización: 2025-08-07
# Versión: 1.0.0
# Propósito: Modelo para gestionar solicitudes de pago de comisiones con datos bancarios
#            temporales por request
#
# Modificaciones:
# 2025-08-07 - Creación inicial del modelo PayoutRequest
#
# ---------------------------------------------------------------------------------------------

"""
Modelo PayoutRequest para gestión de solicitudes de pago de comisiones.

Este módulo contiene:
- EstadoPayout: Enum con estados de solicitudes de pago
- PayoutRequest: Modelo principal para almacenar solicitudes
- Validaciones y relationships necesarios
"""

# ~/app/models/payout_request.py
from sqlalchemy import Column, String, DECIMAL, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.models.base import BaseModel

class EstadoPayout(PyEnum):
    SOLICITADO = "SOLICITADO"
    PROCESANDO = "PROCESANDO"
    PAGADO = "PAGADO"
    RECHAZADO = "RECHAZADO"
    
class PayoutRequest(BaseModel):
    __tablename__ = "payout_requests"
    
    # FK al vendedor
    vendedor_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    monto_solicitado = Column(DECIMAL(12, 2), nullable=False)
    estado = Column(SQLEnum(EstadoPayout), default=EstadoPayout.SOLICITADO)
    
    # Datos bancarios temporales del request
    tipo_cuenta = Column(String(20), nullable=False)  # AHORROS, CORRIENTE
    numero_cuenta = Column(String(50), nullable=False)
    banco = Column(String(100), nullable=False)
    observaciones = Column(String(500), nullable=True)
    fecha_procesamiento = Column(DateTime, nullable=True)
    referencia_pago = Column(String(100), nullable=True)
    
    # Relationship
    vendedor = relationship("User", back_populates="payout_requests")
    
    def puede_procesar(self) -> bool:
        """Verificar si el payout puede ser procesado"""
        return self.estado == EstadoPayout.SOLICITADO
        
    def marcar_como_procesando(self) -> bool:
        """Marcar payout como en procesamiento"""
        if self.estado == EstadoPayout.SOLICITADO:
            self.estado = EstadoPayout.PROCESANDO
            return True
        return False