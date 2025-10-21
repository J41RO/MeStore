#!/bin/bash
# =============================================================
# 🚀 MeStore - Script de Reorganización Automática de Tests
# -------------------------------------------------------------
# Este script analiza, clasifica y reorganiza los tests del
# proyecto según su nombre y propósito.
# Crea logs detallados y evita pérdidas o sobrescrituras.
# =============================================================

echo "=== 🧩 INICIO DE REORGANIZACIÓN AUTOMÁTICA DE TESTS ==="
cd "$(dirname "$0")/.."

TIMESTAMP=$(date +%F_%H-%M-%S)
LOG_DIR="logs/reorg_logs"
LOG_FILE="$LOG_DIR/reorganization_$TIMESTAMP.log"

mkdir -p "$LOG_DIR"
echo "Registro de reorganización - $TIMESTAMP" > "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"

# -------------------------------
# Función para mover archivos
# -------------------------------
move_test() {
  local src="$1"
  local dest="$2"
  mkdir -p "$dest"
  mv "$src" "$dest/" && echo "$src --> $dest/" >> "$LOG_FILE"
}

# -------------------------------
# Reglas de clasificación
# -------------------------------
echo "Aplicando reglas de clasificación..." | tee -a "$LOG_FILE"

for file in $(find . -maxdepth 1 -type f -name "test_*.py" | sort); do
  case "$file" in
    *admin*|*api*|*endpoint*|*vendedor*|*vendor*|*user*)
      move_test "$file" "api" ;;
    *model*)
      move_test "$file" "models" ;;
    *schema*)
      move_test "$file" "schemas" ;;
    *storage*|*financial*|*qr_system*|*rejection*)
      move_test "$file" "services" ;;
    *transaction*|*chromadb*|*embedding*|*wompi*|*database*)
      move_test "$file" "integration" ;;
    *health*|*config*|*logger*)
      move_test "$file" "core" ;;
    *makefile*|*script*)
      move_test "$file" "scripts" ;;
    *)
      move_test "$file" "uncategorized" ;;
  esac
done

echo -e "\n✅ Reorganización completada. Log disponible en: $LOG_FILE"
echo "Archivos de test actuales:"
find api models schemas services integration core scripts uncategorized -type f -name 'test_*.py' | wc -l
echo "========================================="
