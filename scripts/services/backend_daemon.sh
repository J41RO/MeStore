#!/bin/bash
# Backend Daemon - Mantiene el backend siempre activo
# v1.0 - Sistema limpio desde cero

PROJECT_DIR="/home/admin-jairo/MeStore"
BACKEND_PID_FILE="/tmp/mestore_backend.pid"
BACKEND_LOG="$PROJECT_DIR/logs/backend.log"
BACKEND_HOST="192.168.1.137"
BACKEND_PORT=8000

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log_backend() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] BACKEND-DAEMON: $1${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] BACKEND-DAEMON: $1" >> "$PROJECT_DIR/logs/backend_daemon.log"
}

start_backend() {
    log_backend "Iniciando backend en modo daemon..."

    # Ir al directorio del proyecto
    cd "$PROJECT_DIR" || exit 1

    # Activar entorno virtual si existe
    [ -f ".venv/bin/activate" ] && source .venv/bin/activate

    # Limpiar puerto
    fuser -k $BACKEND_PORT/tcp 2>/dev/null || true
    sleep 2

    # Iniciar backend
    nohup python -m uvicorn app.main:app \
        --reload \
        --reload-dir ./app \
        --host "$BACKEND_HOST" \
        --port "$BACKEND_PORT" \
        > "$BACKEND_LOG" 2>&1 &

    local pid=$!
    echo "$pid" > "$BACKEND_PID_FILE"

    log_backend "Backend iniciado con PID: $pid"

    # Verificar que inició correctamente
    sleep 5
    if kill -0 "$pid" 2>/dev/null; then
        log_backend "✅ Backend corriendo exitosamente en $BACKEND_HOST:$BACKEND_PORT"
        return 0
    else
        log_backend "❌ Error: Backend falló al iniciar"
        return 1
    fi
}

stop_backend() {
    if [ -f "$BACKEND_PID_FILE" ]; then
        local pid=$(cat "$BACKEND_PID_FILE")
        log_backend "Deteniendo backend PID: $pid"
        kill -TERM "$pid" 2>/dev/null
        sleep 3
        kill -9 "$pid" 2>/dev/null
        rm -f "$BACKEND_PID_FILE"
        log_backend "Backend detenido"
    fi
}

is_backend_running() {
    [ -f "$BACKEND_PID_FILE" ] && kill -0 "$(cat "$BACKEND_PID_FILE")" 2>/dev/null
}

case "$1" in
    start)
        if is_backend_running; then
            log_backend "Backend ya está corriendo"
        else
            start_backend
        fi
        ;;
    stop)
        stop_backend
        ;;
    restart)
        stop_backend
        sleep 2
        start_backend
        ;;
    status)
        if is_backend_running; then
            echo -e "${GREEN}Backend está corriendo (PID: $(cat $BACKEND_PID_FILE))${NC}"
        else
            echo -e "${RED}Backend no está corriendo${NC}"
        fi
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
