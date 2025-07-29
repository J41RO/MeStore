# ~/tests/schemas/test_financial_reports.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests para Schemas de Reportes Financieros
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""Tests para schemas de reportes financieros"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from uuid import uuid4

from app.schemas.financial_reports import (
    MetricaVentas,
    MetricaComisiones,
    ReporteVendedor,
    DashboardFinanciero,
    AnalyticsTransacciones,
    ExportacionReporte
)
from app.models.transaction import EstadoTransaccion, TransactionType, MetodoPago


class TestSchemasFinancieros:
    """Test suite para schemas financieros"""

    def test_metrica_ventas_schema(self):
        """Test schema MetricaVentas"""
        data = {
            "periodo": "2025-01",
            "total_ventas": Decimal("1000000.00"),
            "cantidad_transacciones": 150,
            "ticket_promedio": Decimal("6666.67")
        }
        metrica = MetricaVentas(**data)
        assert metrica.total_ventas == Decimal("1000000.00")
        assert metrica.cantidad_transacciones == 150
        assert metrica.periodo == "2025-01"

    def test_metrica_comisiones_schema(self):
        """Test schema MetricaComisiones"""
        data = {
            "periodo": "2025-Q1",
            "total_comisiones": Decimal("50000.00"),
            "porcentaje_promedio": Decimal("5.00"),
            "monto_vendedores": Decimal("950000.00")
        }
        metrica = MetricaComisiones(**data)
        assert metrica.total_comisiones == Decimal("50000.00")
        assert metrica.porcentaje_promedio == Decimal("5.00")

    def test_reporte_vendedor_schema(self):
        """Test schema ReporteVendedor"""
        vendedor_id = uuid4()
        data = {
            "vendedor_id": vendedor_id,
            "periodo_inicio": date(2025, 1, 1),
            "periodo_fin": date(2025, 1, 31),
            "total_ventas": Decimal("500000.00"),
            "cantidad_productos": 25,
            "transacciones_completadas": 23,
            "comisiones_pagadas": Decimal("25000.00"),
            "ingresos_netos": Decimal("475000.00"),
            "porcentaje_comision_promedio": Decimal("5.00")
        }
        reporte = ReporteVendedor(**data)
        assert reporte.vendedor_id == vendedor_id
        assert reporte.total_ventas == Decimal("500000.00")
        assert reporte.cantidad_productos == 25

    def test_dashboard_financiero_schema(self):
        """Test schema DashboardFinanciero"""
        vendedor_id = uuid4()
        reporte_vendedor = ReporteVendedor(
            vendedor_id=vendedor_id,
            periodo_inicio=date(2025, 1, 1),
            periodo_fin=date(2025, 1, 31),
            total_ventas=Decimal("500000.00"),
            cantidad_productos=25,
            transacciones_completadas=23,
            comisiones_pagadas=Decimal("25000.00"),
            ingresos_netos=Decimal("475000.00"),
            porcentaje_comision_promedio=Decimal("5.00")
        )

        metrica_ventas = MetricaVentas(
            periodo="2025-01-15",
            total_ventas=Decimal("100000.00"),
            cantidad_transacciones=10,
            ticket_promedio=Decimal("10000.00")
        )

        data = {
            "fecha_generacion": datetime(2025, 1, 31, 12, 0, 0),
            "ventas_totales": Decimal("2000000.00"),
            "comisiones_totales": Decimal("100000.00"),
            "transacciones_activas": 45,
            "distribucion_metodos_pago": {
                "EFECTIVO": Decimal("800000.00"),
                "TARJETA_CREDITO": Decimal("1200000.00")
            },
            "top_vendedores": [reporte_vendedor],
            "ventas_por_dia": [metrica_ventas]
        }

        dashboard = DashboardFinanciero(**data)
        assert dashboard.ventas_totales == Decimal("2000000.00")
        assert len(dashboard.top_vendedores) == 1
        assert len(dashboard.ventas_por_dia) == 1

    def test_analytics_transacciones_schema(self):
        """Test schema AnalyticsTransacciones"""
        data = {
            "transacciones_por_estado": {
                EstadoTransaccion.COMPLETADA: 100,
                EstadoTransaccion.PENDIENTE: 15,
                EstadoTransaccion.FALLIDA: 5
            },
            "transacciones_por_tipo": {
                TransactionType.VENTA: 110,
                TransactionType.COMISION: 110,
                TransactionType.DEVOLUCION: 5
            },
            "tiempo_promedio_procesamiento": 2.5,
            "tasa_exitosas": 83.33,
            "principales_causas_falla": [
                "Fondos insuficientes",
                "Tarjeta vencida",
                "Error de conectividad"
            ]
        }

        analytics = AnalyticsTransacciones(**data)
        assert analytics.tiempo_promedio_procesamiento == 2.5
        assert analytics.tasa_exitosas == 83.33
        assert len(analytics.principales_causas_falla) == 3

    def test_exportacion_reporte_schema(self):
        """Test schema ExportacionReporte"""
        data = {
            "tipo_reporte": "ventas_mensuales",
            "formato": "excel",
            "fecha_inicio": date(2025, 1, 1),
            "fecha_fin": date(2025, 1, 31),
            "filtros": {
                "vendedor_id": str(uuid4()),
                "min_monto": 100000
            }
        }

        exportacion = ExportacionReporte(**data)
        assert exportacion.tipo_reporte == "ventas_mensuales"
        assert exportacion.formato == "excel"
        assert exportacion.filtros["min_monto"] == 100000

    def test_exportacion_reporte_sin_filtros(self):
        """Test ExportacionReporte sin filtros opcionales"""
        data = {
            "tipo_reporte": "comisiones_diarias",
            "formato": "pdf",
            "fecha_inicio": date(2025, 1, 1),
            "fecha_fin": date(2025, 1, 31)
        }

        exportacion = ExportacionReporte(**data)
        assert exportacion.filtros is None
        assert exportacion.formato == "pdf"


class TestValidacionesCamposFinancieros:
    """Tests específicos para validaciones de campos financieros"""

    def test_campos_decimales_precision(self):
        """Test precisión de campos decimales"""
        data = {
            "periodo": "test",
            "total_ventas": Decimal("999999.99"),
            "cantidad_transacciones": 1,
            "ticket_promedio": Decimal("999999.99")
        }

        metrica = MetricaVentas(**data)
        assert metrica.total_ventas == Decimal("999999.99")

    def test_campos_obligatorios_metrica_ventas(self):
        """Test campos obligatorios en MetricaVentas"""
        with pytest.raises(ValueError):
            MetricaVentas(
                periodo="test",
                total_ventas=Decimal("1000.00"),
                cantidad_transacciones=1
                # ticket_promedio faltante
            )

    def test_formatos_fecha_exportacion(self):
        """Test formatos de fecha en ExportacionReporte"""
        data = {
            "tipo_reporte": "test",
            "formato": "csv",
            "fecha_inicio": date(2025, 1, 1),
            "fecha_fin": date(2025, 1, 31)
        }

        exportacion = ExportacionReporte(**data)
        assert isinstance(exportacion.fecha_inicio, date)
        assert isinstance(exportacion.fecha_fin, date)