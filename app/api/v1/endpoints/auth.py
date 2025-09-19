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
        user = await auth_service.authenticate_user(
            email=login_data.email,
            password=login_data.password,
            db=db,
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
                   user_id=normalized_id, email=user.email, ip=ip_address)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600
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
    request: LoginRequest,
    request_info: Request,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Endpoint específico para autenticación administrativa.
    """
    auth_service = get_auth_service()
    ip_address = request_info.client.host if request_info.client else None
    user_agent = request_info.headers.get("User-Agent")
    
    try:
        # Intentar autenticación
        user = await auth_service.authenticate_user(
            db=db,
            email=request.email,
            password=request.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificación específica de rol admin (uppercase values)
        # Ensure user_type is an enum first
        from app.models.user import UserType
        if isinstance(user.user_type, str):
            try:
                user.user_type = UserType(user.user_type)
            except ValueError:
                user.user_type = UserType.BUYER

        if user.user_type.value not in ["ADMIN", "SUPERUSER"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: Se requieren privilegios administrativos"
            )
        
        # Generar tokens with consistent ID format
        normalized_id = normalize_uuid_string(user.id)
        if normalized_id is None:
            logger.warning(f"Admin user {user.email} has null ID, using email as fallback")
            normalized_id = user.email
        access_token = create_access_token(data={"sub": normalized_id})
        refresh_token = create_refresh_token(data={"sub": normalized_id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600
        )
        
    except HTTPException:
        raise
    except Exception as e:
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
    auth_service = get_auth_service()

    try:
        # Crear nuevo usuario con datos adicionales
        new_user = await auth_service.create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            user_type=user_data.user_type.value if user_data.user_type else "BUYER",
            nombre=user_data.nombre,
            telefono=user_data.telefono
        )
        
        # Generar tokens para el nuevo usuario with consistent ID format
        normalized_id = normalize_uuid_string(new_user.id)
        access_token = create_access_token(data={"sub": normalized_id})
        refresh_token = create_refresh_token(data={"sub": normalized_id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600
        )
        
    except Exception as e:
        logger.error(f"Error en register: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/forgot-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def forgot_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Solicita recuperación de contraseña por email."""
    auth_service = get_auth_service()
    
    try:
        success, message = await auth_service.send_password_reset_email(
            db=db,
            email=request.email
        )
        
        return PasswordResetResponse(
            success=True,
            message="Si el email existe, recibirás instrucciones de recuperación"
        )

    except Exception as e:
        logger.error(f"Error en forgot_password: {str(e)}")
        return PasswordResetResponse(
            success=True,
            message="Si el email existe, recibirás instrucciones de recuperación"
        )


@router.post("/reset-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def reset_password(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Confirma reset de contraseña con token."""
    auth_service = get_auth_service()
    
    try:
        if request.new_password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las contraseñas no coinciden"
            )

        success, message = await auth_service.reset_password_with_token(
            db=db,
            token=request.token,
            new_password=request.new_password
        )

        if success:
            return PasswordResetResponse(success=True, message=message)
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