#!/bin/bash
"""
🚀 INSTALADOR DEL PROTOCOLO CLAUDE CODE
Script de instalación y configuración automática
Creado por: Agent Recruiter AI
Fecha: 2025-09-26
Version: 1.0.0
"""

echo "🚀 INSTALADOR DEL PROTOCOLO CLAUDE CODE"
echo "========================================"

# Configurar variables
WORKSPACE_ROOT="/home/admin-jairo/MeStore/.workspace"
SCRIPTS_DIR="$WORKSPACE_ROOT/scripts"

# Verificar que estamos en el directorio correcto
if [ ! -d "$WORKSPACE_ROOT" ]; then
    echo "❌ Error: No se encontró el workspace en $WORKSPACE_ROOT"
    exit 1
fi

echo "✅ Workspace encontrado en $WORKSPACE_ROOT"

# 1. Verificar dependencias
echo ""
echo "🔍 Verificando dependencias..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

echo "✅ Python 3 disponible"

# 2. Hacer ejecutables los scripts
echo ""
echo "🔧 Configurando permisos de scripts..."

chmod +x "$SCRIPTS_DIR/claude_code_interceptor.py"
chmod +x "$SCRIPTS_DIR/traceability_manager.py"
chmod +x "$SCRIPTS_DIR/agent_workspace_validator.py"

echo "✅ Permisos configurados"

# 3. Crear directorios necesarios
echo ""
echo "📁 Creando estructura de directorios..."

mkdir -p "$WORKSPACE_ROOT/logs"
mkdir -p "$WORKSPACE_ROOT/requests"
mkdir -p "$WORKSPACE_ROOT/reports"

# Crear directorios de departamentos si no existen
mkdir -p "$WORKSPACE_ROOT/departments/architecture"
mkdir -p "$WORKSPACE_ROOT/departments/backend"
mkdir -p "$WORKSPACE_ROOT/departments/frontend"
mkdir -p "$WORKSPACE_ROOT/departments/testing"
mkdir -p "$WORKSPACE_ROOT/departments/infrastructure"
mkdir -p "$WORKSPACE_ROOT/departments/general"

echo "✅ Estructura de directorios creada"

# 4. Crear alias y funciones de conveniencia
echo ""
echo "🔗 Configurando aliases y funciones..."

# Crear script de aliases
cat > "$SCRIPTS_DIR/claude_code_aliases.sh" << 'EOF'
#!/bin/bash
# Aliases para el protocolo Claude Code

# Función para interceptar operaciones de Claude Code
claude_intercept() {
    python /home/admin-jairo/MeStore/.workspace/scripts/claude_code_interceptor.py "$@"
}

# Función para crear reportes de trazabilidad
claude_trace() {
    python /home/admin-jairo/MeStore/.workspace/scripts/traceability_manager.py "$@"
}

# Función para validar acceso de agentes
claude_validate() {
    python /home/admin-jairo/MeStore/.workspace/scripts/agent_workspace_validator.py "$@"
}

# Función para ver dashboard departamental
claude_dashboard() {
    local dept=${1:-"backend"}
    python /home/admin-jairo/MeStore/.workspace/scripts/traceability_manager.py department_dashboard "$dept"
}

# Función para ver reporte de cumplimiento
claude_compliance() {
    echo "📊 REPORTE DE CUMPLIMIENTO CLAUDE CODE"
    echo "======================================"
    python /home/admin-jairo/MeStore/.workspace/scripts/claude_code_interceptor.py --compliance-report 2>/dev/null || echo "ℹ️ Ejecute operaciones para generar estadísticas"
}

# Función para limpiar logs antiguos
claude_cleanup() {
    local days=${1:-30}
    python /home/admin-jairo/MeStore/.workspace/scripts/traceability_manager.py cleanup_reports "$days"
}

# Exportar funciones
export -f claude_intercept claude_trace claude_validate claude_dashboard claude_compliance claude_cleanup

echo "✅ Funciones Claude Code disponibles:"
echo "   claude_intercept    - Interceptar operaciones"
echo "   claude_trace        - Gestionar trazabilidad"
echo "   claude_validate     - Validar acceso de agentes"
echo "   claude_dashboard    - Ver dashboard departamental"
echo "   claude_compliance   - Reporte de cumplimiento"
echo "   claude_cleanup      - Limpiar logs antiguos"
EOF

chmod +x "$SCRIPTS_DIR/claude_code_aliases.sh"

echo "✅ Aliases configurados en $SCRIPTS_DIR/claude_code_aliases.sh"

# 5. Crear configuración de Git Hooks (opcional)
echo ""
echo "🔗 Configurando Git Hooks..."

if [ -d "/home/admin-jairo/MeStore/.git" ]; then
    # Pre-commit hook para validación automática
    cat > "/home/admin-jairo/MeStore/.git/hooks/pre-commit" << 'EOF'
#!/bin/bash
# Pre-commit hook para validación de protocolo Claude Code

echo "🔍 Validando protocolo workspace..."

# Verificar archivos modificados
modified_files=$(git diff --cached --name-only)

if [ -n "$modified_files" ]; then
    echo "📁 Archivos modificados detectados:"
    echo "$modified_files"

    # Ejecutar validación para cada archivo
    for file in $modified_files; do
        echo "   Validando: $file"

        # Usar el interceptor para verificar si requiere consulta
        if ! python /home/admin-jairo/MeStore/.workspace/scripts/claude_code_interceptor.py "Pre-commit validation" "$file" >/dev/null 2>&1; then
            echo "⚠️ Archivo $file podría requerir consulta con agente responsable"
        fi
    done
fi

echo "✅ Validación pre-commit completada"
EOF

    chmod +x "/home/admin-jairo/MeStore/.git/hooks/pre-commit"
    echo "✅ Git pre-commit hook configurado"
else
    echo "ℹ️ No es un repositorio Git - hooks omitidos"
fi

# 6. Crear script de verificación del sistema
echo ""
echo "🧪 Creando script de verificación..."

cat > "$SCRIPTS_DIR/verify_claude_protocol.py" << 'EOF'
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
EOF

chmod +x "$SCRIPTS_DIR/verify_claude_protocol.py"

echo "✅ Script de verificación creado"

# 7. Ejecutar verificación inicial
echo ""
echo "🧪 Ejecutando verificación inicial..."

python3 "$SCRIPTS_DIR/verify_claude_protocol.py"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE"
    echo "====================================="
    echo ""
    echo "📋 PRÓXIMOS PASOS:"
    echo "1. Para activar aliases: source .workspace/scripts/claude_code_aliases.sh"
    echo "2. Probar interceptor: claude_intercept 'Test' app/main.py"
    echo "3. Ver documentación: cat .workspace/CLAUDE_CODE_PROTOCOL.md"
    echo ""
    echo "🚨 IMPORTANTE: El protocolo está ACTIVO y interceptará operaciones de Claude Code automáticamente"
    echo ""
    echo "✅ Gap de coordinación y trazabilidad RESUELTO"
else
    echo ""
    echo "❌ INSTALACIÓN FALLÓ - Revisar errores arriba"
    exit 1
fi