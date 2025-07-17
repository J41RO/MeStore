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

from app.core.database import Base


class UserType(PyEnum):
    """Tipos de usuario en MeStore"""

    SUPERUSER = "superuser"
    ADMIN = "admin"
    VENDEDOR = "vendedor"
    COMPRADOR = "comprador"


class User(Base):
    """Modelo de usuario optimizado para async operations"""

    __tablename__ = "users"

    # Primary key UUID para mejor performance
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="ID único del usuario",
    )

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

    is_active = Column(
        Boolean, default=True, nullable=False, comment="Usuario activo en el sistema"
    )

    # Timestamps automáticos con server defaults
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Fecha de creación",
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Fecha de última actualización",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, type={self.user_type.value})>"

    def to_dict(self) -> dict:
        """Convertir modelo a diccionario (sin password)"""
        return {
            "id": str(self.id),
            "email": self.email,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "user_type": self.user_type.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def full_name(self) -> str:
        """Nombre completo del usuario"""
        return f"{self.nombre} {self.apellido}"
