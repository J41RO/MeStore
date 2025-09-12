#!/usr/bin/env python3
# create_admin_user.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserType
from app.utils.password import hash_password
from sqlalchemy import select

async def create_admin_user():
    """
    Crea un usuario universal con privilegios de SUPERUSER para testing.
    Email: secure.admin@mestore.com
    Password: SecurePortal2024!
    """
    engine = create_async_engine('postgresql+asyncpg://mestocker_user:mestocker_pass@localhost/mestocker_dev')
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        try:
            # Verificar si usuario ya existe
            result = await session.execute(
                select(User).where(User.email == "secure.admin@mestore.com")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("✅ Usuario ya existe:")
                print(f"   Email: {existing_user.email}")
                print(f"   Nombre: {existing_user.nombre}")
                print(f"   Tipo: {existing_user.user_type}")
                print(f"   Activo: {existing_user.is_active}")
                return existing_user
                
            # Crear usuario universal con todos los privilegios
            admin_user = User(
                email="secure.admin@mestore.com",
                password_hash=hash_password("SecurePortal2024!"),
                nombre="Super Admin",
                apellido="Universal",
                user_type=UserType.SUPERUSER,  # Máximo nivel de privilegios
                is_active=True,
                is_verified=True,  # Pre-verificado
                email_verified=True,  # Email pre-verificado
                phone_verified=False,  # Teléfono no requerido
                cedula="12345678",  # Cédula de ejemplo
                telefono="+57300123456",
                ciudad="Bogotá",
                empresa="MeStore Corp",
                direccion="Calle 72 # 10-07, Bogotá, Colombia"
            )
            
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)
            
            print("🎉 Usuario admin creado exitosamente:")
            print(f"   📧 Email: {admin_user.email}")
            print(f"   👤 Nombre: {admin_user.full_name}")
            print(f"   🔐 Password: SecurePortal2024!")
            print(f"   🏷️ Tipo: {admin_user.user_type.value}")
            print(f"   ✅ Activo: {admin_user.is_active}")
            print(f"   📞 Teléfono: {admin_user.telefono}")
            print(f"   🏢 Empresa: {admin_user.empresa}")
            print("")
            print("🔗 Puedes usar estas credenciales en:")
            print("   http://192.168.1.137:5173/admin-login")
            
            return admin_user
            
        except Exception as e:
            await session.rollback()
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