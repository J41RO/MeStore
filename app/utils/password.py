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
# Última Actualización: 2025-07-31
# Versión: 1.1.0
# Propósito: Utilidades para hash y verificación segura de contraseñas usando bcrypt
#            CORRECCIÓN: Manejo async/sync corregido para prevenir RuntimeError
#
# Modificaciones:
# 2025-07-21 - Extracción inicial desde app/core/security.py
# 2025-07-31 - CORRECCIÓN CRÍTICA: ThreadPoolExecutor global para evitar "Event loop is closed"
#
# ---------------------------------------------------------------------------------------------

"""
Utilidades para hash y verificación de contraseñas.

Este módulo contiene funciones para:
- Hash seguro de contraseñas usando bcrypt
- Verificación de contraseñas contra su hash
- Configuración del contexto de encriptación

CORRECCIÓN APLICADA v1.1.0:
- ThreadPoolExecutor ahora usa instancia global
- Evita RuntimeError: Event loop is closed
- Corrige ERROR 500 en validación de email duplicado

Extraído desde app/core/security.py para mejor modularización.
"""

import asyncio
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from passlib.context import CryptContext

# Configuración del contexto de passwords con bcrypt
# Environment-aware configuration for performance optimization

def _get_bcrypt_rounds():
    """Get bcrypt rounds based on environment for performance optimization."""
    environment = os.getenv("ENVIRONMENT", "development")
    testing = (
        "pytest" in sys.modules or
        os.getenv("PYTEST_CURRENT_TEST") is not None or
        os.getenv("TESTING") == "true" or
        environment == "testing"
    )

    if testing:
        # Testing: Very fast, minimal security (only for tests)
        return 4
    elif environment == "development":
        # Development: Fast but some security
        return 8
    else:
        # Production: Full security
        return 12

# Configure bcrypt with environment-appropriate rounds
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=_get_bcrypt_rounds()
)

# CORRECCIÓN CRÍTICA: ThreadPoolExecutor global para evitar RuntimeError
_bcrypt_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="bcrypt-pool")


async def hash_password(password: str) -> str:
    """
    Generar hash seguro de una contraseña usando bcrypt.
    
    CORRECCIÓN v1.1.0: Usa ThreadPoolExecutor global para evitar
    RuntimeError: Event loop is closed que causaba ERROR 500

    Args:
        password: Contraseña en texto plano

    Returns:
        str: Hash bcrypt de la contraseña

    Example:
        >>> hash1 = await hash_password("mi_password")
        >>> hash2 = await hash_password("mi_password")
        >>> hash1 != hash2  # Cada hash es único (salt diferente)
        True
        >>> len(hash1)  # Longitud típica de hash bcrypt
        60
    """
    # CORRECCIÓN: Usar executor global en lugar de with statement
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_bcrypt_executor, pwd_context.hash, password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar si una contraseña en texto plano coincide con su hash.
    
    CORRECCIÓN v1.1.0: Usa ThreadPoolExecutor global para evitar
    RuntimeError: Event loop is closed que causaba ERROR 500

    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de la contraseña (generado con hash_password)

    Returns:
        bool: True si la contraseña coincide, False en caso contrario

    Example:
        >>> hashed = await hash_password("mi_password")
        >>> await verify_password("mi_password", hashed)
        True
        >>> await verify_password("password_incorrecta", hashed)
        False
    """
    # CORRECCIÓN: Usar executor global en lugar de with statement
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_bcrypt_executor, pwd_context.verify, plain_password, hashed_password)


def cleanup_bcrypt_executor():
    """
    Función para limpiar el ThreadPoolExecutor al cerrar la aplicación.
    
    Debe ser llamada en el shutdown de la aplicación FastAPI.
    """
    global _bcrypt_executor
    if _bcrypt_executor:
        _bcrypt_executor.shutdown(wait=True)
