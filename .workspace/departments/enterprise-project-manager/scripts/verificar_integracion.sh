#!/bin/bash
# Script: verificar_integracion.sh
# Propósito: Verificación continua de integración TODO enterprise
# Autor: Manager Universal
# Fecha: 2025-09-13

echo "🎯 === VERIFICACIÓN INTEGRACIÓN TODO ENTERPRISE ==="
echo "📅 Fecha: $(date)"
echo ""

# Variables de configuración
WORKSPACE_DIR="/home/admin-jairo/MeStore/.workspace/departments"
MANAGER_TODO_DIR="$WORKSPACE_DIR/manager/todo"
BACKEND_TODO_DIR="$WORKSPACE_DIR/team/backend/tasks"
FRONTEND_TODO_DIR="$WORKSPACE_DIR/team/frontend/tasks"

echo "📋 1. REVISANDO DEPENDENCIAS SATISFECHAS..."
echo "   🔍 Backend TODOs: $(find $BACKEND_TODO_DIR -name "*.md" 2>/dev/null | wc -l) archivos"
echo "   🔍 Frontend TODOs: $(find $FRONTEND_TODO_DIR -name "*.md" 2>/dev/null | wc -l) archivos"
echo "   🔍 Manager TODOs: $(find $MANAGER_TODO_DIR -name "*.md" 2>/dev/null | wc -l) archivos"
echo ""

echo "⚠️  2. DETECTANDO CONFLICTOS EMERGENTES..."
echo "   🔍 Verificando archivos modificados recientemente..."
echo "   📝 Backend modificado últimas 24h: $(find $BACKEND_TODO_DIR -name "*.md" -mtime -1 2>/dev/null | wc -l)"
echo "   📝 Frontend modificado últimas 24h: $(find $FRONTEND_TODO_DIR -name "*.md" -mtime -1 2>/dev/null | wc -l)"
echo ""

echo "✅ 3. VALIDANDO CHECKPOINTS COMPLETADOS..."
echo "   🎯 Buscando mapas de integración activos..."
MAPAS_ACTIVOS=$(find $MANAGER_TODO_DIR -name "MAPA_*" 2>/dev/null | wc -l)
echo "   📊 Mapas conceptuales activos: $MAPAS_ACTIVOS"
echo ""

echo "🎯 4. ACTUALIZANDO PROGRESO MAPA CONCEPTUAL..."
if [ $MAPAS_ACTIVOS -gt 0 ]; then
    echo "   📋 Mapas encontrados:"
    find $MANAGER_TODO_DIR -name "MAPA_*" 2>/dev/null | sed 's/.*\//   - /'
else
    echo "   📋 No hay mapas activos de integración"
fi
echo ""

echo "📈 5. MÉTRICAS DE COORDINACIÓN..."
TOTAL_TODOS=$(find $WORKSPACE_DIR -name "*todo*.md" 2>/dev/null | wc -l)
echo "   📊 Total archivos TODO en workspace: $TOTAL_TODOS"
echo "   ⏰ Última verificación: $(date)"
echo ""

echo "🎯 === VERIFICACIÓN COMPLETADA ==="
echo "📋 Para coordinar nuevos TODOs, use: PROTOCOLO_COORDINACION_TODO_ENTERPRISE.md"
echo ""