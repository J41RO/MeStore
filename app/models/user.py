# ~/app/models/user.py
# ---------------------------------------------------------------------------------------------
# MeStore - Modelo SQLAlchemy User
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: user.py
# Ruta: ~/app/models/user.py
# Autor: Jairo
# Fecha de Creación: 2025-07-25
# Última Actualización: 2025-07-25
# Versión: 1.1.0
# Propósito: Modelo SQLAlchemy para gestión de usuarios del sistema
#            Incluye campos básicos, constraints de seguridad y optimizaciones
#
# Modificaciones:
# 2025-07-25 - Creación inicial del modelo User básico
# 2025-07-25 - Agregados campos nombre y apellido
# 2025-07-25 - Agregados métodos full_name y to_dict
#
# ---------------------------------------------------------------------------------------------

"""
Modelo SQLAlchemy User para MeStore.

Este módulo contiene el modelo principal para gestión de usuarios:
- Campos básicos: id, email, password_hash, nombre, apellido
- Constraints de seguridad: email único, campos obligatorios
- Timestamps automáticos: created_at, updated_at
- Optimizaciones: índices apropiados para consultas frecuentes
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from sqlalchemy import Enum

from app.models.base import BaseModel


class UserType(PyEnum):
    """
    Enumeración para tipos de usuario en el sistema.

    Valores:
        COMPRADOR: Usuario que puede realizar compras
        VENDEDOR: Usuario que puede vender productos
    """
    COMPRADOR = "comprador"
    VENDEDOR = "vendedor"


class User(BaseModel):
    """
    Modelo SQLAlchemy para usuarios del sistema.

    Campos:
        id: Clave primaria autoincremental
        email: Email único del usuario (índice para búsquedas)
        password_hash: Hash bcrypt de la contraseña
        nombre: Nombre del usuario
        apellido: Apellido del usuario
        user_type: Tipo de usuario (comprador/vendedor)
        is_active: Estado activo del usuario
        created_at: Timestamp de creación automático
        updated_at: Timestamp de última actualización automático

    Constraints:
        - Email debe ser único en toda la tabla
        - Email y password_hash son campos obligatorios
        - nombre y apellido son opcionales
        - Índices optimizados para consultas frecuentes
    """

    __tablename__ = "users"

    # Clave primaria
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="Identificador único UUID del usuario"
    )

    # Campos de autenticación
    email = Column(
        String(255), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="Email único del usuario, usado para login"
    )

    password_hash = Column(
        String(255),
        nullable=False,
        comment="Hash bcrypt de la contraseña del usuario"
    )

    # Campos de información personal
    nombre = Column(
        String(100),
        nullable=True,
        comment="Nombre del usuario"
    )

    apellido = Column(
        String(100),
        nullable=True,
        comment="Apellido del usuario"
    )

    # Tipo de usuario
    user_type = Column(
        Enum(UserType),
        nullable=False,
        default=UserType.COMPRADOR,
        comment="Tipo de usuario: comprador o vendedor"
    )

    # Estado del usuario
    is_active = Column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Indica si el usuario está activo en el sistema"
    )

    # Timestamps automáticos
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp de creación del registro"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp de última actualización del registro"
    )

    def __repr__(self) -> str:
        """Representación string del objeto User para debugging."""
        return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>"

    def __str__(self) -> str:
        """Representación string amigable del User."""
        status = "activo" if self.is_active else "inactivo"
        return f"Usuario {self.email} ({status})"

    @property
    def full_name(self) -> str:
        """Retorna el nombre completo del usuario."""
        if self.nombre and self.apellido:
            return f"{self.nombre} {self.apellido}"
        elif self.nombre:
            return self.nombre
        elif self.apellido:
            return self.apellido
        else:
            return "Usuario sin nombre"

    def to_dict(self) -> dict:
        """Convierte el objeto User a diccionario para serialización."""
        return {
            'id': str(self.id) if self.id else None,
            'email': self.email,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'user_type': self.user_type.value if self.user_type else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'full_name': self.full_name
        }
