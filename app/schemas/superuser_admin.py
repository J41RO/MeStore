# ~/app/schemas/superuser_admin.py
# ---------------------------------------------------------------------------------------------
# MeStore - Esquemas Pydantic para Portal de Administrador Superusuario
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: superuser_admin.py
# Ruta: ~/app/schemas/superuser_admin.py
# Autor: Backend Framework AI
# Fecha de Creación: 2025-09-26
# Propósito: Esquemas Pydantic para operaciones avanzadas de administración de usuarios
#            incluye filtrado, paginación, estadísticas y gestión completa de usuarios
#
# ---------------------------------------------------------------------------------------------

"""
Esquemas Pydantic para Portal de Administrador Superusuario.

Este módulo contiene esquemas especializados para:
- Listado paginado de usuarios con filtros avanzados
- Gestión completa de usuarios (CRUD operations)
- Estadísticas y analytics para dashboard administrativo
- Validaciones de seguridad específicas para operaciones críticas
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from uuid import UUID
import re
from enum import Enum

from app.models.user import UserType, VendorStatus
from app.schemas.base import BaseSchema, BaseResponseSchema


class UserFilterSortBy(str, Enum):
    """Opciones de ordenamiento para listado de usuarios."""
    CREATED_AT_DESC = "created_at_desc"
    CREATED_AT_ASC = "created_at_asc"
    EMAIL_ASC = "email_asc"
    EMAIL_DESC = "email_desc"
    LAST_LOGIN_DESC = "last_login_desc"
    LAST_LOGIN_ASC = "last_login_asc"
    USER_TYPE = "user_type"
    IS_ACTIVE = "is_active"


class UserFilterStatus(str, Enum):
    """Estados para filtrar usuarios."""
    ALL = "all"
    ACTIVE = "active"
    INACTIVE = "inactive"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    EMAIL_VERIFIED = "email_verified"
    PHONE_VERIFIED = "phone_verified"


class UserFilterParameters(BaseSchema):
    """
    Parámetros avanzados de filtrado para listado de usuarios.

    Permite filtros complejos para facilitar administración de usuarios.
    """
    # Filtros de búsqueda
    search: Optional[str] = Field(None, description="Búsqueda en email, nombre, apellido o cédula")
    email: Optional[str] = Field(None, description="Filtro exacto por email")

    # Filtros por tipo y estado
    user_type: Optional[UserType] = Field(None, description="Filtrar por tipo de usuario")
    status: Optional[UserFilterStatus] = Field(UserFilterStatus.ALL, description="Estado del usuario")
    is_active: Optional[bool] = Field(None, description="Filtrar por estado activo/inactivo")
    is_verified: Optional[bool] = Field(None, description="Filtrar por verificación general")
    email_verified: Optional[bool] = Field(None, description="Filtrar por verificación de email")
    phone_verified: Optional[bool] = Field(None, description="Filtrar por verificación de teléfono")

    # Filtros de fecha
    created_after: Optional[date] = Field(None, description="Usuarios creados después de esta fecha")
    created_before: Optional[date] = Field(None, description="Usuarios creados antes de esta fecha")
    last_login_after: Optional[date] = Field(None, description="Último login después de esta fecha")
    last_login_before: Optional[date] = Field(None, description="Último login antes de esta fecha")

    # Filtros específicos para vendors
    vendor_status: Optional[VendorStatus] = Field(None, description="Estado específico del vendor")
    has_products: Optional[bool] = Field(None, description="Vendedores con/sin productos")

    # Filtros administrativos
    security_clearance_min: Optional[int] = Field(None, ge=1, le=5, description="Nivel mínimo de clearance")
    security_clearance_max: Optional[int] = Field(None, ge=1, le=5, description="Nivel máximo de clearance")
    department_id: Optional[str] = Field(None, description="ID del departamento")

    # Paginación y ordenamiento
    page: int = Field(1, ge=1, description="Número de página")
    size: int = Field(10, ge=1, le=100, description="Elementos por página")
    sort_by: UserFilterSortBy = Field(UserFilterSortBy.CREATED_AT_DESC, description="Criterio de ordenamiento")

    @field_validator("search")
    @classmethod
    def validate_search_security(cls, v):
        """Validar términos de búsqueda para prevenir inyecciones."""
        if not v:
            return v

        # Remover caracteres peligrosos
        if re.search(r"[<>\"';\\&|`$()]", v):
            raise ValueError("Término de búsqueda contiene caracteres no permitidos")

        # Limitar longitud
        if len(v) > 100:
            raise ValueError("Término de búsqueda demasiado largo (máximo 100 caracteres)")

        return v.strip()

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "search": "juan.perez",
                "user_type": "VENDOR",
                "status": "active",
                "created_after": "2025-01-01",
                "page": 1,
                "size": 20,
                "sort_by": "created_at_desc"
            }
        }
    )


class UserSummary(BaseSchema):
    """
    Resumen básico de usuario para listados.

    Contiene información esencial sin datos sensibles.
    """
    id: str = Field(..., description="ID único del usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    nombre: Optional[str] = Field(None, description="Nombre")
    apellido: Optional[str] = Field(None, description="Apellido")
    full_name: str = Field(..., description="Nombre completo")
    user_type: UserType = Field(..., description="Tipo de usuario")
    is_active: bool = Field(..., description="Estado activo")
    is_verified: bool = Field(..., description="Estado de verificación general")
    email_verified: bool = Field(..., description="Email verificado")
    phone_verified: bool = Field(..., description="Teléfono verificado")
    created_at: datetime = Field(..., description="Fecha de creación")
    last_login: Optional[datetime] = Field(None, description="Último login")

    # Campos específicos para vendors
    vendor_status: Optional[VendorStatus] = Field(None, description="Estado del vendor")
    business_name: Optional[str] = Field(None, description="Nombre del negocio")

    # Campos administrativos
    security_clearance_level: Optional[int] = Field(None, description="Nivel de clearance")
    department_id: Optional[str] = Field(None, description="ID del departamento")
    failed_login_attempts: Optional[int] = Field(None, description="Intentos fallidos de login")
    account_locked: bool = Field(False, description="Cuenta bloqueada")

    model_config = ConfigDict(from_attributes=True)


class UserDetailedInfo(BaseResponseSchema):
    """
    Información detallada completa del usuario.

    Para visualización en detalle de usuario específico.
    """
    email: EmailStr = Field(..., description="Email del usuario")
    nombre: Optional[str] = Field(None, description="Nombre")
    apellido: Optional[str] = Field(None, description="Apellido")
    full_name: str = Field(..., description="Nombre completo")
    user_type: UserType = Field(..., description="Tipo de usuario")
    is_active: bool = Field(..., description="Estado activo")
    is_verified: bool = Field(..., description="Estado de verificación general")

    # Información de verificación
    email_verified: bool = Field(..., description="Email verificado")
    phone_verified: bool = Field(..., description="Teléfono verificado")
    last_login: Optional[datetime] = Field(None, description="Último login")

    # Información personal
    cedula: Optional[str] = Field(None, description="Cédula de ciudadanía")
    telefono: Optional[str] = Field(None, description="Número de teléfono")
    ciudad: Optional[str] = Field(None, description="Ciudad de residencia")
    empresa: Optional[str] = Field(None, description="Empresa")
    direccion: Optional[str] = Field(None, description="Dirección completa")

    # Información específica de vendor
    vendor_status: Optional[VendorStatus] = Field(None, description="Estado del vendor")
    business_name: Optional[str] = Field(None, description="Nombre del negocio")
    business_description: Optional[str] = Field(None, description="Descripción del negocio")
    website_url: Optional[str] = Field(None, description="Sitio web")

    # Información administrativa
    security_clearance_level: Optional[int] = Field(None, description="Nivel de clearance de seguridad")
    department_id: Optional[str] = Field(None, description="ID del departamento")
    employee_id: Optional[str] = Field(None, description="ID de empleado")
    performance_score: Optional[int] = Field(None, description="Puntuación de desempeño")

    # Información de seguridad
    failed_login_attempts: int = Field(0, description="Intentos fallidos de login")
    account_locked_until: Optional[datetime] = Field(None, description="Cuenta bloqueada hasta")
    force_password_change: bool = Field(False, description="Requiere cambio de contraseña")

    # Información bancaria (solo para vendors)
    bank_name: Optional[str] = Field(None, description="Nombre del banco")
    account_holder_name: Optional[str] = Field(None, description="Titular de la cuenta")
    account_number: Optional[str] = Field(None, description="Número de cuenta")

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseSchema):
    """
    Respuesta paginada para listado de usuarios.

    Incluye metadatos de paginación y estadísticas.
    """
    users: List[UserSummary] = Field(..., description="Lista de usuarios")
    total: int = Field(..., description="Total de usuarios que coinciden con filtros")
    page: int = Field(..., description="Página actual")
    size: int = Field(..., description="Elementos por página")
    total_pages: int = Field(..., description="Total de páginas")
    has_next: bool = Field(..., description="Hay página siguiente")
    has_previous: bool = Field(..., description="Hay página anterior")

    # Estadísticas adicionales
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Filtros aplicados")
    summary_stats: Dict[str, Union[int, float]] = Field(default_factory=dict, description="Estadísticas del resultado")

    model_config = ConfigDict(from_attributes=True)


class UserCreateRequest(BaseSchema):
    """
    Schema para crear usuarios desde portal admin.

    Incluye validaciones de seguridad mejoradas.
    """
    email: EmailStr = Field(..., description="Email único del usuario")
    password: str = Field(..., min_length=8, description="Contraseña")
    nombre: str = Field(..., min_length=2, max_length=50, description="Nombre")
    apellido: str = Field(..., min_length=2, max_length=50, description="Apellido")
    user_type: UserType = Field(..., description="Tipo de usuario")

    # Campos opcionales
    cedula: Optional[str] = Field(None, description="Cédula de ciudadanía")
    telefono: Optional[str] = Field(None, description="Teléfono")
    ciudad: Optional[str] = Field(None, description="Ciudad")
    empresa: Optional[str] = Field(None, description="Empresa")
    direccion: Optional[str] = Field(None, description="Dirección")

    # Configuración inicial
    is_active: bool = Field(True, description="Activar usuario inmediatamente")
    is_verified: bool = Field(False, description="Estado de verificación inicial")
    security_clearance_level: int = Field(1, ge=1, le=5, description="Nivel de clearance")

    # Metadatos de creación
    created_by_admin: bool = Field(True, description="Creado por administrador")
    notes: Optional[str] = Field(None, max_length=500, description="Notas del administrador")

    @field_validator("email")
    @classmethod
    def validate_email_security(cls, v):
        """Validación de seguridad para email."""
        if not v:
            raise ValueError("Email es requerido")

        email_str = str(v)

        # Validar patrones de inyección
        injection_patterns = [r"['\";]", r"--", r"/\*", r"\*/", r"<script", r"javascript:"]
        for pattern in injection_patterns:
            if re.search(pattern, email_str, re.IGNORECASE):
                raise ValueError("Email contiene caracteres no permitidos por seguridad")

        if len(email_str) > 254:
            raise ValueError("Email excede longitud máxima")

        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        """Validación de fortaleza de contraseña."""
        if len(v) < 8:
            raise ValueError("Contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Contraseña debe tener al menos una mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("Contraseña debe tener al menos una minúscula")
        if not re.search(r"\d", v):
            raise ValueError("Contraseña debe tener al menos un número")
        if any(pattern in v.lower() for pattern in ["'", '"', "--", "/*", "*/"]):
            raise ValueError("Contraseña contiene caracteres no permitidos")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "usuario@mestore.com",
                "password": "SecurePass123",
                "nombre": "Juan",
                "apellido": "Pérez",
                "user_type": "BUYER",
                "cedula": "12345678",
                "telefono": "+57 300 123 4567",
                "ciudad": "Bogotá",
                "is_active": True,
                "security_clearance_level": 2,
                "notes": "Usuario creado desde panel administrativo"
            }
        }
    )


class UserUpdateRequest(BaseSchema):
    """
    Schema para actualizar usuarios.

    Todos los campos opcionales para actualizaciones parciales.
    """
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    apellido: Optional[str] = Field(None, min_length=2, max_length=50)
    user_type: Optional[UserType] = None
    cedula: Optional[str] = None
    telefono: Optional[str] = None
    ciudad: Optional[str] = None
    empresa: Optional[str] = None
    direccion: Optional[str] = None

    # Estados
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    email_verified: Optional[bool] = None
    phone_verified: Optional[bool] = None

    # Campos administrativos
    security_clearance_level: Optional[int] = Field(None, ge=1, le=5)
    department_id: Optional[str] = None
    employee_id: Optional[str] = None
    performance_score: Optional[int] = Field(None, ge=0, le=100)

    # Configuraciones de seguridad
    force_password_change: Optional[bool] = None
    failed_login_attempts: Optional[int] = Field(None, ge=0)

    # Metadatos
    admin_notes: Optional[str] = Field(None, max_length=500, description="Notas del administrador")

    model_config = ConfigDict(from_attributes=True)


class UserStatsResponse(BaseSchema):
    """
    Estadísticas de usuarios para dashboard administrativo.
    """
    total_users: int = Field(..., description="Total de usuarios")
    active_users: int = Field(..., description="Usuarios activos")
    inactive_users: int = Field(..., description="Usuarios inactivos")
    verified_users: int = Field(..., description="Usuarios verificados")

    # Por tipo de usuario
    buyers: int = Field(..., description="Compradores")
    vendors: int = Field(..., description="Vendedores")
    admins: int = Field(..., description="Administradores")
    superusers: int = Field(..., description="Superusuarios")

    # Estadísticas de verificación
    email_verified: int = Field(..., description="Emails verificados")
    phone_verified: int = Field(..., description="Teléfonos verificados")
    both_verified: int = Field(..., description="Ambos verificados")

    # Estadísticas temporales
    created_today: int = Field(..., description="Creados hoy")
    created_this_week: int = Field(..., description="Creados esta semana")
    created_this_month: int = Field(..., description="Creados este mes")

    # Estadísticas de vendors
    vendor_stats: Dict[str, int] = Field(default_factory=dict, description="Estadísticas específicas de vendors")

    # Actividad reciente
    recent_logins: int = Field(..., description="Logins en últimas 24h")
    locked_accounts: int = Field(..., description="Cuentas bloqueadas")

    # Metadata
    calculated_at: datetime = Field(default_factory=datetime.now, description="Fecha de cálculo")
    period: str = Field("all_time", description="Período de las estadísticas")

    model_config = ConfigDict(from_attributes=True)


class UserDeleteResponse(BaseSchema):
    """
    Respuesta para eliminación de usuarios.

    Incluye información sobre dependencias y cleanup.
    """
    success: bool = Field(..., description="Éxito de la operación")
    user_id: str = Field(..., description="ID del usuario eliminado")
    email: str = Field(..., description="Email del usuario eliminado")
    deleted_at: datetime = Field(default_factory=datetime.now, description="Timestamp de eliminación")

    # Información de cleanup
    dependencies_checked: List[str] = Field(default_factory=list, description="Dependencias verificadas")
    data_cleanup: Dict[str, int] = Field(default_factory=dict, description="Datos eliminados por tabla")
    warnings: List[str] = Field(default_factory=list, description="Advertencias durante eliminación")

    # Metadatos
    deleted_by: str = Field(..., description="ID del administrador que eliminó")
    reason: Optional[str] = Field(None, description="Razón de la eliminación")

    model_config = ConfigDict(from_attributes=True)


class BulkUserActionRequest(BaseSchema):
    """
    Schema para operaciones bulk sobre usuarios.

    Para operaciones masivas como activar/desactivar múltiples usuarios.
    """
    user_ids: List[str] = Field(..., min_length=1, max_length=100, description="Lista de IDs de usuarios")
    action: str = Field(..., description="Acción a realizar")
    reason: Optional[str] = Field(None, max_length=500, description="Razón de la acción")

    # Parámetros específicos por acción
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parámetros adicionales")

    @field_validator("user_ids")
    @classmethod
    def validate_user_ids(cls, v):
        """Validar que todos los IDs sean UUIDs válidos."""
        for user_id in v:
            try:
                UUID(user_id)
            except ValueError:
                raise ValueError(f"ID de usuario inválido: {user_id}")
        return v

    @field_validator("action")
    @classmethod
    def validate_action(cls, v):
        """Validar acción permitida."""
        allowed_actions = [
            "activate", "deactivate", "verify_email", "unverify_email",
            "reset_failed_attempts", "force_password_change", "update_clearance"
        ]
        if v not in allowed_actions:
            raise ValueError(f"Acción no permitida: {v}. Permitidas: {', '.join(allowed_actions)}")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "user_ids": ["uuid1", "uuid2", "uuid3"],
                "action": "activate",
                "reason": "Reactivación masiva post-mantenimiento",
                "parameters": {}
            }
        }
    )


class BulkUserActionResponse(BaseSchema):
    """
    Respuesta para operaciones bulk.
    """
    success: bool = Field(..., description="Éxito general de la operación")
    action: str = Field(..., description="Acción realizada")
    total_requested: int = Field(..., description="Total de usuarios solicitados")
    successful: int = Field(..., description="Operaciones exitosas")
    failed: int = Field(..., description="Operaciones fallidas")

    # Detalles
    successful_users: List[str] = Field(default_factory=list, description="IDs procesados exitosamente")
    failed_users: List[Dict[str, str]] = Field(default_factory=list, description="Fallos con razón")
    warnings: List[str] = Field(default_factory=list, description="Advertencias generales")

    # Metadatos
    processed_at: datetime = Field(default_factory=datetime.now, description="Timestamp de procesamiento")
    processed_by: str = Field(..., description="ID del administrador")

    model_config = ConfigDict(from_attributes=True)


# Exports para facilitar imports
__all__ = [
    "UserFilterParameters",
    "UserFilterSortBy",
    "UserFilterStatus",
    "UserSummary",
    "UserDetailedInfo",
    "UserListResponse",
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserStatsResponse",
    "UserDeleteResponse",
    "BulkUserActionRequest",
    "BulkUserActionResponse"
]