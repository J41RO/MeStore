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
from datetime import datetime

from sqlalchemy import (
    DECIMAL,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    DateTime,
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


class TransactionType(PyEnum):
    """
    Enumeración para tipos de transacciones en el marketplace.

    Valores:
    - VENTA: Transacción de venta de producto
    - COMISION: Comisión cobrada por la plataforma
    - DEVOLUCION: Devolución de dinero al comprador
    - AJUSTE: Ajuste contable o corrección
    """
    VENTA = "VENTA"
    COMISION = "COMISION"
    DEVOLUCION = "DEVOLUCION"
    AJUSTE = "AJUSTE"


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

    # Relationship con Inventory
    inventario = relationship(
        "Inventory",
        back_populates="transacciones"
    )
    # Relationship con disputes
    disputes = relationship(
        "ComissionDispute",
        back_populates="transaction"
    )
    

    # FK para relación con Inventory
    inventory_id = Column(
        String(36),
        ForeignKey("inventory.id"),
        nullable=True,
        index=True,
        comment="ID del inventario específico involucrado en la transacción"
    )

    # Campos de estado adicionales del procesador de pagos
    status = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Estado adicional específico del procesador de pagos"
    )

    fecha_pago = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="Fecha y hora cuando se realizó el pago efectivo"
    )

    referencia_pago = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Referencia específica del pago (diferente a referencia_externa)"
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

    transaction_type = Column(
        Enum(TransactionType),
        nullable=False,
        default=TransactionType.VENTA,
        comment="Tipo de transacción del marketplace"
    )

    # Campos de comisiones
    porcentaje_mestocker = Column(
        DECIMAL(5, 2),  # Hasta 999.99%
        nullable=True,
        comment="Porcentaje de comisión para MeStore (0.00 a 100.00)"
    )

    monto_vendedor = Column(
        DECIMAL(12, 2),
        nullable=True,
        comment="Monto que recibe el vendedor después de comisiones (COP)"
    )
    

    # Relationships con otros modelos
    comprador_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="ID del usuario comprador"
    )

    vendedor_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
        comment="ID del usuario vendedor (nullable para transacciones del sistema)"
    )

    product_id = Column(
        String(36),
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

    # Commission relationship
    commission = relationship(
        "Commission",
        back_populates="transaction",
        uselist=False
    )

    # Constraints e índices
    __table_args__ = (
        Index("ix_transaction_estado_fecha", "estado", "created_at"),
        Index("ix_transaction_comprador_estado", "comprador_id", "estado"),
        Index("ix_transaction_vendedor_estado", "vendedor_id", "estado"),
        Index("ix_transaction_product", "product_id", "estado"),
        Index("ix_transaction_fecha_pago", "fecha_pago"),
        Index("ix_transaction_status_fecha", "status", "fecha_pago"),
        Index("ix_transaction_referencia_pago", "referencia_pago"),
        CheckConstraint("monto > 0", name="ck_transaction_monto_positive"),
        CheckConstraint(
            "porcentaje_mestocker >= 0 AND porcentaje_mestocker <= 100", 
            name="ck_transaction_porcentaje_valid"
        ),
        CheckConstraint(
            "monto_vendedor >= 0", 
            name="ck_transaction_monto_vendedor_positive"
        ),
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

    def marcar_pago_completado(self, referencia: str = None) -> None:
        """Marcar pago como completado con fecha y referencia"""
        self.fecha_pago = datetime.utcnow()
        self.status = "PAGADO"
        if referencia:
            self.referencia_pago = referencia

    def tiene_pago_confirmado(self) -> bool:
        """Verificar si el pago está confirmado"""
        return self.fecha_pago is not None and self.status == "PAGADO"

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
        if self.monto is None:
            return "$0.00 COP"
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

    def calcular_monto_vendedor(self) -> Optional[Decimal]:
        """Calcular monto para vendedor basado en comisión"""
        if self.monto and self.porcentaje_mestocker is not None:
            comision = (self.monto * self.porcentaje_mestocker) / 100
            return self.monto - comision
        return None

    def aplicar_comision_automatica(self, porcentaje: Decimal) -> None:
        """Aplicar comisión y calcular monto vendedor automáticamente"""
        self.porcentaje_mestocker = porcentaje
        self.monto_vendedor = self.calcular_monto_vendedor()

    def to_dict(self) -> dict:
        """Serializar transacción a diccionario"""
        base_dict = super().to_dict()
        transaction_dict = {
            "monto": float(self.monto) if self.monto else None,
            "monto_formateado": self.get_monto_formateado(),
            "porcentaje_mestocker": float(self.porcentaje_mestocker) if self.porcentaje_mestocker else None,
            "monto_vendedor": float(self.monto_vendedor) if self.monto_vendedor else None,
            "metodo_pago": self.metodo_pago.value if self.metodo_pago else None,
            "estado": self.estado.value if self.estado else None,
            "comprador_id": str(self.comprador_id) if self.comprador_id else None,
            "vendedor_id": str(self.vendedor_id) if self.vendedor_id else None,
            "product_id": str(self.product_id) if self.product_id else None,
            "referencia_externa": self.referencia_externa,
            "status": self.status,
            "fecha_pago": self.fecha_pago.isoformat() if self.fecha_pago else None,
            "referencia_pago": self.referencia_pago,
            "observaciones": self.observaciones,
            "esta_completada": self.esta_completada(),
            "puede_cancelar": self.puede_cancelar(),
            "es_pago_digital": self.es_pago_digital(),
        }
        return {**base_dict, **transaction_dict}
# Aliases for English compatibility
TransactionStatus = EstadoTransaccion
PaymentMethod = MetodoPago
