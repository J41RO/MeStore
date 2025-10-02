# ~/app/schemas/vendor.py
# ---------------------------------------------------------------------------------------------
# MeStore - Schemas Pydantic para Vendor Registration
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: vendor.py
# Ruta: ~/app/schemas/vendor.py
# Autor: Jairo
# Fecha de Creación: 2025-10-01
# Última Actualización: 2025-10-01
# Versión: 1.0.0
# Propósito: Schemas Pydantic para registro y gestión de vendors (MVP)
#
# Modificaciones:
# 2025-10-01 - Creación inicial con schemas MVP para vendor registration
#
# ---------------------------------------------------------------------------------------------

"""
Schemas Pydantic para Vendor Registration en MeStore MVP.

Este módulo contiene los schemas para:
- Vendor Registration (single-page form)
- Vendor Response
- Validaciones específicas para campos colombianos
"""

from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
import re


class VendorCreate(BaseModel):
    """
    Schema para registro de vendor (MVP - single-page form).

    Incluye todos los campos necesarios para registro completo en un solo paso.
    Auto-aprobación para MVP (sin verificación manual).
    """

    # Información de autenticación
    email: EmailStr = Field(
        ...,
        description="Email único del vendor para login"
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Contraseña del vendor (mínimo 8 caracteres)"
    )

    # Información personal
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Nombre completo del vendor"
    )

    phone: str = Field(
        ...,
        description="Teléfono del vendor (formato colombiano +57...)"
    )

    # Información del negocio
    business_name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Nombre del negocio"
    )

    city: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Ciudad de operación en Colombia"
    )

    business_type: str = Field(
        ...,
        description="Tipo de negocio: persona_natural o empresa"
    )

    primary_category: str = Field(
        ...,
        description="Categoría principal de productos"
    )

    # Términos y condiciones
    terms_accepted: bool = Field(
        ...,
        description="Usuario acepta términos y condiciones"
    )

    # Validadores
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validar formato de teléfono colombiano."""
        # Remover espacios y guiones
        phone_clean = re.sub(r'[\s-]', '', v)

        # Validar formato colombiano: +573001234567 o 3001234567
        if not re.match(r'^(\+57|57)?[3][0-9]{9}$', phone_clean):
            raise ValueError(
                'Teléfono debe tener formato colombiano: +573001234567 o 3001234567'
            )

        # Asegurar que comience con +57
        if not phone_clean.startswith('+57'):
            if phone_clean.startswith('57'):
                phone_clean = '+' + phone_clean
            else:
                phone_clean = '+57' + phone_clean

        return phone_clean

    @field_validator('business_type')
    @classmethod
    def validate_business_type(cls, v: str) -> str:
        """Validar tipo de negocio."""
        valid_types = {'persona_natural', 'empresa'}
        if v.lower() not in valid_types:
            raise ValueError(
                f'Tipo de negocio debe ser uno de: {valid_types}'
            )
        return v.lower()

    @field_validator('primary_category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validar categoría primaria."""
        valid_categories = {
            'ropa_femenina',
            'ropa_masculina',
            'accesorios',
            'calzado',
            'hogar',
            'tecnologia',
            'deportes',
            'belleza',
            'juguetes',
            'libros',
            'otros'
        }
        if v.lower() not in valid_categories:
            raise ValueError(
                f'Categoría debe ser una de: {valid_categories}'
            )
        return v.lower()

    @field_validator('terms_accepted')
    @classmethod
    def validate_terms(cls, v: bool) -> bool:
        """Validar que términos fueron aceptados."""
        if not v:
            raise ValueError('Debes aceptar los términos y condiciones')
        return v

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validar fortaleza de contraseña."""
        if len(v) < 8:
            raise ValueError('Contraseña debe tener al menos 8 caracteres')

        # Al menos una letra mayúscula
        if not re.search(r'[A-Z]', v):
            raise ValueError('Contraseña debe contener al menos una mayúscula')

        # Al menos una letra minúscula
        if not re.search(r'[a-z]', v):
            raise ValueError('Contraseña debe contener al menos una minúscula')

        # Al menos un número
        if not re.search(r'\d', v):
            raise ValueError('Contraseña debe contener al menos un número')

        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "maria@ejemplo.com",
                "password": "SecurePass123!",
                "full_name": "María González",
                "phone": "+573001234567",
                "business_name": "MaríaStyle",
                "city": "Bucaramanga",
                "business_type": "persona_natural",
                "primary_category": "ropa_femenina",
                "terms_accepted": True
            }
        }
    )


class VendorResponse(BaseModel):
    """
    Schema para respuesta de vendor registration.

    Retorna información básica del vendor creado y próximos pasos.
    """

    vendor_id: str = Field(..., description="UUID del vendor creado")
    email: str = Field(..., description="Email del vendor")
    full_name: str = Field(..., description="Nombre completo del vendor")
    business_name: str = Field(..., description="Nombre del negocio")
    status: str = Field(..., description="Estado del vendor (active para MVP)")
    message: str = Field(..., description="Mensaje de bienvenida")

    next_steps: Dict[str, str] = Field(
        ...,
        description="Enlaces a próximas acciones recomendadas"
    )

    created_at: datetime = Field(..., description="Fecha de registro")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "vendor_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "maria@ejemplo.com",
                "full_name": "María González",
                "business_name": "MaríaStyle",
                "status": "active",
                "message": "¡Registro exitoso! Bienvenida a MeStocker.",
                "next_steps": {
                    "add_products": "/vendor/products/new",
                    "view_dashboard": "/vendor/dashboard"
                },
                "created_at": "2024-02-01T10:00:00Z"
            }
        }
    )


class VendorLogin(BaseModel):
    """Schema para login de vendor."""

    email: EmailStr = Field(..., description="Email del vendor")
    password: str = Field(..., description="Contraseña del vendor")


class VendorBasicInfo(BaseModel):
    """Schema para información básica del vendor (para listados)."""

    vendor_id: str
    email: str
    full_name: str
    business_name: str
    city: str
    primary_category: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VendorRegistrationError(BaseModel):
    """Schema para errores de registro."""

    error: str = Field(..., description="Tipo de error")
    message: str = Field(..., description="Mensaje de error detallado")
    field: Optional[str] = Field(None, description="Campo que causó el error")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "validation_error",
                "message": "El email ya está registrado",
                "field": "email"
            }
        }
    )
