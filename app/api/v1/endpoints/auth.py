# Ruta: MeStore/app/api/v1/endpoints/auth.py
"""
Endpoints de autenticación JWT para la API v1.
Versión corregida sin conflictos entre AuthService.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# IMPORTS CORREGIDOS - Solo del AuthService correcto
from app.services.auth_service import AuthService
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.audit_service import AuditService
from app.core.security import decode_access_token, decode_refresh_token, create_access_token, create_refresh_token
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


# Función auxiliar para get_current_user sin conflictos
async def get_current_user_clean(token: str = Depends(HTTPBearer())) -> User:
    """Obtener usuario actual sin conflictos de AuthService"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    # Obtener usuario de la base de datos
    db_gen = get_db()
    db = next(db_gen)
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
        return user
    finally:
        db.close()


def get_auth_service() -> AuthService:
    """Crear instancia del AuthService correcto sin conflictos."""
    return AuthService()


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Endpoint de autenticación con email y contraseña.
    """
    logger.info("Intento de login", email=login_data.email)
    auth_service = get_auth_service()

    try:
        # Validar credenciales usando AuthService correcto
        user = await auth_service.authenticate_user(
            db=db,
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

        # Generar tokens JWT (sin almacenar en Redis por ahora)
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        logger.info("Login exitoso", user_id=str(user.id), email=user.email)

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
    db: Session = Depends(get_db)
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
        
        # Verificación específica de rol admin
        if user.user_type.value not in ["ADMIN", "SUPERUSER"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: Se requieren privilegios administrativos"
            )
        
        # Generar tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
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
        return {
            "id": str(current_user.id),
            "email": current_user.email,
            "nombre": getattr(current_user, 'nombre', current_user.email.split('@')[0]),
            "user_type": str(current_user.user_type),
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
    user_data: LoginRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """Registrar nuevo usuario."""
    auth_service = get_auth_service()
    
    try:
        # Crear nuevo usuario  
        new_user = await auth_service.create_user(
            db=db,
            email=user_data.email,
            password=user_data.password
        )
        
        # Generar token para el nuevo usuario
        access_token = create_access_token(data={"sub": str(new_user.id)})
        
        return TokenResponse(
            access_token=access_token,
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
        
        # Verificar usuario existe
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
        
        # Generar nuevos tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
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