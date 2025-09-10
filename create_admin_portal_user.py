#!/usr/bin/env python3
"""
Script para crear usuario administrativo del portal oculto.
Credenciales: secure.admin@mestore.com / SecurePortal2024!
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from app.models.user import User, UserType
from app.services.auth_service import AuthService
from sqlalchemy import select

async def create_admin_portal_user():
    """Crear usuario administrativo para el portal oculto."""
    
    email = "secure.admin@mestore.com"
    password = "SecurePortal2024!"
    
    print(f"Creando usuario administrativo: {email}")
    
    try:
        # Crear sesión asíncrona
        async with AsyncSessionLocal() as db:
            auth_service = AuthService()
            
            # Verificar si el usuario ya existe
            result = await db.execute(
                select(User).where(User.email == email)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"Usuario {email} ya existe - actualizando credenciales")
                # Usar función sync para hash
                existing_user.password_hash = auth_service.get_password_hash(password)
                existing_user.user_type = UserType.SUPERUSER
                existing_user.is_active = True
                existing_user.is_verified = True
                await db.commit()
                print(f"Usuario {email} actualizado exitosamente")
                return
            
            # Crear nuevo usuario administrativo
            admin_user = await auth_service.create_user(
                db=db,
                email=email,
                password=password,
                user_type=UserType.SUPERUSER,
                nombre="Administrador",
                apellido="Portal",
                is_active=True,
                is_verified=True,
                ciudad="Bucaramanga",
                empresa="MeStocker"
            )
            
            await db.commit()
            print(f"Usuario administrativo creado exitosamente:")
            print(f"   Email: {email}")
            print(f"   Tipo: {admin_user.user_type}")
            print(f"   ID: {admin_user.id}")
            
    except Exception as e:
        print(f"Error creando usuario administrativo: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Iniciando creacion de usuario administrativo del portal...")
    asyncio.run(create_admin_portal_user())
    print("Proceso completado")
