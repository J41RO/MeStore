"""
Módulo de autenticación centralizado para la aplicación MeStore.

Proporciona servicios de autenticación JWT, validación de usuarios,
y funciones de autorización basadas en roles.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token
from app.utils.password import hash_password, verify_password
from app.core.redis import get_redis_sessions

# Security scheme
security = HTTPBearer()


class AuthService:
    """Servicio de autenticación centralizado"""

    def __init__(self):
        self.secret_key = settings.SECRET_KEY

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña usando función centralizada"""
        return await verify_password(plain_password, hashed_password)

    async def get_password_hash(self, password: str) -> str:
        """Hash de contraseña usando función centralizada"""
        return await hash_password(password)

    async def authenticate_user(self, email: str, password: str):
        """
        Autenticar usuario con email y contraseña.

        Args:
            email: Email del usuario
            password: Contraseña en texto plano

        Returns:
            Usuario si credenciales son válidas, None si son inválidas
        """
        from app.database import AsyncSessionLocal
        from app.models.user import User
        from sqlalchemy import select

        # Obtener sesión de base de datos
        async with AsyncSessionLocal() as db:
            try:
                # Buscar usuario por email
                stmt = select(User).where(User.email == email)
                result = await db.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    return None

                # Verificar contraseña
                if not await self.verify_password(password, user.password_hash):
                    return None

                return user

            except Exception as e:
                # Log error pero no revelar detalles por seguridad
                import logging
                logging.error(f"Error en authenticate_user: {str(e)}")
                return None

    def create_access_token(self, user_id: str, expires_delta: Optional[timedelta] = None):
        """Crear access token JWT para usuario"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=1)

        to_encode = {"sub": str(user_id), "exp": expire}
        return create_access_token(to_encode)

    def create_refresh_token(self, user_id: str) -> str:
        """Crear refresh token JWT para usuario"""
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode = {"sub": str(user_id), "exp": expire, "type": "refresh"}
        return create_access_token(to_encode)

    def verify_token(self, token: str) -> dict:
        """Verificar JWT token usando función centralizada"""
        return decode_access_token(token)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Dependency para obtener usuario actual desde JWT token.

    Args:
        credentials: Token Bearer del header Authorization

    Returns:
        User object del usuario actual

    Raises:
        HTTPException: 401 si token es inválido
    """
    try:
        # Verificar token
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Buscar usuario en base de datos
        from app.database import AsyncSessionLocal
        from app.models.user import User
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            stmt = select(User).where(User.id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no encontrado",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            return user

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Error en get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[dict]:
    """
    Dependency para obtener usuario opcional (puede ser None).

    Args:
        credentials: Token Bearer opcional

    Returns:
        Dict con usuario o None si no hay token válido
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_user_type(*allowed_types: str):
    """
    Decorator para requerir tipos específicos de usuario.

    Args:
        allowed_types: Tipos de usuario permitidos (ej: "VENDEDOR", "COMPRADOR")
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Obtener usuario actual del contexto
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Autenticación requerida"
                )

            user_type = current_user.get("user_type")
            if user_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Acceso denegado. Tipos permitidos: {allowed_types}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def get_auth_service() -> AuthService:
    """
    FastAPI dependency for Auth service
    Usage in endpoints:
        @app.post("/login")
        async def login(auth_svc = Depends(get_auth_service)):
            user = await auth_svc.authenticate_user(...)
    """
    return AuthService()



# Instancia global del servicio de autenticación
auth_service = AuthService()