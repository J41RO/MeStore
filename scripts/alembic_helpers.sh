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
