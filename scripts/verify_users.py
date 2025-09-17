#!/usr/bin/env python3
"""
Critical Database User Verification Script
==========================================

PROPÓSITO: Verificar usuarios por defecto del sistema MeStore usando motor sync.
AUTOR: Backend Senior Developer
FECHA: 2025-09-13

FUNCIONALIDAD:
- Verifica conexión PostgreSQL con motor sync production-ready
- Consulta tabla users para confirmar usuarios por defecto
- Verifica estructura tabla y datos de usuarios específicos
- Reporte completo estado usuarios críticos del sistema

USUARIOS CRÍTICOS A VERIFICAR:
- super@mestore.com (SuperUser) - Sistema
- admin@mestore.com (Admin) - Administración
- vendor@mestore.com (Vendedor) - Pruebas comercio
- buyer@mestore.com (Comprador) - Pruebas compras

REQUISITOS:
- PostgreSQL funcionando en localhost:5432
- Base de datos: mestocker_dev
- Usuario: mestocker_user / mestocker_pass
- Motor SQLAlchemy sync configurado
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from app.core.database import get_sync_engine, SyncSessionLocal
from app.models.user import User, UserType

# Configuración usuarios críticos esperados
CRITICAL_USERS = [
    {
        'email': 'super@mestore.com',
        'user_type': UserType.SUPERUSER,
        'description': 'SuperUser del sistema - máximos permisos'
    },
    {
        'email': 'admin@mestore.com',
        'user_type': UserType.ADMIN,
        'description': 'Administrador principal - gestión completa'
    },
    {
        'email': 'vendor@mestore.com',
        'user_type': UserType.VENDOR,
        'description': 'Vendor de pruebas - comercio electrónico'
    },
    {
        'email': 'buyer@mestore.com',
        'user_type': UserType.BUYER,
        'description': 'Comprador de pruebas - transacciones'
    }
]


def print_header():
    """Imprime encabezado del script de verificación."""
    print("=" * 80)
    print("🔍 BACKEND SENIOR DEVELOPER - VERIFICACIÓN USUARIOS CRÍTICOS")
    print("=" * 80)
    print(f"📅 Fecha: {os.popen('date').read().strip()}")
    print("🎯 Objetivo: Verificar usuarios por defecto del sistema")
    print("🗄️  Base de datos: mestocker_dev")
    print("⚙️  Motor: SQLAlchemy Sync Production-Ready")
    print("=" * 80)


def test_database_connection():
    """
    Verifica conexión a PostgreSQL y estructura tabla users.

    Returns:
        bool: True si conexión exitosa, False en caso contrario
    """
    print("\n📡 MICRO-FASE 4: VALIDACIÓN CONEXIÓN BD")
    print("-" * 50)

    try:
        # Test 1: Crear engine sync
        print("🔧 Creando engine SQLAlchemy sync...")
        engine = get_sync_engine()
        print("✅ Engine sync creado exitosamente")

        # Test 2: Conexión básica
        print("🔗 Probando conexión PostgreSQL...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL conectado: {version[:50]}...")

        # Test 3: Verificar tabla users existe
        print("📋 Verificando estructura tabla users...")
        inspector = inspect(engine)

        if 'users' not in inspector.get_table_names():
            print("❌ ERROR: Tabla 'users' no existe en la base de datos")
            return False

        # Test 4: Describir columnas críticas
        columns = inspector.get_columns('users')
        required_columns = ['id', 'email', 'password_hash', 'user_type', 'is_active']

        existing_columns = [col['name'] for col in columns]
        missing_columns = [col for col in required_columns if col not in existing_columns]

        if missing_columns:
            print(f"❌ ERROR: Columnas faltantes en users: {missing_columns}")
            return False

        print(f"✅ Tabla users válida con {len(existing_columns)} columnas")
        print(f"📊 Columnas críticas presentes: {required_columns}")

        # Test 5: Consulta básica funcional
        print("🔍 Ejecutando consulta básica...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            total_users = result.fetchone()[0]
            print(f"✅ Consulta exitosa: {total_users} usuarios en tabla")

        return True

    except OperationalError as e:
        print(f"❌ ERROR CONEXIÓN: {e}")
        print("💡 SUGERENCIAS:")
        print("  - Verificar que PostgreSQL esté ejecutándose")
        print("  - Confirmar credenciales: mestocker_user/mestocker_pass")
        print("  - Validar base de datos: mestocker_dev existe")
        return False

    except SQLAlchemyError as e:
        print(f"❌ ERROR SQLALCHEMY: {e}")
        return False

    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        return False


def verify_critical_users():
    """
    Verifica existencia y estado de usuarios críticos del sistema.

    Returns:
        dict: Reporte detallado de verificación de usuarios
    """
    print("\n👥 MICRO-FASE 5: REPORTE USUARIOS COMPLETO")
    print("-" * 50)

    report = {
        'connection_success': False,
        'total_users': 0,
        'users_found': [],
        'users_missing': [],
        'users_inactive': [],
        'summary': {}
    }

    try:
        # Crear sesión sync
        session = SyncSessionLocal()

        try:
            # Obtener total de usuarios
            total_users = session.query(User).count()
            report['total_users'] = total_users
            report['connection_success'] = True

            print(f"📊 Total usuarios en sistema: {total_users}")
            print("\n🔍 Verificando usuarios críticos:")
            print("-" * 50)

            # Verificar cada usuario crítico
            for user_config in CRITICAL_USERS:
                email = user_config['email']
                expected_type = user_config['user_type']
                description = user_config['description']

                print(f"\n🔍 Verificando: {email}")
                print(f"   Tipo esperado: {expected_type.value}")
                print(f"   Descripción: {description}")

                # Buscar usuario en BD
                user = session.query(User).filter(User.email == email).first()

                if user:
                    # Usuario encontrado - verificar detalles
                    user_info = {
                        'email': user.email,
                        'id': str(user.id),
                        'user_type': user.user_type.value,
                        'is_active': user.is_active,
                        'is_verified': user.is_verified,
                        'created_at': user.created_at.isoformat() if user.created_at else None,
                        'nombre': user.nombre,
                        'apellido': user.apellido,
                        'description': description
                    }

                    print(f"   ✅ Usuario encontrado")
                    print(f"   📧 Email: {user.email}")
                    print(f"   🆔 ID: {user.id}")
                    print(f"   👤 Tipo actual: {user.user_type.value}")
                    print(f"   🟢 Activo: {'Sí' if user.is_active else 'No'}")
                    print(f"   ✔️ Verificado: {'Sí' if user.is_verified else 'No'}")
                    print(f"   👤 Nombre: {user.nombre or 'No definido'}")
                    print(f"   📅 Creado: {user.created_at or 'No disponible'}")

                    # Verificar tipo correcto
                    if user.user_type != expected_type:
                        print(f"   ⚠️  ADVERTENCIA: Tipo incorrecto. Esperado: {expected_type.value}")
                        user_info['type_mismatch'] = True
                    else:
                        print(f"   ✅ Tipo correcto: {expected_type.value}")
                        user_info['type_mismatch'] = False

                    # Verificar estado activo
                    if not user.is_active:
                        print(f"   ⚠️  ADVERTENCIA: Usuario inactivo")
                        report['users_inactive'].append(user_info)

                    report['users_found'].append(user_info)

                else:
                    # Usuario no encontrado
                    print(f"   ❌ Usuario NO ENCONTRADO")
                    missing_user = {
                        'email': email,
                        'expected_type': expected_type.value,
                        'description': description
                    }
                    report['users_missing'].append(missing_user)

            # Generar resumen
            print("\n📋 RESUMEN VERIFICACIÓN")
            print("=" * 50)
            print(f"📊 Total usuarios sistema: {total_users}")
            print(f"✅ Usuarios críticos encontrados: {len(report['users_found'])}/4")
            print(f"❌ Usuarios críticos faltantes: {len(report['users_missing'])}/4")
            print(f"⚠️  Usuarios inactivos: {len(report['users_inactive'])}")

            # Reporte detallado usuarios encontrados
            if report['users_found']:
                print("\n✅ USUARIOS ENCONTRADOS:")
                for user in report['users_found']:
                    status = "🟢 ACTIVO" if user['is_active'] else "🔴 INACTIVO"
                    type_status = "✅ CORRECTO" if not user.get('type_mismatch') else "⚠️ TIPO INCORRECTO"
                    print(f"   • {user['email']} - {user['user_type']} - {status} - {type_status}")

            # Reporte usuarios faltantes
            if report['users_missing']:
                print("\n❌ USUARIOS FALTANTES:")
                for user in report['users_missing']:
                    print(f"   • {user['email']} ({user['expected_type']}) - {user['description']}")
                print("\n💡 ACCIÓN REQUERIDA: Crear usuarios faltantes con script de configuración")

            # Reporte usuarios inactivos
            if report['users_inactive']:
                print("\n⚠️ USUARIOS INACTIVOS:")
                for user in report['users_inactive']:
                    print(f"   • {user['email']} - Requiere activación")
                print("\n💡 ACCIÓN REQUERIDA: Activar usuarios críticos inactivos")

            # Estado final del sistema
            print("\n🎯 ESTADO SISTEMA:")
            if len(report['users_found']) == 4 and len(report['users_missing']) == 0:
                print("✅ SISTEMA COMPLETO - Todos los usuarios críticos presentes")
                report['summary']['status'] = 'COMPLETE'
            elif len(report['users_found']) > 0:
                print("⚠️ SISTEMA PARCIAL - Algunos usuarios críticos presentes")
                report['summary']['status'] = 'PARTIAL'
            else:
                print("❌ SISTEMA VACÍO - Ningún usuario crítico encontrado")
                report['summary']['status'] = 'EMPTY'

            report['summary']['verification_complete'] = True

        finally:
            session.close()

    except SQLAlchemyError as e:
        print(f"❌ ERROR CONSULTA BD: {e}")
        report['summary'] = {'error': str(e), 'verification_complete': False}

    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        report['summary'] = {'error': str(e), 'verification_complete': False}

    return report


def print_next_steps(report):
    """
    Imprime próximos pasos basados en resultado de verificación.

    Args:
        report (dict): Reporte de verificación de usuarios
    """
    print("\n🚀 PRÓXIMOS PASOS RECOMENDADOS")
    print("=" * 50)

    if not report['connection_success']:
        print("🔧 CONEXIÓN BD:")
        print("  1. Verificar estado PostgreSQL: systemctl status postgresql")
        print("  2. Confirmar credenciales en config.py")
        print("  3. Validar base de datos mestocker_dev existe")
        return

    status = report['summary'].get('status', 'ERROR')

    if status == 'COMPLETE':
        print("✅ SISTEMA LISTO:")
        print("  1. Todos los usuarios críticos están presentes")
        print("  2. Proceder con pruebas de autenticación")
        print("  3. Validar login funcional para cada usuario")
        print("  4. Confirmar permisos por tipo de usuario")

    elif status == 'PARTIAL':
        print("⚠️ COMPLETAR CONFIGURACIÓN:")
        if report['users_missing']:
            print("  1. EJECUTAR: python scripts/create_default_users.py")
            print("  2. Configurar contraseñas por defecto (123456)")
            print("  3. Activar usuarios recién creados")

        if report['users_inactive']:
            print("  4. EJECUTAR: python scripts/activate_users.py")
            print("  5. Verificar activación exitosa")

    elif status == 'EMPTY':
        print("🔧 CONFIGURACIÓN INICIAL:")
        print("  1. EJECUTAR: python scripts/create_default_users.py")
        print("  2. Confirmar creación con este script")
        print("  3. Configurar permisos específicos por usuario")
        print("  4. Verificar autenticación funcional")

    print("\n📝 COMANDOS ÚTILES:")
    print("  • Ejecutar este script: python scripts/verify_users.py")
    print("  • Ver logs aplicación: tail -f logs/*.log")
    print("  • Test conexión BD: python -c \"from app.core.database import get_sync_engine; print('OK')\"")


def main():
    """Función principal del script de verificación."""
    try:
        # Header del script
        print_header()

        # Fase 4: Validación conexión
        connection_ok = test_database_connection()

        if not connection_ok:
            print("\n❌ VERIFICACIÓN FALLIDA: Problemas conexión BD")
            print("🔧 Resolver problemas conexión antes de continuar")
            sys.exit(1)

        # Fase 5: Verificación usuarios
        report = verify_critical_users()

        # Próximos pasos
        print_next_steps(report)

        # Footer de finalización
        print("\n" + "=" * 80)
        print("🎯 VERIFICACIÓN COMPLETADA")
        print("📋 Revisar reporte anterior para determinar próximos pasos")
        print("🔗 Conexión BD: ✅ FUNCIONAL")
        print("=" * 80)

        # Exit code basado en resultado
        if report['summary'].get('status') == 'COMPLETE':
            sys.exit(0)  # Todo perfecto
        elif report['summary'].get('status') == 'PARTIAL':
            sys.exit(2)  # Configuración parcial
        else:
            sys.exit(1)  # Problemas críticos

    except KeyboardInterrupt:
        print("\n\n⚠️ Script interrumpido por usuario")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        print("🔧 Contactar Backend Senior Developer para soporte")
        sys.exit(1)


if __name__ == "__main__":
    main()