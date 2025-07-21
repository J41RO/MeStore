# ~/app/core/security.py
# ---------------------------------------------------------------------------------------------
# MeStore - Módulo de Seguridad JWT y Passwords
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: security.py
# Ruta: ~/app/core/security.py
# Autor: Jairo
# Fecha de Creación: 2025-07-21
# Última Actualización: 2025-07-21
# Versión: 1.0.0
# Propósito: Funciones de seguridad para autenticación JWT y hash de contraseñas
#            Incluye generación de tokens, verificación de passwords y hashing seguro
#
# Modificaciones:
# 2025-07-21 - Creación inicial del módulo de seguridad
# 2025-07-21 - Refactor: Extraídas funciones de password a app/utils/password.py
#
# ---------------------------------------------------------------------------------------------

"""
Módulo de seguridad para MeStore.

Este módulo contiene las funciones esenciales para:
- Generación y manejo de tokens JWT
- Configuración de seguridad centralizada

Las funciones de hash y verificación de passwords fueron movidas a app/utils/password.py
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import JWTError, jwt
from app.utils.password import hash_password, verify_password, pwd_context

from .config import settings


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """
    Crear un token JWT de acceso.

    Args:
        data: Diccionario con los datos a incluir en el token (ej: {"sub": user_email})
        expires_delta: Tiempo de vida del token. Si es None, usa el default de configuración

    Returns:
        str: Token JWT firmado

    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> len(token) > 100  # Los JWT son largos
        True
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Union[dict, None]:
    """
    Decodificar y validar un token JWT.

    Args:
        token: Token JWT a decodificar

    Returns:
        dict: Payload del token si es válido, None si es inválido o expirado

    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> payload = decode_access_token(token)
        >>> payload["sub"]
        'user@example.com'
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
