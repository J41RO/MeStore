#!/bin/bash
# Hook para comando /test - Master Testing Orchestrator

# Detectar si el usuario escribió "test" o "/test"
if [[ "$CLAUDE_USER_INPUT" == *"test"* ]] && [[ "$CLAUDE_USER_INPUT" == *"/"* ]]; then
    echo "🚀 ACTIVANDO MASTER TESTING ORCHESTRATOR"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Ejecutar el script directamente
    cd /home/admin-jairo/MeStore
    python .workspace/scripts/master_testing_orchestrator.py

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Master Testing Orchestrator completado"
fi