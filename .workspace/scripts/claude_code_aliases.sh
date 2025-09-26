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
