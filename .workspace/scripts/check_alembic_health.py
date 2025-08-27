#!/usr/bin/env python3
"""
Script de verificación rápida del estado de Alembic.
"""

import subprocess
import sys


def check_alembic_health():
    """Verificar si Alembic está funcionando correctamente"""

    try:
        # Test alembic current
        result = subprocess.run(
            ["alembic", "current"], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            print("✅ ALEMBIC: Funcionando correctamente")
            print(f"📋 Estado actual: {result.stdout.strip()}")
            return True
        else:
            print("❌ ALEMBIC: Problemas detectados")
            print(f"Error: {result.stderr}")

            if "Can't locate revision" in result.stderr:
                print("💡 SOLUCIÓN: python3 .workspace/scripts/fix_alembic_version.py")

            return False

    except subprocess.TimeoutExpired:
        print("⏰ ALEMBIC: Timeout - posible problema de conexión")
        return False
    except FileNotFoundError:
        print("❌ ALEMBIC: No instalado o no en PATH")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    healthy = check_alembic_health()
    sys.exit(0 if healthy else 1)
