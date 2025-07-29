# ~/app/models/transaction.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Transaction Model for Marketplace Financial Operations
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: transaction.py
# Ruta: ~/app/models/transaction.py
# Autor: Jairo
# Fecha de Creación: 2025-07-28
# Última Actualización: 2025-07-28
# Versión: 1.0.0
# Propósito: Modelo Transaction para gestión de transacciones del marketplace
#            Incluye métodos de pago colombianos y estados de transacción
#
# Modificaciones:
# 2025-07-28 - Creación inicial del modelo Transaction con campos básicos
#
# ---------------------------------------------------------------------------------------------

"""
Transaction Model para MeStore Marketplace.

Este módulo contiene:
- Transaction: Modelo principal para transacciones
- MetodoPago: Enumeración de métodos de pago colombianos  
- EstadoTransaccion: Enumeración de estados de transacción
- Relationships bidireccionales con User y Product
- Métodos de utilidad para gestión de estados y validaciones
"""

from decimal import Decimal
from enum import Enum as PyEnum
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    DECIMAL,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UUID as SQLAlchemyUUID,
)
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class MetodoPago(PyEnum):
    """
    Enumeración para métodos de pago en transacciones.

    Métodos de pago disponibles:
        EFECTIVO: Pago en efectivo
        TARJETA_CREDITO: Tarjeta de crédito
        TARJETA_DEBITO: Tarjeta de débito
        PSE: Pagos Seguros en Línea
        NEQUI: Billetera digital Nequi
        DAVIPLATA: Billetera digital Daviplata
    """
    EFECTIVO = "EFECTIVO"
    TARJETA_CREDITO = "TARJETA_CREDITO"
    TARJETA_DEBITO = "TARJETA_DEBITO"
    PSE = "PSE"
    NEQUI = "NEQUI"
    DAVIPLATA = "DAVIPLATA"


class EstadoTransaccion(PyEnum):
    """
    Enumeración para estado de transacciones.

    Estados del flujo de transacción:
        PENDIENTE: Transacción creada, esperando procesamiento
        PROCESANDO: Transacción en proceso de validación
        COMPLETADA: Transacción exitosamente completada
        FALLIDA: Transacción falló por error técnico
        CANCELADA: Transacción cancelada por usuario o sistema
    """
    PENDIENTE = "PENDIENTE"
    PROCESANDO = "PROCESANDO"
    COMPLETADA = "COMPLETADA"
    FALLIDA = "FALLIDA"
    CANCELADA = "CANCELADA"


class Transaction(BaseModel):
    """
    Modelo Transaction para gestión de transacciones del marketplace.

    Campos básicos:
    - monto: Monto de la transacción en pesos colombianos
    - metodo_pago: Método de pago utilizado
    - estado: Estado actual de la transacción
    - Relationships: Conexiones con User y Product

    Hereda de BaseModel:
    - id (UUID): Identificador único
    - created_at (DateTime): Fecha de creación
    - updated_at (DateTime): Fecha de última actualización
    - deleted_at (DateTime): Fecha de eliminación lógica
    """

    __tablename__ = "transactions"

    # Campos básicos de transacción
    monto = Column(
        DECIMAL(12, 2),
        nullable=False,
        comment="Monto de la transacción en pesos colombianos (COP)"
    )

    metodo_pago = Column(
        Enum(MetodoPago),
        nullable=False,
        comment="Método de pago utilizado en la transacción"
    )

    estado = Column(
        Enum(EstadoTransaccion),
        nullable=False,
        default=EstadoTransaccion.PENDIENTE,
        comment="Estado actual de la transacción"
    )

    # Relationships con otros modelos
    comprador_id = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="ID del usuario comprador"
    )

    vendedor_id = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
        comment="ID del usuario vendedor (nullable para transacciones del sistema)"
    )

    product_id = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=True,
        index=True,
        comment="ID del producto involucrado en la transacción"
    )

    # Campos adicionales útiles
    referencia_externa = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Referencia externa del procesador de pagos"
    )

    observaciones = Column(
        Text,
        nullable=True,
        comment="Observaciones adicionales sobre la transacción"
    )

    # Relationships
    comprador = relationship(
        "User",
        foreign_keys=[comprador_id],
        back_populates="transacciones_comprador"
    )

    vendedor = relationship(
        "User",
        foreign_keys=[vendedor_id],
        back_populates="transacciones_vendedor"
    )

    product = relationship(
        "Product",
        back_populates="transacciones"
    )

    # Constraints e índices
    __table_args__ = (
        Index("ix_transaction_estado_fecha", "estado", "created_at"),
        Index("ix_transaction_comprador_estado", "comprador_id", "estado"),
        Index("ix_transaction_vendedor_estado", "vendedor_id", "estado"),
        Index("ix_transaction_product", "product_id", "estado"),
        CheckConstraint("monto > 0", name="ck_transaction_monto_positive"),
    )

    def esta_pendiente(self) -> bool:
        """Verificar si la transacción está pendiente"""
        return self.estado == EstadoTransaccion.PENDIENTE

    def esta_completada(self) -> bool:
        """Verificar si la transacción está completada"""
        return self.estado == EstadoTransaccion.COMPLETADA

    def puede_cancelar(self) -> bool:
        """Verificar si la transacción puede ser cancelada"""
        return self.estado in [EstadoTransaccion.PENDIENTE, EstadoTransaccion.PROCESANDO]

    def marcar_como_completada(self) -> bool:
        """Marcar transacción como completada"""
        if self.estado == EstadoTransaccion.PROCESANDO:
            self.estado = EstadoTransaccion.COMPLETADA
            return True
        return False

    def marcar_como_fallida(self) -> bool:
        """Marcar transacción como fallida"""
        if self.estado in [EstadoTransaccion.PENDIENTE, EstadoTransaccion.PROCESANDO]:
            self.estado = EstadoTransaccion.FALLIDA
            return True
        return False

    def cancelar(self) -> bool:
        """Cancelar transacción si es posible"""
        if self.puede_cancelar():
            self.estado = EstadoTransaccion.CANCELADA
            return True
        return False

    def get_monto_formateado(self) -> str:
        """Obtener monto formateado en pesos colombianos"""
        return f"${self.monto:,.2f} COP"

    def es_pago_digital(self) -> bool:
        """Verificar si es un método de pago digital"""
        return self.metodo_pago in [
            MetodoPago.TARJETA_CREDITO,
            MetodoPago.TARJETA_DEBITO,
            MetodoPago.PSE,
            MetodoPago.NEQUI,
            MetodoPago.DAVIPLATA
        ]

    def to_dict(self) -> dict:
        """Serializar transacción a diccionario"""
        base_dict = super().to_dict()
        transaction_dict = {
            "monto": float(self.monto) if self.monto else None,
            "monto_formateado": self.get_monto_formateado(),
            "metodo_pago": self.metodo_pago.value if self.metodo_pago else None,
            "estado": self.estado.value if self.estado else None,
            "comprador_id": str(self.comprador_id) if self.comprador_id else None,
            "vendedor_id": str(self.vendedor_id) if self.vendedor_id else None,
            "product_id": str(self.product_id) if self.product_id else None,
            "referencia_externa": self.referencia_externa,
            "observaciones": self.observaciones,
            "esta_completada": self.esta_completada(),
            "puede_cancelar": self.puede_cancelar(),
            "es_pago_digital": self.es_pago_digital(),
        }
        return {**base_dict, **transaction_dict}
