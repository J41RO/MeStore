# ~/app/schemas/__init__.py
# ---------------------------------------------------------------------------------------------
# MeStore - Schemas Package Exports
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Schemas package for MeStore application.

Exports all Pydantic schemas for API validation and serialization.
Organized by domain: User schemas, Product schemas, etc.
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
]
