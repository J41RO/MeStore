"""
~/app/services/auth_service.py
-------------------------------------------------------------------------------------
MESTOCKER - Servicio de Autenticación
Copyright (c) 2025 Jairo. Todos los derechos reservados.
Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
-------------------------------------------------------------------------------------

Nombre del Archivo: auth_service.py
Ruta: ~/app/services/auth_service.py  
Autor: Jairo
Fecha de Creación: 2025-07-31
Última Actualización: 2025-07-31
Versión: 1.0.0
Propósito: Servicio centralizado de autenticación con manejo async/sync correcto
           para prevenir RuntimeError: Event loop is closed

Modificaciones:
2025-07-31 - Creación con corrección async/sync para bcrypt

-------------------------------------------------------------------------------------
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from passlib.context import CryptContext


class AuthService:
    """
    Servicio de autenticación con manejo correcto async/sync.
    
    Resuelve el problema de RuntimeError: Event loop is closed
    usando ThreadPoolExecutor para operaciones bcrypt.
    """
    
    def __init__(self):
        """Inicializar servicio con contexto bcrypt y thread pool."""
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto"
        )
        # ThreadPoolExecutor para operaciones bcrypt async
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="bcrypt")
    
    async def get_password_hash(self, password: str) -> str:
        """
        Hash password usando bcrypt con ThreadPoolExecutor.
        
        Esta función corrige el error RuntimeError: Event loop is closed
        ejecutando bcrypt en thread separado.
        
        Args:
            password: Password en texto plano
            
        Returns:
            Password hasheado con bcrypt
        """
        loop = asyncio.get_event_loop()
        
        # Ejecutar bcrypt.hash en thread separado para evitar bloqueo del event loop
        hashed_password = await loop.run_in_executor(
            self.executor,
            self._hash_password_sync,
            password
        )
        
        return hashed_password
    
    def _hash_password_sync(self, password: str) -> str:
        """
        Función sync interna para hash con bcrypt.
        
        Args:
            password: Password a hashear
            
        Returns:
            Password hasheado
        """
        return self.pwd_context.hash(password)
    
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verificar password usando bcrypt con ThreadPoolExecutor.
        
        Args:
            plain_password: Password en texto plano
            hashed_password: Password hasheado a verificar
            
        Returns:
            True si coincide, False si no
        """
        loop = asyncio.get_event_loop()
        
        # Ejecutar bcrypt.verify en thread separado
        is_valid = await loop.run_in_executor(
            self.executor,
            self._verify_password_sync,
            plain_password,
            hashed_password
        )
        
        return is_valid
    
    def _verify_password_sync(self, plain_password: str, hashed_password: str) -> bool:
        """
        Función sync interna para verificar password.
        
        Args:
            plain_password: Password en texto plano
            hashed_password: Password hasheado
            
        Returns:
            True si coincide, False si no
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def __del__(self):
        """Cleanup del ThreadPoolExecutor al destruir el objeto."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
