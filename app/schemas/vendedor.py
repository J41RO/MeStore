# ~/app/schemas/vendedor.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Schema Vendedor Especializado
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: vendedor.py
# Ruta: ~/app/schemas/vendedor.py
# Autor: Jairo
# Fecha de Creación: 2025-07-31
# Última Actualización: 2025-07-31
# Versión: 1.0.0
# Propósito: Schemas específicos para registro y gestión de vendedores
#            con validaciones obligatorias colombianas
#
# Modificaciones:
# 2025-07-31 - Creación inicial con herencia de UserCreate
#
# ---------------------------------------------------------------------------------------------

"""
Schemas específicos para vendedores en MeStore.

Este módulo contiene schemas especializados para:
- Registro de vendedores con campos obligatorios
- Validaciones específicas colombianas
- Response schemas optimizados para vendedores
- Dashboard y estadísticas de vendedores
"""

from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserType
from app.schemas.user import UserCreate, UserRead
from app.utils.validators import validate_celular_colombiano


# =============================================================================
# SCHEMAS DE REGISTRO Y AUTENTICACIÓN
# =============================================================================

class VendedorCreate(UserCreate):
    """
    Schema para registro específico de vendedores.

    Hereda de UserCreate pero hace obligatorios:
    - cedula: Cédula colombiana (obligatoria para vendedores)
    - telefono: Teléfono colombiano (obligatorio para vendedores)
    - nombre: Nombre completo (obligatorio)
    - apellido: Apellido completo (obligatorio)

    El user_type se asigna automáticamente como VENDEDOR.
    """

    # Campos obligatorios para vendedores (override de UserCreate)
    cedula: str = Field(
        ..., description="Cédula de ciudadanía colombiana (obligatoria para vendedores)"
    )
    telefono: str = Field(
        ..., description="Número de teléfono colombiano (obligatorio para vendedores)"
    )
    nombre: str = Field(
        ..., min_length=2, max_length=50, description="Nombre completo (obligatorio)"
    )
    apellido: str = Field(
        ..., min_length=2, max_length=50, description="Apellido completo (obligatorio)"
    )

    # Campo automático - no enviado por cliente
    user_type: UserType = Field(
        default=UserType.VENDEDOR, description="Tipo fijo: VENDEDOR"
    )

    @field_validator("telefono")
    @classmethod
    def validate_telefono_celular(cls, v):
        """
        Validar que el teléfono sea ESPECÍFICAMENTE un celular colombiano.

        Los vendedores requieren números celulares para mayor contactabilidad.
        No se permiten teléfonos fijos.
        """
        return validate_celular_colombiano(v)

    class Config(UserCreate.Config):
        json_schema_extra = {
            "example": {
                "email": "juan.vendedor@email.com",
                "password": "MiPassword123",
                "nombre": "Juan Carlos",
                "apellido": "Pérez García",
                "cedula": "12345678",
                "telefono": "+57 300 123 4567",
                "ciudad": "Bogotá",
                "empresa": "Mi Tienda SAS",
                "direccion": "Calle 123 #45-67, Bogotá",
            }
        }


class VendedorResponse(BaseModel):
    """
    Schema de respuesta para registro exitoso de vendedor.

    Incluye datos relevantes del vendedor registrado,
    excluyendo información sensible como password_hash.
    """

    success: bool = Field(True, description="Indicador de éxito del registro")
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    vendedor: UserRead = Field(..., description="Datos del vendedor registrado")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Vendedor registrado exitosamente",
                "vendedor": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "juan.vendedor@email.com",
                    "nombre": "Juan Carlos",
                    "apellido": "Pérez García",
                    "user_type": "VENDEDOR",
                    "cedula": "12345678",
                    "telefono": "+57 300 123 4567",
                    "ciudad": "Bogotá",
                    "empresa": "Mi Tienda SAS",
                    "is_active": True,
                    "is_verified": False,
                    "created_at": "2025-07-30T20:30:00Z",
                },
            }
        }


class VendedorErrorResponse(BaseModel):
    """Schema para respuestas de error específicas de vendedores."""

    error: str = Field(..., description="Mensaje de error")
    details: Optional[str] = Field(None, description="Detalles adicionales del error")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Email ya registrado",
                "details": "Un vendedor con este email ya existe",
            }
        }


class VendedorLogin(BaseModel):
    """Schema para login específico de vendedores."""

    email: EmailStr = Field(..., description="Email del vendedor")
    password: str = Field(..., min_length=6, description="Contraseña del vendedor")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "vendedor@empresa.com",
                "password": "mi_password_seguro",
            }
        }


# =============================================================================
# SCHEMAS DE DASHBOARD Y ESTADÍSTICAS
# =============================================================================

class VendedorDashboardResumen(BaseModel):
    """Schema para el resumen del dashboard del vendedor."""
    
    total_productos: int = Field(0, description="Total de productos del vendedor")
    productos_activos: int = Field(0, description="Productos publicados y activos")
    ventas_mes: int = Field(0, description="Ventas realizadas este mes")
    ingresos_mes: Decimal = Field(Decimal("0.0"), description="Ingresos generados este mes")
    comision_total: Decimal = Field(Decimal("0.0"), description="Comisión total acumulada")
    estadisticas_mes: Optional[str] = Field(None, description="Resumen estadísticas del mes")


# =============================================================================
# SCHEMAS DE GRÁFICOS DE VENTAS
# =============================================================================

class PeriodoVentas(str, Enum):
    """Enum para tipos de período de análisis de ventas."""
    DIARIO = "diario"
    SEMANAL = "semanal"
    MENSUAL = "mensual"


class VentasPorPeriodo(BaseModel):
    """Schema para datos de ventas agrupados por período."""
    
    periodo: str = Field(..., description="Etiqueta del período (ej: '2025-08', 'Semana 32')")
    ventas_cantidad: int = Field(0, description="Número de ventas en el período")
    ventas_monto: Decimal = Field(Decimal("0.0"), description="Monto total vendido")


class DashboardVentasResponse(BaseModel):
    """Schema de respuesta para el dashboard de ventas por período."""
    
    periodo_solicitado: PeriodoVentas = Field(..., description="Tipo de período solicitado")
    datos_grafico: List[VentasPorPeriodo] = Field(default_factory=list, description="Datos para el gráfico")
    total_ventas: Decimal = Field(Decimal("0.0"), description="Total de ventas en todos los períodos")
    total_transacciones: int = Field(0, description="Total de transacciones")
    ventas_totales: Decimal = Field(Decimal("0.0"), description="Total de ventas (alias)")
    pedidos_pendientes: int = Field(0, description="Pedidos pendientes de procesar")
    productos_activos: int = Field(0, description="Productos activos del vendedor")
    comision_total: Decimal = Field(Decimal("0.0"), description="Comisión total acumulada")


# =============================================================================
# SCHEMAS DE RANKING DE PRODUCTOS
# =============================================================================

class TipoRankingProducto(str, Enum):
    """Enum para tipos de ranking de productos."""
    VENTAS = "ventas"
    INGRESOS = "ingresos"
    POPULARIDAD = "popularidad"


class ProductoTop(BaseModel):
    """Schema para un producto en el ranking top."""
    
    sku: str = Field(..., description="SKU del producto")
    nombre: str = Field(..., description="Nombre del producto")
    ventas_cantidad: int = Field(0, description="Cantidad de unidades vendidas")
    ingresos_total: Decimal = Field(Decimal("0.0"), description="Ingresos totales generados")
    precio_venta: Decimal = Field(Decimal("0.0"), description="Precio de venta actual")
    posicion_ranking: int = Field(1, description="Posición en el ranking")


class DashboardProductosTopResponse(BaseModel):
    """Schema de respuesta para el dashboard de productos top."""
    
    tipo_ranking: TipoRankingProducto = Field(..., description="Tipo de ranking solicitado")
    productos_ranking: List[ProductoTop] = Field(default_factory=list, description="Lista de productos en ranking")
    total_productos_analizados: int = Field(0, description="Total de productos analizados para el ranking")
    periodo_analisis: str = Field("último_mes", description="Período de análisis del ranking")


from datetime import date
from enum import Enum

class EstadoComision(str, Enum):
    PENDIENTE = "pendiente"
    PAGADA = "pagada"
    RETENIDA = "retenida"

class ComisionDetalle(BaseModel):
    transaccion_id: str = Field(..., description="ID de la transacción")
    fecha_transaccion: date = Field(..., description="Fecha de la transacción")
    producto_sku: str = Field(..., description="SKU del producto vendido")
    monto_venta: Decimal = Field(..., description="Monto total de la venta")
    comision_porcentaje: Decimal = Field(..., description="Porcentaje de comisión aplicado")
    comision_monto: Decimal = Field(..., description="Monto de comisión generado")
    monto_vendedor: Decimal = Field(..., description="Monto que recibe el vendedor")
    estado: EstadoComision = Field(..., description="Estado de la comisión")

class DashboardComisionesResponse(BaseModel):
    """Schema de respuesta para el dashboard de comisiones."""
    
    comisiones_detalle: List[ComisionDetalle] = Field(default_factory=list, description="Detalle de comisiones")
    total_comisiones_generadas: Decimal = Field(Decimal("0.0"), description="Total de comisiones generadas")
    total_earnings_vendedor: Decimal = Field(Decimal("0.0"), description="Total de earnings del vendedor")
    comisiones_pendientes: Decimal = Field(Decimal("0.0"), description="Comisiones pendientes de pago")
    periodo_analisis: str = Field("último_mes", description="Período de análisis")
    """Schema de respuesta para el dashboard de productos top."""
    
    tipo_ranking: TipoRankingProducto = Field(..., description="Tipo de ranking solicitado")
    productos_ranking: List[ProductoTop] = Field(default_factory=list, description="Lista de productos en ranking")
    total_productos_analizados: int = Field(0, description="Total de productos analizados para el ranking")
    periodo_analisis: str = Field("último_mes", description="Período de análisis del ranking")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Registro y autenticación
    "VendedorCreate",
    "VendedorResponse", 
    "VendedorErrorResponse",
    "VendedorLogin",
    # Dashboard
    "VendedorDashboardResumen",
    # Ventas
    "PeriodoVentas",
    "VentasPorPeriodo",
    "DashboardVentasResponse",
    # Ranking de productos
    "TipoRankingProducto",
    "ProductoTop",
    "DashboardProductosTopResponse",
]