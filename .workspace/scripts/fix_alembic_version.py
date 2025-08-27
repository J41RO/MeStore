#!/usr/bin/env python3
"""
Script para reparar tabla alembic_version usando la conexión correcta.
"""

import asyncio
import sys

sys.path.append(".")

from sqlalchemy import text

from app.database.session import engine


async def fix_alembic_version():
    """Reparar tabla alembic_version con revisión correcta"""

    try:
        print("🔗 Conectando a PostgreSQL usando engine de session.py...")

        async with engine.begin() as conn:
            print("✅ Conexión establecida exitosamente")

            # Verificar versión actual problemática
            result = await conn.execute(
                text("SELECT version_num FROM alembic_version LIMIT 1;")
            )
            current_version = result.scalar()
            print(f"🔍 Versión problemática actual: {current_version}")

            # Corregir a la última versión válida conocida
            correct_version = "5e0e1b1f0cfc"  # Última migración válida del historial
            print(f"🔧 Corrigiendo a versión válida: {correct_version}")

            await conn.execute(
                text("UPDATE alembic_version SET version_num = :version;"),
                {"version": correct_version},
            )

            # Verificar corrección
            verify_result = await conn.execute(
                text("SELECT version_num FROM alembic_version LIMIT 1;")
            )
            new_version = verify_result.scalar()
            print(f"✅ Nueva versión en BD: {new_version}")

            if new_version == correct_version:
                print("🎉 ✅ TABLA ALEMBIC_VERSION REPARADA EXITOSAMENTE")
                return True
            else:
                print("❌ La corrección no se aplicó correctamente")
                return False

    except Exception as e:
        print(f"❌ ERROR durante reparación: {e}")
        return False


if __name__ == "__main__":
    print("=== 🔧 REPARANDO TABLA ALEMBIC_VERSION ===")
    success = asyncio.run(fix_alembic_version())

    if success:
        print("\n🎯 REPARACIÓN COMPLETADA - PROBANDO ALEMBIC...")

        # Test que alembic funciona
        import subprocess

        result = subprocess.run(["alembic", "current"], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ ALEMBIC FUNCIONA CORRECTAMENTE AHORA")
            print(f"📋 Estado actual: {result.stdout.strip()}")
        else:
            print("❌ ALEMBIC AÚN TIENE PROBLEMAS")
            print(f"Error: {result.stderr}")
    else:
        print("\n❌ REPARACIÓN FALLÓ - USAR MÉTODO ALTERNATIVO")
