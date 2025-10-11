"""
Schemas de autenticación para endpoints JWT.

Contiene los modelos Pydantic para request/response de autenticación:
- LoginRequest: Datos de entrada para login
- TokenResponse: Respuesta con tokens JWT  
- RefreshTokenRequest: Request para refresh de token
"""

from typing import Optional, Dict, Any
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
                "telefono": "+573001234567",
                "user_type": "VENDOR"
            }
        }
    )

    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=6, description="Contraseña del usuario")
    nombre: str = Field(..., min_length=2, description="Nombre del usuario")
    telefono: str = Field(..., pattern=r'^\+[1-9]\d{1,14}$', description="Teléfono en formato internacional E.164 (+573001234567)")
    user_type: Optional[UserType] = Field(UserType.BUYER, description="Tipo de usuario")


class TokenResponse(BaseModel):
    """Esquema para response de tokens JWT."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": "user-uuid",
                    "email": "admin@mestocker.com",
                    "user_type": "ADMIN",
                    "nombre": "Admin User",
                    "is_active": True,
                    "is_verified": True
                }
            }
        }
    )

    access_token: str = Field(..., description="Token de acceso JWT")
    refresh_token: str = Field(..., description="Token de refresh JWT")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    user: Optional[Dict[str, Any]] = Field(None, description="Información del usuario autenticado")


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
                "new_password": "SecurePass123!"
            }
        }
    )

    token: str = Field(..., min_length=32, max_length=100, description="Token de reset recibido por email")
    new_password: str = Field(..., min_length=8, max_length=128, description="Nueva contraseña (mínimo 8 caracteres)")
    confirm_password: Optional[str] = Field(None, min_length=8, max_length=128, description="Confirmación de la nueva contraseña (opcional, frontend ya valida)")

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        # Only validate if confirm_password is provided
        if v is not None and 'new_password' in info.data and v != info.data['new_password']:
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


# === CUSTOMER REGISTRATION SCHEMAS ===

class CustomerRegisterRequest(BaseModel):
    """Esquema para registro de nuevo comprador/customer."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "cliente@ejemplo.com",
                "password": "MiPassword123",
                "confirm_password": "MiPassword123",
                "first_name": "Juan",
                "last_name": "Pérez",
                "phone": "+573001234567"
            }
        }
    )

    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=8, max_length=128, description="Contraseña (mínimo 8 caracteres)")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Confirmación de contraseña")
    first_name: str = Field(..., min_length=2, max_length=50, description="Nombre(s)")
    last_name: str = Field(..., min_length=2, max_length=50, description="Apellido(s)")
    phone: str = Field(..., pattern=r'^\+[1-9]\d{1,14}$', description="Teléfono en formato internacional E.164 (+573001234567)")

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Valida que las contraseñas coincidan."""
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Valida la fortaleza de la contraseña."""
        import re
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v


class CustomerRegisterResponse(BaseModel):
    """Respuesta del registro de customer."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Registro exitoso. Por favor verifica tu email y teléfono.",
                "user_id": "uuid-here",
                "email": "cliente@ejemplo.com",
                "phone": "+573001234567",
                "account_status": "pending"
            }
        }
    )

    success: bool = Field(..., description="Indica si el registro fue exitoso")
    message: str = Field(..., description="Mensaje descriptivo")
    user_id: str = Field(..., description="ID del usuario creado")
    email: str = Field(..., description="Email registrado")
    phone: str = Field(..., description="Teléfono registrado")
    account_status: str = Field(..., description="Estado de la cuenta (pending, active, suspended)")


class VerifyEmailRequest(BaseModel):
    """Esquema para verificar email con código."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "cliente@ejemplo.com",
                "code": "123456"
            }
        }
    )

    email: EmailStr = Field(..., description="Email a verificar")
    code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$', description="Código de 6 dígitos")


class VerifyPhoneRequest(BaseModel):
    """Esquema para verificar teléfono con código."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "phone": "+573001234567",
                "code": "123456"
            }
        }
    )

    phone: str = Field(..., pattern=r'^\+[1-9]\d{1,14}$', description="Teléfono en formato E.164")
    code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$', description="Código de 6 dígitos")


class VerificationResponse(BaseModel):
    """Respuesta de verificación de email o phone."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Teléfono verificado exitosamente",
                "email_verified": True,
                "phone_verified": True,
                "account_active": True
            }
        }
    )

    success: bool = Field(..., description="Indica si la verificación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")
    email_verified: bool = Field(..., description="Si el email está verificado")
    phone_verified: bool = Field(..., description="Si el teléfono está verificado")
    account_active: bool = Field(..., description="Si la cuenta está activa (ambos verificados)")


# === USER PROFILE UPDATE SCHEMAS ===

class UserProfileUpdateRequest(BaseModel):
    """Esquema para actualización de perfil de usuario."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_type": "VENDOR",
                "cedula": "1098765432",
                "direccion": "Calle 123 #45-67",
                "ciudad": "Bucaramanga",
                "departamento": "Santander",
                "direccion_fiscal": "Carrera 27 #123-45",
                "ciudad_fiscal": "Bucaramanga",
                "departamento_fiscal": "Santander",
                "nombre_empresa": "Mi Empresa S.A.S",
                "nit": "123456789-0",
                "tipo_vendedor": "persona_juridica"
            }
        }
    )

    # Campos actualizables
    user_type: Optional[UserType] = Field(None, description="Tipo de usuario (BUYER/VENDOR)")

    # Campos comunes
    cedula: Optional[str] = Field(None, min_length=8, max_length=10, description="Cédula de ciudadanía")
    direccion: Optional[str] = Field(None, min_length=10, description="Dirección de entrega")
    ciudad: Optional[str] = Field(None, min_length=3, description="Ciudad")
    departamento: Optional[str] = Field(None, min_length=3, description="Departamento")
    codigo_postal: Optional[str] = Field(None, max_length=10, description="Código postal colombiano")

    # Campos de vendedor
    direccion_fiscal: Optional[str] = Field(None, min_length=10, description="Dirección fiscal (vendedores)")
    ciudad_fiscal: Optional[str] = Field(None, min_length=3, description="Ciudad fiscal (vendedores)")
    departamento_fiscal: Optional[str] = Field(None, min_length=3, description="Departamento fiscal (vendedores)")
    nombre_empresa: Optional[str] = Field(None, min_length=3, description="Nombre de empresa (persona jurídica)")
    nit: Optional[str] = Field(None, pattern=r'^\d{9}-\d$', description="NIT (formato: 123456789-0)")
    tipo_vendedor: Optional[str] = Field(None, pattern="^(persona_natural|persona_juridica)$", description="Tipo de vendedor")


class UserProfileUpdateResponse(BaseModel):
    """Respuesta de actualización de perfil."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Perfil actualizado exitosamente",
                "user": {
                    "id": "uuid-here",
                    "email": "usuario@ejemplo.com",
                    "user_type": "VENDOR",
                    "nombre": "Usuario Test",
                    "cedula": "1098765432",
                    "ciudad": "Bucaramanga"
                }
            }
        }
    )

    success: bool = Field(..., description="Indica si la actualización fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")
    user: Dict[str, Any] = Field(..., description="Datos actualizados del usuario")


# === REGISTRO MULTI-TIPO: BUYER, VENDOR NATURAL, VENDOR JURÍDICA ===

class BuyerRegistrationData(BaseModel):
    """Datos específicos para registro de BUYER (Comprador)."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "comprador@ejemplo.com",
                "password": "Comprador123!",
                "nombre": "Carlos",
                "apellido": "Rodríguez",
                "telefono": "+573001234567",
                "cedula": "1098765432",
                "direccion": "Calle 45 #12-34",
                "ciudad": "Bogotá",
                "departamento": "Cundinamarca",
                "codigo_postal": "110111"
            }
        }
    )

    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=8, max_length=128, description="Contraseña (mínimo 8 caracteres)")
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre(s)")
    apellido: Optional[str] = Field(None, min_length=2, max_length=100, description="Apellido(s)")
    telefono: str = Field(..., pattern=r'^\+[1-9]\d{1,14}$', description="Teléfono en formato E.164 (+573001234567)")
    cedula: Optional[str] = Field(None, min_length=8, max_length=10, description="Cédula de ciudadanía")
    direccion: Optional[str] = Field(None, min_length=10, description="Dirección de entrega")
    ciudad: Optional[str] = Field(None, min_length=3, description="Ciudad")
    departamento: Optional[str] = Field(None, min_length=3, description="Departamento")
    codigo_postal: Optional[str] = Field(None, max_length=10, description="Código postal")

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Valida la fortaleza de la contraseña."""
        import re
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v


class VendorNaturalRegistrationData(BaseModel):
    """Datos específicos para registro de VENDOR Persona Natural."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "vendedor@ejemplo.com",
                "password": "Vendedor123!",
                "nombre": "María",
                "apellido": "González",
                "telefono": "+573001234567",
                "cedula": "52123456",
                "direccion": "Carrera 15 #23-45",
                "ciudad": "Medellín",
                "departamento": "Antioquia",
                "codigo_postal": "050001",
                "direccion_fiscal": "Carrera 15 #23-45",
                "ciudad_fiscal": "Medellín",
                "departamento_fiscal": "Antioquia"
            }
        }
    )

    # Campos básicos obligatorios
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=8, max_length=128, description="Contraseña (mínimo 8 caracteres)")
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre(s)")
    apellido: str = Field(..., min_length=2, max_length=100, description="Apellido(s)")
    telefono: str = Field(..., pattern=r'^\+[1-9]\d{1,14}$', description="Teléfono en formato E.164")
    cedula: str = Field(..., min_length=8, max_length=10, description="Cédula de ciudadanía (obligatorio para vendedor)")

    # Dirección personal
    direccion: str = Field(..., min_length=10, description="Dirección de residencia")
    ciudad: str = Field(..., min_length=3, description="Ciudad de residencia")
    departamento: str = Field(..., min_length=3, description="Departamento de residencia")
    codigo_postal: Optional[str] = Field(None, max_length=10, description="Código postal")

    # Dirección fiscal (puede ser la misma que la personal)
    direccion_fiscal: str = Field(..., min_length=10, description="Dirección fiscal")
    ciudad_fiscal: str = Field(..., min_length=3, description="Ciudad fiscal")
    departamento_fiscal: str = Field(..., min_length=3, description="Departamento fiscal")

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Valida la fortaleza de la contraseña."""
        import re
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v


class VendorJuridicaRegistrationData(BaseModel):
    """Datos específicos para registro de VENDOR Persona Jurídica."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "empresa@ejemplo.com",
                "password": "Empresa123!",
                "razon_social": "Distribuidora XYZ S.A.S.",
                "nombre_comercial": "XYZ Store",
                "nit": "890123456-7",
                "representante_legal": "Juan Carlos Pérez",
                "cedula_representante": "79123456",
                "email_representante": "jperez@ejemplo.com",
                "telefono_empresa": "+573101234567",
                "direccion_fiscal": "Carrera 50 #12-34 Oficina 501",
                "ciudad_fiscal": "Cali",
                "departamento_fiscal": "Valle del Cauca",
                "codigo_postal": "760001"
            }
        }
    )

    # Autenticación
    email: EmailStr = Field(..., description="Email corporativo de la empresa")
    password: str = Field(..., min_length=8, max_length=128, description="Contraseña (mínimo 8 caracteres)")

    # Datos de la empresa
    razon_social: str = Field(..., min_length=3, max_length=200, description="Razón social de la empresa")
    nombre_comercial: str = Field(..., min_length=3, max_length=200, description="Nombre comercial del negocio")
    nit: str = Field(..., pattern=r'^\d{9}-\d$', description="NIT de la empresa (formato: 890123456-7)")

    # Datos del representante legal
    representante_legal: str = Field(..., min_length=5, max_length=100, description="Nombre completo del representante legal")
    cedula_representante: str = Field(..., min_length=8, max_length=10, description="Cédula del representante legal")
    email_representante: EmailStr = Field(..., description="Email del representante legal")

    # Contacto empresarial
    telefono_empresa: str = Field(..., pattern=r'^\+[1-9]\d{1,14}$', description="Teléfono corporativo en formato E.164")

    # Dirección fiscal de la empresa
    direccion_fiscal: str = Field(..., min_length=10, description="Dirección fiscal de la empresa")
    ciudad_fiscal: str = Field(..., min_length=3, description="Ciudad fiscal")
    departamento_fiscal: str = Field(..., min_length=3, description="Departamento fiscal")
    codigo_postal: Optional[str] = Field(None, max_length=10, description="Código postal")

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Valida la fortaleza de la contraseña."""
        import re
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v


class MultiTypeRegistrationResponse(BaseModel):
    """Respuesta unificada para registro de cualquier tipo de usuario."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Registro exitoso. Por favor verifica tu email.",
                "user_id": "uuid-here",
                "email": "usuario@ejemplo.com",
                "user_type": "VENDOR",
                "vendor_type": "persona_natural",
                "account_status": "pending",
                "requires_approval": True,
                "next_steps": [
                    "Verifica tu email mediante el enlace enviado",
                    "Completa la verificación SMS",
                    "Espera la aprobación del administrador"
                ]
            }
        }
    )

    success: bool = Field(..., description="Indica si el registro fue exitoso")
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    user_id: str = Field(..., description="ID del usuario creado")
    email: str = Field(..., description="Email registrado")
    user_type: str = Field(..., description="Tipo de usuario: BUYER o VENDOR")
    vendor_type: Optional[str] = Field(None, description="Subtipo de vendor: persona_natural o persona_juridica")
    account_status: str = Field(..., description="Estado de la cuenta: pending, active, draft")
    vendor_status: Optional[str] = Field(None, description="Estado del vendor: draft, pending_documents, etc.")
    requires_approval: bool = Field(..., description="Si requiere aprobación administrativa")
    next_steps: list[str] = Field(..., description="Pasos siguientes para activar la cuenta")