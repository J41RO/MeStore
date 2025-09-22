#!/usr/bin/env python3
"""
Script para crear superuser definitivo - SOLUCIÓN FINAL
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.auth_service import AuthService
from app.models.user import UserType
from app.core.database import AsyncSessionLocal

async def create_superuser_final():
    """Crear superuser definitivo"""

    async with AsyncSessionLocal() as db:
        auth_service = AuthService()

        try:
            print("🔄 Creando superuser definitivo...")

            user = await auth_service.create_user(
                db=db,
                email='super@mestore.com',
                password='123456',
                nombre='Super',
                apellido='Administrator',
                user_type=UserType.SUPERUSER
            )

            await db.commit()
            print(f"✅ Superuser creado exitosamente!")
            print(f"📧 Email: {user.email}")
            print(f"🔑 Password: 123456")
            print(f"👤 Type: {user.user_type}")
            print(f"🆔 ID: {user.id}")

            return True

        except ValueError as e:
            if "ya existe" in str(e):
                print("✅ Superuser ya existe - verificando...")
                # Verificar que existe
                from sqlalchemy import select
                from app.models.user import User

                result = await db.execute(
                    select(User).where(User.email == 'super@mestore.com')
                )
                existing_user = result.scalar_one_or_none()

                if existing_user:
                    print(f"✅ Superuser confirmado: {existing_user.email}")
                    print(f"👤 Type: {existing_user.user_type}")
                    print(f"🔑 Password: 123456 (use existing)")
                    return True
                else:
                    print("❌ Error: Usuario no encontrado después de verificación")
                    return False
            else:
                print(f"❌ Error creando superuser: {e}")
                return False

        except Exception as e:
            await db.rollback()
            print(f"❌ Error general: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(create_superuser_final())
    if success:
        print("\n🎉 SUPERUSER LISTO - Puedes hacer login en:")
        print("🌐 URL: http://192.168.1.137:5173/admin-login")
        print("📧 Email: super@mestore.com")
        print("🔑 Password: 123456")
    else:
        print("\n❌ FALLÓ - Revisar configuración de base de datos")

    sys.exit(0 if success else 1)