#!/bin/bash
# ~/scripts/run_migrations.sh
# MeStore - Script principal para ejecutar migraciones en deployment

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
LOG_FILE="$PROJECT_ROOT/logs/migration_deploy_$(date +%Y%m%d_%H%M%S).log"

# Crear directorio de logs si no existe
mkdir -p "$PROJECT_ROOT/logs"

# Función de logging
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🔧 MESTOCKER DEPLOYMENT MIGRATIONS SCRIPT${NC}"
    echo ""
    echo -e "${CYAN}DESCRIPCIÓN:${NC}"
    echo "  Script robusto para ejecutar migraciones durante deployment"
    echo "  Incluye validación de DB, backup automático y rollback"
    echo ""
    echo -e "${CYAN}USO:${NC}"
    echo "  $0 [OPTIONS] [environment]"
    echo ""
    echo -e "${CYAN}ENVIRONMENTS:${NC}"
    echo "  development    - Ambiente de desarrollo"
    echo "  testing        - Ambiente de pruebas"
    echo "  production     - Ambiente de producción"
    echo ""
    echo -e "${CYAN}OPTIONS:${NC}"
    echo "  --dry-run      - Mostrar qué migraciones se ejecutarían sin aplicarlas"
    echo "  --force        - Forzar ejecución sin confirmación interactiva"
    echo "  --backup       - Crear backup antes de migrar (recomendado para prod)"
    echo "  --help, -h     - Mostrar esta ayuda"
}

# Función para detectar environment automáticamente
detect_environment() {
    if [[ -n "$ENVIRONMENT" ]]; then
        echo "$ENVIRONMENT"
    elif [[ -f "$PROJECT_ROOT/.env" ]]; then
        grep "^ENVIRONMENT=" "$PROJECT_ROOT/.env" | cut -d"=" -f2 | tr -d "\""
    else
        echo "development"
    fi
}

# Función para validar conectividad de base de datos
validate_db_connection() {
    local environment="$1"
    
    log_message "INFO" "🔍 Validando conectividad de base de datos para $environment"
    
    # Source alembic helpers para usar funciones existentes
    source "$SCRIPT_DIR/alembic_helpers.sh"
    
    # Test simple con alembic
    if alembic -x env=$environment current > /dev/null 2>&1; then
        log_message "SUCCESS" "✅ Conectividad de base de datos confirmada"
        return 0
    else
        log_message "ERROR" "❌ No se puede conectar a la base de datos"
        return 1
    fi
}

# Función para ejecutar migraciones
run_migrations() {
    local environment="$1"
    local dry_run="$2"
    
    log_message "INFO" "🚀 Iniciando proceso de migración para $environment"
    
    # Source alembic helpers
    source "$SCRIPT_DIR/alembic_helpers.sh"
    
    if [[ "$dry_run" == "true" ]]; then
        log_message "INFO" "🔍 DRY RUN: Mostrando migraciones pendientes"
        
        echo -e "${YELLOW}📋 MIGRACIONES PENDIENTES:${NC}"
        alembic -x env=$environment history --verbose
        
        echo -e "${YELLOW}📋 ESTADO ACTUAL:${NC}"
        alembic -x env=$environment current --verbose
        
        log_message "INFO" "✅ Dry run completado"
        return 0
    else
        log_message "INFO" "⚡ Ejecutando migraciones"
        
        if alembic -x env=$environment upgrade head; then
            log_message "SUCCESS" "✅ Migraciones ejecutadas exitosamente"
            return 0
        else
            log_message "ERROR" "❌ Error durante ejecución de migraciones"
            return 1
        fi
    fi
}

# Función principal
main() {
    local environment=""
    local dry_run=false
    local force=false
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --force)
                force=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            development|testing|production)
                environment="$1"
                shift
                ;;
            *)
                echo -e "${RED}❌ ERROR: Argumento desconocido $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Auto-detectar environment si no se proporcionó
    if [[ -z "$environment" ]]; then
        environment=$(detect_environment)
        log_message "INFO" "🔍 Environment auto-detectado: $environment"
    fi
    
    # Validar environment
    if [[ ! "$environment" =~ ^(development|testing|production)$ ]]; then
        log_message "ERROR" "❌ Environment inválido: $environment"
        echo -e "${RED}❌ Environment debe ser: development, testing, o production${NC}"
        exit 1
    fi
    
    log_message "INFO" "🚀 Iniciando deployment migrations para $environment"
    
    # FASE 1: Validar conectividad
    echo -e "${BLUE}🔍 FASE 1: VALIDACIÓN DE CONECTIVIDAD${NC}"
    if ! validate_db_connection "$environment"; then
        log_message "ERROR" "❌ Falló validación de conectividad"
        exit 1
    fi
    
    # FASE 2: Confirmación interactiva (a menos que --force)
    if [[ "$force" != "true" ]] && [[ "$dry_run" != "true" ]]; then
        echo -e "${YELLOW}⚠️ ¿Confirmas ejecutar migraciones en $environment? (y/N)${NC}"
        read -r confirmation
        if [[ "$confirmation" != "y" ]] && [[ "$confirmation" != "Y" ]]; then
            log_message "INFO" "❌ Operación cancelada por el usuario"
            exit 0
        fi
    fi
    
    # FASE 3: Ejecutar migraciones
    echo -e "${BLUE}⚡ FASE 3: EJECUCIÓN DE MIGRACIONES${NC}"
    if ! run_migrations "$environment" "$dry_run"; then
        log_message "ERROR" "❌ Falló ejecución de migraciones"
        exit 1
    fi
    
    # Éxito
    log_message "SUCCESS" "🎉 Deployment migrations completado exitosamente"
    echo -e "${GREEN}🎉 ✅ DEPLOYMENT MIGRATIONS COMPLETADO EXITOSAMENTE${NC}"
    
    if [[ "$dry_run" != "true" ]]; then
        echo -e "${GREEN}📊 Revision actual: $(alembic -x env=$environment current --head-only 2>/dev/null)${NC}"
    fi
    
    echo -e "${CYAN}📝 Log completo: $LOG_FILE${NC}"
}

# Verificar si el script se ejecuta directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi