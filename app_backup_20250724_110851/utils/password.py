# ~/app/utils/password.py
# ---------------------------------------------------------------------------------------------
# MeStore - Utilidades de Hash y Verificación de Passwords
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: password.py
# Ruta: ~/app/utils/password.py
# Autor: Jairo
# Fecha de Creación: 2025-07-21
# Última Actualización: 2025-07-21
# Versión: 1.0.0
# Propósito: Utilidades para hash y verificación segura de contraseñas usando bcrypt
#
# Modificaciones:
# 2025-07-21 - Extracción inicial desde app/core/security.py
#
# ---------------------------------------------------------------------------------------------

"""
Utilidades para hash y verificación de contraseñas.

Este módulo contiene funciones para:
- Hash seguro de contraseñas usando bcrypt
- Verificación de contraseñas contra su hash
- Configuración del contexto de encriptación

Extraído desde app/core/security.py para mejor modularización.
"""

from passlib.context import CryptContext

# Configuración del contexto de passwords con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Generar hash seguro de una contraseña usando bcrypt.

    Args:
        password: Contraseña en texto plano

    Returns:
        str: Hash bcrypt de la contraseña

    Example:
        >>> hash1 = hash_password("mi_password")
        >>> hash2 = hash_password("mi_password")
        >>> hash1 != hash2  # Cada hash es único (salt diferente)
        True
        >>> len(hash1)  # Longitud típica de hash bcrypt
        60
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar si una contraseña en texto plano coincide con su hash.

    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de la contraseña (generado con hash_password)

    Returns:
        bool: True si la contraseña coincide, False en caso contrario

    Example:
        >>> hashed = hash_password("mi_password")
        >>> verify_password("mi_password", hashed)
        True
        >>> verify_password("password_incorrecta", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)
