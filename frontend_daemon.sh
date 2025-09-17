#!/bin/bash
# Frontend Daemon - Mantiene el frontend siempre activo
# v1.0 - Sistema limpio desde cero

PROJECT_DIR="/home/admin-jairo/MeStore"
FRONTEND_DIR="$PROJECT_DIR/frontend"
FRONTEND_PID_FILE="/tmp/mestore_frontend.pid"
FRONTEND_LOG="$PROJECT_DIR/logs/frontend.log"
FRONTEND_HOST="192.168.1.137"
FRONTEND_PORT=5173

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_frontend() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] FRONTEND-DAEMON: $1${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] FRONTEND-DAEMON: $1" >> "$PROJECT_DIR/logs/frontend_daemon.log"
}

start_frontend() {
    log_frontend "Iniciando frontend en modo daemon..."

    # Ir al directorio del frontend
    cd "$FRONTEND_DIR" || exit 1

    # Verificar que node_modules existe
    if [ ! -d "node_modules" ]; then
        log_frontend "Instalando dependencias..."
        npm install
    fi

    # Limpiar puerto
    fuser -k $FRONTEND_PORT/tcp 2>/dev/null || true
    sleep 2

    # Iniciar frontend
    nohup npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" \
        > "$FRONTEND_LOG" 2>&1 &

    local pid=$!
    echo "$pid" > "$FRONTEND_PID_FILE"

    log_frontend "Frontend iniciado con PID: $pid"

    # Verificar que inició correctamente
    sleep 5
    if kill -0 "$pid" 2>/dev/null; then
        log_frontend "✅ Frontend corriendo exitosamente en $FRONTEND_HOST:$FRONTEND_PORT"
        return 0
    else
        log_frontend "❌ Error: Frontend falló al iniciar"
        return 1
    fi
}

stop_frontend() {
    if [ -f "$FRONTEND_PID_FILE" ]; then
        local pid=$(cat "$FRONTEND_PID_FILE")
        log_frontend "Deteniendo frontend PID: $pid"
        kill -TERM "$pid" 2>/dev/null
        sleep 3
        kill -9 "$pid" 2>/dev/null
        rm -f "$FRONTEND_PID_FILE"

        # Limpiar procesos vite huérfanos
        pkill -f "vite.*$FRONTEND_PORT" 2>/dev/null || true

        log_frontend "Frontend detenido"
    fi
}

is_frontend_running() {
    [ -f "$FRONTEND_PID_FILE" ] && kill -0 "$(cat "$FRONTEND_PID_FILE")" 2>/dev/null
}

case "$1" in
    start)
        if is_frontend_running; then
            log_frontend "Frontend ya está corriendo"
        else
            start_frontend
        fi
        ;;
    stop)
        stop_frontend
        ;;
    restart)
        stop_frontend
        sleep 2
        start_frontend
        ;;
    status)
        if is_frontend_running; then
            echo -e "${GREEN}Frontend está corriendo (PID: $(cat $FRONTEND_PID_FILE))${NC}"
        else
            echo -e "${RED}Frontend no está corriendo${NC}"
        fi
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac