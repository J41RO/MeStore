# Ruta: MeStore/app/api/v1/endpoints/auth.py
"""
Endpoints de autenticación JWT para la API v1.

Proporciona endpoints para:
- POST /login: Autenticación con email/password
- POST /refresh-token: Renovación de access token
- POST /logout: Invalidación de sesión
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.auth import AuthService, get_auth_service
from app.core.security import decode_access_token, decode_refresh_token
from app.schemas.auth import (
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