#!/bin/bash
# MeStore Development Helper Script

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_help() {
    echo "MeStore Development Helper"
    echo ""
    echo "Uso: ./scripts/dev.sh [COMMAND]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start     - Iniciar todos los servicios"
    echo "  stop      - Detener todos los servicios"
    echo "  restart   - Reiniciar todos los servicios"
    echo "  build     - Rebuildar containers"
    echo "  logs      - Ver logs de todos los servicios"
    echo "  logs-be   - Ver logs solo del backend"
    echo "  logs-fe   - Ver logs solo del frontend"
    echo "  shell-be  - Abrir shell en container backend"
    echo "  status    - Ver estado de servicios"
    echo "  clean     - Limpiar containers y volúmenes"
    echo "  help      - Mostrar esta ayuda"
}

case "$1" in
    "start")
        log_info "Iniciando servicios de desarrollo..."
        docker-compose up -d
        log_success "Servicios iniciados"
        log_info "Backend: http://localhost:8000"
        log_info "Frontend: http://localhost:5173"
        ;;
    "stop")
        log_info "Deteniendo servicios..."
        docker-compose down
        log_success "Servicios detenidos"
        ;;
    "restart")
        log_info "Reiniciando servicios..."
        docker-compose restart
        log_success "Servicios reiniciados"
        ;;
    "build")
        log_info "Rebuilding containers..."
        docker-compose build --no-cache
        log_success "Containers rebuilded"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "logs-be")
        docker-compose logs -f backend
        ;;
    "logs-fe")
        docker-compose logs -f frontend
        ;;
    "shell-be")
        log_info "Abriendo shell en backend container..."
        docker-compose exec backend /bin/bash
        ;;
    "status")
        log_info "Estado de servicios:"
        docker-compose ps
        ;;
    "clean")
        log_warning "Limpiando containers y volúmenes..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        log_success "Limpieza completada"
        ;;
    "help"|*)
        show_help
        ;;
esac
