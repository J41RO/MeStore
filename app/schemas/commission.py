# ~/app/schemas/commission.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Commission Pydantic Schemas (PRODUCTION_READY)
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: commission.py
# Ruta: ~/app/schemas/commission.py
# Autor: Jairo
# Fecha de Creación: 2025-09-13
# Última Actualización: 2025-09-13
# Versión: 1.0.0
# Propósito: Schemas Pydantic para sistema de comisiones enterprise
#            Validación robusta, serialización optimizada para APIs
#
# Modificaciones:
# 2025-09-13 - Creación inicial con validación enterprise
#
# ---------------------------------------------------------------------------------------------

"""
PRODUCTION_READY: Schemas Pydantic para sistema de comisiones

Este módulo contiene:
- CommissionBase: Schema base con validaciones financieras
- CommissionCreate: Para creación de comisiones automáticas
- CommissionRead: Para respuestas API con metadata completa
- VendorEarnings: Reporte de ganancias del vendor
- CommissionReport: Reporte administrativo de comisiones
- CommissionSummary: Resumen ejecutivo para dashboards
"""

import os
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field

from app.models.commission import CommissionStatus, CommissionType


class CommissionBase(BaseModel):
    """Schema base para Commission con validaciones financieras enterprise"""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        json_encoders={
            Decimal: lambda x: float(x),
            datetime: lambda x: x.isoformat(),
        }
    )

    order_amount: Decimal = Field(
        ...,
        gt=0,
        description="Monto total de la orden en pesos colombianos",
        json_schema_extra={"example": 150000.00}
    )
    commission_rate: Decimal = Field(
        ...,
        ge=0,
        le=1,
        description="Tasa de comisión (0.05 = 5%)",
        json_schema_extra={"example": 0.05}
    )
    commission_amount: Decimal = Field(
        ...,
        ge=0,
        description="Monto de comisión calculado",
        json_schema_extra={"example": 7500.00}
    )
    vendor_amount: Decimal = Field(
        ...,
        ge=0,
        description="Monto que recibe el vendor",
        json_schema_extra={"example": 142500.00}
    )
    platform_amount: Decimal = Field(
        ...,
        ge=0,
        description="Monto que retiene la plataforma",
        json_schema_extra={"example": 7500.00}
    )
    commission_type: CommissionType = Field(
        default=CommissionType.STANDARD,
        description="Tipo de comisión aplicada"
    )
    currency: str = Field(
        default="COP",
        min_length=3,
        max_length=3,
        description="Código de moneda ISO",
        json_schema_extra={"example": "COP"}
    )

    @field_validator('commission_rate')
    @classmethod
    def validate_commission_rate(cls, v: Decimal) -> Decimal:
        """Validar que la tasa de comisión esté en rango válido"""
        if v < 0 or v > 1:
            raise ValueError('Commission rate must be between 0 and 1 (0% to 100%)')
        return v

    @field_validator('order_amount', 'commission_amount', 'vendor_amount', 'platform_amount')
    @classmethod
    def validate_positive_amounts(cls, v: Decimal) -> Decimal:
        """Validar que los montos sean positivos"""
        if v < 0:
            raise ValueError('Financial amounts must be non-negative')
        return v

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validar código de moneda"""
        v = v.upper()
        allowed_currencies = ['COP', 'USD', 'EUR']  # Expandir según necesidades
        if v not in allowed_currencies:
            raise ValueError(f'Currency must be one of: {", ".join(allowed_currencies)}')
        return v


class CommissionCreate(CommissionBase):
    """Schema para creación de comisiones (uso interno del servicio)"""

    order_id: int = Field(..., gt=0, description="ID de la orden asociada")
    vendor_id: UUID = Field(..., description="ID del vendor")
    transaction_id: Optional[UUID] = Field(None, description="ID de transacción asociada")
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Notas adicionales sobre la comisión"
    )

    @computed_field
    @property
    def commission_number(self) -> str:
        """Generar número de comisión único"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"COM-{timestamp}-{self.order_id}"


class CommissionRead(CommissionBase):
    """Schema completo para lectura de comisiones"""

    id: UUID = Field(..., description="ID único de la comisión")
    commission_number: str = Field(..., description="Número único de comisión")
    order_id: int = Field(..., description="ID de la orden asociada")
    vendor_id: UUID = Field(..., description="ID del vendor")
    transaction_id: Optional[UUID] = Field(None, description="ID de transacción")

    status: CommissionStatus = Field(..., description="Estado actual de la comisión")
    calculation_method: str = Field(
        default="automatic",
        description="Método de cálculo utilizado"
    )
    notes: Optional[str] = Field(None, description="Notas públicas")
    admin_notes: Optional[str] = Field(None, description="Notas administrativas")

    # Timestamps de auditoría
    calculated_at: datetime = Field(..., description="Fecha de cálculo")
    approved_at: Optional[datetime] = Field(None, description="Fecha de aprobación")
    paid_at: Optional[datetime] = Field(None, description="Fecha de pago")
    disputed_at: Optional[datetime] = Field(None, description="Fecha de disputa")
    resolved_at: Optional[datetime] = Field(None, description="Fecha de resolución")

    approved_by_id: Optional[UUID] = Field(None, description="ID del aprobador")

    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")

    @computed_field
    @property
    def status_display(self) -> str:
        """Texto amigable del estado en español"""
        status_map = {
            CommissionStatus.PENDING: "Pendiente",
            CommissionStatus.APPROVED: "Aprobada",
            CommissionStatus.PAID: "Pagada",
            CommissionStatus.DISPUTED: "En Disputa",
            CommissionStatus.REFUNDED: "Reembolsada",
            CommissionStatus.CANCELLED: "Cancelada"
        }
        return status_map.get(self.status, "Desconocido")

    @computed_field
    @property
    def days_since_calculation(self) -> int:
        """Días transcurridos desde el cálculo"""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        calc_date = self.calculated_at
        if calc_date.tzinfo is None:
            calc_date = calc_date.replace(tzinfo=timezone.utc)
        return (now - calc_date).days


class VendorEarnings(BaseModel):
    """Schema para reporte de ganancias del vendor"""

    model_config = ConfigDict(from_attributes=True)

    vendor_id: UUID = Field(..., description="ID del vendor")
    vendor_name: str = Field(..., description="Nombre del vendor")
    vendor_email: str = Field(..., description="Email del vendor")

    # Totales acumulados
    total_earned: Decimal = Field(
        ...,
        ge=0,
        description="Total ganado (después de comisiones)",
        json_schema_extra={"example": 2500000.00}
    )
    total_orders: int = Field(
        ...,
        ge=0,
        description="Total de órdenes procesadas",
        json_schema_extra={"example": 45}
    )
    total_commission_paid: Decimal = Field(
        ...,
        ge=0,
        description="Total comisiones pagadas a la plataforma",
        json_schema_extra={"example": 125000.00}
    )

    # Métricas del mes actual
    earnings_this_month: Decimal = Field(
        ...,
        ge=0,
        description="Ganancias del mes actual",
        json_schema_extra={"example": 450000.00}
    )
    orders_this_month: int = Field(
        ...,
        ge=0,
        description="Órdenes del mes actual",
        json_schema_extra={"example": 8}
    )
    commission_this_month: Decimal = Field(
        ...,
        ge=0,
        description="Comisiones del mes actual",
        json_schema_extra={"example": 22500.00}
    )

    # Métricas de estado
    pending_commissions: Decimal = Field(
        ...,
        ge=0,
        description="Comisiones pendientes de aprobación",
        json_schema_extra={"example": 15000.00}
    )
    average_commission_rate: Decimal = Field(
        ...,
        ge=0,
        le=1,
        description="Tasa promedio de comisión",
        json_schema_extra={"example": 0.05}
    )

    # Metadata del reporte
    report_period: str = Field(..., description="Período del reporte")
    generated_at: datetime = Field(..., description="Fecha de generación")
    currency: str = Field(default="COP", description="Moneda de los montos")

    @computed_field
    @property
    def average_order_value(self) -> Decimal:
        """Valor promedio por orden"""
        if self.total_orders == 0:
            return Decimal('0.00')
        return Decimal(str(self.total_earned / self.total_orders)).quantize(Decimal('0.01'))

    @computed_field
    @property
    def commission_percentage(self) -> Decimal:
        """Porcentaje de comisión efectivo"""
        total_gross = self.total_earned + self.total_commission_paid
        if total_gross == 0:
            return Decimal('0.00')
        return Decimal(str(self.total_commission_paid / total_gross * 100)).quantize(Decimal('0.01'))


class CommissionReport(BaseModel):
    """Schema para reporte administrativo de comisiones"""

    model_config = ConfigDict(from_attributes=True)

    vendor_id: UUID = Field(..., description="ID del vendor")
    vendor_name: str = Field(..., description="Nombre del vendor")
    vendor_email: str = Field(..., description="Email del vendor")

    # Totales por estado
    total_commissions: Decimal = Field(
        ...,
        ge=0,
        description="Total comisiones generadas",
        json_schema_extra={"example": 125000.00}
    )
    pending_amount: Decimal = Field(
        ...,
        ge=0,
        description="Monto pendiente de aprobación",
        json_schema_extra={"example": 15000.00}
    )
    approved_amount: Decimal = Field(
        ...,
        ge=0,
        description="Monto aprobado para pago",
        json_schema_extra={"example": 35000.00}
    )
    paid_amount: Decimal = Field(
        ...,
        ge=0,
        description="Monto ya pagado",
        json_schema_extra={"example": 75000.00}
    )

    # Métricas de órdenes
    total_orders: int = Field(
        ...,
        ge=0,
        description="Total órdenes con comisión",
        json_schema_extra={"example": 45}
    )
    average_commission_rate: Decimal = Field(
        ...,
        ge=0,
        le=1,
        description="Tasa promedio de comisión",
        json_schema_extra={"example": 0.05}
    )

    # Período del reporte
    date_from: date = Field(..., description="Fecha inicio del reporte")
    date_to: date = Field(..., description="Fecha fin del reporte")
    generated_at: datetime = Field(..., description="Fecha de generación")
    currency: str = Field(default="COP", description="Moneda del reporte")

    @computed_field
    @property
    def completion_rate(self) -> Decimal:
        """Porcentaje de comisiones completadas (pagadas)"""
        if self.total_commissions == 0:
            return Decimal('0.00')
        return Decimal(str(self.paid_amount / self.total_commissions * 100)).quantize(Decimal('0.01'))


class CommissionSummary(BaseModel):
    """Schema para resumen ejecutivo de comisiones (dashboard)"""

    model_config = ConfigDict(from_attributes=True)

    # Totales generales
    total_commissions: Decimal = Field(..., ge=0, description="Total comisiones generadas")
    total_revenue: Decimal = Field(..., ge=0, description="Total ingresos por comisiones")
    total_orders: int = Field(..., ge=0, description="Total órdenes procesadas")
    total_vendors: int = Field(..., ge=0, description="Total vendors activos")

    # Métricas por estado
    pending_count: int = Field(..., ge=0, description="Comisiones pendientes")
    approved_count: int = Field(..., ge=0, description="Comisiones aprobadas")
    paid_count: int = Field(..., ge=0, description="Comisiones pagadas")
    disputed_count: int = Field(..., ge=0, description="Comisiones en disputa")

    # Métricas de tiempo
    avg_approval_time_days: Decimal = Field(
        ...,
        ge=0,
        description="Tiempo promedio de aprobación en días"
    )
    avg_payment_time_days: Decimal = Field(
        ...,
        ge=0,
        description="Tiempo promedio de pago en días"
    )

    # Metadata
    period: str = Field(..., description="Período del resumen")
    generated_at: datetime = Field(..., description="Fecha de generación")
    currency: str = Field(default="COP", description="Moneda de los montos")

    @computed_field
    @property
    def average_commission_value(self) -> Decimal:
        """Valor promedio por comisión"""
        if self.total_orders == 0:
            return Decimal('0.00')
        return Decimal(str(self.total_revenue / self.total_orders)).quantize(Decimal('0.01'))


class CommissionApproval(BaseModel):
    """Schema para aprobación de comisiones"""

    commission_ids: List[UUID] = Field(
        ...,
        min_length=1,
        description="Lista de IDs de comisiones a aprobar"
    )
    admin_notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Notas del administrador"
    )

    @field_validator('commission_ids')
    @classmethod
    def validate_commission_ids(cls, v: List[UUID]) -> List[UUID]:
        """Validar que no se repitan IDs"""
        if len(v) != len(set(v)):
            raise ValueError('Commission IDs must be unique')
        return v


class CommissionFilters(BaseModel):
    """Schema para filtros de búsqueda de comisiones"""

    vendor_id: Optional[UUID] = Field(None, description="Filtrar por vendor")
    status: Optional[CommissionStatus] = Field(None, description="Filtrar por estado")
    commission_type: Optional[CommissionType] = Field(None, description="Filtrar por tipo")

    date_from: Optional[date] = Field(None, description="Fecha inicio")
    date_to: Optional[date] = Field(None, description="Fecha fin")

    min_amount: Optional[Decimal] = Field(None, ge=0, description="Monto mínimo")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="Monto máximo")

    order_id: Optional[int] = Field(None, gt=0, description="Filtrar por orden específica")

    limit: int = Field(default=50, ge=1, le=500, description="Límite de resultados")
    offset: int = Field(default=0, ge=0, description="Offset para paginación")

    @field_validator('date_to')
    @classmethod
    def validate_date_range(cls, v: Optional[date], info) -> Optional[date]:
        """Validar que date_to sea posterior a date_from"""
        if v and 'date_from' in info.data and info.data['date_from']:
            if v < info.data['date_from']:
                raise ValueError('date_to must be after date_from')
        return v

    @field_validator('max_amount')
    @classmethod
    def validate_amount_range(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Validar que max_amount sea mayor a min_amount"""
        if v and 'min_amount' in info.data and info.data['min_amount']:
            if v < info.data['min_amount']:
                raise ValueError('max_amount must be greater than min_amount')
        return v


# Schemas de respuesta para APIs
class CommissionListResponse(BaseModel):
    """Schema de respuesta para lista de comisiones"""

    commissions: List[CommissionRead] = Field(..., description="Lista de comisiones")
    total: int = Field(..., ge=0, description="Total de registros")
    page: int = Field(..., ge=1, description="Página actual")
    pages: int = Field(..., ge=1, description="Total de páginas")
    has_next: bool = Field(..., description="Existe página siguiente")
    has_prev: bool = Field(..., description="Existe página anterior")


class CommissionResponse(BaseModel):
    """Schema de respuesta estándar para operaciones de comisión"""

    success: bool = Field(..., description="Éxito de la operación")
    message: str = Field(..., description="Mensaje descriptivo")
    commission: Optional[CommissionRead] = Field(None, description="Datos de la comisión")
    error_code: Optional[str] = Field(None, description="Código de error específico")