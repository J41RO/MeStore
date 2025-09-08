# Ruta: MeStore/app/api/v1/endpoints/auth.py
"""
Endpoints de autenticación JWT para la API v1.

Proporciona endpoints para:
- POST /login: Autenticación con email/password
- POST /refresh-token: Renovación de access token
- POST /logout: Invalidación de sesión
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.auth import AuthService, get_auth_service
from app.core.auth import get_current_user
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.audit_service import AuditService
from fastapi import HTTPException
from app.core.security import decode_access_token, decode_refresh_token
from app.schemas.auth import (
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse,
    OTPSendRequest,
    OTPVerifyRequest, 
    OTPResponse,
    UserVerificationStatus,
    LoginRequest, 
    TokenResponse, 
    RefreshTokenRequest, 
    LogoutRequest,
    AuthResponse
)
from app.core.redis import RedisService, get_redis_service
from app.core.logger import get_logger

# Configurar router y logger
router = APIRouter()
logger = get_logger(__name__)
security = HTTPBearer()


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
    redis_service: RedisService = Depends(get_redis_service)
) -> TokenResponse:
    """
    Endpoint de autenticación con email y contraseña.

    Args:
        login_data: Datos de login (email, password)
        auth_service: Servicio de autenticación
        redis_service: Servicio de Redis para sesiones

    Returns:
        TokenResponse: Tokens de acceso y refresh

    Raises:
        HTTPException: 401 si credenciales inválidas
    """
    logger.info("Intento de login", email=login_data.email)

    try:
        # Validar credenciales usando AuthService
        user = await auth_service.authenticate_user(
            email=login_data.email,
            password=login_data.password
        )

        if not user:
            logger.warning("Login fallido - credenciales inválidas", email=login_data.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Generar tokens JWT
        access_token = auth_service.create_access_token(user_id=user.id)
        refresh_token = auth_service.create_refresh_token(user_id=user.id)

        # Guardar refresh token en Redis para invalidación posterior
        await redis_service.set_with_ttl(
            key=f"refresh_token:{user.id}",
            value=refresh_token,
            ttl_seconds=7 * 24 * 3600  # 7 días
        )

        logger.info("Login exitoso", user_id=str(user.id), email=user.email)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600  # 1 hora para access token
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error interno en login", error=str(e), email=login_data.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/refresh-token", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
    redis_service: RedisService = Depends(get_redis_service)
) -> TokenResponse:
    """
    Endpoint para renovar access token usando refresh token.

    Args:
        refresh_data: Datos con refresh token
        auth_service: Servicio de autenticación
        redis_service: Servicio de Redis

    Returns:
        TokenResponse: Nuevo access token y refresh token

    Raises:
        HTTPException: 401 si refresh token inválido o expirado
    """
    logger.info("Intento de refresh token")

    try:
        # Decodificar y validar refresh token
        payload = decode_refresh_token(refresh_data.refresh_token)
        if not payload:
            logger.warning("Refresh token inválido o malformado")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido o expirado"
            )
        
        user_id = payload.get("sub")

        if not user_id:
            logger.warning("Refresh token sin user_id válido")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresh inválido",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Verificar que el refresh token existe en Redis
        stored_token = await redis_service.get(f"refresh_token:{user_id}")
        if not stored_token or stored_token != refresh_data.refresh_token:
            logger.warning("Refresh token no encontrado en Redis", user_id=user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresh inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Generar nuevos tokens
        new_access_token = await auth_service.create_access_token(user_id=user_id)
        new_refresh_token = await auth_service.create_refresh_token(user_id=user_id)

        # Actualizar refresh token en Redis
        await redis_service.set_with_ttl(
            key=f"refresh_token:{user_id}",
            value=new_refresh_token,
            ttl_seconds=7 * 24 * 3600  # 7 días
        )

        logger.info("Refresh token exitoso", user_id=user_id)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=3600  # 1 hora para access token
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error interno en refresh token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/logout", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def logout(
    logout_data: LogoutRequest = LogoutRequest(),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis_service: RedisService = Depends(get_redis_service)
) -> AuthResponse:
    """
    Endpoint para logout e invalidación de sesión.

    Args:
        logout_data: Datos de logout (opcional revoke_all)
        credentials: Token de autorización del header
        redis_service: Servicio de Redis

    Returns:
        AuthResponse: Confirmación de logout

    Raises:
        HTTPException: 401 si token inválido
    """
    logger.info("Intento de logout")

    try:
        # Decodificar access token para obtener user_id
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")

        if not user_id:
            logger.warning("Access token sin user_id válido")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso inválido",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Agregar access token a blacklist en Redis
        token_jti = payload.get("jti")  # JWT ID único
        if token_jti:
            await redis_service.set_with_ttl(
                key=f"blacklist_token:{token_jti}",
                value="revoked",
                ttl_seconds=3600  # TTL igual al tiempo de vida del access token
            )

        # Invalidar refresh token
        await redis_service.delete(f"refresh_token:{user_id}")

        # Si revoke_all es True, invalidar todas las sesiones del usuario
        if logout_data.revoke_all:
            # Buscar y eliminar todos los refresh tokens del usuario
            pattern = f"refresh_token:{user_id}*"
            keys = await redis_service.scan_keys(pattern)
            if keys:
                await redis_service.delete(*keys)
            logger.info("Logout con revoke_all", user_id=user_id, tokens_revoked=len(keys))
        else:
            logger.info("Logout exitoso", user_id=user_id)

        return AuthResponse(
            success=True,
            message="Logout exitoso - sesión invalidada"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error interno en logout", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


# === ENDPOINTS OTP PARA VERIFICACIÓN EMAIL/SMS ===

@router.post("/send-verification-email", response_model=OTPResponse, status_code=status.HTTP_200_OK)
async def send_verification_email(
    request: OTPSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Envía código OTP por email para verificación.

    - **otp_type**: Debe ser "EMAIL" para este endpoint
    - Requiere autenticación JWT
    - El usuario debe tener email registrado
    - Respeta cooldown de 1 minuto entre envíos
    - Código válido por 10 minutos
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
            return OTPResponse(
                success=False,
                message="El email ya está verificado",
                verification_status={
                    "email_verified": True,
                    "phone_verified": current_user.phone_verified
                }
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/send-verification-sms", response_model=OTPResponse, status_code=status.HTTP_200_OK)
async def send_verification_sms(
    request: OTPSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Envía código OTP por SMS para verificación.

    - **otp_type**: Debe ser "SMS" para este endpoint
    - Requiere autenticación JWT
    - El usuario debe tener teléfono registrado
    - Respeta cooldown de 1 minuto entre envíos
    - Código válido por 10 minutos
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
            return OTPResponse(
                success=False,
                message="El teléfono ya está verificado",
                verification_status={
                    "email_verified": current_user.email_verified,
                    "phone_verified": True
                }
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/verify-email-otp", response_model=OTPResponse, status_code=status.HTTP_200_OK)
async def verify_email_otp(
    request: OTPVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
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

        # Verificar código OTP
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/verify-phone-otp", response_model=OTPResponse, status_code=status.HTTP_200_OK)
async def verify_phone_otp(
    request: OTPVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
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

        # Verificar código OTP
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/verification-status", response_model=UserVerificationStatus, status_code=status.HTTP_200_OK)
async def get_verification_status(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Obtiene el estado completo de verificación del usuario autenticado.

    - Requiere autenticación JWT
    - Retorna estado de email_verified, phone_verified
    - Incluye información sobre OTP activo si existe
    - Indica si puede solicitar nuevo OTP
    """
    try:
        verification_status = await auth_service.get_user_verification_status(current_user)
        return UserVerificationStatus(**verification_status)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo estado de verificación"
        )



# === ENDPOINTS PARA RECUPERACIÓN DE CONTRASEÑA ===

@router.post("/forgot-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Solicita recuperación de contraseña por email.

    - **email**: Email registrado en el sistema
    - No requiere autenticación
    - Cooldown de 5 minutos entre solicitudes
    - Por seguridad, siempre responde exitosamente (no revela si email existe)
    """
    try:
        logger.info(f"Solicitud de recuperación de contraseña para: {request.email}")

        # Enviar email de recuperación
        success, message = await auth_service.send_password_reset_email(
            db=db,
            email=request.email
        )

        # Por seguridad, siempre respondemos que fue exitoso
        # (no revelamos si el email existe en el sistema)
        return PasswordResetResponse(
            success=True,
            message="Si el email existe, recibirás instrucciones de recuperación"
        )

    except Exception as e:
        logger.error(f"Error en forgot_password: {str(e)}")
        # Por seguridad, no revelar error interno
        return PasswordResetResponse(
            success=True,
            message="Si el email existe, recibirás instrucciones de recuperación"
        )


@router.post("/reset-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Confirma reset de contraseña con token.

    - **token**: Token de reset recibido por email
    - **new_password**: Nueva contraseña (mín. 8 caracteres, mayús, minús, número)
    - **confirm_password**: Confirmación de nueva contraseña
    - No requiere autenticación JWT
    - Token expira en 1 hora
    - Máximo 3 intentos por día
    """
    try:
        logger.info(f"Intento de reset de contraseña con token: {request.token[:10]}...")

        # Validar que las contraseñas coincidan (ya validado en schema)
        if request.new_password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las contraseñas no coinciden"
            )

        # Resetear contraseña
        success, message = await auth_service.reset_password_with_token(
            db=db,
            token=request.token,
            new_password=request.new_password
        )

        if success:
            return PasswordResetResponse(
                success=True,
                message=message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en reset_password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/validate-reset-token", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def validate_reset_token(
    token: str = Query(..., description="Token de reset a validar"),
    db: Session = Depends(get_db)
):
    """
    Valida si un token de reset es válido y no ha expirado.

    - **token**: Token de reset a validar
    - No requiere autenticación
    - Útil para validar token antes de mostrar formulario de reset
    """
    try:
        from app.models.user import User

        # Buscar usuario por token
        user = db.query(User).filter(User.reset_token == token).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de recuperación inválido"
            )

        # Verificar que el token no haya expirado
        if not user.is_reset_token_valid():
            # Limpiar token expirado
            user.clear_reset_data()
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El enlace de recuperación ha expirado"
            )

        # Verificar si está bloqueado
        if user.is_reset_blocked():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Demasiados intentos fallidos. Contacte soporte"
            )

        return PasswordResetResponse(
            success=True,
            message="Token válido. Puede proceder con el reset"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en validate_reset_token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )



@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Registrar nuevo usuario.
    
    Crea una nueva cuenta de usuario con email y password.
    Retorna token de acceso para autenticación inmediata.
    """
    try:
        # Verificar que el email no exista
        existing_user = await auth_service.get_user_by_email(user_data.email, db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear nuevo usuario  
        new_user = await auth_service.create_user(
            email=user_data.email,
            password=user_data.password,
            db=db
        )
        
        # Generar token para el nuevo usuario
        access_token = auth_service.create_access_token(data={"sub": new_user.email})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en register: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )



@router.get("/me", response_model=dict, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtener información del usuario actual autenticado.
    
    Retorna información básica del usuario basada en el token JWT.
    Requiere autenticación válida.
    """
    try:
        return {
            "id": current_user.id,
            "email": current_user.email,
            "nombre": getattr(current_user, 'nombre', current_user.email.split('@')[0]),
            "email_verified": getattr(current_user, 'email_verified', False),
            "phone_verified": getattr(current_user, 'phone_verified', False),
            "is_active": getattr(current_user, 'is_active', True),
            "created_at": current_user.created_at.isoformat() if hasattr(current_user, 'created_at') else None
        }
        
    except Exception as e:
        logger.error(f"Error en get_current_user_info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener información del usuario"
        )



@router.post("/admin-login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def admin_login(
    request: LoginRequest,
    request_info: Request,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Endpoint específico para autenticación administrativa.
    Incluye verificación de rol y auditoría completa.
    """
    ip_address = request_info.client.host if request_info.client else None
    user_agent = request_info.headers.get("User-Agent")
    
    try:
        # Intentar autenticación
        result = await auth_service.authenticate_user(
            email=request.email,
            password=request.password
        )
        
        if not result["success"]:
            # Log intento fallido
            AuditService.log_admin_login_attempt(
                email=request.email,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message=result["message"]
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"],
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = result["user"]
        
        # Verificación específica de rol admin
        if user.user_type not in ["ADMIN", "SUPERUSER"]:
            AuditService.log_admin_access_denied(
                email=request.email,
                reason=f"Usuario {user.user_type} intentó acceso admin",
                ip_address=ip_address,
                user_agent=user_agent
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: Se requieren privilegios administrativos"
            )
        
        # Generar tokens
        tokens = await auth_service.create_tokens_for_user(user, db)
        
        # Log login exitoso
        AuditService.log_admin_login_success(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            portal_type="admin-secure-portal"
        )
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=tokens["expires_in"],
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                nombre=user.nombre,
                apellido=user.apellido,
                user_type=user.user_type,
                is_active=user.is_active,
                is_verified=user.is_verified
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error inesperado
        AuditService.log_admin_login_attempt(
            email=request.email,
            success=False,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=f"Error inesperado: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )