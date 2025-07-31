# ~/app/schemas/storage.py
# ---------------------------------------------------------------------------------------------
# MeStore - Storage Schemas para API y validación
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: storage.py
# Ruta: ~/app/schemas/storage.py
# Autor: Jairo
# Fecha de Creación: 2025-07-29
# Última Actualización: 2025-07-29
# Versión: 1.0.0
# Propósito: Schemas Pydantic para Storage con validaciones completas y facturación
#            Incluye schemas CRUD base y schemas especializados para billing
#
# Modificaciones:
# 2025-07-29 - Creación inicial con schemas base, CRUD y facturación
#
# ---------------------------------------------------------------------------------------------

"""
Storage Pydantic Schemas para MeStore Marketplace.

Schemas incluidos:
- StorageBase: Campos base compartidos
- StorageCreate: Para creación de nuevos storages  
- StorageUpdate: Para actualización de storages existentes
- StorageResponse: Para respuestas API completas
- StorageBilling: Para cálculos de facturación
- BillingCalculation: Para resultados de facturación
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.models.storage import StorageType


class StorageBase(BaseModel):
    """Schema base para Storage con campos comunes."""

    tipo: StorageType = Field(..., description="Tipo de espacio de almacenamiento")
    capacidad_max: int = Field(..., gt=0, description="Capacidad máxima en productos")

    @field_validator('capacidad_max')
    @classmethod
    def validate_capacidad_max(cls, v):
        if v <= 0:
            raise ValueError('La capacidad máxima debe ser mayor a 0')
        return v


class StorageCreate(StorageBase):
    """Schema para creación de Storage."""

    # Campos pricing opcionales
    tarifa_mensual: Optional[Decimal] = Field(None, ge=0, description="Tarifa mensual en COP")
    tarifa_por_producto: Optional[Decimal] = Field(None, ge=0, description="Tarifa por producto en COP")

    # Campos relationship opcionales
    vendedor_id: Optional[UUID] = Field(None, description="ID del vendedor propietario")

    # Campos contrato opcionales
    fecha_inicio: Optional[datetime] = Field(None, description="Fecha inicio del contrato")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha fin del contrato")
    renovacion_automatica: bool = Field(False, description="Renovación automática del contrato")

    @field_validator('fecha_fin')
    @classmethod
    def validate_fecha_fin(cls, v, info):
        if v and info.data.get('fecha_inicio') and v <= info.data['fecha_inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v


class StorageUpdate(BaseModel):
    """Schema para actualización de Storage."""

    tipo: Optional[StorageType] = Field(None, description="Tipo de espacio de almacenamiento")
    capacidad_max: Optional[int] = Field(None, gt=0, description="Capacidad máxima en productos")
    tarifa_mensual: Optional[Decimal] = Field(None, ge=0, description="Tarifa mensual en COP")
    tarifa_por_producto: Optional[Decimal] = Field(None, ge=0, description="Tarifa por producto en COP")
    vendedor_id: Optional[UUID] = Field(None, description="ID del vendedor propietario")
    fecha_inicio: Optional[datetime] = Field(None, description="Fecha inicio del contrato")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha fin del contrato")
    renovacion_automatica: Optional[bool] = Field(None, description="Renovación automática del contrato")


class StorageResponse(StorageBase):
    """Schema para respuestas API de Storage."""

    # Campos BaseModel
    id: UUID = Field(..., description="ID único del storage")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    # Campos pricing
    tarifa_mensual: Optional[Decimal] = Field(None, description="Tarifa mensual en COP")
    tarifa_por_producto: Optional[Decimal] = Field(None, description="Tarifa por producto en COP")

    # Campos relationship
    vendedor_id: Optional[UUID] = Field(None, description="ID del vendedor propietario")

    # Campos tracking
    productos_actuales: int = Field(..., description="Número actual de productos almacenados")
    ocupacion_actual: Decimal = Field(..., description="Porcentaje actual de ocupación")
    ultima_actualizacion: Optional[datetime] = Field(None, description="Última actualización tracking")

    # Campos contrato
    fecha_inicio: Optional[datetime] = Field(None, description="Fecha inicio del contrato")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha fin del contrato")
    renovacion_automatica: bool = Field(..., description="Renovación automática del contrato")

    model_config = ConfigDict(from_attributes=True)


class StorageBilling(BaseModel):
    """Schema para información de facturación de Storage."""

    storage_id: UUID = Field(..., description="ID del storage")
    vendedor_id: Optional[UUID] = Field(None, description="ID del vendedor")
    tipo: StorageType = Field(..., description="Tipo de storage")
    capacidad_max: int = Field(..., description="Capacidad máxima")
    productos_actuales: int = Field(..., description="Productos actuales")

    # Tarifas
    tarifa_mensual: Optional[Decimal] = Field(None, description="Tarifa mensual")
    tarifa_por_producto: Optional[Decimal] = Field(None, description="Tarifa por producto")

    # Período de facturación
    fecha_inicio_periodo: datetime = Field(..., description="Inicio del período de facturación")
    fecha_fin_periodo: datetime = Field(..., description="Fin del período de facturación")

    model_config = ConfigDict(from_attributes=True)


class BillingCalculation(BaseModel):
    """Schema para resultados de cálculo de facturación."""

    storage_billing: StorageBilling = Field(..., description="Información del storage")

    # Cálculos
    costo_mensual_base: Decimal = Field(..., description="Costo base mensual")
    costo_por_productos: Decimal = Field(..., description="Costo por productos almacenados")
    costo_total: Decimal = Field(..., description="Costo total del período")

    # Detalles
    dias_facturados: int = Field(..., description="Días del período facturado")
    productos_promedio: Decimal = Field(..., description="Promedio de productos en el período")

    # Metadata
    fecha_calculo: datetime = Field(default_factory=datetime.utcnow, description="Fecha del cálculo")
    es_gratuito: bool = Field(..., description="Si el storage es gratuito")

    @field_validator('costo_total')
    @classmethod
    def validate_costo_total(cls, v):
        if v < 0:
            raise ValueError('El costo total no puede ser negativo')
        return v
