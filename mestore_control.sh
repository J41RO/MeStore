#!/bin/bash
# MeStore Control - Script principal para manejar todo el sistema
# v1.0 - Sistema completo desde cero

PROJECT_DIR="/home/admin-jairo/MeStore"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BRIGHT_GREEN='\033[1;32m'
NC='\033[0m'

show_banner() {
    clear
    echo -e "${BRIGHT_GREEN}"
    echo "╔══════════════════════════════════════════════════════════════════════════╗"
    echo "║                            🛡️  MESTORE CONTROL v1.0                      ║"
    echo "║                          Sistema de Control Completo                    ║"
    echo "╚══════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

show_status() {
    echo -e "${CYAN}=== ESTADO DEL SISTEMA ===${NC}"

    # Backend
    if [ -f "/tmp/mestore_backend.pid" ] && kill -0 "$(cat /tmp/mestore_backend.pid)" 2>/dev/null; then
        echo -e "Backend:     ${GREEN}● CORRIENDO${NC} (PID: $(cat /tmp/mestore_backend.pid))"
    else
        echo -e "Backend:     ${RED}● DETENIDO${NC}"
    fi

    # Frontend
    if [ -f "/tmp/mestore_frontend.pid" ] && kill -0 "$(cat /tmp/mestore_frontend.pid)" 2>/dev/null; then
        echo -e "Frontend:    ${GREEN}● CORRIENDO${NC} (PID: $(cat /tmp/mestore_frontend.pid))"
    else
        echo -e "Frontend:    ${RED}● DETENIDO${NC}"
    fi

    # Backend Watchdog
    if [ -f "/tmp/backend_watchdog.pid" ] && kill -0 "$(cat /tmp/backend_watchdog.pid)" 2>/dev/null; then
        echo -e "Backend WD:  ${GREEN}● ACTIVO${NC} (PID: $(cat /tmp/backend_watchdog.pid))"
    else
        echo -e "Backend WD:  ${RED}● INACTIVO${NC}"
    fi

    # Frontend Watchdog
    if [ -f "/tmp/frontend_watchdog.pid" ] && kill -0 "$(cat /tmp/frontend_watchdog.pid)" 2>/dev/null; then
        echo -e "Frontend WD: ${GREEN}● ACTIVO${NC} (PID: $(cat /tmp/frontend_watchdog.pid))"
    else
        echo -e "Frontend WD: ${RED}● INACTIVO${NC}"
    fi

    echo ""
}

start_all() {
    echo -e "${YELLOW}🚀 Iniciando sistema completo...${NC}"

    echo "1. Iniciando Backend Daemon..."
    ./backend_daemon.sh start

    echo "2. Iniciando Frontend Daemon..."
    ./frontend_daemon.sh start

    echo "3. Iniciando Backend Watchdog..."
    ./backend_watchdog.sh start

    echo "4. Iniciando Frontend Watchdog..."
    ./frontend_watchdog.sh start

    echo "5. Configurando rotación de logs..."
    ./log_rotator.sh setup-cron

    sleep 3
    echo -e "${GREEN}✅ Sistema iniciado completamente${NC}"
    show_status
}

stop_all() {
    echo -e "${YELLOW}🛑 Deteniendo sistema completo...${NC}"

    echo "1. Deteniendo Watchdogs..."
    ./backend_watchdog.sh stop 2>/dev/null
    ./frontend_watchdog.sh stop 2>/dev/null

    echo "2. Deteniendo servicios..."
    ./backend_daemon.sh stop 2>/dev/null
    ./frontend_daemon.sh stop 2>/dev/null

    echo "3. Limpieza final..."
    pkill -f "vite.*5173" 2>/dev/null || true
    pkill -f "uvicorn.*8000" 2>/dev/null || true
    fuser -k 8000/tcp 2>/dev/null || true
    fuser -k 5173/tcp 2>/dev/null || true

    echo -e "${GREEN}✅ Sistema detenido completamente${NC}"
}

restart_all() {
    echo -e "${YELLOW}🔄 Reiniciando sistema completo...${NC}"
    stop_all
    sleep 3
    start_all
}

show_logs() {
    case "$2" in
        backend)
            echo -e "${BLUE}=== LOGS BACKEND ===${NC}"
            tail -f logs/backend.log
            ;;
        frontend)
            echo -e "${BLUE}=== LOGS FRONTEND ===${NC}"
            tail -f logs/frontend.log
            ;;
        backend-watchdog)
            echo -e "${BLUE}=== LOGS BACKEND WATCHDOG ===${NC}"
            tail -f logs/backend_watchdog.log
            ;;
        frontend-watchdog)
            echo -e "${BLUE}=== LOGS FRONTEND WATCHDOG ===${NC}"
            tail -f logs/frontend_watchdog.log
            ;;
        *)
            echo "Logs disponibles:"
            echo "  $0 logs backend           - Ver logs del backend"
            echo "  $0 logs frontend          - Ver logs del frontend"
            echo "  $0 logs backend-watchdog  - Ver logs del watchdog backend"
            echo "  $0 logs frontend-watchdog - Ver logs del watchdog frontend"
            ;;
    esac
}

show_menu() {
    show_banner
    show_status

    echo -e "${CYAN}=== OPCIONES DISPONIBLES ===${NC}"
    echo "1. Iniciar sistema completo"
    echo "2. Detener sistema completo"
    echo "3. Reiniciar sistema completo"
    echo "4. Ver logs backend"
    echo "5. Ver logs frontend"
    echo "6. Ver logs backend watchdog"
    echo "7. Ver logs frontend watchdog"
    echo "8. Estadísticas de logs"
    echo "9. Rotar logs manualmente"
    echo "0. Salir"
    echo ""
    echo -e "${YELLOW}Selecciona una opción:${NC} "
    read -r option

    case $option in
        1) start_all ;;
        2) stop_all ;;
        3) restart_all ;;
        4) show_logs logs backend ;;
        5) show_logs logs frontend ;;
        6) show_logs logs backend-watchdog ;;
        7) show_logs logs frontend-watchdog ;;
        8) ./log_rotator.sh stats ;;
        9) ./log_rotator.sh rotate ;;
        0) exit 0 ;;
        *) echo -e "${RED}Opción inválida${NC}"; sleep 2; show_menu ;;
    esac
}

case "$1" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart_all
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$@"
        ;;
    menu)
        show_menu
        ;;
    *)
        echo "MeStore Control v1.0 - Sistema de control completo"
        echo ""
        echo "Uso: $0 {start|stop|restart|status|logs|menu}"
        echo ""
        echo "  start   - Iniciar sistema completo (daemons + watchdogs)"
        echo "  stop    - Detener sistema completo"
        echo "  restart - Reiniciar sistema completo"
        echo "  status  - Mostrar estado de todos los servicios"
        echo "  logs    - Ver logs (backend|frontend|backend-watchdog|frontend-watchdog)"
        echo "  menu    - Mostrar menú interactivo"
        echo ""
        echo "Para logs individuales:"
        echo "  ./backend_watchdog.sh logs     - Logs watchdog backend en tiempo real"
        echo "  ./frontend_watchdog.sh logs    - Logs watchdog frontend en tiempo real"
        exit 1
        ;;
esac