#!/bin/bash
# SMART DEV SYSTEM v1.5.0 - Smart Commit Script
# Commit inteligente con validación controlada

COMMIT_MESSAGE="$1"

if [ -z "$COMMIT_MESSAGE" ]; then
    echo "❌ Error: Mensaje de commit requerido"
    echo "Uso: bash .workspace/scripts/smart_commit.sh 'mensaje del commit'"
    exit 1
fi

echo "💾 SMART DEV SYSTEM v1.5.0 - COMMIT INTELIGENTE"
echo "=============================================="

# Leer configuración del usuario
COMMIT_FREQ=$(grep "commit_frequency:" .workspace/start.yaml | cut -d'"' -f2)
USER_NAME=$(grep "name:" .workspace/start.yaml | cut -d'"' -f2)

echo "👤 Usuario: $USER_NAME"
echo "📋 Estrategia: $COMMIT_FREQ"
echo "💬 Mensaje: $COMMIT_MESSAGE"
echo ""

# Verificar estado del repositorio
echo "🔍 Verificando estado del repositorio..."
git status --porcelain

# Pre-commit validation si existe
if [ -f ".workspace/scripts/pre_commit_validation.sh" ]; then
    echo "✅ Ejecutando validación pre-commit..."
    bash .workspace/scripts/pre_commit_validation.sh
    if [ $? -ne 0 ]; then
        echo "❌ Validación falló - Commit cancelado"
        exit 1
    fi
fi

# Realizar commit
echo "💾 Realizando commit..."
git add .
git commit -m "$COMMIT_MESSAGE" --no-verify

if [ $? -eq 0 ]; then
    echo "✅ COMMIT EXITOSO"

    # Actualizar historial
    echo "$(date -Iseconds) | SUCCESS | COMMIT | $COMMIT_MESSAGE | user=$USER_NAME,strategy=$COMMIT_FREQ" >> .workspace/history.log

    # Actualizar log
    cat > .workspace/context/log.md << EOF
# ÚLTIMA ACCIÓN EJECUTADA

**Estado**: ✅ COMMIT REALIZADO
**Comando ejecutado**: git commit -m "$COMMIT_MESSAGE"
**Resultado**: ✅ EXITOSO - Cambios guardados en repositorio
**Próxima acción**: Continuar con siguiente tarea según plan
**Timestamp**: $(date -Iseconds)
**Usuario**: $USER_NAME
**Estrategia**: $COMMIT_FREQ
EOF

    echo "📝 Logs actualizados"
else
    echo "❌ COMMIT FALLÓ"
    exit 1
fi
