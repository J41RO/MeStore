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
#
# ---------------------------------------------------------------------------------------------

"""
Módulo de seguridad para MeStore.

Este módulo contiene las funciones esenciales para:
- Generación y manejo de tokens JWT
- Hash seguro de contraseñas con bcrypt
- Verificación de contraseñas
- Configuración de seguridad centralizada
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from app.utils.password import hash_password, verify_password, pwd_context

from .config import settings





def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:














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






    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de la contraseña (generado con get_password_hash)

    Returns:
        bool: True si la contraseña coincide, False en caso contrario


        >>> hashed = get_password_hash("mi_password")
        >>> verify_password("mi_password", hashed)
        True
        >>> verify_password("password_incorrecta", hashed)
        False





    """
    Generar hash seguro de una contraseña usando bcrypt.

    Args:
        password: Contraseña en texto plano

    Returns:
        str: Hash bcrypt de la contraseña


        >>> hash1 = get_password_hash("mi_password")
        >>> hash2 = get_password_hash("mi_password")
        >>> hash1 != hash2  # Cada hash es único (salt diferente)
        True
        >>> len(hash1)  # Longitud típica de hash bcrypt
        60
    """



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