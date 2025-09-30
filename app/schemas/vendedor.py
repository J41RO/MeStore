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
# Última Actualización: 2025-08-07
# Versión: 1.1.0
# Propósito: Schemas específicos para registro y gestión de vendedores
#            con validaciones obligatorias colombianas y schemas de inventario
#
# Modificaciones:
# 2025-07-31 - Creación inicial con herencia de UserCreate
# 2025-08-07 - Agregados schemas de inventario y corrección de DashboardComisionesResponse
#
# ---------------------------------------------------------------------------------------------

"""
Schemas específicos para vendedores en MeStore.

Este módulo contiene schemas especializados para:
- Registro de vendedores con campos obligatorios
- Validaciones específicas colombianas
- Response schemas optimizados para vendedores
- Dashboard y estadísticas de vendedores
- Métricas de inventario y stock
"""

from datetime import date
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

from app.models.user import UserType
from app.schemas.user import UserCreate, UserRead
from app.utils.validators import validate_celular_colombiano
# Enum para tendencias de KPIs
class TendenciaKPI(str, Enum):
    """Enum para representar la tendencia de un KPI."""
    SUBIENDO = "subiendo"
    BAJANDO = "bajando"  
    ESTABLE = "estable"

# =============================================================================

# =============================================================================
# SCHEMAS DE EXPORTACIÓN  
# =============================================================================

class FormatoExport(str, Enum):
    """Formatos disponibles para exportación."""
    PDF = "pdf"
    EXCEL = "excel"


class TipoReporte(str, Enum):
    """Tipos de reportes disponibles."""
    RESUMEN = "resumen"
    VENTAS = "ventas"
    PRODUCTOS_TOP = "productos_top"
    COMISIONES = "comisiones"
    INVENTARIO = "inventario"
    COMPLETO = "completo"


class ExportRequest(BaseModel):
    """Schema para solicitud de exportación."""
    tipo_reporte: TipoReporte = Field(..., description="Tipo de reporte a exportar")
    formato: FormatoExport = Field(..., description="Formato de exportación")
    incluir_graficos: bool = Field(False, description="Incluir gráficos en el reporte")
    periodo_dias: int = Field(30, ge=1, le=365, description="Período en días para el reporte")


class ExportResponse(BaseModel):
    """Schema para respuesta de exportación."""
    success: bool = Field(..., description="Indica si la exportación fue exitosa")
    filename: str = Field(..., description="Nombre del archivo generado")
    download_url: str = Field(..., description="URL para descargar el archivo")
    file_size: int = Field(..., description="Tamaño del archivo en bytes")
    formato: FormatoExport = Field(..., description="Formato del archivo generado")
    fecha_generacion: datetime = Field(default_factory=datetime.now, description="Fecha de generación")
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
        default=UserType.VENDOR, description="Tipo fijo: VENDOR"
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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
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
    )


class VendedorResponse(BaseModel):
    """
    Schema de respuesta para registro exitoso de vendedor.

    Incluye datos relevantes del vendedor registrado,
    excluyendo información sensible como password_hash.
    """

    success: bool = Field(True, description="Indicador de éxito del registro")
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    vendedor: UserRead = Field(..., description="Datos del vendedor registrado")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Vendedor registrado exitosamente",
                "vendedor": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "juan.vendedor@email.com",
                    "nombre": "Juan Carlos",
                    "apellido": "Pérez García",
                    "user_type": "vendor",
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
    )


class VendedorErrorResponse(BaseModel):
    """Schema para respuestas de error específicas de vendedores."""

    error: str = Field(..., description="Mensaje de error")
    # Exportación
    "FormatoExport",
    "TipoReporte", 
    "ExportRequest",
    "ExportResponse",

    # VendorList
    "EstadoVendedor",
    "TipoCuentaVendedor", 
    "VendorListFilter",
    "VendorItem",
    "VendorListResponse",

    details: Optional[str] = Field(None, description="Detalles adicionales del error")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Email ya registrado",
                "details": "Un vendedor con este email ya existe",
            }
        }
    )


class VendedorLogin(BaseModel):
    """Schema para login específico de vendedores."""

    email: EmailStr = Field(..., description="Email del vendedor")
    password: str = Field(..., min_length=6, description="Contraseña del vendedor")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "vendedor@empresa.com",
                "password": "mi_password_seguro",
            }
        }
    )


# =============================================================================
# SCHEMAS DE DASHBOARD Y ESTADÍSTICAS
# =============================================================================

class VendedorDashboardResumen(BaseModel):
    """Schema para el resumen del dashboard del vendedor con estados de productos."""

    total_productos: int = Field(0, description="Total de productos del vendedor")
    productos_aprobados: int = Field(0, description="Productos aprobados y visibles en marketplace")
    productos_pendientes: int = Field(0, description="Productos pendientes de aprobación")
    productos_rechazados: int = Field(0, description="Productos rechazados por el administrador")
    productos_activos: int = Field(0, description="Productos publicados y activos (legacy)")
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


# =============================================================================
# SCHEMAS DE COMISIONES
# =============================================================================

class EstadoComision(str, Enum):
    """Estados posibles de las comisiones."""
    PENDIENTE = "pendiente"
    PAGADA = "pagada"
    RETENIDA = "retenida"


class ComisionDetalle(BaseModel):
    """Schema para detalle de comisiones individuales."""
    transaccion_id: str = Field(..., description="ID de la transacción")
    fecha_transaccion: date = Field(..., description="Fecha de la transacción")
    producto_sku: str = Field(..., description="SKU del producto vendido")
    monto_venta: Decimal = Field(..., description="Monto total de la venta")
    comision_porcentaje: Decimal = Field(..., description="Porcentaje de comisión aplicado")
    comision_monto: Decimal = Field(..., description="Monto de comisión generado")
    monto_vendedor: Decimal = Field(..., description="Monto que recibe el vendedor")
    estado: EstadoComision = Field(..., description="Estado de la comisión")


class DashboardComisionesResponse(BaseModel):
    """Schema de respuesta para el dashboard de comisiones del vendedor."""
    comisiones_detalle: List[ComisionDetalle] = Field(default_factory=list, description="Lista de comisiones detalladas")
    total_comisiones_generadas: Decimal = Field(Decimal("0.0"), description="Total de comisiones generadas")
    comisiones_pendientes: Decimal = Field(Decimal("0.0"), description="Comisiones pendientes de pago")
    comisiones_pagadas: Decimal = Field(Decimal("0.0"), description="Comisiones ya pagadas")
    comisiones_retenidas: Decimal = Field(Decimal("0.0"), description="Comisiones retenidas")
    periodo_analisis: str = Field("último_mes", description="Período de análisis de comisiones")


# =============================================================================
# SCHEMAS DE INVENTARIO
# =============================================================================

class EstadoStock(str, Enum):
    """Estados posibles del stock de inventario."""
    DISPONIBLE = "disponible"
    BAJO_STOCK = "bajo_stock"
    AGOTADO = "agotado"
    RESERVADO = "reservado"


class InventarioMetrica(BaseModel):
    """Métrica individual de inventario."""
    producto_sku: str = Field(..., description="SKU del producto")
    nombre_producto: str = Field(..., description="Nombre del producto")
    ubicacion: str = Field(..., description="Ubicación física en almacén")
    cantidad_total: int = Field(0, description="Cantidad total en stock")
    cantidad_reservada: int = Field(0, description="Cantidad reservada")
    cantidad_disponible: int = Field(0, description="Cantidad disponible para venta")
    estado_stock: EstadoStock = Field(..., description="Estado actual del stock")
    ultimo_movimiento: date = Field(..., description="Fecha del último movimiento")


class DashboardInventarioResponse(BaseModel):
    """Response schema para métricas de inventario del dashboard."""
    inventario_metricas: List[InventarioMetrica] = Field(default_factory=list, description="Métricas de inventario")
    total_productos_inventario: int = Field(0, description="Total de productos en inventario")
    productos_bajo_stock: int = Field(0, description="Productos con stock bajo")
    productos_agotados: int = Field(0, description="Productos agotados")
    total_unidades_disponibles: int = Field(0, description="Total de unidades disponibles")
    valor_inventario_estimado: Decimal = Field(Decimal("0.0"), description="Valor estimado del inventario")

# =============================================================================
# SCHEMAS COMPARATIVOS - TAREA 1.5.6.6
# =============================================================================

class KPIComparison(BaseModel):
    """Schema para comparación de KPIs entre períodos."""
    valor_actual: Decimal = Field(..., description="Valor del KPI en el período actual")
    valor_anterior: Decimal = Field(..., description="Valor del KPI en el período anterior") 
    variacion_porcentual: Decimal = Field(..., description="Variación porcentual entre períodos")
    tendencia: TendenciaKPI = Field(..., description="Tendencia del KPI basada en la variación")

    model_config = ConfigDict(
        json_encoders={
            Decimal: str
        }
    )


class DashboardComparativoResponse(BaseModel):
    """Schema para respuesta del dashboard comparativo con KPIs de períodos."""
    ventas_mes: KPIComparison = Field(..., description="Comparativa de ventas mensuales")
    ingresos_mes: KPIComparison = Field(..., description="Comparativa de ingresos mensuales") 
    comision_total: KPIComparison = Field(..., description="Comparativa de comisiones totales")
    productos_vendidos: KPIComparison = Field(..., description="Comparativa de productos vendidos")
    clientes_nuevos: KPIComparison = Field(..., description="Comparativa de clientes nuevos")
    
    # Metadatos del período
    periodo_actual: str = Field(..., description="Descripción del período actual (ej: 'Enero 2025')")
    periodo_anterior: str = Field(..., description="Descripción del período anterior (ej: 'Diciembre 2024')")
    fecha_calculo: datetime = Field(..., description="Timestamp del cálculo de la comparativa")

    model_config = ConfigDict(
        json_encoders={
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
    )
# =============================================================================
# EXPORTS
# =============================================================================


# ============================================================================
# VENDORLIST - Schemas para listado y filtrado de vendedores
# ============================================================================

class EstadoVendedor(str, Enum):
    """Estados posibles para vendedores."""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    SUSPENDIDO = "suspendido"
    PENDIENTE = "pendiente"

class TipoCuentaVendedor(str, Enum):
    """Tipos de cuenta para vendedores."""
    BASICA = "basica"
    PREMIUM = "premium"
    EMPRESARIAL = "empresarial"
    VIP = "vip"

class VendorListFilter(BaseModel):
    """Filtros para listado de vendedores."""
    estado: Optional[EstadoVendedor] = Field(None, description="Filtrar por estado del vendedor")
    tipo_cuenta: Optional[TipoCuentaVendedor] = Field(None, description="Filtrar por tipo de cuenta")
    limit: int = Field(20, ge=1, le=100, description="Número máximo de resultados")
    offset: int = Field(0, ge=0, description="Número de resultados a saltar")

class VendorItem(BaseModel):
    """Item individual de vendedor para listado."""
    id: int = Field(..., description="ID único del vendedor")
    email: EmailStr = Field(..., description="Email del vendedor")
    nombre_completo: Optional[str] = Field(None, description="Nombre completo del vendedor")
    estado: EstadoVendedor = Field(..., description="Estado actual del vendedor")
    tipo_cuenta: TipoCuentaVendedor = Field(..., description="Tipo de cuenta del vendedor")
    fecha_registro: datetime = Field(..., description="Fecha de registro del vendedor")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class VendorListResponse(BaseModel):
    """Respuesta del listado de vendedores."""
    vendedores: List[VendorItem] = Field(..., description="Lista de vendedores")
    total: int = Field(..., description="Total de vendedores que cumplen los filtros")
    limit: int = Field(..., description="Límite aplicado")
    offset: int = Field(..., description="Número de offset aplicado")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )



# Schemas para workflow de aprobación
class ApproveVendorRequest(BaseModel):
    """Schema para solicitud de aprobación de vendedor"""
    reason: Optional[str] = Field(
        None,
        description="Razón opcional para la aprobación",
        max_length=500
    )

class RejectVendorRequest(BaseModel):
    """Schema para solicitud de rechazo de vendedor"""
    rejection_reason: str = Field(
        ...,
        description="Razón obligatoria para el rechazo",
        min_length=5,
        max_length=500
    )

class ApprovalResponse(BaseModel):
    """Schema para respuesta de acciones de aprobación/rechazo"""
    status: str = Field(..., description="Estado de la operación")
    message: str = Field(..., description="Mensaje descriptivo")
    vendedor_id: str = Field(..., description="ID del vendedor procesado")
    approved_by: Optional[str] = Field(None, description="ID del admin que aprobó")
    rejected_by: Optional[str] = Field(None, description="ID del admin que rechazó")
    reason: Optional[str] = Field(None, description="Razón de aprobación")
    rejection_reason: Optional[str] = Field(None, description="Razón de rechazo")


__all__ = [
    # Notas internas y auditoría
    "VendorNoteCreate",
    "VendorNoteResponse",
    "AuditLogResponse",
    "VendorNotesListResponse",
    "VendorAuditHistoryResponse",
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
    # Comisiones
    "EstadoComision",
    "ComisionDetalle",
    "DashboardComisionesResponse",
    # Inventario
    "EstadoStock",
    "InventarioMetrica",
    "DashboardInventarioResponse",
    # Workflow de aprobación
    "ApproveVendorRequest",
    "RejectVendorRequest", 
    "ApprovalResponse",
]



# Schemas para acciones bulk
from typing import List
from pydantic import BaseModel, Field

class BulkActionRequest(BaseModel):
    vendor_ids: List[int] = Field(..., min_items=1, max_items=50, description='Lista de IDs de vendedores (máximo 50)')

class BulkApproveRequest(BulkActionRequest):
    pass

class BulkSuspendRequest(BulkActionRequest):
    reason: str = Field(..., min_length=5, max_length=500, description='Razón de la suspensión')

class BulkEmailRequest(BulkActionRequest):
    subject: str = Field(..., min_length=1, max_length=200, description='Asunto del email')
    message: str = Field(..., min_length=1, max_length=2000, description='Contenido del email')

class BulkActionResponse(BaseModel):
    success: bool
    success_count: int
    failed_items: List[int] = []
    message: str
    details: dict = {}


# =============================================================================
# SCHEMAS PARA NOTAS INTERNAS Y AUDITORÍA - MICRO-FASE 3
# =============================================================================

class VendorNoteCreate(BaseModel):
    """Schema para crear una nueva nota interna sobre un vendedor."""
    note_text: str = Field(
        ..., 
        min_length=5, 
        max_length=2000, 
        description="Contenido de la nota interna"
    )

class VendorNoteResponse(BaseModel):
    """Schema para respuesta de nota de vendedor."""
    id: str = Field(..., description="ID único de la nota")
    vendor_id: str = Field(..., description="ID del vendedor")
    admin_id: str = Field(..., description="ID del administrador que creó la nota")
    note_text: str = Field(..., description="Contenido de la nota")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    vendor_name: Optional[str] = Field(None, description="Nombre del vendedor")
    admin_name: Optional[str] = Field(None, description="Nombre del administrador")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class AuditLogResponse(BaseModel):
    """Schema para respuesta de log de auditoría."""
    id: str = Field(..., description="ID único del log")
    vendor_id: str = Field(..., description="ID del vendedor afectado")
    admin_id: str = Field(..., description="ID del administrador que realizó la acción")
    action_type: str = Field(..., description="Tipo de acción realizada")
    old_values: Optional[dict] = Field(None, description="Valores anteriores")
    new_values: Optional[dict] = Field(None, description="Valores nuevos")
    description: Optional[str] = Field(None, description="Descripción adicional")
    created_at: datetime = Field(..., description="Fecha de la acción")
    vendor_name: Optional[str] = Field(None, description="Nombre del vendedor")
    admin_name: Optional[str] = Field(None, description="Nombre del administrador")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class VendorNotesListResponse(BaseModel):
    """Schema para lista de notas de un vendedor."""
    vendor_id: str = Field(..., description="ID del vendedor")
    notes: List[VendorNoteResponse] = Field(default_factory=list, description="Lista de notas")
    total_notes: int = Field(0, description="Total de notas del vendedor")

class VendorAuditHistoryResponse(BaseModel):
    """Schema para historial de auditoría de un vendedor."""
    vendor_id: str = Field(..., description="ID del vendedor")
    audit_logs: List[AuditLogResponse] = Field(default_factory=list, description="Lista de logs de auditoría")
    total_logs: int = Field(0, description="Total de logs del vendedor")