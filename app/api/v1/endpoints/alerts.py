# ~/app/api/v1/endpoints/alerts.py
# ---------------------------------------------------------------------------------------------
# MeStore - Alerts API Endpoints
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.product import Product
from app.schemas.alerts import (
    AlertConfig,
    AlertDashboard,
    AlertResponse,
    ProductoSinMovimiento,
    StockAlert,
)

router = APIRouter()


@router.get("/stock-bajo", response_model=List[StockAlert])
async def get_productos_stock_bajo(
    umbral: int = Query(default=10, ge=0, description="Umbral mínimo de stock"),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener productos con stock bajo según umbral configurado.
    """
    try:
        # Obtener productos con stock bajo
        productos_bajo_stock = Product.get_low_stock_products(db, umbral)

        alertas = []
        for producto in productos_bajo_stock:
            stock_actual = producto.get_stock_total()
            alerta = StockAlert(
                producto_id=producto.id,
                nombre_producto=producto.name,
                stock_actual=stock_actual,
                umbral_minimo=umbral,
                tipo_alerta="stock_bajo",
            )
            alertas.append(alerta)

        return alertas

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener productos con stock bajo: {str(e)}",
        )


@router.get("/sin-movimiento", response_model=List[ProductoSinMovimiento])
async def get_productos_sin_movimiento(
    dias: int = Query(default=30, ge=1, description="Días sin movimiento"),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener productos sin movimiento en el período especificado.
    """
    try:
        # Obtener productos sin movimiento
        productos_inactivos = Product.get_inactive_products(db, dias)

        alertas = []
        for producto in productos_inactivos:
            dias_sin_movimiento = producto.days_since_last_movement()
            alerta = ProductoSinMovimiento(
                producto_id=producto.id,
                nombre_producto=producto.name,
                dias_sin_movimiento=dias_sin_movimiento,
                ultima_actualizacion=producto.updated_at,
                tipo_alerta="sin_movimiento",
            )
            alertas.append(alerta)

        return alertas

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener productos sin movimiento: {str(e)}",
        )


@router.get("/dashboard", response_model=AlertDashboard)
async def get_dashboard_alertas(
    umbral_stock: int = Query(default=10, ge=0, description="Umbral para stock bajo"),
    dias_inactividad: int = Query(
        default=30, ge=1, description="Días para considerar sin movimiento"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener dashboard completo de alertas con resumen y detalles.
    """
    try:
        # Configuración
        config = AlertConfig(
            umbral_stock_bajo=umbral_stock, dias_sin_movimiento=dias_inactividad
        )

        # Obtener alertas de stock bajo
        productos_bajo_stock = Product.get_low_stock_products(db, umbral_stock)
        alertas_stock_bajo = []
        for producto in productos_bajo_stock:
            stock_actual = producto.get_stock_total()
            alerta = StockAlert(
                producto_id=producto.id,
                nombre_producto=producto.name,
                stock_actual=stock_actual,
                umbral_minimo=umbral_stock,
                tipo_alerta="stock_bajo",
            )
            alertas_stock_bajo.append(alerta)

        # Obtener productos sin movimiento
        productos_inactivos = Product.get_inactive_products(db, dias_inactividad)
        productos_sin_movimiento = []
        for producto in productos_inactivos:
            dias_sin_movimiento = producto.days_since_last_movement()
            alerta = ProductoSinMovimiento(
                producto_id=producto.id,
                nombre_producto=producto.name,
                dias_sin_movimiento=dias_sin_movimiento,
                ultima_actualizacion=producto.updated_at,
                tipo_alerta="sin_movimiento",
            )
            productos_sin_movimiento.append(alerta)

        # Calcular productos críticos (ambos problemas)
        ids_stock_bajo = {alerta.producto_id for alerta in alertas_stock_bajo}
        ids_sin_movimiento = {alerta.producto_id for alerta in productos_sin_movimiento}
        productos_criticos = len(ids_stock_bajo.intersection(ids_sin_movimiento))

        # Crear respuesta de alertas
        alertas_detalladas = AlertResponse(
            alertas_stock_bajo=alertas_stock_bajo,
            productos_sin_movimiento=productos_sin_movimiento,
            total_alertas=len(alertas_stock_bajo) + len(productos_sin_movimiento),
            configuracion=config,
            timestamp=datetime.now(),
        )

        # Crear dashboard
        dashboard = AlertDashboard(
            resumen_stock_bajo=len(alertas_stock_bajo),
            resumen_sin_movimiento=len(productos_sin_movimiento),
            productos_criticos=productos_criticos,
            alertas_detalladas=alertas_detalladas,
        )

        return dashboard

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar dashboard de alertas: {str(e)}",
        )
