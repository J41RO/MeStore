# ~/app/schemas/vendor_profile.py
# ---------------------------------------------------------------------------------------------
# MeStore - Schemas Pydantic para Perfil de Vendor
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: vendor_profile.py
# Ruta: ~/app/schemas/vendor_profile.py
# Autor: Jairo
# Fecha de Creación: 2025-09-11
# Última Actualización: 2025-09-11
# Versión: 1.0.0
# Propósito: Schemas Pydantic para validación de datos de perfil de vendor
#            Incluye información del negocio, configuraciones bancarias y notificaciones
#
# Modificaciones:
# 2025-09-11 - Creación inicial con schemas completos de perfil vendor
#
# ---------------------------------------------------------------------------------------------

"""
Schemas Pydantic para Perfil de Vendor en MeStore.

Este módulo contiene los schemas para:
- Información básica del perfil de vendor
- Configuraciones de notificaciones
- Información bancaria
- Respuestas de API con timestamps
- Validaciones específicas para campos colombianos
"""

from datetime import datetime
from typing import Dict, Optional
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl, validator
import re


class VendorProfileBase(BaseModel):
    """Schema base para perfil de vendor con validaciones."""
    
    business_name: Optional[str] = Field(
        None, 
        max_length=200,
        description="Nombre comercial del negocio"
    )
    
    business_description: Optional[str] = Field(
        None, 
        max_length=1000,
        description="Descripción del negocio"
    )
    
    website_url: Optional[HttpUrl] = Field(
        None,
        description="Sitio web del vendor"
    )
    
    social_media_links: Optional[Dict[str, HttpUrl]] = Field(
        None,
        description="Enlaces de redes sociales (facebook, instagram, twitter, etc.)"
    )
    
    business_hours: Optional[Dict[str, str]] = Field(
        None,
        description="Horarios de atención por día de la semana"
    )
    
    shipping_policy: Optional[str] = Field(
        None, 
        max_length=2000,
        description="Política de envíos"
    )
    
    return_policy: Optional[str] = Field(
        None, 
        max_length=2000,
        description="Política de devoluciones"
    )

    @validator('business_hours')
    def validate_business_hours(cls, v):
        """Validar formato de horarios de negocio."""
        if v is None:
            return v
        
        valid_days = {'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'}
        time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]-([01]?[0-9]|2[0-3]):[0-5][0-9]$|^closed$')
        
        for day, hours in v.items():
            if day.lower() not in valid_days:
                raise ValueError(f'Día inválido: {day}. Debe ser uno de {valid_days}')
            if not time_pattern.match(hours):
                raise ValueError(f'Formato de hora inválido para {day}: {hours}. Use HH:MM-HH:MM o "closed"')
        
        return v

    @validator('social_media_links')
    def validate_social_media_links(cls, v):
        """Validar enlaces de redes sociales."""
        if v is None:
            return v
        
        valid_platforms = {'facebook', 'instagram', 'twitter', 'linkedin', 'youtube', 'tiktok'}
        for platform in v.keys():
            if platform.lower() not in valid_platforms:
                raise ValueError(f'Plataforma no válida: {platform}. Debe ser una de {valid_platforms}')
        
        return v


class VendorProfileUpdate(VendorProfileBase):
    """Schema para actualización de perfil de vendor."""
    pass


class VendorProfileResponse(VendorProfileBase):
    """Schema para respuesta de perfil de vendor con timestamps."""
    
    id: UUID
    avatar_url: Optional[str] = Field(None, description="URL del avatar/logo del vendor")
    email: str = Field(..., description="Email del vendor")
    nombre: Optional[str] = Field(None, description="Nombre del vendor")
    apellido: Optional[str] = Field(None, description="Apellido del vendor")
    user_type: str = Field(..., description="Tipo de usuario")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    class Config:
        from_attributes = True


class VendorBankingInfo(BaseModel):
    """Schema para información bancaria del vendor."""
    
    bank_name: Optional[str] = Field(
        None, 
        max_length=100,
        description="Nombre del banco"
    )
    
    account_holder_name: Optional[str] = Field(
        None, 
        max_length=200,
        description="Titular de la cuenta"
    )
    
    account_number: Optional[str] = Field(
        None,
        description="Número de cuenta bancaria"
    )
    
    tipo_cuenta: Optional[str] = Field(
        None,
        description="Tipo de cuenta: AHORROS o CORRIENTE"
    )

    @validator('account_number')
    def validate_account_number(cls, v):
        """Validar número de cuenta colombiano."""
        if v is None:
            return v
        
        # Remover espacios y guiones
        v = re.sub(r'[\s-]', '', v)
        
        # Validar que sean solo números
        if not re.match(r'^\d{10,20}$', v):
            raise ValueError('Número de cuenta debe tener entre 10 y 20 dígitos')
        
        return v

    @validator('tipo_cuenta')
    def validate_account_type(cls, v):
        """Validar tipo de cuenta."""
        if v is None:
            return v
        
        valid_types = {'AHORROS', 'CORRIENTE'}
        if v.upper() not in valid_types:
            raise ValueError(f'Tipo de cuenta debe ser uno de: {valid_types}')
        
        return v.upper()


class VendorNotificationPreferences(BaseModel):
    """Schema para preferencias de notificaciones del vendor."""
    
    email_new_orders: bool = Field(
        True,
        description="Recibir email cuando llegue una nueva orden"
    )
    
    email_low_stock: bool = Field(
        True,
        description="Recibir email cuando el stock esté bajo"
    )
    
    sms_urgent_orders: bool = Field(
        False,
        description="Recibir SMS para órdenes urgentes"
    )
    
    push_daily_summary: bool = Field(
        True,
        description="Recibir resumen diario por push notification"
    )


class VendorAvatarUploadResponse(BaseModel):
    """Schema para respuesta de upload de avatar."""
    
    avatar_url: str = Field(..., description="URL del avatar subido")
    message: str = Field(..., description="Mensaje de éxito")


class VendorProfileCompleteResponse(BaseModel):
    """Schema para respuesta completa de perfil de vendor."""
    
    profile: VendorProfileResponse
    banking_info: VendorBankingInfo
    notification_preferences: VendorNotificationPreferences
    
    class Config:
        from_attributes = True


# Schemas para validación de request
class VendorProfileUpdateRequest(BaseModel):
    """Schema para request de actualización de perfil."""
    
    business_name: Optional[str] = None
    business_description: Optional[str] = None
    website_url: Optional[str] = None
    social_media_links: Optional[Dict[str, str]] = None
    business_hours: Optional[Dict[str, str]] = None
    shipping_policy: Optional[str] = None
    return_policy: Optional[str] = None


class VendorBankingUpdateRequest(BaseModel):
    """Schema para request de actualización bancaria."""
    
    bank_name: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None
    tipo_cuenta: Optional[str] = None


class VendorNotificationUpdateRequest(BaseModel):
    """Schema para request de actualización de notificaciones."""
    
    email_new_orders: Optional[bool] = None
    email_low_stock: Optional[bool] = None
    sms_urgent_orders: Optional[bool] = None
    push_daily_summary: Optional[bool] = None


# Schema de respuesta estándar
class StandardResponse(BaseModel):
    """Schema estándar para respuestas de API."""
    
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[dict] = Field(None, description="Datos opcionales de respuesta")