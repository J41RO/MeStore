#!/bin/bash
# 📋 ALEMBIC MULTI-ENVIRONMENT HELPER SCRIPT
# MeStore - Sistema de migrations por environment

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔧 ALEMBIC MULTI-ENVIRONMENT HELPERS LOADED"

# Función para ejecutar alembic con environment específico
alembic_env() {
    local environment="$1"
    shift
    
    if [[ ! "$environment" =~ ^(development|testing|production)$ ]]; then
        echo -e "${RED}❌ ERROR: Environment debe ser 'development', 'testing', o 'production'${NC}"
        echo -e "${YELLOW}💡 Uso: alembic_env <environment> <comando_alembic>${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🎯 Ejecutando Alembic en environment: ${environment}${NC}"
    
    # Setear environment variable y ejecutar alembic
    ENVIRONMENT="$environment" alembic "$@"
}

# Shortcuts para environments específicos
alembic-dev() {
    echo -e "${GREEN}🔧 DEVELOPMENT ENVIRONMENT${NC}"
    alembic_env development "$@"
}

alembic-test() {
    echo -e "${YELLOW}🧪 TESTING ENVIRONMENT${NC}"
    alembic_env testing "$@"
}

alembic-prod() {
    echo -e "${RED}🚀 PRODUCTION ENVIRONMENT${NC}"
    read -p "⚠️  CONFIRMA OPERACIÓN EN PRODUCCIÓN [y/N]: " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        alembic_env production "$@"
    else
        echo -e "${YELLOW}🔄 Operación cancelada${NC}"
        return 1
    fi
}

# Función para mostrar status de todos los environments
alembic-status() {
    echo -e "${BLUE}📊 STATUS DE MIGRATIONS POR ENVIRONMENT${NC}"
    echo ""
    
    echo -e "${GREEN}🔧 DEVELOPMENT:${NC}"
    alembic_env development current 2>/dev/null || echo "❌ No disponible"
    echo ""
    
    echo -e "${YELLOW}🧪 TESTING:${NC}"
    alembic_env testing current 2>/dev/null || echo "❌ No disponible"
    echo ""
    
    echo -e "${RED}🚀 PRODUCTION:${NC}"
    alembic_env production current 2>/dev/null || echo "❌ No disponible"
}

# Función para verificar configuración
alembic-check() {
    echo -e "${BLUE}🔍 VERIFICANDO CONFIGURACIÓN MULTI-ENVIRONMENT${NC}"
    echo ""
    
    # Verificar archivos .env
    for env in "development" "testing" "production"; do
        env_file=".env"
        if [[ "$env" == "testing" ]]; then
            env_file=".env.test"
        elif [[ "$env" == "production" ]]; then
            env_file=".env.production"
        fi
        
        if [[ -f "$env_file" ]]; then
            echo -e "${GREEN}✅ $env_file existe${NC}"
            if grep -q "DATABASE_URL" "$env_file"; then
                echo -e "   📋 DATABASE_URL configurado"
            else
                echo -e "${YELLOW}   ⚠️ DATABASE_URL no encontrado${NC}"
            fi
        else
            echo -e "${RED}❌ $env_file no existe${NC}"
        fi
    done
    
    echo ""
    echo -e "${BLUE}📋 SECTIONS EN ALEMBIC.INI:${NC}"
    if grep -q "\[alembic:development\]" alembic.ini; then
        echo -e "${GREEN}✅ [alembic:development]${NC}"
    else
        echo -e "${RED}❌ [alembic:development] no encontrado${NC}"
    fi
    
    if grep -q "\[alembic:testing\]" alembic.ini; then
        echo -e "${GREEN}✅ [alembic:testing]${NC}"
    else
        echo -e "${RED}❌ [alembic:testing] no encontrado${NC}"
    fi
    
    if grep -q "\[alembic:production\]" alembic.ini; then
        echo -e "${GREEN}✅ [alembic:production]${NC}"
    else
        echo -e "${RED}❌ [alembic:production] no encontrado${NC}"
    fi
}

# Mostrar ayuda
alembic-help() {
    echo -e "${BLUE}📚 ALEMBIC MULTI-ENVIRONMENT COMMANDS${NC}"
    echo ""
    echo -e "${GREEN}Comandos básicos:${NC}"
    echo "  alembic-dev <command>    - Ejecutar en development"
    echo "  alembic-test <command>   - Ejecutar en testing"
    echo "  alembic-prod <command>   - Ejecutar en production (con confirmación)"
    echo ""
    echo -e "${GREEN}Comandos de utilidad:${NC}"
    echo "  alembic-status          - Mostrar status de todos los environments"
    echo "  alembic-check           - Verificar configuración"
    echo "  alembic-help            - Mostrar esta ayuda"
    echo ""
    echo -e "${GREEN}Ejemplos:${NC}"
    echo "  alembic-dev current                    # Ver revision actual en dev"
    echo "  alembic-test upgrade head              # Migrar testing a latest"
    echo "  alembic-prod history                   # Ver historial en production"
    echo "  alembic_env development revision --autogenerate -m 'Add new field'"
}

echo -e "${GREEN}✅ Helpers cargados. Usa 'alembic-help' para ver comandos disponibles${NC}"



# ============================================================================
# FUNCIONES DE DEPLOYMENT AGREGADAS 2025-07-24
# ============================================================================

# Función para health check completo de base de datos
health_check_database() {
    local environment="$1"
    
    echo -e "${BLUE}🔍 HEALTH CHECK DATABASE - $environment${NC}"
    
    # Test 1: Conectividad básica
    if ! alembic -x env=$environment current > /dev/null 2>&1; then
        echo -e "${RED}❌ ERROR: No se puede conectar a la base de datos${NC}"
        return 1
    fi
    
    # Test 2: Verificar que las tablas críticas existen
    echo -e "🔍 Verificando tablas críticas..."
    
    # Test 3: Verificar estado de migraciones
    local current_rev=$(alembic -x env=$environment current --head-only 2>/dev/null)
    local head_rev=$(alembic -x env=$environment heads --head-only 2>/dev/null)
    
    echo -e "📊 Revisión actual: $current_rev"
    echo -e "📊 Revisión esperada: $head_rev"
    
    if [[ "$current_rev" != "$head_rev" ]]; then
        echo -e "${YELLOW}⚠️ WARNING: Base de datos no está en la revisión más reciente${NC}"
        echo -e "   Migraciones pendientes detectadas"
        return 2  # Warning, no error crítico
    fi
    
    echo -e "${GREEN}✅ Health check completado - Base de datos saludable${NC}"
    return 0
}

# Función específica para deployment con validaciones extra
deploy_migrate() {
    local environment="$1"
    local backup_enabled="${2:-false}"
    
    echo -e "${CYAN}🚀 DEPLOY MIGRATE - $environment${NC}"
    
    # Validaciones previas más estrictas para deployment
    if [[ "$environment" == "production" ]]; then
        echo -e "${YELLOW}⚠️ DEPLOYMENT EN PRODUCCIÓN - Validaciones estrictas activadas${NC}"
        
        # Confirmar que hay migraciones pendientes
        local current_rev=$(alembic -x env=$environment current --head-only 2>/dev/null)
        local head_rev=$(alembic -x env=$environment heads --head-only 2>/dev/null)
        
        if [[ "$current_rev" == "$head_rev" ]]; then
            echo -e "${GREEN}ℹ️ Base de datos ya está actualizada - No hay migraciones pendientes${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}📋 Migraciones a aplicar:${NC}"
        alembic -x env=$environment history --indicate-current | grep -A 10 "(current)"
        
        # Pausa adicional para producción
        echo -e "${RED}⚠️ ÚLTIMA CONFIRMACIÓN PARA PRODUCCIÓN${NC}"
        echo -e "¿Estás COMPLETAMENTE SEGURO de aplicar estas migraciones? (escriba 'CONFIRMO'): "
        read -r final_confirmation
        
        if [[ "$final_confirmation" != "CONFIRMO" ]]; then
            echo -e "${RED}❌ Deployment cancelado - Confirmación requerida${NC}"
            return 1
        fi
    fi
    
    # Ejecutar migración usando función existente
    echo -e "⚡ Ejecutando migraciones..."
    if alembic_upgrade "$environment"; then
        echo -e "${GREEN}✅ Deploy migration completado exitosamente${NC}"
        
        # Verificación post-deployment
        health_check_database "$environment"
        return $?
    else
        echo -e "${RED}❌ Error durante deploy migration${NC}"
        return 1
    fi
}

# Función para rollback de emergencia
emergency_rollback() {
    local environment="$1"
    local target_revision="$2"
    
    echo -e "${RED}🚨 EMERGENCY ROLLBACK - $environment${NC}"
    echo -e "${YELLOW}⚠️ ATENCIÓN: Esta operación puede causar pérdida de datos${NC}"
    
    if [[ -z "$target_revision" ]]; then
        echo -e "${RED}❌ ERROR: Debe especificar revisión objetivo para rollback${NC}"
        echo -e "Uso: emergency_rollback <environment> <revision>"
        return 1
    fi
    
    # Mostrar estado actual
    echo -e "📊 Estado actual:"
    alembic -x env=$environment current --verbose
    
    echo -e "📊 Objetivo de rollback: $target_revision"
    
    # Confirmación estricta
    echo -e "${RED}⚠️ ¿CONFIRMA ROLLBACK DE EMERGENCIA? (escriba 'EMERGENCY'): ${NC}"
    read -r emergency_confirmation
    
    if [[ "$emergency_confirmation" != "EMERGENCY" ]]; then
        echo -e "${RED}❌ Rollback cancelado${NC}"
        return 1
    fi
    
    # Ejecutar rollback
    echo -e "🔄 Ejecutando rollback..."
    if alembic -x env=$environment downgrade "$target_revision"; then
        echo -e "${GREEN}✅ Emergency rollback completado${NC}"
        
        # Verificar estado post-rollback
        echo -e "📊 Estado post-rollback:"
        alembic -x env=$environment current --verbose
        
        return 0
    else
        echo -e "${RED}❌ Error durante emergency rollback${NC}"
        return 1
    fi
}

# Función para preparar environment para deployment
prepare_deployment_environment() {
    local environment="$1"
    
    echo -e "${BLUE}🔧 PREPARANDO ENVIRONMENT PARA DEPLOYMENT - $environment${NC}"
    
    # Verificar variables de entorno críticas
    local env_file=".env"
    if [[ "$environment" != "development" ]]; then
        env_file=".env.$environment"
    fi
    
    if [[ ! -f "$env_file" ]]; then
        echo -e "${RED}❌ ERROR: Archivo de configuración no encontrado: $env_file${NC}"
        return 1
    fi
    
    echo -e "✅ Archivo de configuración encontrado: $env_file"
    
    # Source del archivo de configuración
    source "$env_file"
    
    # Verificar variables críticas
    local required_vars=("DATABASE_URL" "ENVIRONMENT")
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            echo -e "${RED}❌ ERROR: Variable requerida no configurada: $var${NC}"
            return 1
        else
            echo -e "✅ Variable configurada: $var"
        fi
    done
    
    echo -e "${GREEN}✅ Environment preparado para deployment${NC}"
    return 0
}

echo "🔧 ALEMBIC DEPLOYMENT HELPERS LOADED - Extended 2025-07-24"
