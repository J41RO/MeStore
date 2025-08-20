#!/bin/bash
# 🧪 SURGICAL MODIFIER ULTIMATE v5.3 - TEST RUNNER SCRIPT

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}🧪 SURGICAL MODIFIER ULTIMATE v5.3 - TEST SUITE${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Verificar que estamos en el directorio correcto
if [[ ! -f "surgical_modifier_ultimate.py" ]]; then
    echo -e "${RED}❌ ERROR: Debe ejecutar desde directorio .workspace/scripts/${NC}"
    echo -e "${YELLOW}💡 Solución: cd .workspace/scripts && ./run_tests.sh${NC}"
    exit 1
fi

# Función para mostrar ayuda
show_help() {
    echo -e "${YELLOW}USO:${NC}"
    echo "  ./run_tests.sh                 # Ejecutar tests básicos"
    echo "  ./run_tests.sh --coverage      # Ejecutar con reporte de cobertura"
    echo "  ./run_tests.sh --html          # Generar reporte HTML"
    echo "  ./run_tests.sh --fast          # Solo tests rápidos"
    echo "  ./run_tests.sh --help          # Mostrar esta ayuda"
    echo ""
}

# Verificar dependencias
check_dependencies() {
    echo -e "${BLUE}🔍 Verificando dependencias...${NC}"
    
    if ! command -v pytest &> /dev/null; then
        echo -e "${RED}❌ pytest no encontrado${NC}"
        echo -e "${YELLOW}💡 Instalando: pip install -r requirements.txt${NC}"
        pip install -r requirements.txt
    else
        echo -e "${GREEN}✅ pytest disponible${NC}"
    fi
    
    echo ""
}

# Tests básicos
run_basic_tests() {
    echo -e "${BLUE}🚀 Ejecutando tests básicos...${NC}"
    pytest tests/test_color_logger.py tests/test_backup_manager_simple.py tests/test_surgical_modifier_simple.py -v
    
    if [[ $? -eq 0 ]]; then
        echo ""
        echo -e "${GREEN}🎉 ¡TODOS LOS TESTS PASAN!${NC}"
    else
        echo ""
        echo -e "${RED}❌ Algunos tests fallaron${NC}"
        exit 1
    fi
}

# Tests con cobertura
run_coverage_tests() {
    echo -e "${BLUE}📊 Ejecutando tests con cobertura...${NC}"
    pytest tests/test_color_logger.py tests/test_backup_manager_simple.py tests/test_surgical_modifier_simple.py \
           --cov=surgical_modifier_ultimate \
           --cov-report=term-missing \
           --cov-report=html:htmlcov \
           -v
    
    if [[ $? -eq 0 ]]; then
        echo ""
        echo -e "${GREEN}🎉 ¡TESTS Y COBERTURA COMPLETADOS!${NC}"
        echo -e "${YELLOW}📁 Reporte HTML disponible en: htmlcov/index.html${NC}"
    else
        echo ""
        echo -e "${RED}❌ Tests fallaron${NC}"
        exit 1
    fi
}

# Tests rápidos
run_fast_tests() {
    echo -e "${BLUE}⚡ Ejecutando tests rápidos...${NC}"
    pytest tests/test_color_logger.py::TestColorLogger::test_color_logger_initialization \
           tests/test_backup_manager_simple.py::TestBackupManagerSimple::test_backup_manager_creation \
           tests/test_surgical_modifier_simple.py::TestSurgicalModifierSimple::test_modifier_creation \
           -v
}

# Generar solo reporte HTML
generate_html_report() {
    echo -e "${BLUE}📄 Generando reporte HTML...${NC}"
    pytest tests/ --cov=surgical_modifier_ultimate --cov-report=html:htmlcov --quiet
    echo -e "${GREEN}✅ Reporte HTML generado en: htmlcov/index.html${NC}"
}

# Main logic
case "${1:-}" in
    --help|-h)
        show_help
        ;;
    --coverage)
        check_dependencies
        run_coverage_tests
        ;;
    --html)
        check_dependencies
        generate_html_report
        ;;
    --fast)
        check_dependencies
        run_fast_tests
        ;;
    "")
        check_dependencies
        run_basic_tests
        ;;
    *)
        echo -e "${RED}❌ Opción desconocida: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎯 Testing suite completado exitosamente${NC}"
echo -e "${BLUE}📚 Para más información: cat README_TESTING.md${NC}"
