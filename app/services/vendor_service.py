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
- Create new vendor (registration)
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserType, VendorStatus
from app.schemas.vendor import VendorCreate
from app.utils.password import hash_password


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

    async def create_vendor(self, vendor_data: VendorCreate) -> User:
        """
        Crear nuevo vendor con auto-aprobación (MVP).

        Reglas de Negocio:
        - Email debe ser único
        - Password hasheado con bcrypt
        - user_type = UserType.VENDOR
        - vendor_status = VendorStatus.APPROVED (auto-aprobado para MVP)
        - commission_rate no se maneja en modelo User (será agregado en futuro)
        - is_active = True
        - Separar full_name en nombre y apellido

        Args:
            vendor_data: VendorCreate schema con datos de registro

        Returns:
            User: Vendor creado

        Raises:
            ValueError: Si email ya existe
        """
        # Verificar que el email no exista
        existing_user = await self.db.execute(
            select(User).where(User.email == vendor_data.email)
        )
        if existing_user.scalar_one_or_none():
            raise ValueError("El email ya está registrado")

        # Hashear password
        password_hash = await hash_password(vendor_data.password)

        # Separar full_name en nombre y apellido
        name_parts = vendor_data.full_name.strip().split(maxsplit=1)
        nombre = name_parts[0] if len(name_parts) > 0 else ""
        apellido = name_parts[1] if len(name_parts) > 1 else ""

        # Crear nuevo vendor
        new_vendor = User(
            email=vendor_data.email,
            password_hash=password_hash,
            nombre=nombre,
            apellido=apellido,
            user_type=UserType.VENDOR,
            vendor_status=VendorStatus.APPROVED,  # Auto-aprobado para MVP
            is_active=True,
            telefono=vendor_data.phone,
            ciudad=vendor_data.city,
            empresa=vendor_data.business_name,
            business_name=vendor_data.business_name  # Campo específico de vendor
        )

        self.db.add(new_vendor)
        await self.db.commit()
        await self.db.refresh(new_vendor)

        return new_vendor