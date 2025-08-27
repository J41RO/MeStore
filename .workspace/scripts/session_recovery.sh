#!/bin/bash
# SMART DEV SYSTEM v1.5.0 - Session Recovery Script
# Recupera contexto completo del proyecto tras gaps de tiempo

echo "🔄 SMART DEV SYSTEM v1.5.0 - RECUPERACIÓN DE SESIÓN"
echo "=================================================="

echo "📋 Analizando contexto del proyecto..."

# Leer configuración del usuario
USER_NAME=$(grep "name:" .workspace/start.yaml | cut -d'"' -f2)
TECH_LEVEL=$(grep "technical_level:" .workspace/start.yaml | cut -d'"' -f2)
PROJECT_NAME=$(grep "name:" .workspace/start.yaml | head -1 | cut -d'"' -f2)

echo "👤 Usuario: $USER_NAME (Nivel: $TECH_LEVEL)"
echo "📂 Proyecto: $PROJECT_NAME"
echo ""

echo "=== ESTADO ACTUAL DEL PROYECTO ==="
echo "📅 Última actividad:"
cat .workspace/context/log.md | head -5

echo ""
echo "=== TAREAS PENDIENTES ==="
echo "🔍 Próximas tareas:"
grep -E "(🔁|⬜)" .workspace/context/todo.md | head -5

echo ""
echo "=== HISTORIAL RECIENTE ==="
echo "📊 Actividad reciente:"
tail -5 .workspace/history.log

echo ""
echo "=== ERRORES/APRENDIZAJES ==="
echo "🧠 Conocimiento acumulado:"
grep -c "ÉXITO\|ERROR" .workspace/error_knowledge.md
echo "Entradas en base de conocimiento: $(grep -c "##" .workspace/error_knowledge.md)"

echo ""
echo "✅ CONTEXTO RECUPERADO - Sistema listo para continuar"
echo "🚀 Próximo paso: Ejecutar /start/ en tu IA para continuar desarrollo"

# Generar resumen en archivo
cat > .workspace/context/session_summary.md << EOF
# RESUMEN DE SESIÓN RECUPERADA - $(date)

## Usuario Configurado
- **Nombre**: $USER_NAME
- **Nivel**: $TECH_LEVEL
- **Proyecto**: $PROJECT_NAME

## Estado Actual
$(cat .workspace/context/log.md | head -3)

## Próximas Tareas
$(grep -E "(🔁|⬜)" .workspace/context/todo.md | head -3)

## Recomendación
Ejecutar `/start/` en tu IA para continuar con el desarrollo personalizado.
EOF

echo "📄 Resumen guardado en: .workspace/context/session_summary.md"
