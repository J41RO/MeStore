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
