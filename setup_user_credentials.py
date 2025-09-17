#!/usr/bin/env python3
"""
Script para configurar credenciales de usuarios de testing
"""

import asyncio
import sys
import os
from sqlalchemy import select, delete

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal
from app.models.user import User, UserType
from app.utils.password import hash_password

async def setup_credentials():
    """Configurar credenciales estándar para testing"""
    
    # Credenciales estándar
    test_users = [
        {
            'email': 'buyer@mestore.com',
            'password': 'Buyer123!',
            'user_type': UserType.BUYER,
            'nombre': 'Buyer',
            'apellido': 'Demo',
            'is_active': True,
            'email_verified': True
        },
        {
            'email': 'vendor@mestore.com', 
            'password': 'Vendor123!',
            'user_type': UserType.VENDOR,
            'nombre': 'Vendor',
            'apellido': 'Demo',
            'is_active': True,
            'email_verified': True
        },
        {
            'email': 'admin@mestore.com',
            'password': 'Admin123!', 
            'user_type': UserType.ADMIN,
            'nombre': 'Admin',
            'apellido': 'MeStore',
            'is_active': True,
            'email_verified': True
        },
        {
            'email': 'super@mestore.com',
            'password': 'Super123!',
            'user_type': UserType.SUPERUSER,
            'nombre': 'Super',
            'apellido': 'Admin',
            'is_active': True,
            'email_verified': True
        }
    ]
    
    async with AsyncSessionLocal() as db:
        try:
            print("🔄 Configurando credenciales de testing...")
            
            for user_data in test_users:
                # Verificar si el usuario ya existe
                result = await db.execute(
                    select(User).filter(User.email == user_data['email'])
                )
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    print(f"📝 Actualizando usuario: {user_data['email']}")
                    # Actualizar contraseña (await porque es async)
                    existing_user.password_hash = await hash_password(user_data['password'])
                    existing_user.user_type = user_data['user_type']
                    existing_user.is_active = user_data['is_active']
                    existing_user.email_verified = user_data['email_verified']
                else:
                    print(f"🆕 Creando usuario: {user_data['email']}")
                    # Crear nuevo usuario (await porque hash_password es async)
                    new_user = User(
                        email=user_data['email'],
                        password_hash=await hash_password(user_data['password']),
                        user_type=user_data['user_type'],
                        nombre=user_data['nombre'],
                        apellido=user_data['apellido'],
                        is_active=user_data['is_active'],
                        email_verified=user_data['email_verified']
                    )
                    db.add(new_user)
            
            await db.commit()
            
            print("✅ Credenciales configuradas exitosamente!")
            print("\n=== CREDENCIALES DE TESTING ===")
            for user_data in test_users:
                print(f"📧 {user_data['email']} | 🔑 {user_data['password']} | 👤 {user_data['user_type'].value}")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error configurando credenciales: {e}")
            return False
            
    return True

if __name__ == "__main__":
    success = asyncio.run(setup_credentials())
    sys.exit(0 if success else 1)