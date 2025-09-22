#!/usr/bin/env python3
"""
Script para limpiar usuarios existentes y crear usuarios específicos para el proyecto.
Usuarios a crear:
- admin@mestore.com / 123456 (Admin)
- vendor@mestore.com / 123456 (Vendedor)
- buyer@mestore.com / 123456 (Comprador)  
- super@mestore.com / 123456 (SuperUser)
"""
import sys
import os
from datetime import datetime, timezone

# Agregar el directorio raíz al path para importar los módulos
sys.path.append('/home/admin-jairo/MeStore')

from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, delete
from app.core.database import engine
from app.models.user import User, UserType
from app.utils.password import hash_password
import asyncio

async def setup_project_users():
    """Configura los usuarios específicos para el proyecto"""
    print("🔧 Iniciando configuración de usuarios del proyecto...")
    
    # Crear sesión de base de datos
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # 1. LIMPIAR TODOS LOS USUARIOS EXISTENTES
        print("\n🗑️  PASO 1: Limpiando usuarios existentes...")
        
        # Eliminar usuarios
        deleted_users = session.execute(delete(User)).rowcount
        print(f"   ✅ Eliminados {deleted_users} usuarios")
        
        session.commit()
        print("   ✅ Base de datos limpiada exitosamente")
        
        # 2. CREAR USUARIOS ESPECÍFICOS
        print("\n👥 PASO 2: Creando usuarios específicos...")
        
        users_to_create = [
            {
                "email": "admin@mestore.com",
                "password": "123456", 
                "user_type": UserType.ADMIN,
                "nombre": "Admin",
                "apellido": "MeStore"
            },
            {
                "email": "vendor@mestore.com",
                "password": "123456",
                "user_type": UserType.VENDEDOR, 
                "nombre": "Vendor",
                "apellido": "Demo"
            },
            {
                "email": "buyer@mestore.com", 
                "password": "123456",
                "user_type": UserType.COMPRADOR,
                "nombre": "Buyer",
                "apellido": "Demo"
            },
            {
                "email": "super@mestore.com",
                "password": "123456",
                "user_type": UserType.SUPERUSER,
                "nombre": "Super", 
                "apellido": "Admin"
            }
        ]
        
        created_users = []
        
        for user_data in users_to_create:
            print(f"\n   🔧 Creando usuario: {user_data['email']}")
            
            # Crear usuario
            hashed_password = await hash_password(user_data['password'])
            user = User(
                email=user_data['email'],
                hashed_password=hashed_password,
                user_type=user_data['user_type'],
                nombre=user_data['nombre'],
                apellido=user_data['apellido'],
                is_active=True,
                is_verified=True,
                email_verified=True,
                cedula=f"1{len(created_users)+1:08d}",  # Cédula fake
                telefono="123-456-7890",
                ciudad="Bogotá",
                empresa="MeStore Demo",
                direccion="Dirección Demo",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            session.add(user)
            created_users.append(user_data)
            
            print(f"   ✅ Usuario {user_data['email']} creado como {user_data['user_type'].value}")
        
        session.commit()
        
        # 3. VERIFICACIÓN
        print("\n✅ PASO 3: Verificación de usuarios creados...")
        total_users = session.query(User).count()
        
        print(f"   📊 Total usuarios en DB: {total_users}")
        
        # Mostrar todos los usuarios creados
        users = session.query(User).all()
        print("\n📋 USUARIOS FINALES:")
        for user in users:
            print(f"   🔑 {user.email} / 123456 ({user.user_type.value}) - {user.nombre} {user.apellido}")
        
        print(f"\n🎉 ¡Configuración completada exitosamente!")
        print(f"📝 Total de usuarios creados: {len(created_users)}")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error durante la configuración: {str(e)}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return False
    finally:
        session.close()

def main():
    """Función principal"""
    print("🚀 MeStore - Configurador de Usuarios del Proyecto")
    print("=" * 50)
    
    # Ejecutar configuración
    try:
        result = asyncio.run(setup_project_users())
        if result:
            print("\n" + "=" * 50)
            print("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
            print("\n🔐 CREDENCIALES DE ACCESO:")
            print("   • admin@mestore.com / 123456 (Admin)")
            print("   • vendor@mestore.com / 123456 (Vendedor)")  
            print("   • buyer@mestore.com / 123456 (Comprador)")
            print("   • super@mestore.com / 123456 (SuperUser)")
            print("\n🌐 Acceder en: http://localhost:5174")
        else:
            print("\n❌ CONFIGURACIÓN FALLÓ - Ver errores arriba")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error crítico: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()