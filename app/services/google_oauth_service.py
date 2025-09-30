# ~/app/services/google_oauth_service.py
# ---------------------------------------------------------------------------------------------
# MeStocker - Servicio Google OAuth
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Servicio para autenticación OAuth con Google.

Este módulo maneja:
- Verificación de tokens de Google
- Obtención de información de usuario desde Google
- Creación de usuarios con OAuth
- Vinculación de cuentas existentes con Google
"""

import requests
from typing import Optional, Dict, Tuple
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google.auth.exceptions import GoogleAuthError
import os
from datetime import datetime

from app.core.logger import get_logger
from app.models.user import User, UserType
from app.services.auth_service import auth_service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = get_logger(__name__)


class GoogleOAuthService:
    """
    Servicio para manejar autenticación OAuth con Google.
    """

    def __init__(self):
        from app.core.config import settings
        # Estos se configurarán en el .env
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET

    def _get_google_client_id(self) -> str:
        """Obtiene el Client ID de Google desde variables de entorno."""
        from app.core.config import settings
        client_id = settings.GOOGLE_CLIENT_ID
        if not client_id:
            # Para desarrollo, usar un client ID de ejemplo
            return "your-google-client-id.apps.googleusercontent.com"
        return client_id

    async def verify_google_token(self, token: str) -> Optional[Dict]:
        """
        Verifica un token ID de Google y retorna la información del usuario.

        Args:
            token: Token ID de Google

        Returns:
            Dict con información del usuario o None si el token es inválido
        """
        try:
            client_id = self._get_google_client_id()

            # Verificar el token con Google
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                client_id
            )

            # Validar que el token es para nuestra aplicación
            if idinfo['aud'] != client_id:
                logger.error("Token audience mismatch")
                return None

            # Validar que el token viene de Google
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                logger.error("Token issuer invalid")
                return None

            logger.info(f"Google token verified for user: {idinfo.get('email')}")
            return idinfo

        except GoogleAuthError as e:
            logger.error(f"Google auth error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error verifying Google token: {str(e)}")
            return None

    async def find_user_by_google_id(self, db: AsyncSession, google_id: str) -> Optional[User]:
        """
        Busca un usuario por su Google ID.

        Args:
            db: Sesión de base de datos
            google_id: ID de Google del usuario

        Returns:
            Usuario si existe, None en caso contrario
        """
        try:
            result = await db.execute(
                select(User).where(User.google_id == google_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error finding user by Google ID: {str(e)}")
            return None

    async def find_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Busca un usuario por email.

        Args:
            db: Sesión de base de datos
            email: Email del usuario

        Returns:
            Usuario si existe, None en caso contrario
        """
        try:
            result = await db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error finding user by email: {str(e)}")
            return None

    async def create_user_from_google(
        self,
        db: AsyncSession,
        google_info: Dict,
        user_type: str = "BUYER"
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Crea un nuevo usuario usando información de Google.

        Args:
            db: Sesión de base de datos
            google_info: Información del usuario desde Google
            user_type: Tipo de usuario a crear

        Returns:
            Tuple (success, message, user)
        """
        try:
            # Extraer información de Google
            email = google_info.get('email')
            name = google_info.get('name', '')
            picture = google_info.get('picture', '')
            google_id = google_info.get('sub')
            email_verified = google_info.get('email_verified', False)

            if not email or not google_id:
                return False, "Información de Google incompleta", None

            # Dividir el nombre en nombre y apellido
            name_parts = name.split(' ', 1) if name else ['', '']
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            # Crear usuario sin contraseña (OAuth)
            user = User(
                email=email,
                password_hash="oauth_no_password",  # Placeholder para OAuth
                nombre=first_name,
                apellido=last_name,
                user_type=UserType(user_type),
                is_active=True,
                is_verified=True,  # Email ya verificado por Google
                email_verified=True,
                google_id=google_id,
                google_email=email,
                google_name=name,
                google_picture=picture,
                google_verified_email=email_verified,
                oauth_provider="google",
                oauth_linked_at=datetime.utcnow()
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

            logger.info(f"Created new user from Google OAuth: {email}")
            return True, "Usuario creado exitosamente", user

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating user from Google: {str(e)}")
            return False, f"Error creando usuario: {str(e)}", None

    async def link_google_to_existing_user(
        self,
        db: AsyncSession,
        user: User,
        google_info: Dict
    ) -> Tuple[bool, str]:
        """
        Vincula una cuenta de Google a un usuario existente.

        Args:
            db: Sesión de base de datos
            user: Usuario existente
            google_info: Información de Google

        Returns:
            Tuple (success, message)
        """
        try:
            # Actualizar campos de Google
            user.google_id = google_info.get('sub')
            user.google_email = google_info.get('email')
            user.google_name = google_info.get('name', '')
            user.google_picture = google_info.get('picture', '')
            user.google_verified_email = google_info.get('email_verified', False)
            user.oauth_provider = "google"
            user.oauth_linked_at = datetime.utcnow()

            # Si no tenía email verificado y Google lo tiene verificado
            if not user.email_verified and google_info.get('email_verified'):
                user.email_verified = True
                user.is_verified = True

            await db.commit()
            await db.refresh(user)

            logger.info(f"Linked Google account to existing user: {user.email}")
            return True, "Cuenta de Google vinculada exitosamente"

        except Exception as e:
            await db.rollback()
            logger.error(f"Error linking Google to user: {str(e)}")
            return False, f"Error vinculando cuenta: {str(e)}"

    async def authenticate_or_create_user(
        self,
        db: AsyncSession,
        token: str,
        user_type: str = "BUYER"
    ) -> Tuple[bool, str, Optional[User], Optional[str]]:
        """
        Autentica o crea un usuario usando un token de Google.

        Args:
            db: Sesión de base de datos
            token: Token ID de Google
            user_type: Tipo de usuario a crear si no existe

        Returns:
            Tuple (success, message, user, jwt_token)
        """
        try:
            # Verificar token de Google
            google_info = await self.verify_google_token(token)
            if not google_info:
                return False, "Token de Google inválido", None, None

            google_id = google_info.get('sub')
            email = google_info.get('email')

            if not google_id or not email:
                return False, "Información de Google incompleta", None, None

            # Buscar usuario por Google ID
            user = await self.find_user_by_google_id(db, google_id)

            if user:
                # Usuario existe con Google ID
                logger.info(f"User found by Google ID: {email}")
                jwt_token = auth_service.create_access_token(data={"sub": user.email})
                return True, "Login exitoso", user, jwt_token

            # Buscar por email
            user = await self.find_user_by_email(db, email)

            if user:
                # Usuario existe pero sin Google vinculado
                success, message = await self.link_google_to_existing_user(db, user, google_info)
                if success:
                    jwt_token = auth_service.create_access_token(data={"sub": user.email})
                    return True, "Cuenta vinculada y login exitoso", user, jwt_token
                else:
                    return False, message, None, None

            # Usuario no existe, crear nuevo
            success, message, user = await self.create_user_from_google(db, google_info, user_type)

            if success and user:
                jwt_token = auth_service.create_access_token(data={"sub": user.email})
                return True, "Usuario creado y login exitoso", user, jwt_token
            else:
                return False, message, None, None

        except Exception as e:
            logger.error(f"Error in Google authentication: {str(e)}")
            return False, f"Error en autenticación: {str(e)}", None, None


# Instancia global del servicio
google_oauth_service = GoogleOAuthService()