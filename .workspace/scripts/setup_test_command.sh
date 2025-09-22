#!/bin/bash
# Setup script for /test command configuration

echo "🔧 Configurando comando /test para Claude Code..."

# Create the configuration directory if it doesn't exist
mkdir -p ~/.claude-code

# Configuration template
cat > ~/.claude-code/test-command-config.json << 'EOF'
{
  "slash_commands": {
    "test": {
      "description": "Backend Testing Suite - Master Orchestrator completo",
      "command": "python .workspace/scripts/master_testing_orchestrator.py",
      "working_directory": "/home/admin-jairo/MeStore",
      "timeout": 1800,
      "environment": {
        "PYTHONPATH": "/home/admin-jairo/MeStore",
        "TESTING_MODE": "true"
      }
    }
  }
}
EOF

echo "✅ Configuración creada en ~/.claude-code/test-command-config.json"
echo ""
echo "📋 INSTRUCCIONES:"
echo "1. Ejecuta: /settings en Claude Code"
echo "2. Copia el contenido de ~/.claude-code/test-command-config.json"
echo "3. Pega en la sección 'slash_commands'"
echo "4. Guarda configuración"
echo "5. Prueba con: /test"
echo ""
echo "🎯 Comando configurado: /test"
echo "   - Activa Master Testing Orchestrator"
echo "   - Máximo 3 agentes simultáneos"
echo "   - Meta: 85% cobertura + 100% tests pasando"
echo "   - Reportes en tiempo real"