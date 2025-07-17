# ~/app/schemas/user.py
# ---------------------------------------------------------------------------------------------
# MeStore - Esquemas de Usuario (Stub Básico)
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file
# in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Esquemas de Usuario - Stub Básico

Definición inicial de esquemas Pydantic para User
"""

from pydantic import BaseModel, EmailStr

from app.models.user import UserType


class UserBase(BaseModel):
    """Esquema base de usuario"""

    email: EmailStr
    nombre: str
    apellido: str
    user_type: UserType = UserType.COMPRADOR


class UserCreate(UserBase):
    """Esquema para crear usuario"""

    password: str


class UserRead(UserBase):
    """Esquema para leer usuario"""

    id: int
    is_active: bool

    class Config:
        from_attributes = True
