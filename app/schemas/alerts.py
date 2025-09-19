# ~/app/schemas/alerts.py
# ---------------------------------------------------------------------------------------------
# MeStore - Alerts Pydantic Schemas
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: alerts.py
# Ruta: ~/app/schemas/alerts.py
# Autor: Jairo

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class StockAlert(BaseModel):
    """Schema para alertas de stock bajo"""

    producto_id: int = Field(..., description="ID del producto")
    nombre_producto: str = Field(..., description="Nombre del producto")
    stock_actual: int = Field(..., ge=0, description="Stock actual del producto")
    umbral_minimo: int = Field(..., ge=0, description="Umbral mínimo configurado")
    tipo_alerta: str = Field(default="stock_bajo", description="Tipo de alerta")

    class Config:
        from_attributes = True


class ProductoSinMovimiento(BaseModel):
    """Schema para productos sin movimiento"""

    producto_id: int = Field(..., description="ID del producto")
    nombre_producto: str = Field(..., description="Nombre del producto")
    dias_sin_movimiento: int = Field(..., ge=0, description="Días sin movimiento")
    ultima_actualizacion: Optional[datetime] = Field(
        None, description="Última actualización"
    )
    tipo_alerta: str = Field(default="sin_movimiento", description="Tipo de alerta")

    class Config:
        from_attributes = True


class AlertConfig(BaseModel):
    """Schema para configuración de alertas"""

    umbral_stock_bajo: int = Field(
        default=10, ge=0, description="Umbral para stock bajo"
    )
    dias_sin_movimiento: int = Field(
        default=30, ge=1, description="Días para considerar producto sin movimiento"
    )

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    """Schema para respuesta completa de alertas"""

    alertas_stock_bajo: List[StockAlert] = Field(default_factory=list)
    productos_sin_movimiento: List[ProductoSinMovimiento] = Field(default_factory=list)
    total_alertas: int = Field(..., description="Total de alertas generadas")
    configuracion: AlertConfig = Field(..., description="Configuración utilizada")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Timestamp de generación"
    )

    class Config:
        from_attributes = True


class AlertDashboard(BaseModel):
    """Schema para dashboard de alertas"""

    resumen_stock_bajo: int = Field(
        ..., description="Cantidad de productos con stock bajo"
    )
    resumen_sin_movimiento: int = Field(
        ..., description="Cantidad de productos sin movimiento"
    )
    productos_criticos: int = Field(..., description="Productos con ambos problemas")
    alertas_detalladas: AlertResponse = Field(..., description="Alertas detalladas")

    class Config:
        from_attributes = True
