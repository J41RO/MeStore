# ~/app/schemas/vendedor.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Schema Vendedor Especializado
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: vendedor.py
# Ruta: ~/app/schemas/vendedor.py
# Autor: Jairo
# Fecha de Creación: 2025-07-31
# Última Actualización: 2025-07-31
# Versión: 1.0.0
# Propósito: Schemas específicos para registro y gestión de vendedores
#            con validaciones obligatorias colombianas
#
# Modificaciones:
# 2025-07-31 - Creación inicial con herencia de UserCreate
#
# ---------------------------------------------------------------------------------------------

"""
Schemas específicos para vendedores en MeStore.

Este módulo contiene schemas especializados para:
- Registro de vendedores con campos obligatorios
- Validaciones específicas colombianas
- Response schemas optimizados para vendedores
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.schemas.user import UserCreate, UserRead
from app.models.user import UserType


class VendedorCreate(UserCreate):
    """
    Schema para registro específico de vendedores.

    Hereda de UserCreate pero hace obligatorios:
    - cedula: Cédula colombiana (obligatoria para vendedores)
    - telefono: Teléfono colombiano (obligatorio para vendedores)
    - nombre: Nombre completo (obligatorio)
    - apellido: Apellido completo (obligatorio)

    El user_type se asigna automáticamente como VENDEDOR.
    """

    # Campos obligatorios para vendedores (override de UserCreate)
    cedula: str = Field(..., description="Cédula de ciudadanía colombiana (obligatoria para vendedores)")
    telefono: str = Field(..., description="Número de teléfono colombiano (obligatorio para vendedores)")
    nombre: str = Field(..., min_length=2, max_length=50, description="Nombre completo (obligatorio)")
    apellido: str = Field(..., min_length=2, max_length=50, description="Apellido completo (obligatorio)")

    # Campo automático - no enviado por cliente
    user_type: UserType = Field(default=UserType.VENDEDOR, description="Tipo fijo: VENDEDOR")

    class Config(UserCreate.Config):
        json_schema_extra = {
            "example": {
                "email": "juan.vendedor@email.com",
                "password": "MiPassword123",
                "nombre": "Juan Carlos",
                "apellido": "Pérez García",
                "cedula": "12345678",
                "telefono": "+57 300 123 4567",
                "ciudad": "Bogotá",
                "empresa": "Mi Tienda SAS",
                "direccion": "Calle 123 #45-67, Bogotá"
            }
        }


class VendedorResponse(BaseModel):
    """
    Schema de respuesta para registro exitoso de vendedor.

    Incluye datos relevantes del vendedor registrado,
    excluyendo información sensible como password_hash.
    """

    success: bool = Field(True, description="Indicador de éxito del registro")
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    vendedor: UserRead = Field(..., description="Datos del vendedor registrado")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Vendedor registrado exitosamente",
                "vendedor": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "juan.vendedor@email.com",
                    "nombre": "Juan Carlos",
                    "apellido": "Pérez García",
                    "user_type": "VENDEDOR",
                    "cedula": "12345678",
                    "telefono": "+57 300 123 4567",
                    "ciudad": "Bogotá",
                    "empresa": "Mi Tienda SAS",
                    "is_active": True,
                    "is_verified": False,
                    "created_at": "2025-07-30T20:30:00Z"
                }
            }
        }


class VendedorErrorResponse(BaseModel):
    """
    Schema de respuesta para errores en registro de vendedor.
    """

    success: bool = Field(False, description="Indicador de fallo del registro")
    message: str = Field(..., description="Mensaje descriptivo del error")
    error_type: str = Field(..., description="Tipo de error ocurrido")
    details: Optional[dict] = Field(None, description="Detalles adicionales del error")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Error en validación de datos",
                "error_type": "VALIDATION_ERROR",
                "details": {
                    "field": "cedula",
                    "issue": "Cédula debe ser numérica entre 6-10 dígitos"
                }
            }
        }


# Exports para facilitar imports
__all__ = [
    "VendedorCreate",
    "VendedorResponse", 
    "VendedorErrorResponse"
]