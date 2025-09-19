# ~/app/models/commission_dispute.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Sistema de Disputas de Comisiones
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Modelo ComissionDispute para gestión de disputas de comisiones.

Este módulo contiene:
- EstadoDispute: Enum con estados de disputas
- ComissionDispute: Modelo principal para disputas
- Relationships con Transaction y User
"""

from sqlalchemy import Column, String, Text, Enum as SQLEnum, ForeignKey, Index
# UUID import removed for SQLite compatibility as SQLAlchemyUUID
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.models.base import BaseModel


class EstadoDispute(PyEnum):
    """Estados de una disputa de comisión"""
    ABIERTO = "ABIERTO"
    EN_REVISION = "EN_REVISION"
    RESUELTO = "RESUELTO"
    RECHAZADO = "RECHAZADO"


class ComissionDispute(BaseModel):
    """
    Modelo para disputas de comisiones de transacciones.

    Permite a vendedores reportar discrepancias en comisiones
    cobradas por la plataforma.
    """

    __tablename__ = "commission_disputes"

    # FK a la transacción disputada
    transaction_id = Column(
        String(36), 
        ForeignKey("transactions.id"), 
        nullable=False,
        index=True,
        comment="ID de la transacción en disputa"
    )

    # FK al usuario que reporta la disputa
    usuario_id = Column(
        String(36), 
        ForeignKey("users.id"), 
        nullable=False,
        index=True,
        comment="ID del usuario que reporta la discrepancia"
    )

    # Campos de la disputa
    motivo = Column(
        String(100),
        nullable=False,
        comment="Motivo de la disputa (ej: COMISION_INCORRECTA, CALCULO_ERRONEO)"
    )

    descripcion = Column(
        Text,
        nullable=False,
        comment="Descripción detallada de la discrepancia reportada"
    )

    estado = Column(
        SQLEnum(EstadoDispute),
        default=EstadoDispute.ABIERTO,
        nullable=False,
        index=True,
        comment="Estado actual de la disputa"
    )

    respuesta_admin = Column(
        Text,
        nullable=True,
        comment="Respuesta del administrador a la disputa"
    )

    # Relationships
    transaction = relationship(
        "Transaction",
        back_populates="disputes"
    )

    usuario = relationship(
        "User",
        foreign_keys=[usuario_id],
        back_populates="commission_disputes"
    )

    # Índices y constraints
    __table_args__ = (
        Index("ix_dispute_transaction_estado", "transaction_id", "estado"),
        Index("ix_dispute_usuario_estado", "usuario_id", "estado"),
        Index("ix_dispute_fecha_estado", "created_at", "estado"),
    )

    def puede_resolver(self) -> bool:
        """Verificar si la disputa puede ser resuelta"""
        return self.estado in [EstadoDispute.ABIERTO, EstadoDispute.EN_REVISION]

    def marcar_en_revision(self) -> bool:
        """Marcar disputa como en revisión"""
        if self.estado == EstadoDispute.ABIERTO:
            self.estado = EstadoDispute.EN_REVISION
            return True
        return False

    def resolver(self, respuesta: str) -> bool:
        """Resolver la disputa con respuesta"""
        if self.puede_resolver():
            self.estado = EstadoDispute.RESUELTO
            self.respuesta_admin = respuesta
            return True
        return False

    def rechazar(self, motivo: str) -> bool:
        """Rechazar la disputa con motivo"""
        if self.puede_resolver():
            self.estado = EstadoDispute.RECHAZADO
            self.respuesta_admin = motivo
            return True
        return False