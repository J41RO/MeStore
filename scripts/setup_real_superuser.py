#!/usr/bin/env python3
"""
Script para crear el superusuario real de MeStore
Elimina usuarios de prueba y crea un superusuario verificado con máximo nivel de seguridad
"""

import asyncio
import sys
import os
import getpass
from datetime import datetime
from uuid import uuid4

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
import sqlite3
from app.utils.password import hash_password


def validate_email(email: str) -> bool:
    """Validar formato básico de email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> bool:
    """Validar que la contraseña sea segura"""
    if len(password) < 8:
        print("❌ La contraseña debe tener al menos 8 caracteres")
        return False

    if not any(c.isupper() for c in password):
        print("❌ La contraseña debe tener al menos una letra mayúscula")
        return False

    if not any(c.islower() for c in password):
        print("❌ La contraseña debe tener al menos una letra minúscula")
        return False

    if not any(c.isdigit() for c in password):
        print("❌ La contraseña debe tener al menos un número")
        return False

    return True


def cleanup_test_users(db_path: str):
    """Eliminar usuarios de prueba de la base de datos"""
    print("🧹 Limpiando usuarios de prueba...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Eliminar usuarios de prueba
        test_patterns = [
            '%e2e_admin_%', '%e2e_vendor_%', '%e2e_customer_%',
            '%test%', '%@test.com%', '%@example.com%',
            'journey.admin%', 'concurrent_test_%', 'perf_%', 'xss_test_%',
            '%@teststore.com%'
        ]

        for pattern in test_patterns:
            cursor.execute("DELETE FROM users WHERE email LIKE ?", (pattern,))

        # Contar usuarios eliminados
        conn.commit()

        # Verificar usuarios restantes
        cursor.execute("SELECT COUNT(*) FROM users")
        remaining = cursor.fetchone()[0]

        cursor.execute("SELECT email, user_type FROM users WHERE user_type IN ('ADMIN', 'SUPERUSER')")
        admin_users = cursor.fetchall()

        print(f"✅ Limpieza completada. Usuarios restantes: {remaining}")
        if admin_users:
            print("👑 Usuarios administrativos existentes:")
            for email, user_type in admin_users:
                print(f"   - {email} ({user_type})")

    except Exception as e:
        print(f"❌ Error en limpieza: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_superuser(db_path: str, email: str, nombre: str, password: str):
    """Crear el superusuario en la base de datos"""
    print(f"👑 Creando superusuario: {email}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verificar que no existe otro superusuario activo
        cursor.execute(
            "SELECT email FROM users WHERE user_type = 'SUPERUSER' AND is_verified = 1 AND is_active = 1"
        )
        existing_superuser = cursor.fetchone()

        if existing_superuser:
            print(f"⚠️  Ya existe un superusuario activo: {existing_superuser[0]}")
            response = input("¿Desactivar el superusuario existente? (s/n): ").lower()
            if response != 's':
                print("❌ Operación cancelada")
                return False

            # Desactivar superusuario existente
            cursor.execute(
                "UPDATE users SET is_active = 0 WHERE user_type = 'SUPERUSER'"
            )
            print("✅ Superusuario existente desactivado")

        # Generar hash de contraseña usando bcrypt
        password_hash = hash_password(password)

        # Crear el superusuario
        user_id = str(uuid4())
        now = datetime.utcnow().isoformat() + 'Z'

        cursor.execute("""
            INSERT INTO users (
                id, email, password_hash, nombre, apellido, user_type,
                is_active, is_verified, email_verified, phone_verified,
                security_clearance_level, failed_login_attempts,
                created_at, updated_at,
                notification_preferences
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, email, password_hash, nombre, None, 'SUPERUSER',
            1, 1, 1, 0,  # is_active=1, is_verified=1, email_verified=1
            10, 0,  # security_clearance_level=10 (máximo), failed_login_attempts=0
            now, now,
            '{"email_new_orders": true, "email_low_stock": true, "sms_urgent_orders": true, "push_daily_summary": true}'
        ))

        conn.commit()

        print("✅ Superusuario creado exitosamente!")
        print(f"   📧 Email: {email}")
        print(f"   👤 Nombre: {nombre}")
        print(f"   🔐 User Type: SUPERUSER")
        print(f"   🛡️  Security Level: 10 (máximo)")
        print(f"   ✅ Verificado: Sí")
        print(f"   🆔 ID: {user_id}")

        return True

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: users.email" in str(e):
            print(f"❌ Ya existe un usuario con el email: {email}")
            print("💡 Usa otro email o elimina el usuario existente")
        else:
            print(f"❌ Error de integridad: {e}")
        conn.rollback()
        return False

    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def verify_superuser(db_path: str, email: str, password: str):
    """Verificar que el superusuario se creó correctamente y puede hacer login"""
    print("🔍 Verificando creación del superusuario...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, email, password_hash, user_type, is_active, is_verified,
                   security_clearance_level, created_at
            FROM users
            WHERE email = ? AND user_type = 'SUPERUSER'
        """, (email,))

        user = cursor.fetchone()
        if not user:
            print("❌ Superusuario no encontrado")
            return False

        user_id, db_email, password_hash, user_type, is_active, is_verified, security_level, created_at = user

        print("✅ Superusuario encontrado en base de datos:")
        print(f"   🆔 ID: {user_id}")
        print(f"   📧 Email: {db_email}")
        print(f"   👑 Tipo: {user_type}")
        print(f"   🟢 Activo: {'Sí' if is_active else 'No'}")
        print(f"   ✅ Verificado: {'Sí' if is_verified else 'No'}")
        print(f"   🛡️  Nivel seguridad: {security_level}")
        print(f"   📅 Creado: {created_at}")

        # Verificar hash de contraseña
        if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            print("✅ Hash de contraseña verificado correctamente")
        else:
            print("❌ Error: Hash de contraseña no coincide")
            return False

        # Verificar que es el único superusuario activo
        cursor.execute("""
            SELECT COUNT(*) FROM users
            WHERE user_type = 'SUPERUSER' AND is_active = 1 AND is_verified = 1
        """)
        active_superusers = cursor.fetchone()[0]

        if active_superusers == 1:
            print("✅ Es el único superusuario activo")
        else:
            print(f"⚠️  Hay {active_superusers} superusuarios activos (debería ser 1)")

        return True

    except Exception as e:
        print(f"❌ Error verificando superusuario: {e}")
        return False

    finally:
        conn.close()


def main():
    """Función principal"""
    print("=" * 60)
    print("🔧 CONFIGURACIÓN DE SUPERUSUARIO MESTORE")
    print("=" * 60)
    print()

    # Detectar base de datos
    db_files = ['mestore_development.db', 'mestore_production.db', 'mestore.db']
    db_path = None

    for db_file in db_files:
        if os.path.exists(db_file):
            db_path = db_file
            break

    if not db_path:
        print("❌ No se encontró base de datos SQLite")
        print("💡 Ejecuta este script desde el directorio raíz de MeStore")
        return False

    print(f"🗄️  Usando base de datos: {db_path}")
    print()

    # Paso 1: Limpieza
    cleanup_test_users(db_path)
    print()

    # Paso 2: Solicitar datos del superusuario
    print("👤 Configuración del superusuario:")
    print("-" * 40)

    while True:
        email = input("📧 Email del superusuario: ").strip()
        if not email:
            print("❌ El email es requerido")
            continue
        if not validate_email(email):
            print("❌ Formato de email inválido")
            continue
        break

    while True:
        nombre = input("👤 Nombre completo: ").strip()
        if not nombre:
            print("❌ El nombre es requerido")
            continue
        if len(nombre) < 2:
            print("❌ El nombre debe tener al menos 2 caracteres")
            continue
        break

    while True:
        password = getpass.getpass("🔐 Contraseña segura: ")
        if not password:
            print("❌ La contraseña es requerida")
            continue
        if not validate_password(password):
            continue

        password_confirm = getpass.getpass("🔐 Confirmar contraseña: ")
        if password != password_confirm:
            print("❌ Las contraseñas no coinciden")
            continue
        break

    print()

    # Paso 3: Confirmación
    print("📋 RESUMEN:")
    print(f"   📧 Email: {email}")
    print(f"   👤 Nombre: {nombre}")
    print(f"   🛡️  Tipo: SUPERUSER")
    print(f"   🔐 Nivel seguridad: 10 (máximo)")
    print(f"   🗄️  Base de datos: {db_path}")
    print()

    response = input("✅ ¿Crear superusuario? (s/n): ").lower()
    if response != 's':
        print("❌ Operación cancelada")
        return False

    # Paso 4: Crear superusuario
    print()
    success = create_superuser(db_path, email, nombre, password)

    if not success:
        return False

    # Paso 5: Verificación
    print()
    verify_success = verify_superuser(db_path, email, password)

    if verify_success:
        print()
        print("🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print(f"✅ Superusuario creado: {email}")
        print(f"🔗 URL de login: http://192.168.1.137:5173/admin/login")
        print("💡 Usa estas credenciales para acceder al portal administrativo")
        print()
        return True
    else:
        print()
        print("❌ CONFIGURACIÓN FALLÓ EN LA VERIFICACIÓN")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)