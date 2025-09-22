# ~/app/services/vendor_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Vendor Service
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: vendor_service.py
# Ruta: ~/app/services/vendor_service.py
# Autor: Jairo
# Fecha de Creación: 2025-09-20
# Última Actualización: 2025-09-20
# Versión: 1.0.0
# Propósito: Service class for vendor operations
#
# Modificaciones:
# 2025-09-20 - Creación inicial para soporte de testing
#
# ---------------------------------------------------------------------------------------------

"""
Service layer for vendor operations.

This module provides service methods for vendor management:
- Get vendor by user ID
- Vendor profile operations
- Vendor analytics
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserType


class VendorService:
    """Service class for vendor operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def get_vendor_by_user_id(self, user_id: str) -> Optional[User]:
        """
        Get vendor by user ID.

        Args:
            user_id: User ID to search for

        Returns:
            User object if found and is vendor, None otherwise
        """
        result = await self.db.execute(
            select(User).where(
                User.id == user_id,
                User.user_type == UserType.VENDOR
            )
        )
        return result.scalar_one_or_none()

    async def get_vendor_profile(self, user_id: str) -> Optional[User]:
        """
        Get vendor profile information.

        Args:
            user_id: User ID of the vendor

        Returns:
            User object with vendor profile data
        """
        return await self.get_vendor_by_user_id(user_id)

    async def get_vendor_analytics(self, user_id: str) -> dict:
        """
        Get vendor analytics data.

        Args:
            user_id: User ID of the vendor

        Returns:
            Dictionary with analytics data
        """
        vendor = await self.get_vendor_by_user_id(user_id)
        if not vendor:
            return {}

        # Return mock analytics data for testing
        return {
            "total_sales": 0,
            "total_products": 0,
            "total_orders": 0,
            "revenue": 0.0
        }