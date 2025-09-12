#!/usr/bin/env python3
# create_working_admin.py - Usuario admin con credenciales ultra simples
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.utils.password import hash_password

async def create_working_admin():
    """
    Crea un usuario admin con credenciales super simples que definitivamente funcionan
    Email: admin@admin.com
    Password: admin123
    """
    engine = create_async_engine('postgresql+asyncpg://mestocker_user:mestocker_pass@localhost/mestocker_dev')
    
    async with engine.begin() as conn:
        try:
            # Primero eliminar usuario si existe
            await conn.execute(
                text("DELETE FROM users WHERE email = :email"),
                {"email": "admin@admin.com"}
            )
            
            # Hash de la contraseña super simple
            password_hash = await hash_password("admin123")
            
            print(f"🔐 Generando hash para password: admin123")
            print(f"📝 Hash generado: {password_hash[:20]}...")
            
            # Crear usuario con SQL directo
            await conn.execute(text("""
                INSERT INTO users (
                    id,
                    email, 
                    password_hash, 
                    nombre, 
                    apellido, 
                    user_type,
                    is_active, 
                    is_verified, 
                    email_verified,
                    phone_verified,
                    otp_attempts,
                    reset_attempts,
                    created_at,
                    updated_at
                ) VALUES (
                    gen_random_uuid(),
                    :email, 
                    :password_hash, 
                    :nombre, 
                    :apellido, 
                    :user_type,
                    :is_active, 
                    :is_verified, 
                    :email_verified,
                    :phone_verified,
                    :otp_attempts,
                    :reset_attempts,
                    NOW(),
                    NOW()
                )
            """), {
                "email": "admin@admin.com",
                "password_hash": password_hash,
                "nombre": "Admin",
                "apellido": "User",
                "user_type": "SUPERUSER",
                "is_active": True,
                "is_verified": True,
                "email_verified": True,
                "phone_verified": False,
                "otp_attempts": 0,
                "reset_attempts": 0
            })
            
            print("🎉 Usuario admin SIMPLE creado exitosamente:")
            print(f"   📧 Email: admin@admin.com")
            print(f"   🔐 Password: admin123")
            print(f"   🏷️ Tipo: SUPERUSER")
            print(f"   ✅ Activo: True")
            print("")
            print("🔗 Usa estas credenciales en:")
            print("   http://192.168.1.137:5173/admin-login")
            print("")
            print("⚡ CREDENCIALES ULTRA SIMPLES - GARANTIZADAS:")
            print("   Email: admin@admin.com")
            print("   Password: admin123")
            
        except Exception as e:
            print(f"❌ Error creando usuario: {e}")
            raise
        finally:
            await engine.dispose()

async def test_login():
    """Probar el login inmediatamente después de crear"""
    import aiohttp
    
    print("\n🧪 Probando login inmediatamente...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                'http://192.168.1.137:8000/api/v1/auth/login',
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (compatible; API-Client/1.0)'
                },
                json={
                    'email': 'admin@admin.com',
                    'password': 'admin123'
                }
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    print("✅ LOGIN EXITOSO!")
                    print(f"   Token recibido: {result.get('access_token', '')[:20]}...")
                else:
                    print(f"❌ Login falló: {response.status}")
                    print(f"   Error: {result}")
                    
        except Exception as e:
            print(f"❌ Error en test de login: {e}")

if __name__ == "__main__":
    print("🚀 Creando usuario admin ULTRA SIMPLE...")
    print("=" * 50)
    
    try:
        asyncio.run(create_working_admin())
        print("=" * 50)
        print("✅ Usuario creado, probando login...")
        asyncio.run(test_login())
        print("=" * 50)
        print("✅ Proceso completado")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)