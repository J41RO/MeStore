#!/bin/bash
# Frontend Watchdog - Monitorea frontend y detecta crashes en logs
# v1.0 - Con monitoreo de logs y detección de caídas

PROJECT_DIR="/home/admin-jairo/MeStore"
FRONTEND_DAEMON="$PROJECT_DIR/frontend_daemon.sh"
FRONTEND_PID_FILE="/tmp/mestore_frontend.pid"
FRONTEND_LOG="$PROJECT_DIR/logs/frontend.log"
WATCHDOG_PID_FILE="/tmp/frontend_watchdog.pid"
WATCHDOG_LOG="$PROJECT_DIR/logs/frontend_watchdog.log"
FRONTEND_HOST="192.168.1.137"
FRONTEND_PORT=5173

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
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
        "CRASH") color="$BLUE" ;;
    esac

    echo -e "${color}[$timestamp] [$level] FRONTEND-WATCHDOG: $message${NC}"
    echo "[$timestamp] [$level] FRONTEND-WATCHDOG: $message" >> "$WATCHDOG_LOG"
}

cleanup_zombies() {
    local killed=0

    # Limpiar procesos vite huérfanos
    local zombie_pids=$(ps aux | grep "[v]ite.*--port.*$FRONTEND_PORT" | grep -v $(cat "$FRONTEND_PID_FILE" 2>/dev/null || echo "0") | awk '{print $2}')
    if [ -n "$zombie_pids" ]; then
        echo "$zombie_pids" | xargs -r kill -9 2>/dev/null
        killed=$((killed + $(echo "$zombie_pids" | wc -w)))
    fi

    # Limpiar procesos node huérfanos en el puerto
    local port_pids=$(lsof -ti:$FRONTEND_PORT 2>/dev/null | grep -v $(cat "$FRONTEND_PID_FILE" 2>/dev/null || echo "0"))
    if [ -n "$port_pids" ]; then
        echo "$port_pids" | xargs -r kill -9 2>/dev/null
        killed=$((killed + $(echo "$port_pids" | wc -w)))
    fi

    [ $killed -gt 0 ] && log_watchdog "INFO" "🧹 Limpieza: $killed procesos zombie eliminados"
}

check_frontend_health() {
    # 1. Verificar si el proceso existe
    if [ ! -f "$FRONTEND_PID_FILE" ] || ! kill -0 "$(cat "$FRONTEND_PID_FILE")" 2>/dev/null; then
        return 1
    fi

    # 2. Verificar si responde HTTP
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "http://$FRONTEND_HOST:$FRONTEND_PORT" 2>/dev/null)
    if [ "$http_code" = "200" ]; then
        return 0
    else
        return 2
    fi
}

monitor_frontend_logs() {
    # Monitorear los logs en busca de "Killed" u otros errores críticos
    if [ -f "$FRONTEND_LOG" ]; then
        # Buscar "Killed" en las últimas 10 líneas
        local killed_count=$(tail -n 10 "$FRONTEND_LOG" 2>/dev/null | grep -c "Killed" || echo "0")
        if [ "$killed_count" -gt 0 ]; then
            log_watchdog "CRASH" "💥 Detectado 'Killed' en logs del frontend - agente externo terminó el proceso"
            return 3
        fi

        # Buscar errores críticos
        local error_count=$(tail -n 5 "$FRONTEND_LOG" 2>/dev/null | grep -c -E "(ERROR|Error:|ENOENT|EADDRINUSE)" || echo "0")
        if [ "$error_count" -gt 0 ]; then
            log_watchdog "WARN" "⚠️ Detectados errores en logs del frontend"
            return 4
        fi
    fi
    return 0
}

restart_frontend() {
    local reason="$1"
    log_watchdog "WARN" "🔄 Reiniciando frontend ($reason)..."

    # Cleanup antes de reiniciar
    cleanup_zombies

    # Reiniciar usando el daemon
    "$FRONTEND_DAEMON" restart

    # Verificar que reinició correctamente
    sleep 8
    if check_frontend_health; then
        log_watchdog "INFO" "✅ Frontend reiniciado exitosamente"
        # Sonido de recuperación
        echo -e "\a" 2>/dev/null || true
    else
        log_watchdog "ERROR" "❌ Fallo al reiniciar frontend"
        # Sonido de error
        for i in {1..3}; do echo -e "\a"; sleep 0.2; done 2>/dev/null || true
    fi
}

start_watchdog() {
    echo $$ > "$WATCHDOG_PID_FILE"
    log_watchdog "INFO" "🐕 Frontend Watchdog iniciado (PID: $$)"

    # Iniciar frontend si no está corriendo
    if ! check_frontend_health; then
        log_watchdog "INFO" "🚀 Iniciando frontend..."
        "$FRONTEND_DAEMON" start
        sleep 5
    fi

    # Bucle principal de monitoreo
    while [ -f "$WATCHDOG_PID_FILE" ]; do
        # Verificar salud del proceso
        check_frontend_health
        local health_status=$?

        # Verificar logs por crashes
        monitor_frontend_logs
        local log_status=$?

        case $health_status in
            0)  # Saludable
                case $log_status in
                    0)  # Sin problemas en logs
                        local pid=$(cat "$FRONTEND_PID_FILE" 2>/dev/null)
                        local uptime=$(ps --no-headers -o etime -p "$pid" 2>/dev/null | tr -d ' ' || echo "N/A")
                        log_watchdog "HEALTH" "💚 Frontend OK (uptime: $uptime)"
                        ;;
                    3)  # Detectado "Killed"
                        log_watchdog "ERROR" "💀 Frontend fue terminado por agente externo"
                        restart_frontend "proceso terminado"
                        ;;
                    4)  # Errores en logs
                        log_watchdog "WARN" "⚠️ Errores detectados en logs pero proceso activo"
                        ;;
                esac
                ;;
            1)  # Proceso no existe
                log_watchdog "ERROR" "❌ Frontend no está corriendo - reiniciando..."
                restart_frontend "proceso no existe"
                ;;
            2)  # Proceso existe pero no responde
                log_watchdog "WARN" "⚠️ Frontend no responde HTTP - reiniciando..."
                restart_frontend "no responde HTTP"
                ;;
        esac

        # Limpieza periódica de zombies
        cleanup_zombies

        # Esperar 60 segundos antes de la siguiente verificación (menos agresivo)
        sleep 60
    done

    log_watchdog "INFO" "🛑 Frontend Watchdog detenido"
}

stop_watchdog() {
    if [ -f "$WATCHDOG_PID_FILE" ]; then
        local pid=$(cat "$WATCHDOG_PID_FILE")
        log_watchdog "INFO" "Deteniendo Frontend Watchdog (PID: $pid)"
        rm -f "$WATCHDOG_PID_FILE"
        kill -TERM "$pid" 2>/dev/null
    fi
}

case "$1" in
    start)
        if [ -f "$WATCHDOG_PID_FILE" ] && kill -0 "$(cat "$WATCHDOG_PID_FILE")" 2>/dev/null; then
            echo "Frontend Watchdog ya está corriendo"
        else
            start_watchdog &
        fi
        ;;
    stop)
        stop_watchdog
        ;;
    status)
        if [ -f "$WATCHDOG_PID_FILE" ] && kill -0 "$(cat "$WATCHDOG_PID_FILE")" 2>/dev/null; then
            echo -e "${GREEN}Frontend Watchdog corriendo (PID: $(cat $WATCHDOG_PID_FILE))${NC}"
        else
            echo -e "${RED}Frontend Watchdog no está corriendo${NC}"
        fi
        ;;
    logs)
        echo -e "${BLUE}=== FRONTEND LOGS (Solo Frontend) ===${NC}"
        echo -e "${CYAN}Watchdog Frontend iniciado - Monitoreando...${NC}"
        tail -f "$PROJECT_DIR/logs/frontend.log" 2>/dev/null | while IFS= read -r line; do
            timestamp="${CYAN}[$(date '+%H:%M:%S')]${NC}"
            echo -e "$timestamp ${BLUE}FRONTEND:${NC} $line"
        done
        ;;
    *)
        echo "Uso: $0 {start|stop|status|logs}"
        exit 1
        ;;
esac