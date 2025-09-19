# ~/app/schemas/user.py
# ---------------------------------------------------------------------------------------------
# MeStore - Esquemas de Usuario Completos
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file
# in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Esquemas Pydantic para Usuario - Versión Completa

Incluye:
- UserBase: Campos base compartidos
- UserCreate: Schema para registro de usuarios
- UserUpdate: Schema para actualizaciones parciales
- UserRead: Schema para respuestas de API
- UserResponse: Alias descriptivo de UserRead
- Validadores para datos colombianos
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic import ConfigDict
from typing import Optional, Union
from datetime import datetime
from uuid import UUID
import re

from app.models.user import UserType
from app.schemas.base import BaseSchema, BaseIDSchema, BaseCreateSchema, BaseUpdateSchema, BaseResponseSchema
from app.core.id_validation import IDValidationMixin


class UserBase(BaseSchema):
    """
    Schema base con campos compartidos entre operaciones.

    No incluye:
    - password (sensible)
    - id (autogenerado)
    - timestamps (manejados por sistema)
    """
    email: EmailStr = Field(..., description="Email único del usuario")
    nombre: str = Field(..., min_length=2, max_length=50, description="Nombre del usuario")
    apellido: str = Field(..., min_length=2, max_length=50, description="Apellido del usuario")
    user_type: UserType = Field(default=UserType.BUYER, description="Tipo de usuario en el sistema")

    # Campos específicos colombianos (opcionales)
    cedula: Optional[str] = Field(None, description="Cédula de ciudadanía colombiana")
    telefono: Optional[str] = Field(None, description="Número de teléfono (formato colombiano)")
    ciudad: Optional[str] = Field(None, max_length=100, description="Ciudad de residencia")
    empresa: Optional[str] = Field(None, max_length=200, description="Empresa donde trabaja")
    direccion: Optional[str] = Field(None, max_length=300, description="Dirección completa")
    is_verified: bool = Field(default=False, description="Estado de verificación del usuario")

    @field_validator("cedula")
    def validate_cedula(cls, v):
        """Validar formato de cédula colombiana"""
        if v is None:
            return v
        # Remover espacios y guiones
        cedula_clean = re.sub(r"[\s\-]", "", str(v))
        # Debe ser numérica y entre 6-10 dígitos
        if not cedula_clean.isdigit() or len(cedula_clean) < 6 or len(cedula_clean) > 10:
            raise ValueError("Cédula debe ser numérica entre 6-10 dígitos")
        return cedula_clean

    @field_validator("telefono")
    def validate_telefono(cls, v):
        """Validar formato de teléfono colombiano"""
        if v is None:
            return v
        # Aceptar formatos: +57 XXX XXX XXXX, 3XX XXX XXXX, etc.
        phone_clean = re.sub(r"[\s\-\(\)]", "", str(v))
        # Remover código de país si existe
        if phone_clean.startswith("+57"):
            phone_clean = phone_clean[3:]
        elif phone_clean.startswith("57") and len(phone_clean) > 10:
            phone_clean = phone_clean[2:]

        # Validar que sea numérico y tenga 10 dígitos
        if not phone_clean.isdigit() or len(phone_clean) != 10:
            raise ValueError("Teléfono debe tener 10 dígitos (formato colombiano)")

        # Validar que comience con 3 (celular) o códigos de ciudad válidos
        if not (phone_clean.startswith("3") or 
                phone_clean.startswith(("1", "2", "4", "5", "6", "7", "8"))):
            raise ValueError("Número de teléfono no válido para Colombia")

        return f"+57 {phone_clean}"

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "juan.perez@email.com",
                "nombre": "Juan",
                "apellido": "Pérez",
                "user_type": "buyer",
                "cedula": "12345678",
                "telefono": "+57 300 123 4567",
                "ciudad": "Bogotá",
                "empresa": "Mi Empresa SAS",
                "direccion": "Calle 123 #45-67, Bogotá",
                "is_verified": False
            }
        }
    )


class UserCreate(UserBase, BaseCreateSchema):
    """
    Schema para crear nuevos usuarios.

    Hereda todos los campos de UserBase y agrega password.
    """
    password: str = Field(..., min_length=8, description="Contraseña (mínimo 8 caracteres)")

    @field_validator("password")
    def validate_password(cls, v):
        """Validar fortaleza de contraseña"""
        if len(v) < 8:
            raise ValueError("Contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Contraseña debe tener al menos una mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("Contraseña debe tener al menos una minúscula")
        if not re.search(r"\d", v):
            raise ValueError("Contraseña debe tener al menos un número")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "juan.perez@email.com",
                "nombre": "Juan",
                "apellido": "Pérez",
                "user_type": "buyer",
                "cedula": "12345678",
                "telefono": "+57 300 123 4567",
                "ciudad": "Bogotá",
                "empresa": "Mi Empresa SAS",
                "direccion": "Calle 123 #45-67, Bogotá",
                "is_verified": False,
                "password": "MiPassword123"
            }
        }
    )


class UserUpdate(BaseUpdateSchema):
    """
    Schema para actualizaciones parciales de usuario.

    Todos los campos son opcionales para permitir actualizaciones parciales.
    No incluye password (usar endpoint específico) ni email (requiere verificación especial).
    """
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    apellido: Optional[str] = Field(None, min_length=2, max_length=50)
    user_type: Optional[UserType] = None
    cedula: Optional[str] = None
    telefono: Optional[str] = None
    ciudad: Optional[str] = Field(None, max_length=100)
    empresa: Optional[str] = Field(None, max_length=200)
    direccion: Optional[str] = Field(None, max_length=300)
    is_verified: Optional[bool] = None

    # === CAMPOS BANCARIOS PARA PERFIL ===
    banco: Optional[str] = Field(None, max_length=100, description="Nombre del banco")
    tipo_cuenta: Optional[str] = Field(None, pattern="^(AHORROS|CORRIENTE)$", description="Tipo de cuenta bancaria")
    numero_cuenta: Optional[str] = Field(None, min_length=8, max_length=50, description="Número de cuenta bancaria")

    # Reutilizar validadores de UserBase (Pydantic V2)
    @field_validator("cedula")
    @classmethod
    def validate_cedula(cls, v):
        if v is None:
            return v
        return UserBase.validate_cedula(v)

    @field_validator("telefono")
    @classmethod
    def validate_telefono(cls, v):
        if v is None:
            return v
        return UserBase.validate_telefono(v)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "nombre": "Juan Carlos",
                "telefono": "+57 300 987 6543",
                "ciudad": "Medellín"
            }
        }
    )


class UserRead(BaseResponseSchema):
    """
    Schema para respuestas de API que incluyen datos completos del usuario.

    Incluye campos del sistema:
    - id: UUID autogenerado
    - is_active: Estado del usuario
    - timestamps: created_at, updated_at, last_login

    Usado en auth.py - MANTENER COMPATIBILIDAD
    """
    # Inherit id, created_at, updated_at from BaseResponseSchema
    email: EmailStr = Field(..., description="Email único del usuario")
    nombre: str = Field(..., min_length=2, max_length=50, description="Nombre del usuario")
    apellido: str = Field(..., min_length=2, max_length=50, description="Apellido del usuario")
    user_type: UserType = Field(default=UserType.BUYER, description="Tipo de usuario en el sistema")
    is_active: bool = Field(..., description="Estado activo del usuario")

    # Campos específicos colombianos (opcionales)
    cedula: Optional[str] = Field(None, description="Cédula de ciudadanía colombiana")
    telefono: Optional[str] = Field(None, description="Número de teléfono (formato colombiano)")
    ciudad: Optional[str] = Field(None, max_length=100, description="Ciudad de residencia")
    empresa: Optional[str] = Field(None, max_length=200, description="Empresa donde trabaja")
    direccion: Optional[str] = Field(None, max_length=300, description="Dirección completa")
    is_verified: bool = Field(default=False, description="Estado de verificación del usuario")
    last_login: Optional[datetime] = Field(None, description="Fecha del último login")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "juan.perez@email.com",
                "nombre": "Juan",
                "apellido": "Pérez",
                "user_type": "buyer",
                "cedula": "12345678",
                "telefono": "+57 300 123 4567",
                "ciudad": "Bogotá",
                "empresa": "Mi Empresa SAS",
                "direccion": "Calle 123 #45-67, Bogotá",
                "is_verified": False,
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "is_active": True,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z",
                "last_login": "2025-01-15T10:30:00Z"
            }
        }
    )


# Alias más descriptivo para UserRead
UserResponse = UserRead


class UserInDB(UserRead, IDValidationMixin):
    """
    Schema interno que incluye campos sensibles (solo para uso interno).

    NO usar en respuestas de API.
    """
    password_hash: str = Field(..., description="Hash de la contraseña")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "juan.perez@email.com",
                "nombre": "Juan",
                "apellido": "Pérez",
                "user_type": "buyer",
                "cedula": "12345678",
                "telefono": "+57 300 123 4567",
                "ciudad": "Bogotá",
                "empresa": "Mi Empresa SAS",
                "direccion": "Calle 123 #45-67, Bogotá",
                "is_verified": False,
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "is_active": True,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z",
                "last_login": "2025-01-15T10:30:00Z",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewJM5bfQ9q6ib.rK"
            }
        }
    )


# Exports para facilitar imports
__all__ = [
    "UserBase",
    "UserCreate", 
    "UserUpdate",
    "UserRead",
    "UserResponse",
    "UserInDB"
]