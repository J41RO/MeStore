"""
Admin User Management Schemas
Esquemas Pydantic específicos para la gestión de usuarios por administradores
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.models.user import UserType
from app.schemas.user import UserRead, UserUpdate


class AdminUserDetail(UserRead):
    """
    Schema detallado para usuarios visto por administradores
    Incluye información adicional que solo los admins pueden ver
    """
    # Campos adicionales para admins
    password_hash: Optional[str] = Field(None, description="Hash de contraseña (solo informativo)")
    last_login_ip: Optional[str] = Field(None, description="Última IP de login")
    login_attempts: int = Field(default=0, description="Intentos fallidos de login")
    is_locked: bool = Field(default=False, description="Cuenta bloqueada por seguridad")
    deleted_at: Optional[datetime] = Field(None, description="Fecha de eliminación soft delete")

    # Estadísticas básicas
    total_orders: Optional[int] = Field(0, description="Total de órdenes realizadas")
    total_spent: Optional[float] = Field(0.0, description="Total gastado en la plataforma")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "jairo.colina.co@gmail.com",
                "nombre": "Jairo",
                "apellido": "Colina",
                "user_type": "buyer",
                "cedula": "12345678",
                "telefono": "+57 373 977 1943",
                "ciudad": "Bogotá",
                "empresa": "MeStore",
                "direccion": "Calle 123 #45-67",
                "is_verified": True,
                "is_active": True,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z",
                "last_login": "2025-01-15T15:45:00Z",
                "last_login_ip": "192.168.1.137",
                "login_attempts": 0,
                "is_locked": False,
                "total_orders": 5,
                "total_spent": 150000.0
            }
        }
    )

    @classmethod
    def from_orm(cls, user):
        """
        Crear instancia desde modelo ORM con datos adicionales calculados
        """
        # Datos básicos del usuario
        data = {
            "id": user.id,
            "email": user.email,
            "nombre": user.nombre,
            "apellido": user.apellido,
            "user_type": user.user_type,
            "cedula": user.cedula,
            "telefono": user.telefono,
            "ciudad": user.ciudad,
            "empresa": user.empresa,
            "direccion": user.direccion,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login": user.last_login,
        }

        # Campos adicionales si existen
        data["password_hash"] = getattr(user, 'password_hash', None)
        data["last_login_ip"] = getattr(user, 'last_login_ip', None)
        data["login_attempts"] = getattr(user, 'login_attempts', 0)
        data["is_locked"] = getattr(user, 'is_locked', False)
        data["deleted_at"] = getattr(user, 'deleted_at', None)

        # Calcular estadísticas básicas
        transactions = getattr(user, 'transactions', [])
        data["total_orders"] = len(transactions)
        data["total_spent"] = sum(t.amount for t in transactions if t.amount > 0)

        return cls(**data)


class AdminUserUpdate(UserUpdate):
    """
    Schema para actualizaciones de usuario por administradores
    Incluye campos que solo los admins pueden modificar
    """
    is_active: Optional[bool] = Field(None, description="Estado activo del usuario")
    user_type: Optional[UserType] = Field(None, description="Tipo de usuario")
    is_verified: Optional[bool] = Field(None, description="Estado de verificación")
    is_locked: Optional[bool] = Field(None, description="Bloquear/desbloquear cuenta")
    login_attempts: Optional[int] = Field(None, description="Resetear intentos de login")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "nombre": "Juan Carlos",
                "telefono": "+57 300 987 6543",
                "is_active": True,
                "is_verified": True,
                "is_locked": False,
                "user_type": "vendor"
            }
        }
    )


class AdminUserStats(BaseModel):
    """
    Estadísticas rápidas de usuarios para el dashboard admin
    """
    buyer: int = Field(default=0, description="Total de compradores")
    vendor: int = Field(default=0, description="Total de vendedores")
    admin: int = Field(default=0, description="Total de administradores")
    total: int = Field(default=0, description="Total de usuarios")
    active: int = Field(default=0, description="Usuarios activos")
    verified: int = Field(default=0, description="Usuarios verificados")

    def __init__(self, **data):
        # Calcular total automáticamente
        if 'total' not in data:
            data['total'] = data.get('buyer', 0) + data.get('vendor', 0) + data.get('admin', 0)
        super().__init__(**data)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "buyer": 150,
                "vendor": 25,
                "admin": 3,
                "total": 178,
                "active": 165,
                "verified": 140
            }
        }
    )


class AdminUserListResponse(BaseModel):
    """
    Respuesta paginada para la lista de usuarios
    """
    users: List[AdminUserDetail] = Field(..., description="Lista de usuarios")
    total: int = Field(..., description="Total de usuarios que coinciden con filtros")
    skip: int = Field(..., description="Número de usuarios omitidos (offset)")
    limit: int = Field(..., description="Límite de usuarios por página")
    stats: AdminUserStats = Field(..., description="Estadísticas rápidas")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "users": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "jairo.colina.co@gmail.com",
                        "nombre": "Jairo",
                        "apellido": "Colina",
                        "user_type": "buyer",
                        "is_active": True,
                        "is_verified": True,
                        "created_at": "2025-01-15T10:30:00Z",
                        "total_orders": 5
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 50,
                "stats": {
                    "buyer": 1,
                    "vendor": 0,
                    "admin": 0,
                    "total": 1,
                    "active": 1,
                    "verified": 1
                }
            }
        }
    )


class UserResetRequest(BaseModel):
    """
    Schema para solicitud de reset de usuario
    Permite diferentes tipos de reset según las necesidades
    """
    delete_completely: bool = Field(
        default=True,
        description="Si true, elimina completamente para permitir re-registro. Si false, soft delete"
    )
    reason: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Razón del reset (obligatorio para auditoría)"
    )
    preserve_data: bool = Field(
        default=False,
        description="Si true, preserva datos históricos (órdenes, transacciones)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "delete_completely": True,
                "reason": "Reset for testing different registration scenarios",
                "preserve_data": False
            }
        }
    )


class UserResetResponse(BaseModel):
    """
    Respuesta del reset de usuario
    """
    message: str = Field(..., description="Mensaje de confirmación")
    original_email: str = Field(..., description="Email original del usuario")
    can_reregister: bool = Field(..., description="Si el email queda libre para re-registro")
    reset_type: str = Field(..., description="Tipo de reset realizado (complete/partial)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Usuario jairo.colina.co@gmail.com eliminado completamente. Puede registrarse nuevamente.",
                "original_email": "jairo.colina.co@gmail.com",
                "can_reregister": True,
                "reset_type": "complete"
            }
        }
    )


# Exports
__all__ = [
    "AdminUserDetail",
    "AdminUserUpdate",
    "AdminUserStats",
    "AdminUserListResponse",
    "UserResetRequest",
    "UserResetResponse"
]