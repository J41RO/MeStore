#!/usr/bin/env python3
"""
PROTECCIÓN PERMANENTE SUPERUSER - NO MODIFICAR SIN AUTORIZACIÓN EXPRESA
======================================================================

Este script garantiza que el usuario admin@mestocker.com siempre tenga acceso.
EJECUTAR DESPUÉS DE CUALQUIER MIGRACIÓN O CAMBIO EN LA BASE DE DATOS.

Autor: Sistema de protección automática
Estado: CRÍTICO - NO MODIFICAR
"""

import os
import sys
sys.path.append('.')

from app.database import SessionLocal
from app.models.user import User, UserType
from passlib.context import CryptContext

# CONFIGURACIÓN PROTEGIDA - NO MODIFICAR
SUPERUSER_EMAIL = "admin@mestocker.com"
SUPERUSER_PASSWORD = "admin123"  # SINCRONIZADO CON FRONTEND
SUPERUSER_NOMBRE = "Admin"
SUPERUSER_APELLIDO = "Administrador"

def protect_superuser():
    """
    Garantiza que el superuser siempre exista y tenga acceso.
    FUNCIÓN CRÍTICA - NO MODIFICAR SIN AUTORIZACIÓN.
    """
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    db = SessionLocal()

    try:
        print("🛡️ INICIANDO PROTECCIÓN SUPERUSER...")

        # Buscar o crear superuser
        admin_user = db.query(User).filter(User.email == SUPERUSER_EMAIL).first()

        if not admin_user:
            print(f"⚠️ SUPERUSER NO ENCONTRADO - CREANDO: {SUPERUSER_EMAIL}")
            admin_user = User(
                email=SUPERUSER_EMAIL,
                nombre=SUPERUSER_NOMBRE,
                apellido=SUPERUSER_APELLIDO,
                user_type=UserType.SUPERUSER,
                password_hash=pwd_context.hash(SUPERUSER_PASSWORD),
                is_active=True,
                is_verified=True,
                is_superuser=True
            )
            db.add(admin_user)
        else:
            print(f"✅ SUPERUSER ENCONTRADO: {admin_user.email}")

        # Garantizar configuración correcta
        admin_user.password_hash = pwd_context.hash(SUPERUSER_PASSWORD)
        admin_user.user_type = UserType.SUPERUSER
        admin_user.is_active = True
        admin_user.is_verified = True
        admin_user.nombre = SUPERUSER_NOMBRE
        admin_user.apellido = SUPERUSER_APELLIDO

        # Corregir todos los usuarios con None values
        all_users = db.query(User).all()
        fixed_count = 0

        for user in all_users:
            if user.nombre is None:
                user.nombre = "Usuario"
                fixed_count += 1
            if user.apellido is None:
                user.apellido = "Usuario"
                fixed_count += 1

        db.commit()

        print(f"✅ SUPERUSER PROTEGIDO: {admin_user.email}")
        print(f"🔧 USUARIOS CORREGIDOS: {fixed_count} campos None arreglados")
        print(f"🔑 PASSWORD SINCRONIZADO: {SUPERUSER_PASSWORD}")
        print("🛡️ PROTECCIÓN APLICADA EXITOSAMENTE")

        return True

    except Exception as e:
        print(f"❌ ERROR EN PROTECCIÓN: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = protect_superuser()
    if success:
        print("\n🎯 SUPERUSER PROTECTION: ACTIVE")
        sys.exit(0)
    else:
        print("\n💥 SUPERUSER PROTECTION: FAILED")
        sys.exit(1)