from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from .vendedor import TendenciaKPI


class GlobalKPIs(BaseModel):
    """Schema para KPIs globales de la plataforma"""
    gmv_total: float = Field(..., description="Gross Merchandise Value total")
    vendedores_activos: int = Field(..., description="Número de vendedores activos")
    total_productos: int = Field(..., description="Total de productos en la plataforma")
    total_ordenes: int = Field(..., description="Total de órdenes/transacciones")
    fecha_calculo: datetime = Field(default_factory=datetime.now, description="Fecha de cálculo de métricas")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PeriodMetrics(BaseModel):
    """Schema para métricas con comparación temporal"""
    periodo_actual: GlobalKPIs = Field(..., description="Métricas del período actual")
    periodo_anterior: Optional[GlobalKPIs] = Field(None, description="Métricas del período anterior")
    tendencia_gmv: Optional[TendenciaKPI] = Field(None, description="Tendencia del GMV")
    tendencia_vendedores: Optional[TendenciaKPI] = Field(None, description="Tendencia de vendedores activos")
    tendencia_productos: Optional[TendenciaKPI] = Field(None, description="Tendencia de productos")
    tendencia_ordenes: Optional[TendenciaKPI] = Field(None, description="Tendencia de órdenes")


class AdminDashboardResponse(BaseModel):
    """Schema de respuesta completa para dashboard administrativo"""
    kpis_globales: GlobalKPIs = Field(..., description="KPIs globales actuales")
    metricas_periodo: Optional[PeriodMetrics] = Field(None, description="Métricas con comparación temporal")
    ultimo_update: datetime = Field(default_factory=datetime.now, description="Última actualización de datos")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }