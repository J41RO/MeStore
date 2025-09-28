#!/bin/bash
# ============================================================================
# ⚛️ MESTOCKER FRONTEND MANAGER
# Script moderno para gestión completa del frontend React+Vite
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
REACT="⚛️"

# Variables de configuración
PROJECT_DIR="/home/admin-jairo/MeStore"
FRONTEND_HOST="192.168.1.137"
FRONTEND_PORT=5173
LOG_DIR="$PROJECT_DIR/logs"
FRONTEND_LOG="$LOG_DIR/frontend.log"
PID_FILE="/tmp/mestocker_frontend.pid"

# Cargar configuración externa si existe
CONFIG_FILE="$PROJECT_DIR/config.env"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

# Crear directorio de logs
mkdir -p "$LOG_DIR"
touch "$FRONTEND_LOG"

# Función para mostrar header
show_header() {
    clear
    echo -e "${BRIGHT_CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BRIGHT_CYAN}║                        ${REACT} MESTOCKER FRONTEND MANAGER                      ║${NC}"
    echo -e "${BRIGHT_CYAN}║                           React + Vite Development                           ║${NC}"
    echo -e "${BRIGHT_CYAN}╠═══════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║ Host: ${WHITE}$FRONTEND_HOST:$FRONTEND_PORT${NC} ${GRAY}|${NC} Log: ${WHITE}$FRONTEND_LOG${NC} ║"
    echo -e "${BRIGHT_CYAN}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Función para verificar si el frontend está corriendo
is_frontend_running() {
    # Verificar por PID file
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            if ps -p "$pid" -o cmd --no-headers | grep -q "vite"; then
                return 0
            fi
        fi
        rm -f "$PID_FILE"
    fi

    # Verificar por proceso de vite en puerto específico
    if pgrep -f "vite.*--port.*$FRONTEND_PORT" > /dev/null 2>&1; then
        return 0
    fi

    # Verificar por proceso de vite con host específico
    if pgrep -f "vite.*--host.*$FRONTEND_HOST.*--port.*$FRONTEND_PORT" > /dev/null 2>&1; then
        return 0
    fi

    # Verificar proceso node que tenga vite
    if pgrep -f "node.*vite" > /dev/null 2>&1; then
        return 0
    fi

    return 1
}

# Función para obtener PID real del proceso vite
get_real_pid() {
    # Buscar por varios patrones
    local real_pid=$(pgrep -f "vite.*--port.*$FRONTEND_PORT" | head -1)

    if [ -z "$real_pid" ]; then
        real_pid=$(pgrep -f "vite.*--host.*$FRONTEND_HOST.*--port.*$FRONTEND_PORT" | head -1)
    fi

    if [ -z "$real_pid" ]; then
        real_pid=$(pgrep -f "node.*vite" | head -1)
    fi

    if [ -n "$real_pid" ]; then
        echo "$real_pid" > "$PID_FILE"
        echo "$real_pid"
    elif [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    fi
}

# Función para obtener uptime del proceso
get_uptime() {
    local pid=$(get_real_pid)
    if [ -n "$pid" ] && ps -p "$pid" > /dev/null 2>&1; then
        local start_time=$(ps -o lstart= -p "$pid" 2>/dev/null)
        if [ -n "$start_time" ]; then
            local uptime_seconds=$(( $(date +%s) - $(date -d "$start_time" +%s 2>/dev/null || echo 0) ))
            local hours=$((uptime_seconds / 3600))
            local minutes=$(((uptime_seconds % 3600) / 60))
            echo "${hours}h ${minutes}m"
        else
            echo "N/A"
        fi
    else
        echo "N/A"
    fi
}

# Función para mostrar estado del frontend
show_status() {
    if is_frontend_running; then
        local pid=$(get_real_pid)
        local uptime=$(get_uptime)
        echo -e "${BRIGHT_GREEN}┌─ ${REACT} FRONTEND STATUS ${CHECK} ACTIVO ─────────────────────────────────────────┐${NC}"
        echo -e "${GREEN}│ PID: ${WHITE}$pid${GREEN} │ Uptime: ${WHITE}$uptime${GREEN} │ URL: ${BRIGHT_CYAN}http://$FRONTEND_HOST:$FRONTEND_PORT${GREEN} │${NC}"
        echo -e "${GREEN}│ Vite HMR activo para desarrollo con recarga automática                       │${NC}"
        echo -e "${BRIGHT_GREEN}└──────────────────────────────────────────────────────────────────────────────────┘${NC}"
    else
        echo -e "${BRIGHT_RED}┌─ ${REACT} FRONTEND STATUS ${CROSS} INACTIVO ─────────────────────────────────────────┐${NC}"
        echo -e "${RED}│ El servidor Vite no está ejecutándose                                        │${NC}"
        echo -e "${RED}│ Use la opción 1 para iniciar el frontend                                     │${NC}"
        echo -e "${BRIGHT_RED}└──────────────────────────────────────────────────────────────────────────────────┘${NC}"
    fi
    echo ""
}

# Función para verificar puerto disponible
check_port() {
    # Primero verificar si es nuestro propio proceso
    if is_frontend_running; then
        echo -e "${YELLOW}${WARNING} Frontend ya está ejecutándose${NC}"
        return 1
    fi

    # Verificar otros procesos en el puerto
    if command -v netstat >/dev/null 2>&1; then
        if netstat -tuln 2>/dev/null | grep -q ":$FRONTEND_PORT "; then
            echo -e "${RED}${CROSS} Puerto $FRONTEND_PORT ocupado por otro proceso${NC}"
            return 1
        fi
    elif command -v ss >/dev/null 2>&1; then
        if ss -tuln 2>/dev/null | grep -q ":$FRONTEND_PORT "; then
            echo -e "${RED}${CROSS} Puerto $FRONTEND_PORT ocupado por otro proceso${NC}"
            return 1
        fi
    fi

    return 0
}

# Función para detener frontend
stop_frontend() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        echo -e "${YELLOW}${STOP} Deteniendo frontend (PID: $pid)...${NC}"

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
        echo -e "${GREEN}${CHECK} Frontend detenido${NC}"
    else
        echo -e "${CYAN}${INFO} Frontend no estaba corriendo${NC}"
    fi

    # Limpiar procesos por nombre
    pkill -f "vite.*dev" 2>/dev/null || true
    pkill -f "node.*vite" 2>/dev/null || true

    # Limpiar puerto con diferentes métodos
    echo -e "${CYAN}🧹 Limpiando puerto $FRONTEND_PORT...${NC}"

    # Método 1: fuser
    if command -v fuser >/dev/null 2>&1; then
        fuser -k $FRONTEND_PORT/tcp 2>/dev/null || true
    fi

    # Método 2: lsof + kill
    if command -v lsof >/dev/null 2>&1; then
        local pids=$(lsof -ti :$FRONTEND_PORT 2>/dev/null || true)
        if [ -n "$pids" ]; then
            echo "$pids" | xargs -r kill 2>/dev/null || true
        fi
    fi

    sleep 1
}

# Función para iniciar frontend
start_frontend() {
    echo -e "${CYAN}${ROCKET} Iniciando frontend...${NC}"

    # Verificar directorio frontend
    if [ ! -d "$PROJECT_DIR/frontend" ]; then
        echo -e "${RED}${CROSS} Error: Directorio frontend/ no encontrado${NC}"
        return 1
    fi

    # Verificar puerto disponible
    if ! check_port; then
        echo -e "${YELLOW}${WARNING} Puerto ocupado, limpiando...${NC}"
        stop_frontend
        sleep 2
        if ! check_port; then
            echo -e "${RED}${CROSS} No se pudo liberar el puerto $FRONTEND_PORT${NC}"
            return 1
        fi
    fi

    # Cambiar al directorio frontend
    cd "$PROJECT_DIR/frontend" || return 1

    # Verificar package.json
    if [ ! -f "package.json" ]; then
        echo -e "${RED}${CROSS} Error: package.json no encontrado${NC}"
        return 1
    fi

    # Verificar Node.js
    if ! command -v node >/dev/null 2>&1; then
        echo -e "${RED}${CROSS} Error: Node.js no instalado${NC}"
        return 1
    fi

    # Verificar npm
    if ! command -v npm >/dev/null 2>&1; then
        echo -e "${RED}${CROSS} Error: npm no disponible${NC}"
        return 1
    fi

    # Verificar node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${CYAN}📦 Instalando dependencias...${NC}"
        npm install || {
            echo -e "${RED}${CROSS} Error instalando dependencias${NC}"
            return 1
        }
    fi

    # Verificar script dev existe
    if ! npm run dev --dry-run >/dev/null 2>&1; then
        echo -e "${YELLOW}${WARNING} Script 'dev' no encontrado en package.json${NC}"
    fi

    # Iniciar frontend
    echo -e "${CYAN}${ROCKET} Iniciando Vite dev server en $FRONTEND_HOST:$FRONTEND_PORT...${NC}"

    nohup npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" \
        > "$FRONTEND_LOG" 2>&1 &

    local pid=$!
    echo "$pid" > "$PID_FILE"
    echo -e "${GREEN}🆔 PID: $pid${NC}"

    # Health check
    echo -e "${CYAN}🏥 Verificando que el servidor inicie...${NC}"
    local retries=0
    local max_retries=20

    while [ $retries -lt $max_retries ]; do
        if curl -f -s --connect-timeout 2 --max-time 5 "http://$FRONTEND_HOST:$FRONTEND_PORT" >/dev/null 2>&1; then
            echo -e "${GREEN}${CHECK} Frontend iniciado correctamente${NC}"
            echo -e "${GREEN}🌐 URL: ${BRIGHT_CYAN}http://$FRONTEND_HOST:$FRONTEND_PORT${NC}"
            echo -e "${GREEN}🔥 HMR: Hot Module Replacement activo${NC}"
            return 0
        fi

        retries=$((retries + 1))
        echo -ne "${CYAN}.${NC}"
        sleep 1
    done

    echo -e "\n${RED}${CROSS} Frontend falló al iniciar después de $max_retries intentos${NC}"
    stop_frontend
    return 1
}

# Función para reload frontend
reload_frontend() {
    echo -e "${BRIGHT_YELLOW}${RELOAD} Recargando frontend...${NC}"
    stop_frontend
    sleep 2
    start_frontend
}

# Función para reset completo
reset_frontend() {
    echo -e "${BRIGHT_YELLOW}🔥 Reset completo del frontend...${NC}"
    stop_frontend
    echo -e "${CYAN}🧹 Limpiando logs...${NC}"
    > "$FRONTEND_LOG"  # Vaciar log
    echo -e "${CYAN}🧹 Limpiando cache de Vite...${NC}"
    cd "$PROJECT_DIR/frontend" && rm -rf node_modules/.vite 2>/dev/null || true
    sleep 2
    start_frontend
}

# Función para build de producción
build_frontend() {
    echo -e "${BRIGHT_BLUE}📦 Construyendo para producción...${NC}"
    cd "$PROJECT_DIR/frontend" || return 1

    if [ ! -f "package.json" ]; then
        echo -e "${RED}${CROSS} Error: package.json no encontrado${NC}"
        return 1
    fi

    # Verificar que node_modules existe
    if [ ! -d "node_modules" ]; then
        echo -e "${CYAN}📦 Instalando dependencias...${NC}"
        npm install || {
            echo -e "${RED}${CROSS} Error instalando dependencias${NC}"
            return 1
        }
    fi

    # Ejecutar build
    echo -e "${CYAN}⚡ Ejecutando npm run build...${NC}"
    if npm run build; then
        echo -e "${GREEN}${CHECK} Build completado exitosamente${NC}"
        if [ -d "dist" ]; then
            echo -e "${GREEN}📁 Archivos de producción en: ${WHITE}$PROJECT_DIR/frontend/dist${NC}"
        fi
    else
        echo -e "${RED}${CROSS} Error durante el build${NC}"
        return 1
    fi
}

# Función para mostrar logs en tiempo real
show_logs() {
    echo -e "${BRIGHT_CYAN}┌─ ${LOGS} LOGS FRONTEND EN TIEMPO REAL ────────────────────────────────────────────┐${NC}"
    echo -e "${BRIGHT_CYAN}│ Presiona Ctrl+C para volver al menú                                         │${NC}"
    echo -e "${BRIGHT_CYAN}└──────────────────────────────────────────────────────────────────────────────────┘${NC}"
    echo ""

    tail -f "$FRONTEND_LOG" 2>/dev/null | while IFS= read -r line; do
        local timestamp="${GRAY}[$(date '+%H:%M:%S')]${NC}"

        # Colorear según contenido
        if [[ "$line" == *"✓"* ]] || [[ "$line" == *"ready"* ]] || [[ "$line" == *"compiled"* ]]; then
            echo -e "$timestamp ${BRIGHT_GREEN}[SUCCESS]${NC} ${GREEN}$line${NC}"
        elif [[ "$line" == *"error"* ]] || [[ "$line" == *"Error"* ]] || [[ "$line" == *"✗"* ]]; then
            echo -e "$timestamp ${BRIGHT_RED}[ERROR]${NC} ${RED}$line${NC}"
        elif [[ "$line" == *"warning"* ]] || [[ "$line" == *"Warning"* ]] || [[ "$line" == *"⚠"* ]]; then
            echo -e "$timestamp ${BRIGHT_YELLOW}[WARN]${NC} ${YELLOW}$line${NC}"
        elif [[ "$line" == *"Local:"* ]] || [[ "$line" == *"Network:"* ]]; then
            echo -e "$timestamp ${BRIGHT_CYAN}[SERVER]${NC} ${BRIGHT_CYAN}$line${NC}"
        elif [[ "$line" == *"hmr update"* ]] || [[ "$line" == *"page reload"* ]]; then
            echo -e "$timestamp ${PURPLE}[HMR]${NC} ${PURPLE}$line${NC}"
        else
            echo -e "$timestamp ${BLUE}[FRONTEND]${NC} $line"
        fi
    done || echo -e "${RED}${CROSS} Log no encontrado: $FRONTEND_LOG${NC}"
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
        echo -e "${BRIGHT_GREEN}┌─ GESTIÓN DEL FRONTEND ─────────────────┐${NC}"
        echo -e "${GREEN}│ ${ROCKET} 1  Iniciar Frontend               │${NC}"
        echo -e "${YELLOW}│ ${RELOAD} 2  Reload Frontend                │${NC}"
        echo -e "${PURPLE}│ 🔥 3  Reset Completo (+ limpiar cache)│${NC}"
        echo -e "${RED}│ ${STOP} 4  Detener Frontend               │${NC}"
        echo -e "${BRIGHT_GREEN}└─────────────────────────────────────────┘${NC}"
        echo ""
        echo -e "${BRIGHT_BLUE}┌─ BUILD Y MONITOREO ────────────────────┐${NC}"
        echo -e "${BLUE}│ 📦 5  Build para Producción           │${NC}"
        echo -e "${BLUE}│ ${LOGS} 6  Ver Logs en Tiempo Real        │${NC}"
        echo -e "${BLUE}│ ${STATUS} 7  Actualizar Estado              │${NC}"
        echo -e "${BRIGHT_BLUE}└─────────────────────────────────────────┘${NC}"
        echo ""
        echo -e "${BRIGHT_RED}┌─ SISTEMA ──────────────────────────────┐${NC}"
        echo -e "${WHITE}│ 🚪 0  Salir                            │${NC}"
        echo -e "${BRIGHT_RED}└─────────────────────────────────────────┘${NC}"
        echo ""
        echo -ne "${BRIGHT_CYAN}💻 Selecciona una opción [0-7]: ${NC}"

        read -r option

        case "$option" in
            1)
                echo ""
                stop_frontend  # Detener si existe
                start_frontend
                echo ""
                echo -e "${CYAN}${INFO} Presiona Enter para continuar...${NC}"
                read -r
                ;;
            2)
                echo ""
                reload_frontend
                echo ""
                echo -e "${CYAN}${INFO} Presiona Enter para continuar...${NC}"
                read -r
                ;;
            3)
                echo ""
                reset_frontend
                echo ""
                echo -e "${CYAN}${INFO} Presiona Enter para continuar...${NC}"
                read -r
                ;;
            4)
                echo ""
                stop_frontend
                echo ""
                echo -e "${CYAN}${INFO} Presiona Enter para continuar...${NC}"
                read -r
                ;;
            5)
                echo ""
                build_frontend
                echo ""
                echo -e "${CYAN}${INFO} Presiona Enter para continuar...${NC}"
                read -r
                ;;
            6)
                clear
                show_logs
                ;;
            7)
                # Solo refresh del menú
                ;;
            0)
                echo ""
                echo -e "${BRIGHT_RED}${STOP} Deteniendo frontend y saliendo...${NC}"
                stop_frontend
                echo ""
                echo -e "${BRIGHT_GREEN}👋 ¡Hasta luego!${NC}"
                exit 0
                ;;
            *)
                echo ""
                echo -e "${BRIGHT_RED}${CROSS} Opción inválida. Usa 0-7${NC}"
                sleep 2
                ;;
        esac
    done
}

# Función principal
main() {
    # Verificar directorio del proyecto
    if [ ! -d "$PROJECT_DIR/frontend" ]; then
        echo -e "${RED}${CROSS} Error: Directorio frontend no encontrado: $PROJECT_DIR/frontend${NC}"
        exit 1
    fi

    # Mostrar menú
    show_menu
}

# Ejecutar función principal
main "$@"