#!/usr/bin/env python3
"""
Script rápido para verificar que la cuenta vendedor de testing esté disponible.
Si no existe, la recrea automáticamente.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserType
from app.utils.password import hash_password
from sqlalchemy import select

async def verify_or_create_vendor():
    """Verifica que la cuenta vendedor de testing exista, si no la crea."""
    engine = create_async_engine('postgresql+asyncpg://mestocker_user:mestocker_pass@localhost/mestocker_dev')
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        try:
            # Verificar si usuario existe
            result = await session.execute(
                select(User).where(User.email == "vendedor.test@mestore.com")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("✅ Cuenta vendedor de testing ya existe y está lista:")
                print(f"   📧 Email: {existing_user.email}")
                print(f"   👤 Nombre: {existing_user.nombre} {existing_user.apellido}")
                print(f"   🏷️ Tipo: {existing_user.user_type.value}")
                print(f"   ✅ Activo: {existing_user.is_active}")
                print(f"   ✅ Verificado: {existing_user.is_verified}")
                return True
            
            print("⚠️ Cuenta no existe, creando...")
            
            # Crear cuenta vendedor
            password_hash = await hash_password("VendorTest123!")
            vendor_user = User(
                email="vendedor.test@mestore.com",
                password_hash=password_hash,
                nombre="Vendedor",
                apellido="Testing", 
                user_type=UserType.VENDEDOR,
                is_active=True,
                is_verified=True,
                email_verified=True,
                phone_verified=True,
                otp_attempts=0,
                reset_attempts=0,
                cedula="87654321",
                telefono="+57301234567",
                ciudad="Medellín",
                empresa="TechStore Solutions S.A.S",
                direccion="Carrera 70 # 52-20, Medellín, Antioquia",
                banco="Bancolombia",
                tipo_cuenta="Ahorros", 
                numero_cuenta="12345678901",
                vendor_status="approved"
            )
            
            session.add(vendor_user)
            await session.commit()
            
            print("🎉 Cuenta vendedor creada exitosamente!")
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error: {e}")
            return False
        finally:
            await engine.dispose()

if __name__ == "__main__":
    print("🔍 Verificando cuenta vendedor de testing...")
    
    try:
        success = asyncio.run(verify_or_create_vendor())
        
        if success:
            print("\n🔗 CREDENCIALES PARA LOGIN:")
            print("   URL: http://192.168.1.137:5173/login")
            print("   Email: vendedor.test@mestore.com")
            print("   Password: VendorTest123!")
            print("\n📊 Dashboard: http://192.168.1.137:5173/dashboard")
        
    except Exception as e:
        print(f"❌ Error: {e}")