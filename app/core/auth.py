"""
Autenticación global para MeStore

Proporciona sistema de autenticación basado en:
- JWT tokens para APIs
- Redis sessions para web
- Dependency injection para FastAPI
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.redis import get_redis_sessions
from app.models.user import User
from app.core.security import create_access_token, decode_access_token
from app.utils.password import hash_password, verify_password

# Configuración de seguridad
security = HTTPBearer()


class AuthService:
   """Servicio de autenticación centralizado"""
   
   def __init__(self):
       self.secret_key = settings.SECRET_KEY
   
   def verify_password(self, plain_password: str, hashed_password: str) -> bool:
       """Verificar contraseña usando función centralizada"""
       return verify_password(plain_password, hashed_password)
   
   def get_password_hash(self, password: str) -> str:
       """Hash de contraseña usando función centralizada"""
       return hash_password(password)
   
   def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
       """Crear JWT token usando función centralizada"""
       return create_access_token(data, expires_delta)
   
   def verify_token(self, token: str) -> dict:
       """Verificar JWT token usando función centralizada"""
       payload = decode_access_token(token)
       if payload is None:
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Invalid or expired token"
           )
       return payload


# Instancia global del servicio
auth_service = AuthService()


async def get_current_user(
   credentials: HTTPAuthorizationCredentials = Depends(security),
   redis_sessions = Depends(get_redis_sessions)
) -> dict:
   """
   Dependency para obtener usuario actual desde token JWT
   
   Args:
       credentials: Token de autorización
       redis_sessions: Cliente Redis para sesiones
   
   Returns:
       dict: Datos del usuario actual
   
   Raises:
       HTTPException: Si token es inválido o usuario no existe
   """
   token = credentials.credentials
   
   try:
       # Verificar token JWT usando función centralizada
       payload = auth_service.verify_token(token)
       user_id: str = payload.get("sub")
       
       if user_id is None:
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Invalid token payload"
           )
       
       # Verificar sesión en Redis (opcional, para logout global)
       session_key = f"session:{user_id}"
       session_data = await redis_sessions.get(session_key)
       
       if not session_data:
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Session expired"
           )
       
       return {
           "user_id": user_id,
           "username": payload.get("username"),
           "user_type": payload.get("user_type")
       }
       
   except Exception as e:
       if isinstance(e, HTTPException):
           raise e
       raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail="Could not validate credentials"
       )


async def get_optional_user(
   credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
   redis_sessions = Depends(get_redis_sessions)
) -> Optional[dict]:
   """
   Dependency para obtener usuario actual (opcional)
   
   Returns:
       Optional[dict]: Datos del usuario si está autenticado, None si no
   """
   if not credentials:
       return None
   
   try:
       return await get_current_user(credentials, redis_sessions)
   except HTTPException:
       return None


def require_user_type(*allowed_types: str):
   """
   Decorator para requerir tipos específicos de usuario
   
   Args:
       allowed_types: Tipos de usuario permitidos (ej: "VENDEDOR", "COMPRADOR")
   
   Returns:
       Dependency function
   """
   async def check_user_type(current_user: dict = Depends(get_current_user)):
       user_type = current_user.get("user_type")
       if user_type not in allowed_types:
           raise HTTPException(
               status_code=status.HTTP_403_FORBIDDEN,
               detail=f"Access denied. Required user type: {allowed_types}"
           )
       return current_user
   
   return check_user_type
