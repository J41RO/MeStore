"""
Schemas de autenticación para endpoints JWT.

Contiene los modelos Pydantic para request/response de autenticación:
- LoginRequest: Datos de entrada para login
- TokenResponse: Respuesta con tokens JWT  
- RefreshTokenRequest: Request para refresh de token
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Esquema para request de login."""

    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=6, description="Contraseña del usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "password": "mi_password_seguro"
            }
        }


class TokenResponse(BaseModel):
    """Esquema para response de tokens JWT."""

    access_token: str = Field(..., description="Token de acceso JWT")
    refresh_token: str = Field(..., description="Token de refresh JWT")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class RefreshTokenRequest(BaseModel):
    """Esquema para request de refresh token."""

    refresh_token: str = Field(..., description="Token de refresh válido")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }


class LogoutRequest(BaseModel):
    """Esquema para request de logout (opcional - token va en header)."""

    revoke_all: Optional[bool] = Field(
        default=False, 
        description="Si revocar todas las sesiones del usuario"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "revoke_all": False
            }
        }


class AuthResponse(BaseModel):
    """Esquema base para respuestas de autenticación."""

    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operación completada exitosamente"
            }
        }



# === SCHEMAS OTP PARA VERIFICACIÓN EMAIL/SMS ===

class OTPSendRequest(BaseModel):
    """Schema para solicitar envío de código OTP."""

    otp_type: str = Field(
        ..., 
        pattern="^(EMAIL|SMS)$",
        description="Tipo de OTP a enviar: EMAIL o SMS"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "otp_type": "EMAIL"
            }
        }


class OTPVerifyRequest(BaseModel):
    """Schema para verificar código OTP."""

    otp_code: str = Field(
        ..., 
        min_length=6,
        max_length=6,
        pattern="^[0-9]{6}$",
        description="Código OTP de 6 dígitos numéricos"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "otp_code": "123456"
            }
        }


class OTPResponse(BaseModel):
    """Schema para respuesta de operaciones OTP."""

    success: bool = Field(
        ..., 
        description="Indica si la operación fue exitosa"
    )
    message: str = Field(
        ..., 
        description="Mensaje descriptivo del resultado"
    )
    verification_status: Optional[dict] = Field(
        None,
        description="Estado de verificación del usuario (solo en verificaciones exitosas)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Código enviado exitosamente",
                "verification_status": {
                    "email_verified": True,
                    "phone_verified": False
                }
            }
        }


class UserVerificationStatus(BaseModel):
    """Schema para estado completo de verificación del usuario."""

    email_verified: bool = Field(
        ..., 
        description="Indica si el email está verificado"
    )
    phone_verified: bool = Field(
        ..., 
        description="Indica si el teléfono está verificado"
    )
    has_active_otp: bool = Field(
        ..., 
        description="Indica si tiene un código OTP activo"
    )
    otp_type: Optional[str] = Field(
        None, 
        description="Tipo de OTP activo: EMAIL, SMS o None"
    )
    otp_expires_at: Optional[str] = Field(
        None, 
        description="Fecha/hora de expiración del OTP en formato ISO"
    )
    can_request_new_otp: bool = Field(
        ..., 
        description="Indica si puede solicitar un nuevo OTP"
    )
    is_otp_blocked: bool = Field(
        ..., 
        description="Indica si está bloqueado por demasiados intentos"
    )
    otp_attempts: int = Field(
        ..., 
        description="Número de intentos fallidos de OTP"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email_verified": True,
                "phone_verified": False,
                "has_active_otp": False,
                "otp_type": None,
                "otp_expires_at": None,
                "can_request_new_otp": True,
                "is_otp_blocked": False,
                "otp_attempts": 0
            }
        }