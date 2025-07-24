# ~/app/models/user.py
# ---------------------------------------------------------------------------------------------
# MeStore - Modelo de Usuario (Async Optimizado)
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file
# in the root of this project.
# ---------------------------------------------------------------------------------------------
"""
User Model - Modelo de usuario con SQLAlchemy async

Características:
- UUID como primary key para mejor performance
- Timestamps automáticos con server defaults
- Email único con validación
- Password hash seguro
- Support para async operations
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, DateTime, Enum, String, text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel


class UserType(PyEnum):
    """Tipos de usuario en MeStore"""

    SUPERUSER = "superuser"
    ADMIN = "admin"
    VENDEDOR = "vendedor"
    COMPRADOR = "comprador"


class User(BaseModel):
    """Modelo de usuario optimizado para async operations"""

    __tablename__ = "users"

    # Información básica
    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="Email único del usuario",
    )

    password_hash = Column(
        String(255), nullable=False, comment="Hash seguro de la contraseña"
    )

    nombre = Column(String(100), nullable=False, comment="Nombre del usuario")

    apellido = Column(String(100), nullable=False, comment="Apellido del usuario")

    # Tipo y estado
    user_type = Column(
        Enum(UserType),
        default=UserType.COMPRADOR,
        nullable=False,
        comment="Tipo de usuario en el sistema",
    )

    active_status = Column(
        Boolean, default=True, nullable=False, comment="Estado activo del usuario en el sistema"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, type={self.user_type.value})>"

    def is_user_active(self) -> bool:
        """Verificar si usuario está activo (combina soft delete + active_status)"""
        return self.is_active() and bool(getattr(self, "active_status", False))

    def to_dict(self) -> dict:
        """Convertir modelo a diccionario extendiendo BaseModel (sin password)"""
        # Obtener diccionario base con deleted_at incluido
        base_dict = super().to_dict()
        
        # Agregar campos específicos de User
        user_dict = {
            "email": self.email,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "user_type": self.user_type.value if hasattr(self.user_type, 'value') else str(self.user_type),
            "active_status": self.active_status,
        }
        
        # Combinar ambos diccionarios
        return {**base_dict, **user_dict}

    @property
    def full_name(self) -> str:
        """Nombre completo del usuario"""
        return f"{self.nombre} {self.apellido}"