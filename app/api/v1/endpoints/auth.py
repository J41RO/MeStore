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
    AuthResponse
)
from app.core.redis import RedisService, get_redis_service
from app.core.logger import get_logger
from app.services.email_service import EmailService
import secrets
from datetime import datetime, timedelta

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


# Endpoints adicionales simplificados para funcionalidad básica
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Registrar nuevo usuario con tipo específico."""
    logger.info(f"🔄 Register attempt with data: {user_data.dict()}")
    auth_service = get_auth_service()

    try:
        # Crear nuevo usuario con datos adicionales
        new_user = await auth_service.create_user(
            db,
            email=user_data.email,
            password=user_data.password,
            user_type=user_data.user_type.value if user_data.user_type else "BUYER",
            nombre=user_data.nombre,
            telefono=user_data.telefono
        )
        
        # Generar tokens para el nuevo usuario with consistent ID format
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
            expires_in=3600
        )
        
    except ValueError as e:
        error_message = str(e)
        if "already exists" in error_message:
            logger.warning(f"Duplicate email registration attempt: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado. Por favor usa otro correo o inicia sesión."
            )
        else:
            logger.error(f"Validation error en register: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Datos de registro inválidos"
            )
    except Exception as e:
        logger.error(f"Error interno en register: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# Password reset endpoints moved below (lines 817+) with EmailService implementation

# ===== OTP/SMS VERIFICATION ENDPOINTS =====

@router.post("/send-verification-email", response_model=OTPResponse, status_code=status.HTTP_200_OK)
async def send_verification_email(
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
async def send_verification_sms(
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