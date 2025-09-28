#!/bin/bash
# ============================================================================
# 🐍 MESTOCKER BACKEND MANAGER
# Script moderno para gestión completa del backend FastAPI
# ============================================================================

set -e

# Colores y emojis
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
BRIGHT_GREEN='\033[1;32m'
BRIGHT_RED='\033[1;31m'
BRIGHT_CYAN='\033[1;36m'
BRIGHT_YELLOW='\033[1;33m'
NC='\033[0m'

# Emojis
ROCKET="🚀"
STOP="🛑"
RELOAD="🔄"
LOGS="📋"
STATUS="📊"
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
INFO="ℹ️"
GEAR="⚙️"
PYTHON="🐍"

# Variables de configuración
PROJECT_DIR="/home/admin-jairo/MeStore"
BACKEND_HOST="192.168.1.137"
BACKEND_PORT=8000
LOG_DIR="$PROJECT_DIR/logs"
BACKEND_LOG="$LOG_DIR/backend.log"
PID_FILE="/tmp/mestocker_backend.pid"

# Cargar configuración externa si existe
CONFIG_FILE="$PROJECT_DIR/config.env"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

# Crear directorio de logs
mkdir -p "$LOG_DIR"
touch "$BACKEND_LOG"

# Función para mostrar header
show_header() {
    clear
    echo -e "${BRIGHT_CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BRIGHT_CYAN}║                        ${PYTHON} MESTOCKER BACKEND MANAGER                       ║${NC}"
    echo -e "${BRIGHT_CYAN}║                         FastAPI Development Server                           ║${NC}"
    echo -e "${BRIGHT_CYAN}╠═══════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║ Host: ${WHITE}$BACKEND_HOST:$BACKEND_PORT${NC} ${GRAY}|${NC} Log: ${WHITE}$BACKEND_LOG${NC} ║"
    echo -e "${BRIGHT_CYAN}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Función para verificar si el backend está corriendo
is_backend_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            if ps -p "$pid" -o cmd --no-headers | grep -q "uvicorn"; then
                return 0
            fi
        fi
        rm -f "$PID_FILE"
    fi
    return 1
}

# Función para obtener uptime del proceso
get_uptime() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            local start_time=$(ps -o lstart= -p "$pid" 2>/dev/null)
            if [ -n "$start_time" ]; then
                local uptime_seconds=$(( $(date +%s) - $(date -d "$start_time" +%s 2>/dev/null || echo 0) ))
                local hours=$((uptime_seconds / 3600))
                local minutes=$(((uptime_seconds % 3600) / 60))
                echo "${hours}h ${minutes}m"
            else
                echo "N/A"
            fi
        fi
    fi
}

# Función para mostrar estado del backend
show_status() {
    if is_backend_running; then
        local pid=$(cat "$PID_FILE")
        local uptime=$(get_uptime)
        echo -e "${BRIGHT_GREEN}┌─ ${PYTHON} BACKEND STATUS ${CHECK} ACTIVO ──────────────────────────────────────────┐${NC}"
        echo -e "${GREEN}│ PID: ${WHITE}$pid${GREEN} │ Uptime: ${WHITE}$uptime${GREEN} │ URL: ${BRIGHT_CYAN}http://$BACKEND_HOST:$BACKEND_PORT${GREEN} │${NC}"
        echo -e "${GREEN}│ API Docs: ${BRIGHT_CYAN}http://$BACKEND_HOST:$BACKEND_PORT/docs${GREEN}                            │${NC}"
        echo -e "${BRIGHT_GREEN}└──────────────────────────────────────────────────────────────────────────────────┘${NC}"
    else
        echo -e "${BRIGHT_RED}┌─ ${PYTHON} BACKEND STATUS ${CROSS} INACTIVO ──────────────────────────────────────────┐${NC}"
        echo -e "${RED}│ El servidor FastAPI no está ejecutándose                                     │${NC}"
        echo -e "${RED}│ Use la opción 1 para iniciar el backend                                      │${NC}"
        echo -e "${BRIGHT_RED}└──────────────────────────────────────────────────────────────────────────────────┘${NC}"
    fi
    echo ""
}

# Función para verificar puerto disponible
check_port() {
    if command -v lsof >/dev/null 2>&1; then
        if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${RED}${CROSS} Puerto $BACKEND_PORT ocupado por otro proceso${NC}"
            echo -e "${YELLOW}Procesos usando el puerto:${NC}"
            lsof -Pi :$BACKEND_PORT -sTCP:LISTEN
            return 1
        fi
    fi
    return 0
}

# Función para detener backend
stop_backend() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        echo -e "${YELLOW}${STOP} Deteniendo backend (PID: $pid)...${NC}"

        # Intentar terminar amablemente
        kill "$pid" 2>/dev/null
        sleep 2

        # Forzar si es necesario
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚡ Forzando terminación...${NC}"
            kill -9 "$pid" 2>/dev/null
            sleep 1
        fi

        rm -f "$PID_FILE"
        echo -e "${GREEN}${CHECK} Backend detenido${NC}"
    else
        echo -e "${CYAN}${INFO} Backend no estaba corriendo${NC}"
    fi

    # Limpiar procesos por nombre
    pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
    pkill -f "python.*uvicorn" 2>/dev/null || true

    # Limpiar puerto si fuser está disponible
    if command -v fuser >/dev/null 2>&1; then
        echo -e "${CYAN}🧹 Limpiando puerto $BACKEND_PORT...${NC}"
        fuser -k $BACKEND_PORT/tcp 2>/dev/null || true
        sleep 1
    fi
}

# Función para iniciar backend
start_backend() {
    echo -e "${CYAN}${ROCKET} Iniciando backend...${NC}"

    # Verificar directorio
    if [ ! -d "$PROJECT_DIR/app" ]; then
        echo -e "${RED}${CROSS} Error: Directorio app/ no encontrado en $PROJECT_DIR${NC}"
        return 1
    fi

    # Verificar puerto disponible
    if ! check_port; then
        echo -e "${RED}${CROSS} Abortando inicio del backend${NC}"
        return 1
    fi

    # Cambiar al directorio del proyecto
    cd "$PROJECT_DIR" || return 1

    # Activar entorno virtual
    if [ -f ".venv/bin/activate" ]; then
        echo -e "${CYAN}${GEAR} Activando entorno virtual...${NC}"
        source .venv/bin/activate
    else
        echo -e "${YELLOW}${WARNING} Entorno virtual no encontrado${NC}"
    fi

    # Verificar dependencias
    echo -e "${CYAN}📦 Verificando dependencias...${NC}"
    python -c "import fastapi, uvicorn" 2>/dev/null || {
        echo -e "${RED}${CROSS} Error: FastAPI/Uvicorn no instalados${NC}"
        return 1
    }

    # Iniciar backend
    echo -e "${CYAN}${ROCKET} Iniciando uvicorn en $BACKEND_HOST:$BACKEND_PORT...${NC}"

    nohup python -m uvicorn app.main:app \
        --reload \
        --reload-dir ./app \
        --host "$BACKEND_HOST" \
        --port "$BACKEND_PORT" \
        > "$BACKEND_LOG" 2>&1 &

    local pid=$!
    echo "$pid" > "$PID_FILE"
    echo -e "${GREEN}🆔 PID: $pid${NC}"

    # Health check
    echo -e "${CYAN}🏥 Verificando que el servidor inicie...${NC}"
    local retries=0
    local max_retries=15

    while [ $retries -lt $max_retries ]; do
        if curl -f -s --connect-timeout 2 --max-time 5 "http://$BACKEND_HOST:$BACKEND_PORT/health" >/dev/null 2>&1; then
            echo -e "${GREEN}${CHECK} Backend iniciado correctamente${NC}"
            echo -e "${GREEN}🌐 URL: ${BRIGHT_CYAN}http://$BACKEND_HOST:$BACKEND_PORT${NC}"
            echo -e "${GREEN}📚 Docs: ${BRIGHT_CYAN}http://$BACKEND_HOST:$BACKEND_PORT/docs${NC}"
            return 0
        fi

        retries=$((retries + 1))
        echo -ne "${CYAN}.${NC}"
        sleep 1
    done

    echo -e "\n${RED}${CROSS} Backend falló al iniciar después de $max_retries intentos${NC}"
    stop_backend
    return 1
}

# Función para reload backend
reload_backend() {
    echo -e "${BRIGHT_YELLOW}${RELOAD} Recargando backend...${NC}"
    stop_backend
    sleep 2
    start_backend
}

# Función para reset completo (detener + limpiar logs + iniciar)
reset_backend() {
    echo -e "${BRIGHT_YELLOW}🔥 Reset completo del backend...${NC}"
    stop_backend
    echo -e "${CYAN}🧹 Limpiando logs...${NC}"
    > "$BACKEND_LOG"  # Vaciar log
    sleep 2
    start_backend
}

# Función para mostrar logs en tiempo real
show_logs() {
    echo -e "${BRIGHT_CYAN}┌─ ${LOGS} LOGS BACKEND EN TIEMPO REAL ─────────────────────────────────────────────┐${NC}"
    echo -e "${BRIGHT_CYAN}│ Presiona Ctrl+C para volver al menú                                         │${NC}"
    echo -e "${BRIGHT_CYAN}└──────────────────────────────────────────────────────────────────────────────────┘${NC}"
    echo ""

    tail -f "$BACKEND_LOG" 2>/dev/null | while IFS= read -r line; do
        local timestamp="${GRAY}[$(date '+%H:%M:%S')]${NC}"

        # Colorear según contenido
        if [[ "$line" == *"INFO"* ]]; then
            echo -e "$timestamp ${BRIGHT_GREEN}[INFO]${NC} ${GREEN}$line${NC}"
        elif [[ "$line" == *"ERROR"* ]] || [[ "$line" == *"error"* ]]; then
            echo -e "$timestamp ${BRIGHT_RED}[ERROR]${NC} ${RED}$line${NC}"
        elif [[ "$line" == *"WARNING"* ]] || [[ "$line" == *"warning"* ]]; then
            echo -e "$timestamp ${BRIGHT_YELLOW}[WARN]${NC} ${YELLOW}$line${NC}"
        elif [[ "$line" == *"DEBUG"* ]]; then
            echo -e "$timestamp ${PURPLE}[DEBUG]${NC} ${GRAY}$line${NC}"
        elif [[ "$line" == *"started server"* ]] || [[ "$line" == *"Application startup"* ]]; then
            echo -e "$timestamp ${BRIGHT_GREEN}[START]${NC} ${BRIGHT_GREEN}$line${NC}"
        else
            echo -e "$timestamp ${CYAN}[BACKEND]${NC} $line"
        fi
    done || echo -e "${RED}${CROSS} Log no encontrado: $BACKEND_LOG${NC}"
}

# Función para manejar Ctrl+C
handle_interrupt() {
    echo -e "\n${CYAN}🔄 Regresando al menú...${NC}"
    sleep 1
    show_menu
}

# Función para mostrar menú principal
show_menu() {
    trap handle_interrupt SIGINT

    while true; do
        show_header
        show_status

        echo -e "${BRIGHT_CYAN}🎛️  OPCIONES DISPONIBLES${NC}"
        echo ""
        echo -e "${BRIGHT_GREEN}┌─ GESTIÓN DEL BACKEND ──────────────────┐${NC}"
        echo -e "${GREEN}│ ${ROCKET} 1  Iniciar Backend                │${NC}"
        echo -e "${YELLOW}│ ${RELOAD} 2  Reload Backend                 │${NC}"
        echo -e "${PURPLE}│ 🔥 3  Reset Completo (+ limpiar logs) │${NC}"
        echo -e "${RED}│ ${STOP} 4  Detener Backend                │${NC}"
        echo -e "${BRIGHT_GREEN}└─────────────────────────────────────────┘${NC}"
        echo ""
        echo -e "${BRIGHT_BLUE}┌─ MONITOREO ────────────────────────────┐${NC}"
        echo -e "${BLUE}│ ${LOGS} 5  Ver Logs en Tiempo Real        │${NC}"
        echo -e "${BLUE}│ ${STATUS} 6  Actualizar Estado              │${NC}"
        echo -e "${BRIGHT_BLUE}└─────────────────────────────────────────┘${NC}"
        echo ""
        echo -e "${BRIGHT_RED}┌─ SISTEMA ──────────────────────────────┐${NC}"
        echo -e "${WHITE}│ 🚪 0  Salir                            │${NC}"
        echo -e "${BRIGHT_RED}└─────────────────────────────────────────┘${NC}"
        echo ""
        echo -ne "${BRIGHT_CYAN}💻 Selecciona una opción [0-6]: ${NC}"

        read -r option

        case "$option" in
            1)
                echo ""
                stop_backend  # Detener si existe
                start_backend
                echo ""
                echo -e "${CYAN}${INFO} Presiona Enter para continuar...${NC}"
                read -r
                ;;
            2)
                echo ""
                reload_backend
                echo ""
                echo -e "${CYAN}${INFO} Presiona Enter para continuar...${NC}"
                read -r
                ;;
            3)
                echo ""
                reset_backend
                echo ""
                echo -e "${CYAN}${INFO} Presiona Enter para continuar...${NC}"
                read -r
                ;;
            4)
                echo ""
                stop_backend
                echo ""
                echo -e "${CYAN}${INFO} Presiona Enter para continuar...${NC}"
                read -r
                ;;
            5)
                clear
                show_logs
                ;;
            6)
                # Solo refresh del menú
                ;;
            0)
                echo ""
                echo -e "${BRIGHT_RED}${STOP} Deteniendo backend y saliendo...${NC}"
                stop_backend
                echo ""
                echo -e "${BRIGHT_GREEN}👋 ¡Hasta luego!${NC}"
                exit 0
                ;;
            *)
                echo ""
                echo -e "${BRIGHT_RED}${CROSS} Opción inválida. Usa 0-6${NC}"
                sleep 2
                ;;
        esac
    done
}

# Función principal
main() {
    # Verificar directorio del proyecto
    if [ ! -d "$PROJECT_DIR" ]; then
        echo -e "${RED}${CROSS} Error: Directorio del proyecto no encontrado: $PROJECT_DIR${NC}"
        exit 1
    fi

    # Mostrar menú
    show_menu
}

# Ejecutar función principal
main "$@"