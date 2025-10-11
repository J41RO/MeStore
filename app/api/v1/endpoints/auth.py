# Ruta: MeStore/app/api/v1/endpoints/auth.py
"""
Endpoints de autenticación JWT para la API v1.
Versión corregida sin conflictos entre AuthService.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# IMPORTS INTEGRADOS - Usando IntegratedAuthService para seguridad mejorada
from app.core.integrated_auth import integrated_auth_service
from app.services.auth_service import AuthService  # Fallback legacy
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.services.audit_logging_service import EnterpriseAuditLoggingService
from app.core.security import decode_access_token, decode_refresh_token, create_access_token, create_refresh_token
from app.core.id_validation import IDValidator, normalize_uuid_string
from app.schemas.auth import (
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse,
    OTPSendRequest,
    OTPVerifyRequest,
    OTPResponse,
    UserVerificationStatus,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
    AuthResponse,
    CustomerRegisterRequest,
    CustomerRegisterResponse,
    VerifyEmailRequest,
    VerifyPhoneRequest,
    VerificationResponse,
    UserProfileUpdateRequest,
    UserProfileUpdateResponse,
    BuyerRegistrationData,
    VendorNaturalRegistrationData,
    VendorJuridicaRegistrationData,
    MultiTypeRegistrationResponse
)
from app.core.redis import RedisService, get_redis_service
from app.core.logger import get_logger
from app.services.email_service import EmailService
from app.services.sms_service import SMSService
from app.utils.auth_helpers import generate_verification_code, send_verification_email, send_welcome_email
from app.core.security import get_password_hash
from app.models.user import UserType, AccountStatus, VendorStatus
import secrets
from datetime import datetime, timedelta
from fastapi import BackgroundTasks
from typing import Union

# Configurar router y logger
router = APIRouter()
logger = get_logger(__name__)
security = HTTPBearer()


# Función auxiliar para get_current_user sin conflictos
async def get_current_user_clean(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Obtener usuario actual sin conflictos de AuthService"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Use the centralized decode function for consistency
        payload = decode_access_token(token.credentials)
        if payload is None:
            logger.warning("Token validation failed - payload is None")
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token validation failed - missing sub claim")
            raise credentials_exception
    except Exception as e:
        logger.warning(f"Token decode error: {str(e)}")
        raise credentials_exception

    # Obtener usuario de la base de datos usando async session
    try:
        from sqlalchemy import select
        from app.models.user import UserType

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise credentials_exception

        # Fix user_type enum - handle both lowercase and uppercase values from database
        if hasattr(user, 'user_type') and isinstance(user.user_type, str):
            try:
                # First try direct conversion (for uppercase values)
                user.user_type = UserType(user.user_type)
                logger.debug(f"User type converted successfully: {user.user_type}")
            except ValueError:
                # Handle lowercase values from database - map to uppercase enum
                user_type_mapping = {
                    'buyer': UserType.BUYER,
                    'vendor': UserType.VENDOR,
                    'admin': UserType.ADMIN,
                    'superuser': UserType.SUPERUSER,
                    'system': UserType.SYSTEM
                }

                mapped_type = user_type_mapping.get(user.user_type.lower())
                if mapped_type:
                    user.user_type = mapped_type
                    logger.info(f"User type mapped from '{user.user_type}' to '{mapped_type}'")
                else:
                    # Set a default value if mapping fails
                    user.user_type = UserType.BUYER
                    logger.warning(f"Unknown user_type '{user.user_type}', defaulting to BUYER")

        return user
    except Exception as e:
        logger.error(f"Database error in get_current_user_clean: {str(e)}")
        raise credentials_exception


def get_auth_service():
    """Obtener servicio de autenticación integrado con características de seguridad mejoradas."""
    return integrated_auth_service

def get_legacy_auth_service() -> AuthService:
    """Fallback al AuthService legacy si es necesario."""
    return AuthService()


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Endpoint de autenticación con email y contraseña con seguridad mejorada.
    Incluye protección contra ataques de fuerza bruta y logging de seguridad.
    """
    logger.info("Intento de login con seguridad integrada", email=login_data.email)
    auth_service = get_auth_service()

    # Extraer información de seguridad
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent", "Unknown")

    try:
        # Verificar protección contra fuerza bruta
        if not await auth_service.check_brute_force_protection(login_data.email, ip_address):
            logger.warning("Login bloqueado por protección de fuerza bruta",
                         email=login_data.email, ip=ip_address)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiados intentos fallidos. Cuenta temporalmente bloqueada."
            )

        # Validar credenciales usando IntegratedAuthService
        user = await auth_service.authenticate_user(db,
            login_data.email,
            login_data.password,

            ip_address=ip_address,
            user_agent=user_agent
        )

        if not user:
            logger.warning("Login fallido - credenciales inválidas",
                         email=login_data.email, ip=ip_address)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Generar tokens JWT usando IntegratedAuthService con seguridad mejorada
        access_token, refresh_token = await auth_service.create_user_session(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Ensure consistent ID format in token
        normalized_id = normalize_uuid_string(user.id)

        logger.info("Login exitoso con sesión segura",
                   user_id=normalized_id, email=user.email,
                   user_type=user.user_type.value, ip=ip_address)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            user={
                "id": normalized_id,
                "email": user.email,
                "user_type": user.user_type.value,
                "nombre": getattr(user, 'nombre', None),
                "is_active": getattr(user, 'is_active', True),
                "is_verified": getattr(user, 'is_verified', False)
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error interno en login", error=str(e), email=login_data.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/admin-login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def admin_login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Endpoint de autenticación administrativo con verificación de privilegios.
    Solo permite login a usuarios ADMIN y SUPERUSER.
    """
    logger.info("Intento de login administrativo", email=login_data.email)
    auth_service = get_auth_service()

    # Extraer información de seguridad
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent", "Unknown")

    try:
        # Verificar protección contra fuerza bruta
        if not await auth_service.check_brute_force_protection(login_data.email, ip_address):
            logger.warning("Admin login bloqueado por protección de fuerza bruta",
                         email=login_data.email, ip=ip_address)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiados intentos fallidos. Cuenta temporalmente bloqueada."
            )

        # Validar credenciales usando IntegratedAuthService
        user = await auth_service.authenticate_user(db, 
            login_data.email,
            login_data.password,
            
            ip_address=ip_address,
            user_agent=user_agent
        )

        if not user:
            logger.warning("Admin login fallido - credenciales inválidas",
                         email=login_data.email, ip=ip_address)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # 🛡️ VERIFICACIÓN CRÍTICA DE PRIVILEGIOS ADMINISTRATIVOS - NO MODIFICAR SIN AUTORIZACIÓN
        # Esta validación garantiza que solo OWNER, SUPERUSER y ADMIN puedan acceder al portal administrativo
        # CUALQUIER MODIFICACIÓN DEBE SER APROBADA POR EL USUARIO PRINCIPAL
        from app.models.user import UserType
        allowed_roles = [
            UserType.OWNER,
            UserType.SUPERUSER,
            UserType.ADMIN,
            UserType.ADMIN_SALES,
            UserType.ADMIN_SUPPORT,
            UserType.ADMIN_LOGISTICS,
            UserType.ADMIN_MARKETING
        ]
        if user.user_type not in allowed_roles:
            logger.warning("Acceso administrativo denegado - privilegios insuficientes",
                         email=login_data.email, user_type=user.user_type.value, ip=ip_address)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privilegios administrativos requeridos"
            )

        # Generar tokens JWT usando IntegratedAuthService con seguridad mejorada
        access_token, refresh_token = await auth_service.create_user_session(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Ensure consistent ID format in token
        normalized_id = normalize_uuid_string(user.id)

        logger.info("Admin login exitoso",
                   user_id=normalized_id, email=user.email,
                   user_type=user.user_type.value, ip=ip_address)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            user={
                "id": normalized_id,
                "email": user.email,
                "user_type": user.user_type.value,
                "nombre": getattr(user, 'nombre', None),
                "is_active": getattr(user, 'is_active', True),
                "is_verified": getattr(user, 'is_verified', False)
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error interno en admin login", error=str(e), email=login_data.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )



@router.get("/me", response_model=dict, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: User = Depends(get_current_user_clean)
) -> Dict[str, Any]:
    """
    Obtener información del usuario actual autenticado.
    """
    try:
        # DEBUG: Log user info to debug null ID issue
        logger.debug(f"get_current_user_info DEBUG: current_user.id = {current_user.id}")
        logger.debug(f"get_current_user_info DEBUG: current_user.email = {current_user.email}")

        # TEMPORARY FIX: Handle null ID gracefully
        user_id = normalize_uuid_string(current_user.id)
        if user_id is None:
            logger.warning(f"User {current_user.email} has null ID, using email as fallback")
            user_id = current_user.email

        return {
            "id": user_id,
            "email": current_user.email,
            "nombre": getattr(current_user, 'nombre', current_user.email.split('@')[0]),
            "user_type": current_user.user_type.value if hasattr(current_user.user_type, 'value') else str(current_user.user_type),
            "email_verified": getattr(current_user, 'email_verified', False),
            "phone_verified": getattr(current_user, 'phone_verified', False),
            "is_active": getattr(current_user, 'is_active', True)
        }

    except Exception as e:
        logger.error(f"Error en get_current_user_info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener información del usuario"
        )


@router.put("/users/me", response_model=UserProfileUpdateResponse, status_code=status.HTTP_200_OK)
async def update_current_user_profile(
    update_data: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user_clean),
    db: AsyncSession = Depends(get_db)
) -> UserProfileUpdateResponse:
    """
    Actualizar perfil del usuario actual.

    Permite actualizar:
    - user_type (BUYER/VENDOR)
    - Datos personales (cédula, dirección, ciudad, departamento)
    - Datos de vendedor (dirección fiscal, nombre empresa, NIT, tipo vendedor)

    Requiere autenticación JWT.
    Solo el propio usuario puede actualizar su perfil.
    """
    try:
        logger.info(f"🔄 Actualizando perfil de usuario", user_id=str(current_user.id), email=current_user.email)

        # Actualizar solo los campos que fueron enviados (no None)
        update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)

        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar"
            )

        logger.info(f"📝 Campos a actualizar: {list(update_dict.keys())}")

        # Actualizar user_type si fue enviado
        if "user_type" in update_dict:
            new_user_type = update_dict.pop("user_type")
            current_user.user_type = UserType(new_user_type) if isinstance(new_user_type, str) else new_user_type
            logger.info(f"✅ user_type actualizado a: {current_user.user_type.value}")

        # Actualizar resto de campos
        for field, value in update_dict.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
                logger.debug(f"✅ {field} actualizado")
            else:
                logger.warning(f"⚠️ Campo ignorado (no existe en modelo): {field}")

        # Guardar cambios
        await db.commit()
        await db.refresh(current_user)

        logger.info(f"✅ Perfil actualizado exitosamente", user_id=str(current_user.id))

        # Preparar respuesta
        user_id = normalize_uuid_string(current_user.id)
        user_response = {
            "id": user_id,
            "email": current_user.email,
            "user_type": current_user.user_type.value if hasattr(current_user.user_type, 'value') else str(current_user.user_type),
            "nombre": getattr(current_user, 'nombre', None),
            "cedula": getattr(current_user, 'cedula', None),
            "direccion": getattr(current_user, 'direccion', None),
            "ciudad": getattr(current_user, 'ciudad', None),
            "departamento": getattr(current_user, 'departamento', None),
            "direccion_fiscal": getattr(current_user, 'direccion_fiscal', None),
            "ciudad_fiscal": getattr(current_user, 'ciudad_fiscal', None),
            "departamento_fiscal": getattr(current_user, 'departamento_fiscal', None),
            "nombre_empresa": getattr(current_user, 'nombre_empresa', None),
            "nit": getattr(current_user, 'nit', None),
            "tipo_vendedor": getattr(current_user, 'tipo_vendedor', None)
        }

        # Remover campos None de la respuesta
        user_response = {k: v for k, v in user_response.items() if v is not None}

        return UserProfileUpdateResponse(
            success=True,
            message="Perfil actualizado exitosamente",
            user=user_response
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error actualizando perfil: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


# Endpoints adicionales simplificados para funcionalidad básica
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Registrar nuevo usuario con verificación de email y SMS.

    Flujo:
    1. Valida que email y teléfono no existan
    2. Crea usuario con email_verified=False, phone_verified=False
    3. Genera código de verificación de email
    4. Envía email con código de verificación
    5. Envía SMS con código Twilio Verify
    6. Retorna tokens JWT para acceso inmediato
    """
    logger.info(f"🔄 Register attempt with data: {user_data.dict()}")

    try:
        # 1. Verificar si email ya existe
        logger.info(f"🔍 Verificando unicidad de email: {user_data.email}")
        existing_user = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing_user.scalar_one_or_none():
            logger.warning(f"⚠️ Email ya registrado: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado. Por favor usa otro correo o inicia sesión."
            )
        logger.info(f"✅ Email disponible: {user_data.email}")

        # 2. Verificar si teléfono ya existe
        logger.info(f"🔍 Verificando unicidad de teléfono: {user_data.telefono}")
        existing_phone = await db.execute(
            select(User).where(User.telefono == user_data.telefono)
        )
        if existing_phone.scalar_one_or_none():
            logger.warning(f"⚠️ Teléfono ya registrado: {user_data.telefono}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El teléfono ya está registrado. Por favor usa otro número."
            )
        logger.info(f"✅ Teléfono disponible: {user_data.telefono}")

        # 3. Crear usuario
        logger.info(f"🔐 Generando hash de contraseña")
        password_hash = await get_password_hash(user_data.password)

        logger.info(f"👤 Creando usuario en base de datos")
        user_type_enum = UserType(user_data.user_type.value) if user_data.user_type else UserType.BUYER

        new_user = User(
            email=user_data.email,
            password_hash=password_hash,
            nombre=user_data.nombre,
            telefono=user_data.telefono,
            user_type=user_type_enum,
            is_active=True,
            email_verified=False,
            phone_verified=False
        )

        db.add(new_user)
        logger.info(f"💾 Usuario agregado a sesión DB, ejecutando flush")
        await db.flush()
        logger.info(f"✅ Flush completado, user_id obtenido: {new_user.id}")

        # 4. Generar token de verificación de email (en lugar de código)
        logger.info(f"🎲 Generando token de verificación de email")
        email_token = secrets.token_urlsafe(32)  # Token seguro de 32 bytes
        new_user.email_verification_token = email_token
        new_user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)  # 24 horas de validez
        logger.info(f"✅ Token de verificación generado (expira en 24 horas)")

        # 5. Commit a base de datos ANTES de enviar emails/SMS
        logger.info(f"💾 Ejecutando commit a base de datos")
        await db.commit()
        logger.info(f"✅ Commit exitoso, refrescando usuario")
        await db.refresh(new_user)

        logger.info(f"✅ Usuario creado exitosamente", user_id=str(new_user.id), email=new_user.email)

        # 6. Enviar email de verificación con link (background task)
        logger.info(f"📧 Programando envío de email de verificación con link")
        from app.core.config import settings
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={email_token}"
        background_tasks.add_task(
            send_verification_email,
            new_user.email,
            email_token,  # Enviar token en lugar de código
            user_data.nombre,
            verification_link  # Agregar link como parámetro adicional
        )
        logger.info(f"✅ Email de verificación con link programado")

        # 7. Enviar SMS de verificación (Twilio Verify)
        try:
            logger.info(f"📱 Iniciando envío de SMS verification con Twilio")
            sms_service = SMSService()
            sms_result = await sms_service.send_verification_code(
                phone_number=user_data.telefono,
                channel="sms"
            )
            logger.info(f"✅ SMS verification enviado", phone=user_data.telefono, status=sms_result.get('status'))
        except Exception as sms_error:
            logger.error(f"❌ Error enviando SMS verification: {str(sms_error)}")
            logger.error(f"❌ SMS error type: {type(sms_error).__name__}", exc_info=True)
            # No fallar el registro si SMS falla, el usuario puede reenviar

        # 8. Generar tokens JWT para acceso inmediato
        normalized_id = normalize_uuid_string(new_user.id)
        token_data = {
            "sub": normalized_id,
            "user_id": normalized_id,
            "user_type": new_user.user_type.value,
            "email": new_user.email
        }
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data={"sub": normalized_id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            user={
                "id": normalized_id,
                "email": new_user.email,
                "user_type": new_user.user_type.value,
                "nombre": new_user.nombre,
                "telefono": new_user.telefono,
                "is_active": True,
                "is_verified": False,
                "email_verified": False,
                "phone_verified": False
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR en register: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}", exc_info=True)

        # Rollback de la transacción
        try:
            await db.rollback()
            logger.info(f"✅ Database rollback completado")
        except Exception as rollback_error:
            logger.error(f"❌ Error en rollback: {str(rollback_error)}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando registro de usuario: {type(e).__name__} - {str(e)}"
        )

# Password reset endpoints moved below (lines 817+) with EmailService implementation

# ===== OTP/SMS VERIFICATION ENDPOINTS =====

@router.post("/send-verification-email", response_model=OTPResponse, status_code=status.HTTP_200_OK)
async def send_verification_email_endpoint(
    request: OTPSendRequest,
    current_user: User = Depends(get_current_user_clean),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(lambda: AuthService())
) -> OTPResponse:
    """
    Envía código OTP por email para verificación.

    - **otp_type**: Debe ser "EMAIL" para este endpoint
    - Requiere autenticación JWT
    - El usuario debe tener email registrado
    - Respeta cooldown de 1 minuto entre envíos
    """
    try:
        # Validar que el tipo sea EMAIL
        if request.otp_type != "EMAIL":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este endpoint solo acepta otp_type: EMAIL"
            )

        # Verificar que no esté ya verificado
        if current_user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ya está verificado"
            )

        # Enviar OTP por email
        success, message = await auth_service.send_email_verification_otp(db, current_user)

        if success:
            verification_status = await auth_service.get_user_verification_status(current_user)
            return OTPResponse(
                success=True,
                message=message,
                verification_status=verification_status
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en send_verification_email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/send-verification-sms", response_model=OTPResponse, status_code=status.HTTP_200_OK)
async def send_verification_sms_endpoint(
    request: OTPSendRequest,
    current_user: User = Depends(get_current_user_clean),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(lambda: AuthService())
) -> OTPResponse:
    """
    Envía código OTP por SMS para verificación.

    - **otp_type**: Debe ser "SMS" para este endpoint
    - Requiere autenticación JWT
    - El usuario debe tener teléfono registrado
    - Respeta cooldown de 1 minuto entre envíos
    - Rate limiting: 5 SMS por hora por número
    """
    try:
        # Validar que el tipo sea SMS
        if request.otp_type != "SMS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este endpoint solo acepta otp_type: SMS"
            )

        # Verificar que tiene teléfono
        if not current_user.telefono:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no tiene teléfono registrado"
            )

        # Verificar que no esté ya verificado
        if current_user.phone_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teléfono ya está verificado"
            )

        # Enviar OTP por SMS
        success, message = await auth_service.send_sms_verification_otp(db, current_user)

        if success:
            verification_status = await auth_service.get_user_verification_status(current_user)
            return OTPResponse(
                success=True,
                message=message,
                verification_status=verification_status
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en send_verification_sms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/verify-email-otp", response_model=OTPResponse, status_code=status.HTTP_200_OK)
async def verify_email_otp(
    request: OTPVerifyRequest,
    current_user: User = Depends(get_current_user_clean),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(lambda: AuthService())
) -> OTPResponse:
    """
    Verifica código OTP de email.

    - **otp_code**: Código de 6 dígitos recibido por email
    - Requiere autenticación JWT
    - Máximo 5 intentos por código
    - Al verificar exitosamente, marca email_verified=True
    """
    try:
        # Verificar que tenga OTP activo de tipo EMAIL
        if not current_user.otp_secret or current_user.otp_type != "EMAIL":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay código OTP de email activo"
            )

        # TESTING BYPASS: Permitir código especial para pruebas (funciona con cualquier email en desarrollo)
        testing_bypass_code = "123456"
        from app.core.config import settings
        is_development = settings.ENVIRONMENT.lower() in ["development", "dev", "testing"]
        is_test_email = current_user.email.endswith((".test.com", ".testing.com", ".dev.com", ".example.com"))
        is_real_email = current_user.email.endswith((".gmail.com", ".outlook.com", ".hotmail.com", ".yahoo.com", ".icloud.com"))

        if request.otp_code == testing_bypass_code and (is_test_email or (is_development and is_real_email)):
            logger.info(f"Email OTP testing bypass usado por usuario: {current_user.email}")
            success, message = True, "Código OTP verificado exitosamente (testing bypass)"
            # Mark email as verified
            current_user.email_verified = True
            current_user.otp_secret = None
            current_user.otp_expires_at = None
            current_user.otp_attempts = 0
            current_user.otp_type = None
            await db.commit()
        else:
            # Verificar código OTP normal
            success, message = await auth_service.verify_otp_code(db, current_user, request.otp_code)

        if success:
            verification_status = await auth_service.get_user_verification_status(current_user)
            return OTPResponse(
                success=True,
                message=message,
                verification_status=verification_status
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en verify_email_otp: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/verify-phone-otp", response_model=OTPResponse, status_code=status.HTTP_200_OK)
async def verify_phone_otp(
    request: OTPVerifyRequest,
    current_user: User = Depends(get_current_user_clean),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(lambda: AuthService())
) -> OTPResponse:
    """
    Verifica código OTP de SMS.

    - **otp_code**: Código de 6 dígitos recibido por SMS
    - Requiere autenticación JWT
    - Máximo 5 intentos por código
    - Al verificar exitosamente, marca phone_verified=True
    """
    try:
        # Verificar que tenga OTP activo de tipo SMS
        if not current_user.otp_secret or current_user.otp_type != "SMS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay código OTP de SMS activo"
            )

        # TESTING BYPASS: Permitir código especial para pruebas (funciona con cualquier email en desarrollo)
        testing_bypass_code = "123456"
        from app.core.config import settings
        is_development = settings.ENVIRONMENT.lower() in ["development", "dev", "testing"]
        is_test_email = current_user.email.endswith((".test.com", ".testing.com", ".dev.com", ".example.com"))
        is_real_email = current_user.email.endswith((".gmail.com", ".outlook.com", ".hotmail.com", ".yahoo.com", ".icloud.com"))

        if request.otp_code == testing_bypass_code and (is_test_email or (is_development and is_real_email)):
            logger.info(f"SMS OTP testing bypass usado por usuario: {current_user.email}")
            success, message = True, "Código OTP verificado exitosamente (testing bypass)"
            # Mark phone as verified
            current_user.phone_verified = True
            current_user.otp_secret = None
            current_user.otp_expires_at = None
            current_user.otp_attempts = 0
            current_user.otp_type = None
            await db.commit()
        else:
            # Verificar código OTP normal
            success, message = await auth_service.verify_otp_code(db, current_user, request.otp_code)

        if success:
            verification_status = await auth_service.get_user_verification_status(current_user)
            return OTPResponse(
                success=True,
                message=message,
                verification_status=verification_status
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en verify_phone_otp: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


# ===== EMAIL VERIFICATION BY TOKEN (LINK) =====

@router.get("/verify-email", response_model=VerificationResponse, status_code=status.HTTP_200_OK)
async def verify_email_by_token(
    token: str = Query(..., description="Token de verificación recibido por email"),
    db: AsyncSession = Depends(get_db)
) -> VerificationResponse:
    """
    Verifica email del usuario mediante token de verificación (link clickeable).

    Este endpoint procesa el token enviado en el link del email de verificación.
    Al hacer clic en el botón "Verificar Email" del correo, el usuario es dirigido aquí.

    Args:
        token: Token de verificación único de 32 bytes (generado en /register)

    Returns:
        VerificationResponse con estado de verificación

    Raises:
        HTTPException 400: Token inválido o expirado
        HTTPException 404: Usuario no encontrado
    """
    try:
        logger.info(f"🔗 Verificando email por token (longitud: {len(token)})")

        # 1. Buscar usuario con el token y que no esté expirado
        result = await db.execute(
            select(User).where(
                User.email_verification_token == token,
                User.email_verification_expires > datetime.utcnow()
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"⚠️ Token inválido o expirado")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de verificación inválido o expirado. Por favor solicita un nuevo email de verificación."
            )

        logger.info(f"✅ Token válido para usuario", user_id=str(user.id), email=user.email)

        # 2. Verificar si ya está verificado (evitar doble verificación)
        if user.email_verified:
            logger.info(f"ℹ️ Email ya estaba verificado", email=user.email)
            return VerificationResponse(
                success=True,
                message="Tu email ya estaba verificado anteriormente",
                email_verified=True,
                phone_verified=user.phone_verified,
                account_active=(user.account_status == AccountStatus.ACTIVE)
            )

        # 3. Marcar email como verificado
        user.email_verified = True
        user.email_verification_token = None  # Limpiar token usado
        user.email_verification_expires = None  # Limpiar expiración

        logger.info(f"✅ Email marcado como verificado", email=user.email)

        # 4. Si teléfono también está verificado, activar cuenta
        account_now_active = False
        if user.phone_verified and user.account_status != AccountStatus.ACTIVE:
            user.account_status = AccountStatus.ACTIVE
            account_now_active = True
            logger.info(f"🎉 Cuenta activada completamente (email + teléfono verificados)", user_id=str(user.id))

        await db.commit()
        await db.refresh(user)

        logger.info(f"✅ Verificación de email por token completada exitosamente", email=user.email)

        # 5. Preparar mensaje apropiado
        if account_now_active:
            message = "¡Email verificado exitosamente! Tu cuenta está ahora completamente activa."
        elif user.phone_verified:
            message = "Email verificado exitosamente. Tu cuenta ya estaba activa."
        else:
            message = "Email verificado exitosamente. Ahora verifica tu número de teléfono para activar tu cuenta."

        return VerificationResponse(
            success=True,
            message=message,
            email_verified=True,
            phone_verified=user.phone_verified,
            account_active=(user.account_status == AccountStatus.ACTIVE)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en verify_email_by_token: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando verificación de email"
        )


@router.post("/refresh-token", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Refrescar access token usando refresh token."""
    try:
        # Decodificar refresh token
        payload = decode_refresh_token(request.refresh_token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
            
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Verificar usuario existe usando async session
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
        
        # Generar nuevos tokens with consistent ID format
        normalized_id = normalize_uuid_string(user.id)
        access_token = create_access_token(data={"sub": normalized_id})
        new_refresh_token = create_refresh_token(data={"sub": normalized_id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=3600
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en refresh_token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )


@router.post("/logout", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user_clean)
) -> AuthResponse:
    """
    Endpoint para logout/cierre de sesión.
    """
    try:
        logger.info("Logout exitoso", user_id=normalize_uuid_string(current_user.id), email=current_user.email)
        
        return AuthResponse(
            success=True,
            message="Sesión cerrada exitosamente"
        )
        
    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


# ============================================================================
# PASSWORD RESET ENDPOINTS
# ============================================================================

@router.post("/forgot-password", response_model=PasswordResetResponse)
async def forgot_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
) -> PasswordResetResponse:
    """
    Endpoint para solicitar recuperación de contraseña.
    Genera un token de recuperación y envía email al usuario.

    Security: No revela si el email existe o no para prevenir enumeración de usuarios.
    """
    try:
        from sqlalchemy import select

        # Buscar usuario por email
        result = await db.execute(
            select(User).where(User.email == request.email.lower())
        )
        user = result.scalar_one_or_none()

        # IMPORTANT: Siempre retornar success para prevenir enumeración de usuarios
        if not user:
            logger.warning(f"Password reset solicitado para email no existente", email=request.email)
            return PasswordResetResponse(
                success=True,
                message="Si el correo existe en nuestro sistema, recibirás un enlace de recuperación."
            )

        # Verificar que el usuario esté activo
        if not user.is_active:
            logger.warning(f"Password reset solicitado para usuario inactivo", email=request.email, user_id=str(user.id))
            return PasswordResetResponse(
                success=True,
                message="Si el correo existe en nuestro sistema, recibirás un enlace de recuperación."
            )

        # Generar token de recuperación seguro (permitido para TODOS los usuarios: Admin, Vendor, Buyer)
        reset_token = secrets.token_urlsafe(32)

        # Guardar token en base de datos con expiración de 1 hora
        user.reset_token = reset_token
        user.reset_token_expires_at = datetime.utcnow() + timedelta(hours=1)
        await db.commit()

        # Enviar email con enlace de recuperación
        try:
            email_service = EmailService()
            await email_service.send_password_reset_email(
                to_email=user.email,
                user_name=user.nombre or user.email.split('@')[0],
                reset_token=reset_token
            )
            logger.info(f"Password reset email enviado", email=user.email)
        except Exception as email_error:
            logger.error(f"Error enviando email de reset: {str(email_error)}", email=user.email)
            # Revertir cambios en BD si falla el envío de email
            user.reset_token = None
            user.reset_token_expires_at = None
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error enviando email de recuperación. Por favor intenta de nuevo."
            )

        return PasswordResetResponse(
            success=True,
            message="Si el correo existe en nuestro sistema, recibirás un enlace de recuperación."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en forgot-password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando solicitud de recuperación"
        )


@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
) -> PasswordResetResponse:
    """
    Endpoint para restablecer contraseña con token.
    Valida el token y actualiza la contraseña del usuario.
    """
    try:
        from sqlalchemy import select
        from app.core.security import hash_password

        # Buscar usuario por token
        result = await db.execute(
            select(User).where(User.reset_token == request.token)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de recuperación inválido o expirado"
            )

        # Verificar que el token no haya expirado
        if not user.is_reset_token_valid():
            # Limpiar token expirado
            user.reset_token = None
            user.reset_token_expires_at = None
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de recuperación expirado. Solicita uno nuevo."
            )

        # Validar que las contraseñas coincidan (solo si confirm_password fue enviado)
        if request.confirm_password and request.new_password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las contraseñas no coinciden"
            )

        # Validar fortaleza de contraseña
        if len(request.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe tener al menos 8 caracteres"
            )

        # Validar que la nueva contraseña sea diferente a la anterior
        from app.core.security import verify_password
        is_same_password = await verify_password(request.new_password, user.password_hash)
        if is_same_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe ser diferente a la anterior"
            )

        # Actualizar contraseña
        user.password_hash = await hash_password(request.new_password)

        # Limpiar token de recuperación
        user.reset_token = None
        user.reset_token_expires_at = None

        await db.commit()

        # Enviar email de confirmación
        try:
            email_service = EmailService()
            await email_service.send_password_changed_email(
                to_email=user.email,
                user_name=user.nombre or user.email.split('@')[0]
            )
            logger.info(f"Password actualizado exitosamente y email de confirmación enviado", email=user.email)
        except Exception as email_error:
            logger.error(f"Error enviando email de confirmación: {str(email_error)}", email=user.email)
            # No fallar si el email de confirmación falla, la contraseña ya fue actualizada

        return PasswordResetResponse(
            success=True,
            message="Tu contraseña ha sido actualizada correctamente. Revisa tu email para confirmar el cambio."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en reset-password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando actualización de contraseña"
        )


# =============================================================================
# CUSTOMER REGISTRATION ENDPOINTS
# =============================================================================

@router.post(
    '/register/customer',
    response_model=CustomerRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo comprador/customer",
    description="Crea cuenta de comprador, envía códigos de verificación por email y SMS"
)
async def register_customer(
    data: CustomerRegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Registro de nuevo comprador con verificación dual (email + SMS).

    Flujo:
    1. Valida datos y contraseña
    2. Verifica que email y teléfono no existan
    3. Crea usuario con account_status=PENDING
    4. Genera y envía código de verificación por email
    5. Envía código de verificación por SMS (Twilio Verify)
    6. Envía email de bienvenida
    7. Retorna información del usuario creado
    """
    try:
        logger.info(f"📝 Iniciando registro de customer", email=data.email)

        # 1. Verificar si email ya existe
        logger.info(f"🔍 Verificando unicidad de email: {data.email}")
        existing_user = await db.execute(
            select(User).where(User.email == data.email)
        )
        if existing_user.scalar_one_or_none():
            logger.warning(f"⚠️ Email ya registrado: {data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        logger.info(f"✅ Email disponible: {data.email}")

        # 2. Verificar si teléfono ya existe
        logger.info(f"🔍 Verificando unicidad de teléfono: {data.phone}")
        existing_phone = await db.execute(
            select(User).where(User.telefono == data.phone)
        )
        if existing_phone.scalar_one_or_none():
            logger.warning(f"⚠️ Teléfono ya registrado: {data.phone}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El teléfono ya está registrado"
            )
        logger.info(f"✅ Teléfono disponible: {data.phone}")

        # 3. Crear usuario con account_status=PENDING
        logger.info(f"🔐 Generando hash de contraseña")
        password_hash = await get_password_hash(data.password)

        logger.info(f"👤 Creando usuario en base de datos")
        new_user = User(
            email=data.email,
            password_hash=password_hash,
            nombre=f"{data.first_name} {data.last_name}",
            telefono=data.phone,
            user_type=UserType.BUYER,
            account_status=AccountStatus.PENDING,
            is_active=True,  # Activo pero pendiente de verificación
            email_verified=False,
            phone_verified=False
        )

        db.add(new_user)
        logger.info(f"💾 Usuario agregado a sesión DB, ejecutando flush")
        await db.flush()  # Get user ID without committing
        logger.info(f"✅ Flush completado, user_id obtenido: {new_user.id}")

        # 4. Generar token de verificación de email (en lugar de código)
        logger.info(f"🎲 Generando token de verificación de email")
        email_token = secrets.token_urlsafe(32)  # Token seguro de 32 bytes
        new_user.email_verification_token = email_token
        new_user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)  # 24 horas de validez
        logger.info(f"✅ Token de verificación generado (expira en 24 horas)")

        logger.info(f"💾 Ejecutando commit a base de datos")
        await db.commit()
        logger.info(f"✅ Commit exitoso, refrescando usuario")
        await db.refresh(new_user)

        logger.info(f"✅ Usuario creado exitosamente", user_id=str(new_user.id), email=new_user.email)

        # 5. Enviar código de verificación por email (background)
        logger.info(f"📧 Programando envío de email de verificación")
        background_tasks.add_task(
            send_verification_email,
            new_user.email,      # Parámetro posicional: email
            email_code,          # Parámetro posicional: code
            data.first_name      # Parámetro posicional: name
        )
        logger.info(f"✅ Email de verificación programado en background tasks")

        # 6. Enviar código de verificación por SMS (Twilio Verify)
        try:
            logger.info(f"📱 Iniciando envío de SMS verification con Twilio")
            sms_service = SMSService()
            sms_result = await sms_service.send_verification_code(
                phone_number=data.phone,
                channel="sms"
            )
            logger.info(f"✅ SMS verification enviado", phone=data.phone, status=sms_result.get('status'))
        except Exception as sms_error:
            logger.error(f"❌ Error enviando SMS verification: {str(sms_error)}")
            logger.error(f"❌ SMS error type: {type(sms_error).__name__}", exc_info=True)
            # No fallar el registro si SMS falla, el usuario puede reenviar

        return CustomerRegisterResponse(
            success=True,
            message="Registro exitoso. Por favor verifica tu email y teléfono.",
            user_id=str(new_user.id),
            email=new_user.email,
            phone=new_user.telefono,
            account_status=new_user.account_status.value
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR en register_customer: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        logger.error(f"❌ Full traceback:", exc_info=True)

        # Rollback de la transacción
        try:
            await db.rollback()
            logger.info(f"✅ Database rollback completado")
        except Exception as rollback_error:
            logger.error(f"❌ Error en rollback: {str(rollback_error)}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando registro de usuario: {type(e).__name__} - {str(e)}"
        )


@router.post(
    '/verify/email',
    response_model=VerificationResponse,
    summary="Verificar email con código",
    description="Verifica el email del usuario con código de 6 dígitos"
)
async def verify_email(
    data: VerifyEmailRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica el email del usuario con código de 6 dígitos.

    Si email y teléfono están verificados, activa la cuenta (account_status=ACTIVE).
    """
    try:
        logger.info(f"📧 Verificando email", email=data.email)

        # 1. Buscar usuario por email
        result = await db.execute(
            select(User).where(User.email == data.email)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # 2. Verificar si ya está verificado
        if user.email_verified:
            return VerificationResponse(
                success=True,
                message="El email ya está verificado",
                email_verified=True,
                phone_verified=user.phone_verified,
                account_active=(user.account_status == AccountStatus.ACTIVE)
            )

        # 3. Verificar código y expiración
        if not user.email_verification_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay código de verificación pendiente"
            )

        if user.email_verification_expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código de verificación ha expirado. Solicita uno nuevo."
            )

        if user.email_verification_code != data.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código de verificación inválido"
            )

        # 4. Marcar email como verificado
        user.email_verified = True
        user.email_verification_code = None
        user.email_verification_expires_at = None

        # 5. Enviar email de bienvenida (siempre que se verifique email)
        logger.info(f"📧 Email verificado, programando email de bienvenida")
        background_tasks.add_task(
            send_welcome_email,
            user.email,                    # Parámetro posicional: email
            user.nombre or "Usuario"       # Parámetro posicional: name
        )
        logger.info(f"✅ Email de bienvenida programado en background tasks")

        # 6. Si teléfono también está verificado, activar cuenta
        if user.phone_verified:
            user.account_status = AccountStatus.ACTIVE
            logger.info(f"🎉 Cuenta activada completamente", user_id=str(user.id))

        await db.commit()

        logger.info(f"✅ Email verificado exitosamente", email=user.email)

        return VerificationResponse(
            success=True,
            message="Email verificado exitosamente" if not user.phone_verified
                    else "Email verificado. Tu cuenta está ahora activa.",
            email_verified=True,
            phone_verified=user.phone_verified,
            account_active=(user.account_status == AccountStatus.ACTIVE)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en verify_email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando verificación de email"
        )


@router.post(
    '/verify/phone',
    response_model=VerificationResponse,
    summary="Verificar teléfono con código",
    description="Verifica el teléfono del usuario con código de 6 dígitos (Twilio Verify)"
)
async def verify_phone(
    data: VerifyPhoneRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica el teléfono del usuario con código de 6 dígitos usando Twilio Verify.

    Si email y teléfono están verificados, activa la cuenta (account_status=ACTIVE).
    """
    try:
        logger.info(f"📱 Verificando teléfono", phone=data.phone)

        # 1. Buscar usuario por teléfono
        result = await db.execute(
            select(User).where(User.telefono == data.phone)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # 2. Verificar si ya está verificado
        if user.phone_verified:
            return VerificationResponse(
                success=True,
                message="El teléfono ya está verificado",
                email_verified=user.email_verified,
                phone_verified=True,
                account_active=(user.account_status == AccountStatus.ACTIVE)
            )

        # 3. Verificar código con Twilio Verify
        try:
            sms_service = SMSService()
            verify_result = await sms_service.verify_code(
                phone_number=data.phone,
                code=data.code
            )

            # SMSService returns 'success' not 'valid'
            if not verify_result.get('success'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Código de verificación inválido o expirado. Status: {verify_result.get('status')}"
                )

        except HTTPException:
            raise
        except Exception as twilio_error:
            logger.error(f"❌ Error verificando código con Twilio: {str(twilio_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error verificando código de teléfono"
            )

        # 4. Marcar teléfono como verificado
        user.phone_verified = True

        # 5. Si email también está verificado, activar cuenta
        if user.email_verified:
            user.account_status = AccountStatus.ACTIVE
            logger.info(f"🎉 Cuenta activada completamente", user_id=str(user.id))

        await db.commit()

        logger.info(f"✅ Teléfono verificado exitosamente", phone=user.telefono)

        return VerificationResponse(
            success=True,
            message="Teléfono verificado exitosamente" if not user.email_verified
                    else "Teléfono verificado. Tu cuenta está ahora activa.",
            email_verified=user.email_verified,
            phone_verified=True,
            account_active=(user.account_status == AccountStatus.ACTIVE)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en verify_phone: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando verificación de teléfono"
        )

# ============================================================================
# REGISTRO MULTI-TIPO: BUYER, VENDOR NATURAL, VENDOR JURÍDICA
# ============================================================================

@router.post("/register-multi-type", response_model=MultiTypeRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_multi_type(
    user_data: Union[BuyerRegistrationData, VendorNaturalRegistrationData, VendorJuridicaRegistrationData],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> MultiTypeRegistrationResponse:
    '''
    Registro multi-tipo para BUYER, VENDOR Natural y VENDOR Jurídica.

    Detecta automáticamente el tipo de usuario basado en campos presentes:
    - Si tiene `nit` → VENDOR Persona Jurídica
    - Si tiene `cedula` y `direccion_fiscal` → VENDOR Persona Natural
    - Si no tiene campos de vendor → BUYER

    Flujos por tipo:

    BUYER:
    - user_type: BUYER
    - account_status: PENDING → ACTIVE (después de verificar email + SMS)
    - vendor_status: None
    - Activación inmediata después de verificación

    VENDOR Persona Natural:
    - user_type: VENDOR
    - account_status: PENDING
    - vendor_status: DRAFT (requiere aprobación admin)
    - tipo_vendedor: "persona_natural"
    - Requiere verificación email/SMS + aprobación administrativa

    VENDOR Persona Jurídica:
    - user_type: VENDOR
    - account_status: PENDING
    - vendor_status: PENDING_DOCUMENTS (requiere documentos)
    - tipo_vendedor: "persona_juridica"
    - Requiere verificación email/SMS + documentos + aprobación

    Returns:
        MultiTypeRegistrationResponse con user_id, estados, y next_steps
    '''

    try:
        # ========================================================================
        # 1. DETECTAR TIPO DE USUARIO
        # ========================================================================
        logger.info(f"🔄 Inicio de registro multi-tipo")
        logger.info(f"📝 Datos recibidos: email={user_data.email}")

        # Detectar tipo basado en campos presentes
        is_juridica = hasattr(user_data, 'nit') and user_data.nit
        is_natural = hasattr(user_data, 'cedula') and user_data.cedula and hasattr(user_data, 'direccion_fiscal')
        is_buyer = not is_juridica and not is_natural

        if is_juridica:
            user_type = UserType.VENDOR
            vendor_type = "persona_juridica"
            logger.info(f"🏢 Tipo detectado: VENDOR Persona Jurídica")
        elif is_natural:
            user_type = UserType.VENDOR
            vendor_type = "persona_natural"
            logger.info(f"👤 Tipo detectado: VENDOR Persona Natural")
        else:
            user_type = UserType.BUYER
            vendor_type = None
            logger.info(f"🛒 Tipo detectado: BUYER")

        # ========================================================================
        # 2. VALIDAR UNICIDAD DE EMAIL Y TELÉFONO
        # ========================================================================
        logger.info(f"🔍 Verificando unicidad de email: {user_data.email}")
        existing_user = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing_user.scalar_one_or_none():
            logger.warning(f"⚠️ Email ya registrado: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado. Por favor usa otro correo o inicia sesión."
            )
        logger.info(f"✅ Email disponible")

        # Obtener teléfono del schema correcto
        telefono = getattr(user_data, 'telefono', None) or getattr(user_data, 'telefono_empresa', None)

        if telefono:
            logger.info(f"🔍 Verificando unicidad de teléfono")
            existing_phone = await db.execute(
                select(User).where(User.telefono == telefono)
            )
            if existing_phone.scalar_one_or_none():
                logger.warning(f"⚠️ Teléfono ya registrado")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El teléfono ya está registrado. Por favor usa otro número."
                )
            logger.info(f"✅ Teléfono disponible")

        # ========================================================================
        # 3. VALIDAR NIT ÚNICO (SOLO PERSONA JURÍDICA)
        # ========================================================================
        if is_juridica:
            logger.info(f"🔍 Verificando unicidad de NIT")
            existing_nit = await db.execute(
                select(User).where(User.nit == user_data.nit)
            )
            if existing_nit.scalar_one_or_none():
                logger.warning(f"⚠️ NIT ya registrado")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El NIT ya está registrado. Por favor verifica o inicia sesión."
                )
            logger.info(f"✅ NIT disponible")

        # ========================================================================
        # 4. CREAR USUARIO CON CAMPOS SEGÚN TIPO
        # ========================================================================
        logger.info(f"🔐 Generando hash de contraseña")
        password_hash = await get_password_hash(user_data.password)

        # Determinar estados según tipo
        if user_type == UserType.BUYER:
            account_status = AccountStatus.PENDING  # Se activa al verificar
            vendor_status = None
        else:  # VENDOR
            account_status = AccountStatus.PENDING
            vendor_status = VendorStatus.DRAFT if is_natural else VendorStatus.PENDING_DOCUMENTS

        logger.info(f"👤 Creando usuario con estados: account_status={account_status}, vendor_status={vendor_status}")

        # Crear usuario base
        new_user = User(
            email=user_data.email,
            password_hash=password_hash,
            user_type=user_type,
            account_status=account_status,
            vendor_status=vendor_status,
            tipo_vendedor=vendor_type,
            is_active=True,
            email_verified=False,
            phone_verified=False
        )

        # Agregar campos según tipo
        if is_buyer:
            # BUYER: campos básicos
            new_user.nombre = user_data.nombre
            new_user.apellido = getattr(user_data, 'apellido', None)
            new_user.telefono = user_data.telefono
            new_user.cedula = getattr(user_data, 'cedula', None)
            new_user.direccion = getattr(user_data, 'direccion', None)
            new_user.ciudad = getattr(user_data, 'ciudad', None)
            new_user.departamento = getattr(user_data, 'departamento', None)
            new_user.codigo_postal = getattr(user_data, 'codigo_postal', None)

        elif is_natural:
            # VENDOR NATURAL: persona física + fiscal
            new_user.nombre = user_data.nombre
            new_user.apellido = user_data.apellido
            new_user.telefono = user_data.telefono
            new_user.cedula = user_data.cedula
            new_user.direccion = user_data.direccion
            new_user.ciudad = user_data.ciudad
            new_user.departamento = user_data.departamento
            new_user.codigo_postal = getattr(user_data, 'codigo_postal', None)
            new_user.direccion_fiscal = user_data.direccion_fiscal
            new_user.ciudad_fiscal = user_data.ciudad_fiscal
            new_user.departamento_fiscal = user_data.departamento_fiscal

        else:  # is_juridica
            # VENDOR JURÍDICA: datos empresa + representante
            new_user.razon_social = user_data.razon_social
            new_user.nombre_comercial = user_data.nombre_comercial
            new_user.nit = user_data.nit
            new_user.representante_legal = user_data.representante_legal
            new_user.cedula_representante = user_data.cedula_representante
            new_user.email_representante = user_data.email_representante
            new_user.telefono = user_data.telefono_empresa
            new_user.telefono_empresa = user_data.telefono_empresa
            new_user.direccion_fiscal = user_data.direccion_fiscal
            new_user.ciudad_fiscal = user_data.ciudad_fiscal
            new_user.departamento_fiscal = user_data.departamento_fiscal
            new_user.codigo_postal = getattr(user_data, 'codigo_postal', None)
            # Nombre para display
            new_user.nombre = user_data.nombre_comercial

        db.add(new_user)
        logger.info(f"💾 Usuario agregado a sesión DB, ejecutando flush")
        await db.flush()
        logger.info(f"✅ Flush completado, user_id obtenido: {new_user.id}")

        # ========================================================================
        # 5. GENERAR TOKEN DE VERIFICACIÓN EMAIL (LINK)
        # ========================================================================
        logger.info(f"🎲 Generando token de verificación de email")
        email_token = secrets.token_urlsafe(32)
        new_user.email_verification_token = email_token
        new_user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
        logger.info(f"✅ Token generado (expira en 24h)")

        # ========================================================================
        # 6. COMMIT A BASE DE DATOS
        # ========================================================================
        logger.info(f"💾 Ejecutando commit a base de datos")
        await db.commit()
        await db.refresh(new_user)
        logger.info(f"✅ Usuario creado exitosamente", user_id=str(new_user.id))

        # ========================================================================
        # 7. ENVIAR EMAIL VERIFICACIÓN CON LINK (BACKGROUND)
        # ========================================================================
        logger.info(f"📧 Programando email de verificación con link")
        from app.core.config import settings
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={email_token}"

        background_tasks.add_task(
            send_verification_email,
            new_user.email,
            email_token,
            new_user.nombre or new_user.razon_social,
            verification_link
        )
        logger.info(f"✅ Email programado")

        # ========================================================================
        # 8. ENVIAR SMS VERIFICACIÓN (TWILIO VERIFY)
        # ========================================================================
        if telefono:
            try:
                logger.info(f"📱 Enviando SMS verification con Twilio")
                sms_service = SMSService()
                sms_result = await sms_service.send_verification_code(
                    phone_number=telefono,
                    channel="sms"
                )
                logger.info(f"✅ SMS enviado", status=sms_result.get('status'))
            except Exception as sms_error:
                logger.error(f"❌ Error SMS: {str(sms_error)}", exc_info=True)
                # No fallar registro si SMS falla

        # ========================================================================
        # 9. PREPARAR NEXT_STEPS SEGÚN TIPO
        # ========================================================================
        if user_type == UserType.BUYER:
            next_steps = [
                "Verifica tu email haciendo clic en el enlace enviado",
                "Ingresa el código SMS de 6 dígitos",
                "¡Empieza a comprar! Tu cuenta se activará automáticamente"
            ]
        elif vendor_type == "persona_natural":
            next_steps = [
                "Verifica tu email haciendo clic en el enlace enviado",
                "Ingresa el código SMS de 6 dígitos",
                "Tu solicitud será revisada por nuestro equipo",
                "Recibirás notificación de aprobación en 24-48 horas"
            ]
        else:  # persona_juridica
            next_steps = [
                "Verifica tu email haciendo clic en el enlace enviado",
                "Ingresa el código SMS de 6 dígitos",
                "Sube los documentos requeridos (Cámara de Comercio, RUT)",
                "Espera la revisión y aprobación de tu cuenta empresarial"
            ]

        # ========================================================================
        # 10. RETORNAR RESPUESTA
        # ========================================================================
        logger.info(f"✅ Registro completado exitosamente")

        return MultiTypeRegistrationResponse(
            success=True,
            message=f"Registro exitoso como {vendor_type or 'comprador'}. Por favor verifica tu email y teléfono.",
            user_id=str(new_user.id),
            email=new_user.email,
            user_type=user_type.value,
            vendor_type=vendor_type,
            account_status=account_status.value,
            vendor_status=vendor_status.value if vendor_status else None,
            requires_approval=(user_type == UserType.VENDOR),
            next_steps=next_steps
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ERROR CRÍTICO en register_multi_type: {str(e)}", exc_info=True)

        # Rollback
        try:
            await db.rollback()
            logger.info(f"✅ Rollback completado")
        except Exception as rollback_error:
            logger.error(f"❌ Error en rollback: {str(rollback_error)}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando registro: {type(e).__name__} - {str(e)}"
        )
