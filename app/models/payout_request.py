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
# Última Actualización: 2025-09-03
# Versión: 1.1.0
# Propósito: Modelo para gestionar solicitudes de pago de comisiones con datos bancarios
#            temporales por request y tracking automático de historial
#
# Modificaciones:
# 2025-08-07 - Creación inicial del modelo PayoutRequest
# 2025-09-03 - Integración con PayoutHistory para tracking automático
#
# ---------------------------------------------------------------------------------------------

"""
Modelo PayoutRequest para gestión de solicitudes de pago de comisiones.

Este módulo contiene:
- EstadoPayout: Enum con estados de solicitudes de pago
- PayoutRequest: Modelo principal para almacenar solicitudes
- Validaciones y relationships necesarios
- Tracking automático de cambios de estado
"""

from sqlalchemy import Column, String, DECIMAL, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
# UUID import removed for SQLite compatibility as SQLAlchemyUUID
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.models.base import BaseModel
from app.models.payout_history import PayoutHistory


class EstadoPayout(PyEnum):
    SOLICITADO = "SOLICITADO"
    PROCESANDO = "PROCESANDO"
    PAGADO = "PAGADO"
    RECHAZADO = "RECHAZADO"


class PayoutRequest(BaseModel):
    __tablename__ = "payout_requests"
    
    # FK al vendedor
    vendedor_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    monto_solicitado = Column(DECIMAL(12, 2), nullable=False)
    estado = Column(SQLEnum(EstadoPayout), default=EstadoPayout.SOLICITADO)
    
    # Datos bancarios temporales del request
    tipo_cuenta = Column(String(20), nullable=False)  # AHORROS, CORRIENTE
    numero_cuenta = Column(String(50), nullable=False)
    banco = Column(String(100), nullable=False)
    observaciones = Column(String(500), nullable=True)
    fecha_procesamiento = Column(DateTime, nullable=True)
    referencia_pago = Column(String(100), nullable=True)
    
    # Relationships
    vendedor = relationship("User", back_populates="payout_requests")
    history = relationship("PayoutHistory", back_populates="payout_request")
    
    def puede_procesar(self) -> bool:
        """Verificar si el payout puede ser procesado"""
        return self.estado == EstadoPayout.SOLICITADO
    
    def marcar_como_procesando(self) -> bool:
        """Marcar payout como en procesamiento"""
        if self.estado == EstadoPayout.SOLICITADO:
            self.estado = EstadoPayout.PROCESANDO
            return True
        return False
    
    def cambiar_estado(self, db_session, nuevo_estado: EstadoPayout, observaciones: str = None, usuario_id: int = None) -> bool:
        """
        Cambiar estado del payout con tracking automático en PayoutHistory.
        
        Args:
            db_session: Sesión de base de datos
            nuevo_estado: Nuevo estado del payout
            observaciones: Notas sobre el cambio
            usuario_id: ID del usuario responsable del cambio
            
        Returns:
            bool: True si el cambio fue exitoso
        """
        estado_anterior = self.estado.value if self.estado else None
        
        # Cambiar el estado
        self.estado = nuevo_estado
        
        # Registrar en historial automáticamente
        PayoutHistory.registrar_cambio(
            db_session=db_session,
            payout_request_id=self.id,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado.value,
            observaciones=observaciones,
            usuario_id=usuario_id
        )
        
        return True