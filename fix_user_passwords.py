#!/usr/bin/env python3
"""
Script para actualizar contraseñas de usuarios a 123456
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal
from app.models.user import User, UserType
from app.utils.password import hash_password
from sqlalchemy import select, update

async def fix_passwords():
    """Actualizar contraseñas de todos los usuarios a 123456"""
    
    async with AsyncSessionLocal() as db:
        try:
            print("🔄 Actualizando contraseñas a '123456'...")
            
            # Hash de la nueva contraseña
            new_password_hash = await hash_password("123456")
            
            # Actualizar todos los usuarios
            result = await db.execute(
                update(User).values(password_hash=new_password_hash)
            )
            
            await db.commit()
            
            print(f"✅ {result.rowcount} contraseñas actualizadas exitosamente!")
            print("\n=== CREDENCIALES ACTUALIZADAS ===")
            print("📧 buyer@mestore.com | 🔑 123456 | 👤 COMPRADOR")
            print("📧 vendor@mestore.com | 🔑 123456 | 👤 VENDEDOR")
            print("📧 admin@mestore.com | 🔑 123456 | 👤 ADMIN")
            print("📧 super@mestore.com | 🔑 123456 | 👤 SUPERUSER")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error actualizando contraseñas: {e}")
            return False
            
    return True

if __name__ == "__main__":
    success = asyncio.run(fix_passwords())
    sys.exit(0 if success else 1)