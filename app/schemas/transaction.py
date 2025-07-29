# ~/app/schemas/transaction.py
# ---------------------------------------------------------------------------------------------
# MeStore - Esquemas de Transacción Completos
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file
# in the root of this project.
# ---------------------------------------------------------------------------------------------
"""
Esquemas Pydantic para Transaction - Versión Completa
Incluye:
- TransactionBase: Campos base compartidos
- TransactionCreate: Schema para creación de transacciones
- TransactionUpdate: Schema para actualizaciones parciales
- TransactionRead: Schema para respuestas de API
- Todos los enums: TransactionType, MetodoPago, EstadoTransaccion
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

# Imports de enums desde el modelo
from app.models.transaction import (
    TransactionType,
    MetodoPago, 
    EstadoTransaccion
)


class TransactionBase(BaseModel):
    """Schema base para Transaction con campos comunes."""

    monto: Decimal = Field(
        ..., 
        description="Monto de la transacción en pesos colombianos (COP)",
        gt=0,
        decimal_places=2
    )

    # Campos de estado adicionales (tarea 1.2.4.5)
    status: Optional[str] = Field(
        None,
        max_length=50,
        description="Estado adicional específico del procesador de pagos"
    )

    fecha_pago: Optional[datetime] = Field(
        None,
        description="Fecha y hora cuando se realizó el pago efectivo"
    )

    referencia_pago: Optional[str] = Field(
        None,
        max_length=100,
        description="Referencia específica del pago (diferente a referencia_externa)"
    )

    # Campos adicionales
    vendedor_id: Optional[UUID] = Field(
        None,
        description="ID del usuario vendedor (nullable para transacciones del sistema)"
    )

    product_id: Optional[UUID] = Field(
        None,
        description="ID del producto involucrado en la transacción"
    )

    referencia_externa: Optional[str] = Field(
        None,
        max_length=100,
        description="Referencia externa del procesador de pagos"
    )

    observaciones: Optional[str] = Field(
        None,
        description="Observaciones adicionales sobre la transacción"
    )

    # Campos de comisiones
    porcentaje_mestocker: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="Porcentaje de comisión para MeStore (0.00 a 100.00)"
    )

    monto_vendedor: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=12,
        decimal_places=2,
        description="Monto que recibe el vendedor después de comisiones (COP)"
    )


    metodo_pago: MetodoPago = Field(
        ...,
        description="Método de pago utilizado en la transacción"
    )
    transaction_type: TransactionType = Field(
        default=TransactionType.VENTA,
        description="Tipo de transacción del marketplace"
    )
    estado: EstadoTransaccion = Field(
        default=EstadoTransaccion.PENDIENTE,
        description="Estado actual de la transacción"
    )


class TransactionCreate(TransactionBase):
    """Schema para creación de transacciones."""

    comprador_id: UUID = Field(..., description="ID del usuario comprador")

    @field_validator('monto')
    @classmethod
    def validate_monto(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError('El monto debe ser mayor a 0')
        if v > 999999999.99:
            raise ValueError('Monto máximo excedido')
        return v


class TransactionUpdate(BaseModel):
    """Schema para actualizaciones parciales de transacciones."""

    estado: Optional[EstadoTransaccion] = Field(
        None,
        description="Nuevo estado de la transacción"
    )
    transaction_type: Optional[TransactionType] = Field(
        None,
        description="Nuevo tipo de transacción"
    )


class TransactionRead(TransactionBase):
    """Schema para respuestas de API con datos completos."""

    id: UUID = Field(..., description="ID único de la transacción")
    comprador_id: UUID = Field(..., description="ID del usuario comprador")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    deleted_at: Optional[datetime] = Field(None, description="Fecha de eliminación lógica")

    class Config:
        from_attributes = True


# Alias descriptivo para respuestas
TransactionResponse = TransactionRead

# Agregar campos faltantes después de los campos existentes

# Campos de estado adicionales (tarea 1.2.4.5)
status: Optional[str] = Field(
    None,
    max_length=50,
    description="Estado adicional específico del procesador de pagos"
)

fecha_pago: Optional[datetime] = Field(
    None,
    description="Fecha y hora cuando se realizó el pago efectivo"
)

referencia_pago: Optional[str] = Field(
    None,
    max_length=100,
    description="Referencia específica del pago (diferente a referencia_externa)"
)

# Campos adicionales
vendedor_id: Optional[UUID] = Field(
    None,
    description="ID del usuario vendedor (nullable para transacciones del sistema)"
)

product_id: Optional[UUID] = Field(
    None,
    description="ID del producto involucrado en la transacción"
)

referencia_externa: Optional[str] = Field(
    None,
    max_length=100,
    description="Referencia externa del procesador de pagos"
)

observaciones: Optional[str] = Field(
    None,
    description="Observaciones adicionales sobre la transacción"
)