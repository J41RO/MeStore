#!/usr/bin/env python3
# create_admin_simple.py - Versión simplificada
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.utils.password import hash_password

async def create_admin_user():
    """
    Crea un usuario universal usando SQL directo para evitar problemas de relaciones.
    """
    engine = create_async_engine('postgresql+asyncpg://mestocker_user:mestocker_pass@localhost/mestocker_dev')
    
    async with engine.begin() as conn:
        try:
            # Verificar si usuario ya existe
            result = await conn.execute(
                text("SELECT email, nombre FROM users WHERE email = :email"),
                {"email": "secure.admin@mestore.com"}
            )
            existing_user = result.fetchone()
            
            if existing_user:
                print("✅ Usuario ya existe:")
                print(f"   Email: {existing_user[0]}")
                print(f"   Nombre: {existing_user[1]}")
                return
                
            # Hash de la contraseña
            password_hash = hash_password("SecurePortal2024!")
            
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
                    cedula,
                    telefono,
                    ciudad,
                    empresa,
                    direccion,
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
                    :cedula,
                    :telefono,
                    :ciudad,
                    :empresa,
                    :direccion,
                    NOW(),
                    NOW()
                )
            """), {
                "email": "secure.admin@mestore.com",
                "password_hash": password_hash,
                "nombre": "Super Admin",
                "apellido": "Universal",
                "user_type": "SUPERUSER",
                "is_active": True,
                "is_verified": True,
                "email_verified": True,
                "phone_verified": False,
                "cedula": "12345678",
                "telefono": "+57300123456",
                "ciudad": "Bogotá",
                "empresa": "MeStore Corp",
                "direccion": "Calle 72 # 10-07, Bogotá, Colombia"
            })
            
            print("🎉 Usuario admin creado exitosamente:")
            print(f"   📧 Email: secure.admin@mestore.com")
            print(f"   👤 Nombre: Super Admin Universal")
            print(f"   🔐 Password: SecurePortal2024!")
            print(f"   🏷️ Tipo: SUPERUSER")
            print(f"   ✅ Activo: True")
            print(f"   📞 Teléfono: +57300123456")
            print(f"   🏢 Empresa: MeStore Corp")
            print("")
            print("🔗 Puedes usar estas credenciales en:")
            print("   http://192.168.1.137:5173/admin-login")
            
        except Exception as e:
            print(f"❌ Error creando usuario: {e}")
            raise
        finally:
            await engine.dispose()

if __name__ == "__main__":
    print("🚀 Creando usuario universal para MeStore...")
    print("=" * 50)
    
    try:
        asyncio.run(create_admin_user())
        print("=" * 50)
        print("✅ Operación completada exitosamente")
    except Exception as e:
        print(f"❌ Error durante la creación: {e}")
        exit(1)