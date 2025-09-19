"""
Schemas de autenticación para endpoints JWT.

Contiene los modelos Pydantic para request/response de autenticación:
- LoginRequest: Datos de entrada para login
- TokenResponse: Respuesta con tokens JWT  
- RefreshTokenRequest: Request para refresh de token
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from app.models.user import UserType


class LoginRequest(BaseModel):
    """Esquema para request de login."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "usuario@ejemplo.com",
                "password": "mi_password_seguro"
            }
        }
    )

    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=6, description="Contraseña del usuario")


class RegisterRequest(BaseModel):
    """Esquema para request de registro con tipo de usuario."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "nuevousuario@ejemplo.com",
                "password": "mi_password_seguro",
                "nombre": "Juan Carlos",
                "telefono": "300 123 4567",
                "user_type": "VENDOR"
            }
        }
    )

    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=6, description="Contraseña del usuario")
    nombre: Optional[str] = Field(None, description="Nombre del usuario")
    telefono: Optional[str] = Field(None, description="Teléfono del usuario")
    user_type: Optional[UserType] = Field(UserType.BUYER, description="Tipo de usuario")


class TokenResponse(BaseModel):
    """Esquema para response de tokens JWT."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }
    )

    access_token: str = Field(..., description="Token de acceso JWT")
    refresh_token: str = Field(..., description="Token de refresh JWT")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")


class RefreshTokenRequest(BaseModel):
    """Esquema para request de refresh token."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }
    )

    refresh_token: str = Field(..., description="Token de refresh válido")


class LogoutRequest(BaseModel):
    """Esquema para request de logout (opcional - token va en header)."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "revoke_all": False
            }
        }
    )

    revoke_all: Optional[bool] = Field(
        default=False,
        description="Si revocar todas las sesiones del usuario"
    )


class AuthResponse(BaseModel):
    """Esquema base para respuestas de autenticación."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operación completada exitosamente"
            }
        }
    )

    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")



# === SCHEMAS OTP PARA VERIFICACIÓN EMAIL/SMS ===

class OTPSendRequest(BaseModel):
    """Schema para solicitar envío de código OTP."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "otp_type": "EMAIL"
            }
        }
    )

    otp_type: str = Field(
        ...,
        pattern="^(EMAIL|SMS)$",
        description="Tipo de OTP a enviar: EMAIL o SMS"
    )


class OTPVerifyRequest(BaseModel):
    """Schema para verificar código OTP."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "otp_code": "123456"
            }
        }
    )

    otp_code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern="^[0-9]{6}$",
        description="Código OTP de 6 dígitos numéricos"
    )


class OTPResponse(BaseModel):
    """Schema para respuesta de operaciones OTP."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Código enviado exitosamente",
                "verification_status": {
                    "email_verified": True,
                    "phone_verified": False
                }
            }
        }
    )

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


class UserVerificationStatus(BaseModel):
    """Schema para estado completo de verificación del usuario."""
    model_config = ConfigDict(
        json_schema_extra={
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
    )

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


# === SCHEMAS PARA RESET DE CONTRASEÑA ===

class PasswordResetRequest(BaseModel):
    """Esquema para solicitud de reset de contraseña."""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "usuario@ejemplo.com"
            }
        }
    )

    email: EmailStr = Field(..., description="Email del usuario para enviar token de reset")


class PasswordResetConfirm(BaseModel):
    """Esquema para confirmar reset de contraseña con token."""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "token": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
            }
        }
    )

    token: str = Field(..., min_length=32, max_length=100, description="Token de reset recibido por email")
    new_password: str = Field(..., min_length=8, max_length=128, description="Nueva contraseña (mínimo 8 caracteres)")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Confirmación de la nueva contraseña")

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

    @field_validator('new_password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v


class PasswordResetResponse(BaseModel):
    """Esquema para response de operaciones de reset."""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Se ha enviado un enlace de recuperación a tu email"
            }
        }
    )

    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo del resultado")