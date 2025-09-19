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

# Financial reports schemas
from .financial_reports import (
    AnalyticsTransacciones,
    DashboardFinanciero,
    ExportacionReporte,
    MetricaComisiones,
    MetricaVentas,
    ReporteVendedor,
)

# Inventory schemas
from .inventory import (
    InventoryBase,
    InventoryCreate,
    InventoryRead,
    InventoryResponse,
    InventoryUpdate,
    MovimientoStockBase,
    MovimientoStockCreate,
    MovimientoStockRead,
    TipoMovimiento,
)

# Product schemas
from .product import (
    ProductBase,
    ProductCreate,
    ProductPatch,
    ProductRead,
    ProductResponse,
    ProductUpdate,
)

# Storage schemas
from .storage import (
    BillingCalculation,
    StorageBase,
    StorageBilling,
    StorageCreate,
    StorageResponse,
    StorageUpdate,
)

# Transaction schemas
from .transaction import (
    EstadoTransaccion,
    MetodoPago,
    TransactionBase,
    TransactionCreate,
    TransactionRead,
    TransactionResponse,
    TransactionType,
    TransactionUpdate,
)

# Response base schemas
from .response_base import (
    ErrorCodes,
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationInfo,
    StandardResponse,
    SuccessResponse,
    ValidationErrorResponse,
    create_error_response,
    create_paginated_response,
    create_success_response,
    create_validation_error_response,
)

# User schemas
from .user import (
    UserBase,
    UserCreate,
    UserRead,
    UserResponse,
    UserUpdate,
)

# Export all schemas for easy importing
__all__ = [
    # Response base schemas
    "ErrorCodes",
    "ErrorDetail",
    "ErrorResponse",
    "HealthResponse",
    "MessageResponse",
    "PaginatedResponse",
    "PaginationInfo",
    "StandardResponse",
    "SuccessResponse",
    "ValidationErrorResponse",
    "create_error_response",
    "create_paginated_response",
    "create_success_response",
    "create_validation_error_response",
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
    "ProductPatch",
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
    # Storage schemas
    "StorageBase",
    "StorageCreate",
    "StorageUpdate",
    "StorageResponse",
    "StorageBilling",
    "BillingCalculation",
]
