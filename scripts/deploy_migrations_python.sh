#!/bin/bash
# ~/scripts/deploy_migrations_python.sh
# MeStore - Wrapper para integrar script Python con deployment

# Colores para output
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
NC="\033[0m" # No Color

# Variables de configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="$SCRIPT_DIR/run_migrations.py"

echo -e "${BLUE}=== 🚀 DEPLOY MIGRATIONS PYTHON WRAPPER ===${NC}"
echo -e "${CYAN}📍 Proyecto: $PROJECT_ROOT${NC}"

# Función de ayuda
show_help() {
    echo -e "${YELLOW}Uso: $0 [OPCIONES] [ENTORNO]${NC}"
    echo ""
    echo "Entornos disponibles:"
    echo "  development (default)"
    echo "  production" 
    echo "  test"
    echo ""
    echo "Opciones:"
    echo "  --validate    Solo validar sistema"
    echo "  --dry-run     Simular sin ejecutar"
    echo "  --rollback REV Rollback a revisión"
    echo "  --force       Forzar sin validaciones"
    echo "  --help        Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 --validate production"
    echo "  $0 --dry-run development"
    echo "  $0 production"
    echo "  $0 --rollback abc123 production"
}

# Verificar que existe el script Python
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}❌ Error: Script Python no encontrado: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# Verificar que Python está disponible
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 no está disponible${NC}"
    exit 1
fi

# Procesar argumentos
PYTHON_ARGS=()
ENVIRONMENT="development"

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --validate)
            PYTHON_ARGS+=("--validate")
            shift
            ;;
        --dry-run)
            PYTHON_ARGS+=("--dry-run")
            shift
            ;;
        --rollback)
            PYTHON_ARGS+=("--rollback" "$2")
            shift 2
            ;;
        --force)
            PYTHON_ARGS+=("--force")
            shift
            ;;
        development|production|test)
            ENVIRONMENT="$1"
            shift
            ;;
        *)
            echo -e "${RED}❌ Opción desconocida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Agregar entorno a argumentos Python
PYTHON_ARGS+=("--env" "$ENVIRONMENT")

echo -e "${CYAN}🎯 Entorno: $ENVIRONMENT${NC}"
echo -e "${CYAN}🔧 Argumentos: ${PYTHON_ARGS[*]}${NC}"
echo ""

# Ejecutar script Python
echo -e "${BLUE}🚀 Ejecutando script Python de migraciones...${NC}"
cd "$PROJECT_ROOT"

python3 "$PYTHON_SCRIPT" "${PYTHON_ARGS[@]}"
RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Script Python ejecutado exitosamente${NC}"
else
    echo ""
    echo -e "${RED}❌ Script Python falló con código: $RESULT${NC}"
fi

exit $RESULT
