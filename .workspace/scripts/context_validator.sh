#!/bin/bash
# SMART DEV SYSTEM v1.5.0 - Context Validator
# Valida consistencia del contexto del proyecto

echo "🔍 SMART DEV SYSTEM v1.5.0 - VALIDADOR DE CONTEXTO"
echo "================================================="

echo "📋 Validando consistencia del contexto..."

# Validar archivos críticos
FILES_TO_CHECK=(".workspace/start.yaml" ".workspace/context/todo.md" ".workspace/context/log.md")
MISSING_FILES=()

for file in "${FILES_TO_CHECK[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "❌ ARCHIVOS FALTANTES:"
    printf '%s\n' "${MISSING_FILES[@]}"
    echo "🔧 Ejecuta setup.py para regenerar archivos"
    exit 1
fi

echo "✅ Archivos críticos presentes"

# Validar formato TODO.MD
echo "🔍 Validando formato de TODO.MD..."
TODO_TASKS=$(grep -c -E "(✅|🔁|⬜)" .workspace/context/todo.md)
if [ $TODO_TASKS -eq 0 ]; then
    echo "⚠️ ADVERTENCIA: TODO.MD no contiene tareas con formato correcto"
    echo "Formato esperado: ✅ (completada), 🔁 (en progreso), ⬜ (pendiente)"
fi

# Validar configuración de usuario
echo "🔍 Validando configuración de usuario..."
USER_NAME=$(grep "name:" .workspace/start.yaml | cut -d'"' -f2)
if [ -z "$USER_NAME" ] || [ "$USER_NAME" = "Desarrollador" ]; then
    echo "⚠️ ADVERTENCIA: Configuración de usuario genérica detectada"
    echo "Considera personalizar la configuración en start.yaml"
fi

# Validar sincronización
echo "🔍 Verificando sincronización..."
LAST_UPDATE=$(grep "last_updated:" .workspace/start.yaml | cut -d'"' -f2)
LOG_TIME=$(grep "Timestamp:" .workspace/context/log.md | cut -d' ' -f2)

echo "📊 REPORTE DE VALIDACIÓN:"
echo "   - Archivos críticos: ✅ Presentes"
echo "   - Tareas en TODO.MD: $TODO_TASKS encontradas"
echo "   - Usuario configurado: $USER_NAME"
echo "   - Última actualización: $LAST_UPDATE"

echo ""
echo "✅ VALIDACIÓN COMPLETADA"
