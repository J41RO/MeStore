# ~/app/schemas/financial_reports.py
# ---------------------------------------------------------------------------------------------
# MeStore - Schemas de Reportes Financieros
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: financial_reports.py
# Ruta: ~/app/schemas/financial_reports.py
# Autor: Jairo
# Fecha de Creación: 2025-07-29
# Última Actualización: 2025-07-29
# Versión: 1.0.0
# Propósito: Esquemas Pydantic para Reportes Financieros del marketplace
#            - Métricas de ventas y comisiones
#            - Dashboard financiero ejecutivo
#            - Analytics de transacciones
#
# Modificaciones:
# 2025-07-29 - Implementación inicial con schemas completos
#
# ---------------------------------------------------------------------------------------------

"""
Esquemas Pydantic para Reportes Financieros
- Métricas de ventas
- Reportes de comisiones
- Dashboard financiero
- Analytics de transacciones
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.transaction import EstadoTransaccion, MetodoPago, TransactionType


# Schemas para métricas básicas
class MetricaVentas(BaseModel):
    """Métrica individual de ventas"""

    periodo: str = Field(..., description="Período (día, semana, mes, año)")
    total_ventas: Decimal = Field(..., description="Total vendido en COP")
    cantidad_transacciones: int = Field(..., description="Número de transacciones")
    ticket_promedio: Decimal = Field(..., description="Valor promedio por transacción")


class MetricaComisiones(BaseModel):
    """Métrica de comisiones MeStore"""

    periodo: str = Field(..., description="Período del reporte")
    total_comisiones: Decimal = Field(..., description="Total comisiones generadas")
    porcentaje_promedio: Decimal = Field(
        ..., description="Porcentaje promedio aplicado"
    )
    monto_vendedores: Decimal = Field(..., description="Total pagado a vendedores")


# Schemas para reportes por vendedor
class ReporteVendedor(BaseModel):
    """Reporte financiero individual por vendedor"""

    vendedor_id: UUID = Field(..., description="ID del vendedor")
    periodo_inicio: date = Field(..., description="Fecha inicio del período")
    periodo_fin: date = Field(..., description="Fecha fin del período")

    # Métricas de ventas
    total_ventas: Decimal = Field(..., description="Total vendido")
    cantidad_productos: int = Field(..., description="Productos vendidos")
    transacciones_completadas: int = Field(..., description="Transacciones exitosas")

    # Métricas financieras
    comisiones_pagadas: Decimal = Field(..., description="Comisiones pagadas a MeStore")
    ingresos_netos: Decimal = Field(..., description="Ingresos después de comisiones")
    porcentaje_comision_promedio: Decimal = Field(
        ..., description="% comisión promedio"
    )


# Schemas para dashboard ejecutivo
class DashboardFinanciero(BaseModel):
    """Dashboard financiero completo"""

    fecha_generacion: datetime = Field(
        ..., description="Fecha de generación del reporte"
    )

    # Métricas generales
    ventas_totales: Decimal = Field(..., description="Ventas totales del período")
    comisiones_totales: Decimal = Field(..., description="Comisiones totales generadas")
    transacciones_activas: int = Field(..., description="Transacciones en proceso")

    # Distribución por métodos de pago
    distribucion_metodos_pago: Dict[str, Decimal] = Field(
        ..., description="Ventas por método de pago"
    )

    # Top vendedores
    top_vendedores: List[ReporteVendedor] = Field(
        ..., description="Top 10 vendedores del período"
    )

    # Tendencias
    ventas_por_dia: List[MetricaVentas] = Field(
        ..., description="Ventas diarias del período"
    )


# Schemas para analytics avanzados
class AnalyticsTransacciones(BaseModel):
    """Analytics avanzados de transacciones"""

    # Distribución por estados
    transacciones_por_estado: Dict[EstadoTransaccion, int] = Field(
        ..., description="Cantidad por estado"
    )

    # Distribución por tipos
    transacciones_por_tipo: Dict[TransactionType, int] = Field(
        ..., description="Cantidad por tipo"
    )

    # Métricas de rendimiento
    tiempo_promedio_procesamiento: float = Field(
        ..., description="Tiempo promedio en horas"
    )

    tasa_exitosas: float = Field(
        ..., description="Porcentaje de transacciones exitosas"
    )

    # Análisis de fallas
    principales_causas_falla: List[str] = Field(
        ..., description="Top causas de transacciones fallidas"
    )


# Schema para exportación de reportes
class ExportacionReporte(BaseModel):
    """Schema para solicitudes de exportación"""

    tipo_reporte: str = Field(..., description="Tipo de reporte a exportar")
    formato: str = Field(..., description="Formato: excel, pdf, csv")
    fecha_inicio: date = Field(..., description="Fecha inicio del período")
    fecha_fin: date = Field(..., description="Fecha fin del período")
    filtros: Optional[Dict[str, Any]] = Field(None, description="Filtros adicionales")


class ComisionBreakdown(BaseModel):
    """Schema para breakdown detallado de comisiones de una transacción."""

    transaction_id: UUID = Field(..., description="ID de la transacción")
    monto_total: Decimal = Field(..., description="Monto total de la transacción")
    porcentaje_comision: Decimal = Field(
        ..., description="Porcentaje de comisión aplicado"
    )
    monto_comision: Decimal = Field(..., description="Monto de comisión para MeStore")
    monto_vendedor: Decimal = Field(..., description="Monto que recibe el vendedor")
    fecha_transaccion: datetime = Field(..., description="Fecha de la transacción")
