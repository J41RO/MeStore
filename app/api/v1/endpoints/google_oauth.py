# ~/app/api/v1/endpoints/google_oauth.py
# ---------------------------------------------------------------------------------------------
# MeStocker - Endpoints Google OAuth
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Endpoints para autenticación OAuth con Google.

Este módulo permite:
- Login con Google
- Registro con Google
- Vinculación de cuentas Google
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.google_oauth_service import google_oauth_service
from app.core.logger import get_logger

# Configurar router y logger
router = APIRouter(prefix="/auth/google", tags=["Google OAuth"])
logger = get_logger(__name__)


class GoogleTokenRequest(BaseModel):
    """Request para login/registro con Google."""
    id_token: str = Field(..., description="Token ID de Google")
    user_type: str = Field(default="BUYER", description="Tipo de usuario: BUYER o VENDOR")


class GoogleAuthResponse(BaseModel):
    """Response para autenticación con Google."""
    success: bool
    message: str
    access_token: str = None
    token_type: str = "bearer"
    user: dict = None


@router.post("/login", response_model=GoogleAuthResponse)
async def google_login(
    request: GoogleTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Iniciar sesión con Google OAuth.

    Flujo:
    1. Verifica el token ID de Google
    2. Busca usuario existente por Google ID o email
    3. Si existe, hace login
    4. Si no existe, crea nuevo usuario
    5. Retorna JWT token
    """
    try:
        logger.info(f"Google login attempt for user_type: {request.user_type}")

        # Validar tipo de usuario
        if request.user_type not in ["BUYER", "VENDOR"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de usuario inválido. Debe ser BUYER o VENDOR"
            )

        # Autenticar o crear usuario
        success, message, user, jwt_token = await google_oauth_service.authenticate_or_create_user(
            db=db,
            token=request.id_token,
            user_type=request.user_type
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=message
            )

        # Convertir usuario a dict para respuesta
        user_dict = None
        if user:
            user_dict = {
                "id": user.id,
                "email": user.email,
                "nombre": user.nombre,
                "apellido": user.apellido,
                "user_type": user.user_type.value if user.user_type else None,
                "is_verified": user.is_verified,
                "google_picture": user.google_picture,
                "oauth_provider": user.oauth_provider
            }

        logger.info(f"Google login successful for: {user.email}")

        return GoogleAuthResponse(
            success=True,
            message=message,
            access_token=jwt_token,
            user=user_dict
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Google login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en login con Google: {str(e)}"
        )


@router.post("/register", response_model=GoogleAuthResponse)
async def google_register(
    request: GoogleTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Registrarse con Google OAuth.

    Flujo similar al login, pero enfocado en crear nuevos usuarios.
    Si el usuario ya existe, hace login automáticamente.
    """
    try:
        logger.info(f"Google register attempt for user_type: {request.user_type}")

        # Validar tipo de usuario
        if request.user_type not in ["BUYER", "VENDOR"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de usuario inválido. Debe ser BUYER o VENDOR"
            )

        # Autenticar o crear usuario (mismo flujo que login)
        success, message, user, jwt_token = await google_oauth_service.authenticate_or_create_user(
            db=db,
            token=request.id_token,
            user_type=request.user_type
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        # Convertir usuario a dict para respuesta
        user_dict = None
        if user:
            user_dict = {
                "id": user.id,
                "email": user.email,
                "nombre": user.nombre,
                "apellido": user.apellido,
                "user_type": user.user_type.value if user.user_type else None,
                "is_verified": user.is_verified,
                "google_picture": user.google_picture,
                "oauth_provider": user.oauth_provider
            }

        logger.info(f"Google register successful for: {user.email}")

        return GoogleAuthResponse(
            success=True,
            message=message,
            access_token=jwt_token,
            user=user_dict
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Google register: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en registro con Google: {str(e)}"
        )


@router.get("/config")
async def get_google_config():
    """
    Obtiene la configuración de Google OAuth para el frontend.

    Retorna:
    - Client ID de Google
    - URLs de configuración
    - Estado del servicio
    """
    try:
        import os

        client_id = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id.apps.googleusercontent.com")

        return {
            "client_id": client_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://192.168.1.137:5173"
            ],
            "javascript_origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://192.168.1.137:5173"
            ],
            "service_status": "active"
        }

    except Exception as e:
        logger.error(f"Error getting Google config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo configuración: {str(e)}"
        )