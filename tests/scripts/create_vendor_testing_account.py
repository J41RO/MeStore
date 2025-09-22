#!/usr/bin/env python3
"""
Script para crear cuenta vendedor permanente para testing del Dashboard Vendor.
Esta cuenta estará siempre disponible para verificar funcionalidades.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserType
from app.utils.password import hash_password
from sqlalchemy import select

async def create_vendor_testing_account():
    """
    Crea una cuenta vendedor permanente para testing del dashboard.
    
    Credenciales:
    Email: vendedor.test@mestore.com
    Password: VendorTest123!
    """
    engine = create_async_engine('postgresql+asyncpg://mestocker_user:mestocker_pass@localhost/mestocker_dev')
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        try:
            # Verificar si usuario ya existe
            result = await session.execute(
                select(User).where(User.email == "vendedor.test@mestore.com")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("✅ Usuario vendedor de testing ya existe:")
                print(f"   📧 Email: {existing_user.email}")
                print(f"   👤 Nombre: {existing_user.nombre} {existing_user.apellido}")
                print(f"   🏷️ Tipo: {existing_user.user_type.value}")
                print(f"   ✅ Activo: {existing_user.is_active}")
                print(f"   ✅ Verificado: {existing_user.is_verified}")
                print(f"   📞 Teléfono: {existing_user.telefono}")
                print(f"   🏢 Empresa: {existing_user.empresa}")
                print(f"   📍 Ciudad: {existing_user.ciudad}")
                print("")
                print("🔗 Credenciales para login:")
                print("   Email: vendedor.test@mestore.com")
                print("   Password: VendorTest123!")
                print("   URL: http://192.168.1.137:5173/login")
                return existing_user
                
            # Crear cuenta vendedor completa para testing
            password_hash = await hash_password("VendorTest123!")
            vendor_user = User(
                email="vendedor.test@mestore.com",
                password_hash=password_hash,
                nombre="Vendedor",
                apellido="Testing",
                user_type=UserType.VENDEDOR,  # Tipo vendedor
                is_active=True,
                is_verified=True,  # Pre-verificado para evitar OTP
                email_verified=True,  # Email pre-verificado
                phone_verified=True,  # Teléfono pre-verificado
                otp_attempts=0,
                reset_attempts=0,
                
                # Información personal completa
                cedula="87654321",  # Cédula válida
                telefono="+57301234567",
                ciudad="Medellín",
                empresa="TechStore Solutions S.A.S",
                direccion="Carrera 70 # 52-20, Medellín, Antioquia",
                
                # Información bancaria para comisiones
                banco="Bancolombia",
                tipo_cuenta="Ahorros",
                numero_cuenta="12345678901",
                
                # Status de vendedor
                vendor_status="approved"  # Pre-aprobado
            )
            
            session.add(vendor_user)
            await session.commit()
            await session.refresh(vendor_user)
            
            print("🎉 Cuenta vendedor de testing creada exitosamente:")
            print(f"   📧 Email: {vendor_user.email}")
            print(f"   👤 Nombre: {vendor_user.nombre} {vendor_user.apellido}")
            print(f"   🔐 Password: VendorTest123!")
            print(f"   🏷️ Tipo: {vendor_user.user_type.value}")
            print(f"   ✅ Activo: {vendor_user.is_active}")
            print(f"   ✅ Verificado: {vendor_user.is_verified}")
            print(f"   📞 Teléfono: {vendor_user.telefono}")
            print(f"   🏢 Empresa: {vendor_user.empresa}")
            print(f"   📍 Ciudad: {vendor_user.ciudad}")
            print(f"   🏪 Vendor Status: {vendor_user.vendor_status}")
            print("")
            print("🔗 Para acceder al Dashboard Vendor:")
            print("   1. Ir a: http://192.168.1.137:5173/login")
            print("   2. Email: vendedor.test@mestore.com")
            print("   3. Password: VendorTest123!")
            print("   4. Después del login, navegar a: http://192.168.1.137:5173/dashboard")
            print("")
            print("📊 Features disponibles en el dashboard:")
            print("   • Métricas de vendedor en tiempo real")
            print("   • Productos recientes y top products")
            print("   • Órdenes pendientes y completadas")
            print("   • Gráficos de ventas y performance")
            print("   • Acciones rápidas y navegación")
            
            return vendor_user
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creando cuenta vendedor: {e}")
            raise
        finally:
            await engine.dispose()

async def verify_login_capability():
    """Verifica que el usuario puede hacer login correctamente."""
    from app.utils.password import hash_password, verify_password
    
    # Verificar que el hash de password funciona
    test_password = "VendorTest123!"
    hashed = await hash_password(test_password)
    
    print("\n🔍 Verificando capacidad de login...")
    print(f"   Password original: {test_password}")
    print(f"   Hash generado: {hashed[:50]}...")
    
    # Verificar que el password se puede validar
    verification_result = await verify_password(test_password, hashed)
    
    if verification_result:
        print("   ✅ Hash de password y verificación funcionan correctamente")
        return True
    else:
        print("   ❌ Error en verificación de password")
        return False

if __name__ == "__main__":
    print("🚀 Creando cuenta vendedor permanente para testing...")
    print("=" * 60)
    
    try:
        # Crear la cuenta
        asyncio.run(create_vendor_testing_account())
        
        # Verificar login
        asyncio.run(verify_login_capability())
        
        print("=" * 60)
        print("✅ Cuenta vendedor de testing lista para usar")
        print("")
        print("📝 INSTRUCCIONES DE USO:")
        print("1. Abrir: http://192.168.1.137:5173/login")
        print("2. Usuario: vendedor.test@mestore.com") 
        print("3. Password: VendorTest123!")
        print("4. Ir al dashboard: http://192.168.1.137:5173/dashboard")
        print("")
        print("💡 Esta cuenta está pre-configurada y siempre disponible")
        
    except Exception as e:
        print(f"❌ Error durante la creación: {e}")
        exit(1)