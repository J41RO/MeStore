from datetime import datetime
import uuid
"""
Dependencias de autenticación para endpoints de FastAPI

Este módulo contiene las dependencias centralizadas para autenticación:
- oauth2_scheme: Esquema OAuth2 para extracción de tokens
- get_current_user: Dependencia principal para obtener usuario autenticado
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.auth import auth_service
from app.schemas.user import UserRead
from app.core.redis import get_redis_sessions


# OAuth2 scheme para extracción de tokens del header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    redis_sessions = Depends(get_redis_sessions)
) -> UserRead:
    """
    Dependencia para obtener el usuario actual autenticado.

    Esta función:
    1. Extrae el JWT del header Authorization usando OAuth2PasswordBearer
    2. Verifica el token usando auth_service.verify_token()
    3. Valida la sesión en Redis (opcional para logout global)
    4. Retorna el usuario como objeto UserRead

    Args:
        token: JWT token extraído automáticamente del header Authorization
        redis_sessions: Cliente Redis para validación de sesiones

    Returns:
        UserRead: Objeto del usuario autenticado

    Raises:
        HTTPException 401: Si el token es inválido, expirado o la sesión no existe

    Usage:
        @router.get("/protected")
        async def protected_endpoint(current_user: UserRead = Depends(get_current_user)):
            return {"user": current_user.email}
    """
    try:
        # Verificar token JWT usando el servicio centralizado
        payload = auth_service.verify_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload inválido - missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verificar sesión activa en Redis (opcional para logout global)
        session_key = f"session:{user_id}"
        session_data = await redis_sessions.get(session_key)

        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión expirada - please login again",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Construir objeto UserRead desde payload JWT
        user_data = UserRead(
            id=str(uuid.uuid4()),  # Generar UUID válido
            email=payload.get("email", ""),
            nombre=payload.get("nombre", ""),
            apellido=payload.get("apellido", ""),
            user_type=payload.get("user_type", ""),
            is_active=payload.get("is_active", True),
            is_verified=payload.get("is_verified", False),
            last_login=payload.get("last_login", None),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        return user_data

    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except Exception as e:
        # Capturar cualquier otro error y convertir a 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"No se pudo validar las credenciales: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: UserRead = Depends(get_current_user)
) -> UserRead:
    """
    Dependencia para obtener usuario actual que esté activo.

    Args:
        current_user: Usuario obtenido de get_current_user

    Returns:
        UserRead: Usuario activo

    Raises:
        HTTPException 400: Si el usuario está inactivo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user