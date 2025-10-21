#!/bin/bash
# ==========================================================
# 🧹 MeStore - Limpieza y Organización Automática de Proyecto
# ----------------------------------------------------------
# Este script reordena la raíz, elimina basura temporal y
# asegura que la estructura del proyecto se mantenga limpia.
# ==========================================================

echo "=== 🧹 INICIO DE LIMPIEZA DEL PROYECTO ==="
ROOT_DIR="$(dirname "$0")/.."
cd "$ROOT_DIR" || exit 1

# Crear directorios esperados si faltan
mkdir -p reports/coverage reports/integration reports/tests reports/db
mkdir -p config docs/ai_notes

# Archivos a mover
echo "🧩 Reubicando archivos de reportes y coverage..."
mv coverage.xml htmlcov coverage reports/coverage/ 2>/dev/null || true
mv integration_test_report_*.json reports/integration/ 2>/dev/null || true
mv test_async.db* test_sync.db* reports/db/ 2>/dev/null || true

echo "⚙️ Moviendo archivos de configuración..."
mv logging.conf Procfile render.yaml dev_server.pid config/ 2>/dev/null || true

echo "🧠 Moviendo notas de IA..."
mv CLAUDE*.md docs/ai_notes/ 2>/dev/null || true

echo "💾 Moviendo bases de datos locales..."
mv mestore*.db data/ 2>/dev/null || true

# Limpieza de cachés y temporales
echo "🧽 Limpiando __pycache__, .pytest_cache y archivos basura..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null

# Revalidar estructura del proyecto
echo "✅ Estructura del proyecto después de la limpieza:"
tree -L 2 | grep -v "__pycache__"

echo ""
echo "🎯 Limpieza completada. Proyecto MeStore listo para desarrollo limpio."
