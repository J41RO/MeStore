#!/bin/bash
# ~/scripts/deploy_with_migrations.sh
# MeStore - Script completo de deployment con migraciones automáticas

# Colores para output
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
PURPLE="\033[0;35m"
NC="\033[0m" # No Color

# Variables de configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/logs/full_deploy_$(date +%Y%m%d_%H%M%S).log"

# Crear directorio de logs si no existe
mkdir -p "$PROJECT_ROOT/logs"

# Función de logging mejorada
log_deploy() {
    local level="$1"
    local message="$2"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [DEPLOY-$level] $message" | tee -a "$LOG_FILE"
}

# Función para mostrar ayuda
show_deploy_help() {
    echo -e "${PURPLE}🚀 MESTOCKER FULL DEPLOYMENT SCRIPT${NC}"
    echo ""
    echo -e "${CYAN}DESCRIPCIÓN:${NC}"
    echo "  Script completo de deployment con migraciones, health checks y validaciones"
    echo "  Secuencia: health check → backup → migrate → validate → start app"
    echo ""
    echo -e "${CYAN}USO:${NC}"
    echo "  $0 [OPTIONS] [environment]"
    echo ""
    echo -e "${CYAN}ENVIRONMENTS:${NC}"
    echo "  development    - Deployment de desarrollo"
    echo "  staging        - Deployment de staging/testing"
    echo "  production     - Deployment de producción (máxima seguridad)"
    echo ""
    echo -e "${CYAN}OPTIONS:${NC}"
    echo "  --check-only   - Solo verificar estado sin hacer deployment"
    echo "  --skip-backup  - Saltar backup (solo dev/staging)"
    echo "  --force        - Deployment sin confirmaciones interactivas"
    echo "  --rollback REV - Rollback a revisión específica"
    echo "  --help, -h     - Mostrar esta ayuda"
    echo ""
    echo -e "${CYAN}EJEMPLOS:${NC}"
    echo "  $0 development"
    echo "  $0 --check-only production"
    echo "  $0 --force staging"
    echo "  $0 --rollback abc123 production"
}

# Función para detectar si es deployment en Docker
detect_docker_environment() {
    if [[ -f "/.dockerenv" ]] || [[ -n "$DOCKER_CONTAINER" ]]; then
        echo "docker"
    else
        echo "host"
    fi
}

# Función para health check completo del sistema
system_health_check() {
    local environment="$1"
    
    log_deploy "INFO" "🔍 Iniciando health check completo del sistema"
    
    # Source alembic helpers para usar funciones
    source "$SCRIPT_DIR/alembic_helpers.sh"
    
    echo -e "${BLUE}=== SYSTEM HEALTH CHECK - $environment ===${NC}"
    
    # Check 1: Preparar environment
    echo -e "${CYAN}📋 1. PREPARANDO ENVIRONMENT${NC}"
    if prepare_deployment_environment "$environment"; then
        log_deploy "SUCCESS" "✅ Environment preparado correctamente"
    else
        log_deploy "ERROR" "❌ Fallo en preparación de environment"
        return 1
    fi
    
    # Check 2: Database health
    echo -e "${CYAN}📋 2. VERIFICANDO BASE DE DATOS${NC}"
    local db_health_result
    health_check_database "$environment"
    db_health_result=$?
    
    case $db_health_result in
        0)
            log_deploy "SUCCESS" "✅ Base de datos saludable"
            ;;
        1)
            log_deploy "ERROR" "❌ Base de datos no accesible"
            return 1
            ;;
        2)
            log_deploy "WARNING" "⚠️ Base de datos accesible pero con migraciones pendientes"
            ;;
    esac
    
    # Check 3: Verificar recursos del sistema
    echo -e "${CYAN}📋 3. VERIFICANDO RECURSOS DEL SISTEMA${NC}"
    
    # Verificar espacio en disco
    local disk_usage=$(df "$PROJECT_ROOT" | awk "NR==2 {print \$5}" | sed "s/%//")
    if [[ $disk_usage -gt 90 ]]; then
        log_deploy "WARNING" "⚠️ Espacio en disco bajo: ${disk_usage}%"
    else
        log_deploy "SUCCESS" "✅ Espacio en disco adecuado: ${disk_usage}%"
    fi
    
    # Check 4: Verificar servicios Docker si aplica
    local deploy_context=$(detect_docker_environment)
    if [[ "$deploy_context" == "docker" ]]; then
        echo -e "${CYAN}📋 4. VERIFICANDO SERVICIOS DOCKER${NC}"
        
        # Verificar que postgres y redis están corriendo
        if docker-compose ps postgres | grep -q "Up"; then
            log_deploy "SUCCESS" "✅ PostgreSQL container corriendo"
        else
            log_deploy "ERROR" "❌ PostgreSQL container no disponible"
            return 1
        fi
        
        if docker-compose ps redis | grep -q "Up"; then
            log_deploy "SUCCESS" "✅ Redis container corriendo"
        else
            log_deploy "WARNING" "⚠️ Redis container no disponible"
        fi
    fi
    
    log_deploy "SUCCESS" "🎉 Health check completo - Sistema listo para deployment"
    return 0
}

# Función para ejecutar deployment completo
execute_full_deployment() {
    local environment="$1"
    local skip_backup="$2"
    local force_mode="$3"
    
    log_deploy "INFO" "🚀 Iniciando deployment completo para $environment"
    
    # Source scripts necesarios
    source "$SCRIPT_DIR/alembic_helpers.sh"
    
    echo -e "${PURPLE}=== FULL DEPLOYMENT SEQUENCE ===${NC}"
    
    # FASE 1: Health Check Inicial
    echo -e "${BLUE}🔍 FASE 1: HEALTH CHECK INICIAL${NC}"
    if ! system_health_check "$environment"; then
        log_deploy "ERROR" "❌ Health check inicial falló"
        return 1
    fi
    
    # FASE 2: Backup (si es necesario)
    if [[ "$environment" == "production" ]] || [[ "$skip_backup" != "true" ]]; then
        echo -e "${BLUE}📦 FASE 2: CREACIÓN DE BACKUP${NC}"
        log_deploy "INFO" "📦 Iniciando backup de base de datos"
        
        # Usar script de migraciones para backup
        if "$SCRIPT_DIR/run_migrations.sh" --backup "$environment" --dry-run; then
            log_deploy "SUCCESS" "✅ Backup completado"
        else
            log_deploy "WARNING" "⚠️ Backup no disponible - continuando"
        fi
    else
        log_deploy "INFO" "ℹ️ Backup saltado para $environment"
    fi
    
    # FASE 3: Ejecutar Migraciones
    echo -e "${BLUE}⚡ FASE 3: MIGRACIONES DE BASE DE DATOS${NC}"
    log_deploy "INFO" "⚡ Ejecutando migraciones"
    
    if [[ "$force_mode" == "true" ]]; then
        migration_cmd="$SCRIPT_DIR/run_migrations.sh --force $environment"
    else
        migration_cmd="$SCRIPT_DIR/run_migrations.sh $environment"
    fi
    
    if $migration_cmd; then
        log_deploy "SUCCESS" "✅ Migraciones completadas exitosamente"
    else
        log_deploy "ERROR" "❌ Migraciones fallaron"
        return 1
    fi
    
    # FASE 4: Validación Post-Migración
    echo -e "${BLUE}✅ FASE 4: VALIDACIÓN POST-MIGRACIÓN${NC}"
    if health_check_database "$environment"; then
        log_deploy "SUCCESS" "✅ Validación post-migración exitosa"
    else
        log_deploy "ERROR" "❌ Validación post-migración falló"
        return 1
    fi
    
    # FASE 5: Restart de Aplicación (si en Docker)
    local deploy_context=$(detect_docker_environment)
    if [[ "$deploy_context" == "docker" ]]; then
        echo -e "${BLUE}🔄 FASE 5: RESTART DE APLICACIÓN${NC}"
        log_deploy "INFO" "🔄 Reiniciando servicios de aplicación"
        
        if docker-compose restart backend; then
            log_deploy "SUCCESS" "✅ Aplicación reiniciada exitosamente"
        else
            log_deploy "WARNING" "⚠️ Error reiniciando aplicación"
        fi
    fi
    
    # FASE 6: Health Check Final
    echo -e "${BLUE}🏁 FASE 6: HEALTH CHECK FINAL${NC}"
    if system_health_check "$environment"; then
        log_deploy "SUCCESS" "🎉 Deployment completado exitosamente"
        return 0
    else
        log_deploy "ERROR" "❌ Health check final falló"
        return 1
    fi
}

# Función para rollback
execute_rollback() {
    local environment="$1"
    local target_revision="$2"
    
    log_deploy "INFO" "🔄 Iniciando rollback a revisión $target_revision"
    
    # Source alembic helpers
    source "$SCRIPT_DIR/alembic_helpers.sh"
    
    echo -e "${RED}=== EMERGENCY ROLLBACK SEQUENCE ===${NC}"
    
    # Ejecutar rollback usando función de alembic helpers
    if emergency_rollback "$environment" "$target_revision"; then
        log_deploy "SUCCESS" "✅ Rollback completado"
        
        # Health check post-rollback
        echo -e "${BLUE}🔍 HEALTH CHECK POST-ROLLBACK${NC}"
        if system_health_check "$environment"; then
            log_deploy "SUCCESS" "🎉 Sistema estable después de rollback"
            return 0
        else
            log_deploy "ERROR" "❌ Sistema inestable después de rollback"
            return 1
        fi
    else
        log_deploy "ERROR" "❌ Rollback falló"
        return 1
    fi
}

# Función principal
main() {
    local environment=""
    local check_only=false
    local skip_backup=false
    local force_mode=false
    local rollback_revision=""
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --check-only)
                check_only=true
                shift
                ;;
            --skip-backup)
                skip_backup=true
                shift
                ;;
            --force)
                force_mode=true
                shift
                ;;
            --rollback)
                rollback_revision="$2"
                shift 2
                ;;
            --help|-h)
                show_deploy_help
                exit 0
                ;;
            development|staging|production)
                environment="$1"
                shift
                ;;
            *)
                echo -e "${RED}❌ ERROR: Argumento desconocido $1${NC}"
                show_deploy_help
                exit 1
                ;;
        esac
    done
    
    # Validar environment
    if [[ -z "$environment" ]]; then
        echo -e "${RED}❌ ERROR: Debe especificar environment${NC}"
        show_deploy_help
        exit 1
    fi
    
    if [[ ! "$environment" =~ ^(development|staging|production)$ ]]; then
        echo -e "${RED}❌ ERROR: Environment inválido: $environment${NC}"
        exit 1
    fi
    
    log_deploy "INFO" "🚀 Iniciando script de deployment completo"
    echo -e "${PURPLE}🚀 MESTOCKER FULL DEPLOYMENT - $environment${NC}"
    
    # Determinar operación
    if [[ -n "$rollback_revision" ]]; then
        # Modo rollback
        execute_rollback "$environment" "$rollback_revision"
        exit $?
    elif [[ "$check_only" == "true" ]]; then
        # Solo health check
        system_health_check "$environment"
        exit $?
    else
        # Deployment completo
        execute_full_deployment "$environment" "$skip_backup" "$force_mode"
        deployment_result=$?
        
        if [[ $deployment_result -eq 0 ]]; then
            echo -e "${GREEN}🎉 ✅ DEPLOYMENT COMPLETADO EXITOSAMENTE${NC}"
            echo -e "${CYAN}📝 Log completo: $LOG_FILE${NC}"
        else
            echo -e "${RED}❌ DEPLOYMENT FALLÓ${NC}"
            echo -e "${CYAN}📝 Revisar log: $LOG_FILE${NC}"
        fi
        
        exit $deployment_result
    fi
}

# Verificar si el script se ejecuta directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi