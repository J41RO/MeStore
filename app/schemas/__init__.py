# ~/app/schemas/__init__.py
# ---------------------------------------------------------------------------------------------
# MeStore - Schemas Package Exports
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------
"""
Schemas package for MeStore application.
Exports all Pydantic schemas for API validation and serialization.
Organized by domain: User schemas, Product schemas, Inventory schemas, etc.
"""

# User schemas
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserRead,
    UserResponse,
)

# Product schemas
from .product import (
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductRead,
    ProductResponse,
)

# Inventory schemas
from .inventory import (
    InventoryBase,
    InventoryCreate,
    InventoryUpdate,
    InventoryRead,
    InventoryResponse,
    MovimientoStockBase,
    MovimientoStockCreate,
    MovimientoStockRead,
    TipoMovimiento,
)
# Financial reports schemas
from .financial_reports import (
    MetricaVentas,
    MetricaComisiones,
    ReporteVendedor,
    DashboardFinanciero,
    AnalyticsTransacciones,
    ExportacionReporte,
)

# Export all schemas for easy importing
__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserRead",
    "UserResponse",
    # Product schemas
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductRead",
    "ProductResponse",
    # Inventory schemas
    "InventoryBase",
    "InventoryCreate",
    "InventoryUpdate",
    "InventoryRead",
    "InventoryResponse",
    "MovimientoStockBase",
    "MovimientoStockCreate",
    "MovimientoStockRead",
    "TipoMovimiento",
    # Transaction schemas
    "TransactionBase",
    "TransactionCreate",
    "TransactionUpdate",
    "TransactionRead",
    "TransactionResponse",
    "TransactionType",
    "MetodoPago",
    "EstadoTransaccion",
    # Financial reports schemas
    "MetricaVentas",
    "MetricaComisiones", 
    "ReporteVendedor",
    "DashboardFinanciero",
    "AnalyticsTransacciones",
    "ExportacionReporte",
]

# Transaction schemas
from .transaction import (

# Financial reports schemas
    TransactionBase,
    TransactionCreate,
    TransactionUpdate,
    TransactionRead,
    TransactionResponse,
    TransactionType,
    MetodoPago,
    EstadoTransaccion
)