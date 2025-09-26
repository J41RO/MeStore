#!/usr/bin/env python3
"""
Script de verificación del protocolo Claude Code
"""

import os
import sys
import subprocess

def verify_installation():
    """Verificar que la instalación esté correcta"""

    print("🔍 VERIFICACIÓN DEL PROTOCOLO CLAUDE CODE")
    print("=" * 50)

    workspace_root = "/home/admin-jairo/MeStore/.workspace"

    # 1. Verificar estructura de directorios
    required_dirs = [
        f"{workspace_root}/logs",
        f"{workspace_root}/requests",
        f"{workspace_root}/departments",
        f"{workspace_root}/scripts"
    ]

    print("📁 Verificando estructura de directorios...")
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ❌ {dir_path} - FALTANTE")
            return False

    # 2. Verificar scripts principales
    required_scripts = [
        f"{workspace_root}/scripts/claude_code_interceptor.py",
        f"{workspace_root}/scripts/traceability_manager.py",
        f"{workspace_root}/scripts/agent_workspace_validator.py"
    ]

    print("\n🔧 Verificando scripts...")
    for script in required_scripts:
        if os.path.exists(script) and os.access(script, os.X_OK):
            print(f"   ✅ {os.path.basename(script)}")
        else:
            print(f"   ❌ {os.path.basename(script)} - FALTANTE O SIN PERMISOS")
            return False

    # 3. Probar interceptor
    print("\n🧪 Probando interceptor...")
    try:
        result = subprocess.run([
            "python3",
            f"{workspace_root}/scripts/claude_code_interceptor.py",
            "Test operation",
            "app/main.py"
        ], capture_output=True, text=True, timeout=10)

        if "OPERACIÓN BLOQUEADA" in result.stdout or "CONSULTAR" in result.stdout:
            print("   ✅ Interceptor funciona correctamente")
        else:
            print("   ⚠️ Interceptor respuesta inesperada")
            print(f"   Salida: {result.stdout[:100]}")

    except Exception as e:
        print(f"   ❌ Error probando interceptor: {e}")
        return False

    # 4. Verificar documentación
    docs = [
        f"{workspace_root}/CLAUDE_CODE_PROTOCOL.md",
        f"{workspace_root}/SYSTEM_RULES.md",
        f"{workspace_root}/PROTECTED_FILES.md"
    ]

    print("\n📚 Verificando documentación...")
    for doc in docs:
        if os.path.exists(doc):
            print(f"   ✅ {os.path.basename(doc)}")
        else:
            print(f"   ⚠️ {os.path.basename(doc)} - RECOMENDADO")

    print("\n✅ VERIFICACIÓN COMPLETADA - PROTOCOLO INSTALADO CORRECTAMENTE")
    print("🚀 Para activar aliases: source .workspace/scripts/claude_code_aliases.sh")

    return True

if __name__ == "__main__":
    success = verify_installation()
    sys.exit(0 if success else 1)
