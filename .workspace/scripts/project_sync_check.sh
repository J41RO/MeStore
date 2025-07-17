#!/bin/bash
# SMART DEV SYSTEM v1.5.0 - Project Sync Checker
# Verifica sincronización entre archivos del proyecto y contexto

echo "🔄 SMART DEV SYSTEM v1.5.0 - VERIFICADOR DE SINCRONIZACIÓN"
echo "========================================================="

PROJECT_NAME=$(grep "name:" .workspace/start.yaml | head -1 | cut -d'"' -f2)
echo "📂 Proyecto: $PROJECT_NAME"
echo ""

echo "🔍 Verificando cambios no documentados..."

# Verificar si hay cambios no commiteados
if command -v git &> /dev/null; then
    UNCOMMITTED=$(git status --porcelain | wc -l)
    if [ $UNCOMMITTED -gt 0 ]; then
        echo "📝 Cambios no commiteados encontrados:"
        git status --porcelain
        echo ""
    else
        echo "✅ No hay cambios sin commitear"
    fi
    
    # Últimos commits
    echo "📊 Últimos 3 commits:"
    git log --oneline -3 2>/dev/null || echo "Sin historial de commits"
else
    echo "⚠️ Git no disponible - No se puede verificar estado del repositorio"
fi

echo ""
echo "🔍 Verificando archivos del proyecto..."

# Contar archivos por tipo
PY_FILES=$(find . -name "*.py" ! -path "./.workspace/*" ! -path "./.git/*" | wc -l)
JS_FILES=$(find . -name "*.js" ! -path "./.workspace/*" ! -path "./.git/*" | wc -l)
JSON_FILES=$(find . -name "*.json" ! -path "./.workspace/*" ! -path "./.git/*" | wc -l)

echo "📊 Archivos del proyecto:"
echo "   - Python: $PY_FILES archivos"
echo "   - JavaScript: $JS_FILES archivos"  
echo "   - JSON: $JSON_FILES archivos"

echo ""
echo "🔍 Verificando estado del workspace..."

# Verificar integridad del workspace
WORKSPACE_FILES=$(find .workspace -type f | wc -l)
echo "📁 Archivos en workspace: $WORKSPACE_FILES"

# Verificar última actividad
LAST_ACTION=$(grep "Comando ejecutado" .workspace/context/log.md | cut -d':' -f2)
echo "⚡ Última acción:$LAST_ACTION"
