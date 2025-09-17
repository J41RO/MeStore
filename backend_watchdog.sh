#!/bin/bash
# Backend Watchdog - Monitorea y mantiene el backend saludable
# v1.0 - Con limpieza de zombies y logs detallados

PROJECT_DIR="/home/admin-jairo/MeStore"
BACKEND_DAEMON="$PROJECT_DIR/backend_daemon.sh"
BACKEND_PID_FILE="/tmp/mestore_backend.pid"
WATCHDOG_PID_FILE="/tmp/backend_watchdog.pid"
WATCHDOG_LOG="$PROJECT_DIR/logs/backend_watchdog.log"
BACKEND_HOST="192.168.1.137"
BACKEND_PORT=8000

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_watchdog() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case "$level" in
        "INFO") color="$GREEN" ;;
        "WARN") color="$YELLOW" ;;
        "ERROR") color="$RED" ;;
        "HEALTH") color="$CYAN" ;;
    esac

    echo -e "${color}[$timestamp] [$level] BACKEND-WATCHDOG: $message${NC}"
    echo "[$timestamp] [$level] BACKEND-WATCHDOG: $message" >> "$WATCHDOG_LOG"
}

cleanup_zombies() {
    local killed=0

    # Limpiar procesos uvicorn huérfanos
    local zombie_pids=$(ps aux | grep "[u]vicorn.*app.main:app" | grep -v $(cat "$BACKEND_PID_FILE" 2>/dev/null || echo "0") | awk '{print $2}')
    if [ -n "$zombie_pids" ]; then
        echo "$zombie_pids" | xargs -r kill -9 2>/dev/null
        killed=$((killed + $(echo "$zombie_pids" | wc -w)))
    fi

    # Limpiar procesos Python huérfanos en el puerto
    local port_pids=$(lsof -ti:$BACKEND_PORT 2>/dev/null | grep -v $(cat "$BACKEND_PID_FILE" 2>/dev/null || echo "0"))
    if [ -n "$port_pids" ]; then
        echo "$port_pids" | xargs -r kill -9 2>/dev/null
        killed=$((killed + $(echo "$port_pids" | wc -w)))
    fi

    [ $killed -gt 0 ] && log_watchdog "INFO" "🧹 Limpieza: $killed procesos zombie eliminados"
}

check_backend_health() {
    # 1. Verificar si el proceso existe
    if [ ! -f "$BACKEND_PID_FILE" ] || ! kill -0 "$(cat "$BACKEND_PID_FILE")" 2>/dev/null; then
        return 1
    fi

    # 2. Verificar si responde HTTP
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "http://$BACKEND_HOST:$BACKEND_PORT/health" 2>/dev/null)
    if [ "$http_code" = "200" ]; then
        return 0
    else
        return 2
    fi
}

restart_backend() {
    log_watchdog "WARN" "🔄 Reiniciando backend..."

    # Cleanup antes de reiniciar
    cleanup_zombies

    # Reiniciar usando el daemon
    "$BACKEND_DAEMON" restart

    # Verificar que reinició correctamente
    sleep 8
    if check_backend_health; then
        log_watchdog "INFO" "✅ Backend reiniciado exitosamente"
        # Sonido de recuperación
        echo -e "\a" 2>/dev/null || true
    else
        log_watchdog "ERROR" "❌ Fallo al reiniciar backend"
        # Sonido de error
        for i in {1..3}; do echo -e "\a"; sleep 0.2; done 2>/dev/null || true
    fi
}

start_watchdog() {
    echo $$ > "$WATCHDOG_PID_FILE"
    log_watchdog "INFO" "🐕 Backend Watchdog iniciado (PID: $$)"

    # Iniciar backend si no está corriendo
    if ! check_backend_health; then
        log_watchdog "INFO" "🚀 Iniciando backend..."
        "$BACKEND_DAEMON" start
        sleep 5
    fi

    # Bucle principal de monitoreo
    while [ -f "$WATCHDOG_PID_FILE" ]; do
        check_backend_health
        local health_status=$?

        case $health_status in
            0)  # Saludable
                local pid=$(cat "$BACKEND_PID_FILE" 2>/dev/null)
                local uptime=$(ps --no-headers -o etime -p "$pid" 2>/dev/null | tr -d ' ' || echo "N/A")
                log_watchdog "HEALTH" "💚 Backend OK (uptime: $uptime)"
                ;;
            1)  # Proceso no existe
                log_watchdog "ERROR" "❌ Backend no está corriendo - reiniciando..."
                restart_backend
                ;;
            2)  # Proceso existe pero no responde
                log_watchdog "WARN" "⚠️ Backend no responde HTTP - reiniciando..."
                restart_backend
                ;;
        esac

        # Limpieza periódica de zombies
        cleanup_zombies

        # Esperar 60 segundos antes de la siguiente verificación (menos agresivo)
        sleep 60
    done

    log_watchdog "INFO" "🛑 Backend Watchdog detenido"
}

stop_watchdog() {
    if [ -f "$WATCHDOG_PID_FILE" ]; then
        local pid=$(cat "$WATCHDOG_PID_FILE")
        log_watchdog "INFO" "Deteniendo Backend Watchdog (PID: $pid)"
        rm -f "$WATCHDOG_PID_FILE"
        kill -TERM "$pid" 2>/dev/null
    fi
}

case "$1" in
    start)
        if [ -f "$WATCHDOG_PID_FILE" ] && kill -0 "$(cat "$WATCHDOG_PID_FILE")" 2>/dev/null; then
            echo "Backend Watchdog ya está corriendo"
        else
            start_watchdog &
        fi
        ;;
    stop)
        stop_watchdog
        ;;
    status)
        if [ -f "$WATCHDOG_PID_FILE" ] && kill -0 "$(cat "$WATCHDOG_PID_FILE")" 2>/dev/null; then
            echo -e "${GREEN}Backend Watchdog corriendo (PID: $(cat $WATCHDOG_PID_FILE))${NC}"
        else
            echo -e "${RED}Backend Watchdog no está corriendo${NC}"
        fi
        ;;
    logs)
        echo -e "${GREEN}=== BACKEND LOGS (Solo Backend) ===${NC}"
        echo -e "${CYAN}Watchdog Backend iniciado - Monitoreando...${NC}"
        tail -f "$PROJECT_DIR/logs/backend.log" 2>/dev/null | while IFS= read -r line; do
            timestamp="${CYAN}[$(date '+%H:%M:%S')]${NC}"
            echo -e "$timestamp ${GREEN}BACKEND:${NC} $line"
        done
        ;;
    *)
        echo "Uso: $0 {start|stop|status|logs}"
        exit 1
        ;;
esac