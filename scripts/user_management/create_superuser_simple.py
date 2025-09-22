#!/usr/bin/env python3
"""
Script simple para crear superuser directamente
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from sqlalchemy import text

async def create_superuser_simple():
    """Crear superuser directamente con SQL"""

    async with AsyncSessionLocal() as db:
        try:
            print("🔄 Creando superuser con SQL directo...")

            # Hash the password
            password_hash = hash_password("123456")
            user_id = str(uuid.uuid4())
            now = datetime.utcnow()

            # Insert user directly
            sql = """
            INSERT INTO users (
                id, email, password_hash, nombre, apellido,
                user_type, is_active, is_verified,
                email_verified, phone_verified, otp_attempts,
                created_at, updated_at
            ) VALUES (
                :id, :email, :password_hash, :nombre, :apellido,
                :user_type, :is_active, :is_verified,
                :email_verified, :phone_verified, :otp_attempts,
                :created_at, :updated_at
            )
            """

            await db.execute(text(sql), {
                'id': user_id,
                'email': 'super@mestore.com',
                'password_hash': password_hash,
                'nombre': 'Super',
                'apellido': 'Administrator',
                'user_type': 'SUPERUSER',
                'is_active': True,
                'is_verified': True,
                'email_verified': True,
                'phone_verified': False,
                'otp_attempts': 0,
                'created_at': now,
                'updated_at': now
            })

            await db.commit()

            print("✅ Superuser creado exitosamente!")
            print(f"📧 Email: super@mestore.com")
            print(f"🔑 Password: 123456")
            print(f"👤 Type: SUPERUSER")
            print(f"🆔 ID: {user_id}")

            return True

        except Exception as e:
            await db.rollback()
            if "UNIQUE constraint failed" in str(e):
                print("✅ Superuser ya existe - verificando...")
                try:
                    result = await db.execute(
                        text("SELECT email, user_type FROM users WHERE email = :email"),
                        {'email': 'super@mestore.com'}
                    )
                    user = result.fetchone()
                    if user:
                        print(f"✅ Usuario confirmado: {user.email} ({user.user_type})")
                        print("🔑 Password: 123456")
                        return True
                except Exception as verify_error:
                    print(f"❌ Error verificando usuario existente: {verify_error}")
                    return False
            else:
                print(f"❌ Error creando superuser: {e}")
                return False

if __name__ == "__main__":
    success = asyncio.run(create_superuser_simple())
    if success:
        print("\n🎉 SUPERUSER LISTO - Puedes hacer login en:")
        print("🌐 URL: http://192.168.1.137:5173/admin-login")
        print("📧 Email: super@mestore.com")
        print("🔑 Password: 123456")
    else:
        print("\n❌ FALLÓ - Verificar logs")

    sys.exit(0 if success else 1)