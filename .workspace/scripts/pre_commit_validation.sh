#!/bin/bash
# SMART DEV SYSTEM v1.5.0 - Pre-Commit Validation Script
# Validaciones básicas antes de permitir un commit.

echo "🔎 SMART DEV SYSTEM v1.5.0 - VALIDACIÓN PRE-COMMIT"
echo "==================================================="

# Detectar lenguaje para validación
LANGUAGE=$(grep "language:" .workspace/start.yaml | cut -d'"' -f2)

if [ "$LANGUAGE" = "python" ]; then
    echo "🐍 Validando código Python..."
    if command -v flake8 &> /dev/null; then
        echo "Flake8 encontrado. Analizando código..."
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        if [ $? -ne 0 ]; then
            echo "❌ Flake8 encontró errores. Corrige y vuelve a intentar."
            exit 1
        fi
        echo "✅ Flake8: Sin errores críticos."
    else
        echo "⚠️ ADVERTENCIA: Flake8 no instalado. No se puede validar calidad de código."
    fi
elif [ "$LANGUAGE" = "javascript" ]; then
    echo "📜 Validando código JavaScript..."
    if command -v eslint &> /dev/null; then
        echo "ESLint encontrado. Analizando código..."
        eslint .
        if [ $? -ne 0 ]; then
            echo "❌ ESLint encontró errores. Corrige y vuelve a intentar."
            exit 1
        fi
        echo "✅ ESLint: Sin errores."
    else
        echo "⚠️ ADVERTENCIA: ESLint no instalado. No se puede validar calidad de código."
    fi
else
    echo "🤔 No se encontró un validador para el lenguaje: $LANGUAGE"
fi

echo "✅ Validación Pre-Commit completada."
exit 0
