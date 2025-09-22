#!/bin/bash
# 🚨 PRE-COMMIT HOOK - VERIFICACIÓN WORKSPACE OBLIGATORIA

echo "🔍 VERIFICANDO CUMPLIMIENTO .WORKSPACE..."

# Archivos modificados en este commit
MODIFIED_FILES=$(git diff --cached --name-only)

# Lista de archivos protegidos críticos
PROTECTED_FILES=(
    "app/main.py"
    "frontend/vite.config.ts"
    "docker-compose.yml"
    "app/api/v1/deps/auth.py"
    "app/services/auth_service.py"
    "app/models/user.py"
    "tests/conftest.py"
    "app/core/config.py"
    "app/database.py"
)

# Verificar commit message contiene workspace check
COMMIT_MSG_FILE=".git/COMMIT_EDITMSG"
if [ -f "$COMMIT_MSG_FILE" ]; then
    if ! grep -q "Workspace-Check: ✅" "$COMMIT_MSG_FILE"; then
        echo "❌ ERROR: Commit debe incluir 'Workspace-Check: ✅'"
        echo "📋 Template obligatorio:"
        echo "tipo(área): descripción breve"
        echo ""
        echo "Workspace-Check: ✅ Consultado"
        echo "Archivo: ruta/del/archivo.py"
        echo "Agente: nombre-del-agente"
        echo "Protocolo: [SEGUIDO/CONSULTA_PREVIA/APROBACIÓN_OBTENIDA]"
        echo "Tests: [PASSED/FAILED]"
        exit 1
    fi
fi

# Verificar archivos protegidos
for file in $MODIFIED_FILES; do
    for protected in "${PROTECTED_FILES[@]}"; do
        if [[ "$file" == "$protected" ]]; then
            echo "🚨 ARCHIVO PROTEGIDO DETECTADO: $file"

            # Verificar si existe metadatos
            METADATA_FILE=".workspace/project/${file}.md"
            if [ ! -f "$METADATA_FILE" ]; then
                echo "❌ ERROR: Archivo protegido sin metadatos: $METADATA_FILE"
                exit 1
            fi

            # Verificar aprobación en commit message
            if ! grep -q "Responsable:" "$COMMIT_MSG_FILE"; then
                echo "❌ ERROR: Archivo protegido requiere aprobación de agente responsable"
                echo "📋 Agregar: 'Responsable: nombre-agente-responsable'"
                exit 1
            fi

            echo "⚠️  VERIFICANDO: $file requiere aprobación especial"
        fi
    done
done

# Verificar que tests pasen si hay cambios en código
if echo "$MODIFIED_FILES" | grep -E '\.(py|ts|tsx|js|jsx)$'; then
    echo "🧪 EJECUTANDO TESTS OBLIGATORIOS..."

    # Tests backend si hay cambios Python
    if echo "$MODIFIED_FILES" | grep -q '\.py$'; then
        echo "🐍 Testing backend..."
        python -m pytest tests/ -x --tb=short || {
            echo "❌ TESTS BACKEND FALLARON - Commit bloqueado"
            exit 1
        }
    fi

    # Tests frontend si hay cambios TS/JS
    if echo "$MODIFIED_FILES" | grep -E '\.(ts|tsx|js|jsx)$'; then
        echo "⚛️  Testing frontend..."
        cd frontend && npm run test:ci || {
            echo "❌ TESTS FRONTEND FALLARON - Commit bloqueado"
            exit 1
        }
    fi
fi

# Verificar servicios críticos si se modifican configs
if echo "$MODIFIED_FILES" | grep -E '(docker-compose\.yml|main\.py|vite\.config\.ts)'; then
    echo "🐳 VERIFICANDO SERVICIOS CRÍTICOS..."

    # Verificar que Docker Compose sigue siendo válido
    docker-compose config >/dev/null || {
        echo "❌ docker-compose.yml INVÁLIDO - Commit bloqueado"
        exit 1
    }

    echo "✅ Configuraciones de servicios válidas"
fi

echo "✅ VERIFICACIÓN .WORKSPACE COMPLETADA"
echo "📊 Archivos modificados: $(echo $MODIFIED_FILES | wc -w)"
echo "🛡️  Archivos protegidos verificados: OK"

exit 0