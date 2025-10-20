#!/bin/bash
# ~/scripts/production-entrypoint.sh
# ---------------------------------------------------------------------------------------------
# MESTORE - Production Entrypoint Script
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: production-entrypoint.sh
# Ruta: ~/scripts/production-entrypoint.sh
# Autor: DevOps Integration AI
# Fecha de Creación: 2025-09-17
# Última Actualización: 2025-09-17
# Versión: 1.0.0
# Propósito: Script de inicio para contenedor de producción
#            Incluye validaciones, migraciones y configuración de logging
#
# Modificaciones:
# 2025-09-17 - Script inicial de producción con validaciones completas
#
# ---------------------------------------------------------------------------------------------

set -euo pipefail

# Colores para logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función de logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Función para validar variables de entorno requeridas
validate_environment() {
    log "Validating environment variables..."

    local required_vars=(
        "DATABASE_URL"
        "SECRET_KEY"
        "ENVIRONMENT"
    )

    local missing_vars=()

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi

    log_success "Environment variables validated"
}

# Función para validar conectividad de base de datos
validate_database() {
    log "Validating database connectivity..."

    local max_attempts=30
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if python -c "
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_connection():
    try:
        engine = create_async_engine('${DATABASE_URL}')
        async with engine.begin() as conn:
            await conn.execute(text('SELECT 1'))
        await engine.dispose()
        return True
    except Exception as e:
        print(f'Database connection failed: {e}', file=sys.stderr)
        return False

result = asyncio.run(test_connection())
sys.exit(0 if result else 1)
" 2>/dev/null; then
            log_success "Database connectivity validated"
            return 0
        else
            log_warning "Database connection attempt $attempt/$max_attempts failed, retrying in 2 seconds..."
            sleep 2
            ((attempt++))
        fi
    done

    log_error "Failed to connect to database after $max_attempts attempts"
    exit 1
}

# Función para validar conectividad de Redis (opcional)
validate_redis() {
    if [[ -n "${REDIS_URL:-}" ]]; then
        log "Validating Redis connectivity..."

        if python -c "
import redis
import sys
try:
    r = redis.from_url('${REDIS_URL}')
    r.ping()
    print('Redis connection successful')
except Exception as e:
    print(f'Redis connection failed: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
            log_success "Redis connectivity validated"
        else
            log_warning "Redis connection failed, continuing without cache"
        fi
    else
        log_warning "Redis URL not configured, running without cache"
    fi
}

# Función para ejecutar migraciones de base de datos
run_migrations() {
    if [[ "${RUN_MIGRATIONS:-true}" == "true" ]]; then
        log "Running database migrations..."

        # Verificar que Alembic esté configurado
        if [[ ! -f "alembic.ini" ]]; then
            log_error "alembic.ini not found"
            exit 1
        fi

        # Ejecutar migraciones
        if alembic upgrade head; then
            log_success "Database migrations completed successfully"
        else
            log_error "Database migrations failed"
            exit 1
        fi
    else
        log "Skipping database migrations (RUN_MIGRATIONS=false)"
    fi
}

# Función para crear directorios necesarios
setup_directories() {
    log "Setting up application directories..."

    local dirs=("logs" "uploads" "qr_codes" "temp")

    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log "Created directory: $dir"
        fi
    done

    log_success "Application directories ready"
}

# Función para configurar logging
setup_logging() {
    log "Configuring application logging..."

    # Crear archivo de log si no existe
    touch logs/app.log
    touch logs/access.log
    touch logs/error.log

    # Configurar rotación de logs
    log_success "Logging configuration completed"
}

# Función para verificar la salud de la aplicación
health_check() {
    log "Performing application health check..."

    # Verificar que los módulos principales se pueden importar
    if python -c "
import app.main
import app.core.config
import app.models
import app.services
print('Application modules loaded successfully')
" 2>/dev/null; then
        log_success "Application health check passed"
    else
        log_error "Application health check failed"
        exit 1
    fi
}

# Función principal de inicio
main() {
    log "🚀 Starting MeStore Backend Production Server"
    log "Environment: ${ENVIRONMENT:-production}"
    log "Python Path: ${PYTHONPATH:-/home/appuser/app}"

    # Ejecutar validaciones
    validate_environment
    setup_directories
    setup_logging
    validate_database
    validate_redis
    run_migrations
    health_check

    log_success "All pre-flight checks completed successfully"
    log "🎯 Starting uvicorn server..."

    # Configurar parámetros de uvicorn basados en el entorno
    local uvicorn_args=(
        "app.main:app"
        "--host=${UVICORN_HOST:-0.0.0.0}"
        "--port=${UVICORN_PORT:-8000}"
        "--workers=${UVICORN_WORKERS:-4}"
        "--loop=${UVICORN_LOOP:-uvloop}"
        "--http=${UVICORN_HTTP:-httptools}"
    )

    # Configuraciones específicas para desarrollo vs producción
    if [[ "${ENVIRONMENT}" == "development" ]]; then
        uvicorn_args+=(
            "--reload"
            "--log-level=debug"
        )
        log "🔧 Development mode enabled with hot-reload"
    else
        uvicorn_args+=(
            "--log-level=${UVICORN_LOG_LEVEL:-info}"
            "--access-log"
        )
        log "🏭 Production mode enabled"
    fi

    # Logs adicionales de configuración
    log "Uvicorn configuration:"
    log "  Host: ${UVICORN_HOST:-0.0.0.0}"
    log "  Port: ${UVICORN_PORT:-8000}"
    log "  Workers: ${UVICORN_WORKERS:-4}"
    log "  Loop: ${UVICORN_LOOP:-uvloop}"
    log "  HTTP: ${UVICORN_HTTP:-httptools}"

    # Iniciar el servidor
    exec uvicorn "${uvicorn_args[@]}"
}

# Manejar señales de cierre
cleanup() {
    log "🛑 Received shutdown signal, performing cleanup..."
    # Aquí podrías agregar lógica de limpieza adicional
    exit 0
}

# Configurar manejo de señales
trap cleanup SIGTERM SIGINT

# Ejecutar función principal
main "$@"