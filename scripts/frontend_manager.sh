#!/bin/bash
# ============================================================================
# ⚛️ MESTOCKER FRONTEND MANAGER V2
# Script robusto para gestión completa del frontend React+Vite
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
CLEAN="🧹"

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
    echo -e "${BRIGHT_CYAN}║                        ${REACT} FRONTEND MANAGER V2                           ║${NC}"
    echo -e "${BRIGHT_CYAN}║                           React + Vite Development                           ║${NC}"
    echo -e "${BRIGHT_CYAN}╠═══════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║ Host: ${WHITE}$FRONTEND_HOST:$FRONTEND_PORT${NC} ${GRAY}|${NC} Log: ${WHITE}$FRONTEND_LOG${NC} ║"
    echo -e "${BRIGHT_CYAN}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Función robusta para encontrar todos los procesos relacionados con frontend
find_all_frontend_processes() {
    local pids=()

    # Buscar por diferentes patrones
    local patterns=(
        "vite"
        "npm.*dev"
        "node.*vite"
        "frontend.*dev"
        "npm run dev"
    )

    for pattern in "${patterns[@]}"; do
        local found_pids=$(pgrep -f "$pattern" 2>/dev/null || true)
        if [ -n "$found_pids" ]; then
            pids+=($found_pids)
        fi
    done

    # Buscar por puerto específico si lsof está disponible
    if command -v lsof >/dev/null 2>&1; then
        local port_pids=$(lsof -ti :$FRONTEND_PORT 2>/dev/null || true)
        if [ -n "$port_pids" ]; then
            pids+=($port_pids)
        fi
    fi

    # Eliminar duplicados y retornar
    printf '%s\n' "${pids[@]}" | sort -u | tr '\n' ' '
}

# Función para verificar si el frontend está corriendo
is_frontend_running() {
    local pids=$(find_all_frontend_processes)
    [ -n "$pids" ] && return 0 || return 1
}

# Función para obtener el PID principal del frontend
get_main_frontend_pid() {
    # Buscar el proceso principal de vite
    local main_pid=$(pgrep -f "vite.*--host.*$FRONTEND_HOST.*--port.*$FRONTEND_PORT" 2>/dev/null | head -1)

    if [ -z "$main_pid" ]; then
        main_pid=$(pgrep -f "node.*vite" 2>/dev/null | head -1)
    fi

    if [ -z "$main_pid" ]; then
        main_pid=$(find_all_frontend_processes | awk '{print $1}')
    fi

    if [ -n "$main_pid" ]; then
        echo "$main_pid" > "$PID_FILE"
        echo "$main_pid"
    elif [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    fi
}

# Función para obtener uptime del proceso
get_uptime() {
    local pid=$(get_main_frontend_pid)
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
        local pid=$(get_main_frontend_pid)
        local uptime=$(get_uptime)
        local all_pids=$(find_all_frontend_processes)
        echo -e "${BRIGHT_GREEN}┌─ ${REACT} FRONTEND STATUS ${CHECK} ACTIVO ─────────────────────────────────────────┐${NC}"
        echo -e "${GREEN}│ PID: ${WHITE}$pid${GREEN} │ Uptime: ${WHITE}$uptime${GREEN} │ URL: ${BRIGHT_CYAN}http://$FRONTEND_HOST:$FRONTEND_PORT${GREEN} │${NC}"
        echo -e "${GREEN}│ Procesos activos: ${WHITE}$(echo $all_pids | wc -w)${GREEN} │ Vite HMR activo                             │${NC}"
        echo -e "${BRIGHT_GREEN}└──────────────────────────────────────────────────────────────────────────────────┘${NC}"
    else
        echo -e "${BRIGHT_RED}┌─ ${REACT} FRONTEND STATUS ${CROSS} INACTIVO ─────────────────────────────────────────┐${NC}"
        echo -e "${RED}│ El servidor Vite no está ejecutándose                                        │${NC}"
        echo -e "${RED}│ Use la opción 1 para iniciar el frontend                                     │${NC}"
        echo -e "${BRIGHT_RED}└──────────────────────────────────────────────────────────────────────────────────┘${NC}"
    fi
    echo ""
}

# Función robusta para detener completamente el frontend
stop_frontend_completely() {
    echo -e "${YELLOW}${STOP} Deteniendo frontend completamente...${NC}"

    # Método agresivo: repetir limpieza hasta 3 veces
    local attempts=0
    local max_attempts=3

    while [ $attempts -lt $max_attempts ]; do
        attempts=$((attempts + 1))
        echo -e "${CYAN}${INFO} Intento $attempts de $max_attempts...${NC}"

        # Encontrar todos los procesos relacionados
        local all_pids=$(find_all_frontend_processes)

        if [ -n "$all_pids" ]; then
            echo -e "${CYAN}${INFO} Procesos encontrados: $all_pids${NC}"

            for pid in $all_pids; do
                if ps -p "$pid" > /dev/null 2>&1; then
                    echo -e "${YELLOW}🔸 Terminando proceso $pid...${NC}"
                    kill -9 "$pid" 2>/dev/null || true
                fi
            done
        fi

        # Limpiar por patrones de proceso (más agresivo)
        echo -e "${CYAN}${CLEAN} Limpieza agresiva por patrones...${NC}"
        pkill -9 -f "vite" 2>/dev/null || true
        pkill -9 -f "npm.*dev" 2>/dev/null || true
        pkill -9 -f "node.*vite" 2>/dev/null || true
        pkill -9 -f "frontend.*dev" 2>/dev/null || true

        # Limpiar puerto con múltiples métodos
        echo -e "${CYAN}${CLEAN} Liberando puerto $FRONTEND_PORT...${NC}"

        # Método 1: fuser (más agresivo)
        if command -v fuser >/dev/null 2>&1; then
            fuser -k -9 $FRONTEND_PORT/tcp 2>/dev/null || true
        fi

        # Método 2: lsof + kill -9
        if command -v lsof >/dev/null 2>&1; then
            local port_pids=$(lsof -ti :$FRONTEND_PORT 2>/dev/null || true)
            if [ -n "$port_pids" ]; then
                echo "$port_pids" | xargs -r kill -9 2>/dev/null || true
            fi
        fi

        # Método 3: netstat + kill -9
        if command -v netstat >/dev/null 2>&1; then
            local netstat_pids=$(netstat -tlnp 2>/dev/null | grep ":$FRONTEND_PORT " | awk '{print $7}' | cut -d'/' -f1 | grep -v '^-$' || true)
            if [ -n "$netstat_pids" ]; then
                echo "$netstat_pids" | xargs -r kill -9 2>/dev/null || true
            fi
        fi

        # Limpiar archivos PID
        rm -f "$PID_FILE"

        sleep 2

        # Verificar si se detuvo
        if ! is_frontend_running; then
            echo -e "${GREEN}${CHECK} Frontend detenido completamente en intento $attempts${NC}"
            return 0
        else
            echo -e "${YELLOW}${WARNING} Aún hay procesos activos, reintentando...${NC}"
        fi

        sleep 1
    done

    # Verificación final
    if is_frontend_running; then
        echo -e "${RED}${WARNING} No se pudieron detener todos los procesos después de $max_attempts intentos${NC}"
        local remaining_pids=$(find_all_frontend_processes)
        echo -e "${RED}Procesos persistentes: $remaining_pids${NC}"
        for pid in $remaining_pids; do
            if [ -n "$pid" ] && ps -p "$pid" > /dev/null 2>&1; then
                echo -e "${RED}  - PID $pid: $(ps -p $pid -o comm= 2>/dev/null)${NC}"
            fi
        done
        return 1
    else
        echo -e "${GREEN}${CHECK} Frontend detenido completamente${NC}"
        return 0
    fi
}

# Función para verificar puerto disponible
check_port_available() {
    # Verificar con netstat
    if command -v netstat >/dev/null 2>&1; then
        if netstat -tuln 2>/dev/null | grep -q ":$FRONTEND_PORT "; then
            return 1
        fi
    fi

    # Verificar con ss
    if command -v ss >/dev/null 2>&1; then
        if ss -tuln 2>/dev/null | grep -q ":$FRONTEND_PORT "; then
            return 1
        fi
    fi

    # Verificar con lsof
    if command -v lsof >/dev/null 2>&1; then
        if lsof -i :$FRONTEND_PORT 2>/dev/null | grep -q LISTEN; then
            return 1
        fi
    fi

    return 0
}

# Función para iniciar frontend limpio
start_frontend_clean() {
    echo -e "${CYAN}${ROCKET} Iniciando frontend limpio...${NC}"

    # Paso 1: Detener todo completamente
    echo -e "${CYAN}📍 Paso 1: Limpieza completa...${NC}"
    stop_frontend_completely

    # Paso 2: Verificar directorio
    echo -e "${CYAN}📍 Paso 2: Verificando directorio...${NC}"
    if [ ! -d "$PROJECT_DIR/frontend" ]; then
        echo -e "${RED}${CROSS} Error: Directorio frontend/ no encontrado${NC}"
        return 1
    fi

    # Paso 3: Verificar puerto libre
    echo -e "${CYAN}📍 Paso 3: Verificando puerto libre...${NC}"
    if ! check_port_available; then
        echo -e "${RED}${CROSS} Puerto $FRONTEND_PORT aún ocupado${NC}"
        return 1
    fi

    # Paso 4: Verificar Node.js y npm
    echo -e "${CYAN}📍 Paso 4: Verificando herramientas...${NC}"
    if ! command -v node >/dev/null 2>&1; then
        echo -e "${RED}${CROSS} Error: Node.js no instalado${NC}"
        return 1
    fi

    if ! command -v npm >/dev/null 2>&1; then
        echo -e "${RED}${CROSS} Error: npm no disponible${NC}"
        return 1
    fi

    # Paso 5: Cambiar al directorio
    echo -e "${CYAN}📍 Paso 5: Navegando al directorio...${NC}"
    cd "$PROJECT_DIR/frontend" || return 1

    # Paso 6: Verificar package.json
    echo -e "${CYAN}📍 Paso 6: Verificando configuración...${NC}"
    if [ ! -f "package.json" ]; then
        echo -e "${RED}${CROSS} Error: package.json no encontrado${NC}"
        return 1
    fi

    # Paso 7: Instalar dependencias si es necesario
    echo -e "${CYAN}📍 Paso 7: Verificando dependencias...${NC}"
    if [ ! -d "node_modules" ]; then
        echo -e "${CYAN}📦 Instalando dependencias...${NC}"
        npm install || {
            echo -e "${RED}${CROSS} Error instalando dependencias${NC}"
            return 1
        }
    fi

    # Paso 8: Limpiar log anterior
    echo -e "${CYAN}📍 Paso 8: Preparando logs...${NC}"
    > "$FRONTEND_LOG"  # Limpiar log

    # Paso 9: Iniciar frontend
    echo -e "${CYAN}📍 Paso 9: Iniciando servidor Vite...${NC}"
    echo -e "${BRIGHT_GREEN}${ROCKET} Comando: npm run dev -- --host $FRONTEND_HOST --port $FRONTEND_PORT${NC}"

    nohup npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" \
        > "$FRONTEND_LOG" 2>&1 &

    local pid=$!
    echo "$pid" > "$PID_FILE"
    echo -e "${GREEN}🆔 PID inicial: $pid${NC}"

    # Paso 10: Health check robusto
    echo -e "${CYAN}📍 Paso 10: Verificando arranque...${NC}"
    local retries=0
    local max_retries=30
    local success=false

    while [ $retries -lt $max_retries ]; do
        # Verificar que el proceso sigue vivo
        if ! ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${RED}${CROSS} Proceso principal terminó inesperadamente${NC}"
            break
        fi

        # Verificar conexión HTTP
        if curl -f -s --connect-timeout 2 --max-time 5 "http://$FRONTEND_HOST:$FRONTEND_PORT" >/dev/null 2>&1; then
            success=true
            break
        fi

        retries=$((retries + 1))
        echo -ne "${CYAN}.${NC}"
        sleep 1
    done

    echo ""

    if [ "$success" = true ]; then
        local real_pid=$(get_main_frontend_pid)
        echo -e "${GREEN}${CHECK} Frontend iniciado correctamente${NC}"
        echo -e "${GREEN}🆔 PID final: ${WHITE}$real_pid${NC}"
        echo -e "${GREEN}🌐 URL: ${BRIGHT_CYAN}http://$FRONTEND_HOST:$FRONTEND_PORT${NC}"
        echo -e "${GREEN}🔥 HMR: Hot Module Replacement activo${NC}"
        echo -e "${GREEN}📋 Logs: ${WHITE}$FRONTEND_LOG${NC}"
        return 0
    else
        echo -e "${RED}${CROSS} Frontend falló al iniciar después de $max_retries intentos${NC}"
        stop_frontend_completely
        return 1
    fi
}

# Función para reload frontend
reload_frontend() {
    echo -e "${BRIGHT_YELLOW}${RELOAD} Recargando frontend...${NC}"
    stop_frontend_completely
    sleep 2
    start_frontend_clean
}

# Función para reset completo
reset_frontend() {
    echo -e "${BRIGHT_YELLOW}🔥 Reset completo del frontend...${NC}"
    stop_frontend_completely
    echo -e "${CYAN}${CLEAN} Limpiando cache de Vite...${NC}"
    cd "$PROJECT_DIR/frontend" && rm -rf node_modules/.vite dist .vite 2>/dev/null || true
    echo -e "${CYAN}${CLEAN} Limpiando logs...${NC}"
    > "$FRONTEND_LOG"
    sleep 2
    start_frontend_clean
}

# Función para build de producción
build_frontend() {
    echo -e "${BRIGHT_BLUE}📦 Construyendo para producción...${NC}"

    # Detener desarrollo si está corriendo
    if is_frontend_running; then
        echo -e "${YELLOW}${WARNING} Deteniendo servidor de desarrollo...${NC}"
        stop_frontend_completely
    fi

    cd "$PROJECT_DIR/frontend" || return 1

    if [ ! -f "package.json" ]; then
        echo -e "${RED}${CROSS} Error: package.json no encontrado${NC}"
        return 1
    fi

    # Verificar dependencias
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
        echo -e "${GREEN}│ ${ROCKET} 1  Iniciar Frontend Limpio        │${NC}"
        echo -e "${YELLOW}│ ${RELOAD} 2  Reload Frontend                │${NC}"
        echo -e "${PURPLE}│ 🔥 3  Reset Completo (+ limpiar cache)│${NC}"
        echo -e "${RED}│ ${STOP} 4  Detener Frontend Completamente │${NC}"
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
                start_frontend_clean
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
                stop_frontend_completely
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
                echo -e "${BRIGHT_RED}${STOP} Saliendo...${NC}"
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