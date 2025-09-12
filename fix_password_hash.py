#!/usr/bin/env python3
"""
Script para generar hash correcto de contraseña y actualizar usuarios.
"""
import sys
import os
import asyncio

# Agregar el directorio raíz al path
sys.path.append('/home/admin-jairo/MeStore')

from app.utils.password import hash_password
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.user import User

async def fix_passwords():
    """Corregir las contraseñas de los usuarios"""
    print("🔧 Generando hash correcto para contraseña '123456'...")
    
    # Generar hash correcto
    correct_hash = await hash_password("123456")
    print(f"✅ Hash generado: {correct_hash}")
    
    # Actualizar base de datos
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Actualizar todos los usuarios
        users = session.query(User).all()
        for user in users:
            user.password_hash = correct_hash
            print(f"✅ Actualizado hash para {user.email}")
        
        session.commit()
        print(f"\n🎉 Actualizados {len(users)} usuarios exitosamente!")
        
        # Verificar
        print("\n📋 USUARIOS ACTUALIZADOS:")
        for user in users:
            print(f"   🔑 {user.email} / 123456 ({user.user_type.value})")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(fix_passwords())