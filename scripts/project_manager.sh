#!/bin/bash
# ~/scripts/project_manager_v3.sh
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Gestor de Proyecto Completo v3.0
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: project_manager_v3.sh
# Propósito: Gestión completa de backend y frontend con menú interactivo avanzado
# Funcionalidades: Inicio/parada automática, reload, logging, detección de procesos,
#                  validación de puertos, rotación de logs, health checks robustos,
#                  interfaz mejorada con información del sistema
# v3.0: Interfaz mejorada, indicadores visuales, menú reorganizado, progress bars
#
# ---------------------------------------------------------------------------------------------

# Colores y estilos para output
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
NC='\033[0m' # No Color

# Símbolos especiales
CHECK_MARK="✅"
CROSS_MARK="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"
GEAR="⚙️"
CLOCK="⏰"
CPU="🖥️"
MEMORY="💾"
NETWORK="🌐"
LOG="📋"
UP_ARROW="⬆️"
DOWN_ARROW="⬇️"

# Variables globales (se pueden sobrescribir con config.env)
PROJECT_DIR="/home/admin-jairo/MeStore"
BACKEND_PORT=8000
FRONTEND_PORT=5173
BACKEND_HOST="192.168.1.137"
FRONTEND_HOST="192.168.1.137"

# Cargar configuración externa si existe
CONFIG_FILE="$PROJECT_DIR/config.env"
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${CYAN}🔧 Cargando configuración desde config.env...${NC}"
    source "$CONFIG_FILE"
fi

# PID files para tracking
BACKEND_PID_FILE="/tmp/mestocker_backend.pid"
FRONTEND_PID_FILE="/tmp/mestocker_frontend.pid"

# Log files
LOG_DIR="$PROJECT_DIR/logs"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

# Función para obtener información del sistema
get_system_info() {
    local uptime_info=$(uptime | awk -F'up ' '{print $2}' | awk -F',' '{print $1}')
    local load_avg=$(uptime | awk -F'load average: ' '{print $2}')
    local mem_info=$(free -h | awk '/^Mem:/ {printf "%.1fG/%.1fG", $3, $2}' | sed 's/Gi/G/g')
    local disk_info=$(df -h "$PROJECT_DIR" 2>/dev/null | awk 'NR==2 {print $4" free"}')
    local current_ip=$(hostname -I | awk '{print $1}')

    echo "$uptime_info|$load_avg|$mem_info|$disk_info|$current_ip"
}

# Función para mostrar barra de progreso
show_progress() {
    local duration=$1
    local message="$2"
    local progress=0
    local bar_length=30

    echo -ne "${CYAN}$message ${NC}"

    for ((i=0; i<=duration; i++)); do
        progress=$((i * bar_length / duration))
        printf "\r${CYAN}$message ${NC}["

        for ((j=0; j<bar_length; j++)); do
            if [ $j -lt $progress ]; then
                printf "${GREEN}█${NC}"
            else
                printf "${GRAY}░${NC}"
            fi
        done

        printf "] %d%%" $((i * 100 / duration))
        sleep 0.1
    done

    printf "\n"
}

# Función mejorada para limpiar pantalla con información del sistema
clear_screen() {
    clear
    local sys_info=$(get_system_info)
    local uptime=$(echo "$sys_info" | cut -d'|' -f1)
    local load=$(echo "$sys_info" | cut -d'|' -f2)
    local memory=$(echo "$sys_info" | cut -d'|' -f3)
    local disk=$(echo "$sys_info" | cut -d'|' -f4)
    local ip=$(echo "$sys_info" | cut -d'|' -f5)

    echo -e "${BRIGHT_CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BRIGHT_CYAN}║                    🏗️  MESTOCKER PROJECT MANAGER v3.0                        ║${NC}"
    echo -e "${BRIGHT_CYAN}║                         Gestión Avanzada de Servicios                        ║${NC}"
    echo -e "${BRIGHT_CYAN}╠═══════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║ ${CPU} Sistema: ${WHITE}$(uname -n)${NC} ${GRAY}|${NC} ${CLOCK} Uptime: ${WHITE}$uptime${NC} ${GRAY}|${NC} ${NETWORK} IP: ${WHITE}$ip${NC} ║"
    echo -e "${CYAN}║ ${MEMORY} RAM: ${WHITE}$memory${NC} ${GRAY}|${NC} ${GEAR} Load: ${WHITE}$load${NC} ${GRAY}|${NC} 💿 Disk: ${WHITE}$disk${NC}     ║"
    echo -e "${BRIGHT_CYAN}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Función para crear directorio de logs
setup_logs() {
    mkdir -p "$LOG_DIR"
    touch "$BACKEND_LOG" "$FRONTEND_LOG"
}

# Función para rotar logs automáticamente
rotate_logs() {
    local max_size=10485760  # 10MB

    # Rotar backend log
    if [ -f "$BACKEND_LOG" ] && [ $(stat -c%s "$BACKEND_LOG" 2>/dev/null || echo 0) -gt $max_size ]; then
        echo -e "${YELLOW}🔄 Rotando log del backend...${NC}"
        mv "$BACKEND_LOG" "${BACKEND_LOG}.$(date +%Y%m%d_%H%M%S)"
        touch "$BACKEND_LOG"
    fi

    # Rotar frontend log
    if [ -f "$FRONTEND_LOG" ] && [ $(stat -c%s "$FRONTEND_LOG" 2>/dev/null || echo 0) -gt $max_size ]; then
        echo -e "${YELLOW}🔄 Rotando log del frontend...${NC}"
        mv "$FRONTEND_LOG" "${FRONTEND_LOG}.$(date +%Y%m%d_%H%M%S)"
        touch "$FRONTEND_LOG"
    fi

    # Limpiar logs antiguos (más de 7 días)
    find "$LOG_DIR" -name "*.log.*" -mtime +7 -delete 2>/dev/null || true
}

# Función para verificar si un puerto está ocupado
check_port() {
    local port=$1
    local service_name=$2

    if command -v lsof >/dev/null 2>&1; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${RED}❌ Puerto $port ya está ocupado por otro proceso${NC}"
            echo -e "${YELLOW}💡 Procesos usando el puerto $port:${NC}"
            lsof -Pi :$port -sTCP:LISTEN
            return 1
        fi
    elif command -v netstat >/dev/null 2>&1; then
        if netstat -tuln | grep -q ":$port "; then
            echo -e "${RED}❌ Puerto $port ya está ocupado${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️ No se puede verificar el puerto $port (lsof/netstat no disponibles)${NC}"
    fi

    return 0
}

# Función mejorada para health check
health_check() {
    local service=$1
    local url=$2
    local max_retries=15
    local retries=0

    echo -e "${CYAN}🏥 Verificando salud de $service...${NC}"

    while [ $retries -lt $max_retries ]; do
        if curl -f -s --connect-timeout 2 --max-time 5 "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service respondiendo correctamente${NC}"
            return 0
        fi

        retries=$((retries + 1))
        echo -ne "${CYAN}.${NC}"
        sleep 1
    done

    echo -e "\n${RED}❌ $service no respondió después de $max_retries intentos${NC}"
    return 1
}

# Función para reproducir sonido de alerta
play_alert_sound() {
    local alert_type="$1"  # "crash", "restart", "warning"

    # Intentar diferentes métodos de sonido según disponibilidad
    if command -v paplay >/dev/null 2>&1 && [ -f "/usr/share/sounds/alsa/Front_Left.wav" ]; then
        # PulseAudio (Ubuntu/Debian)
        case "$alert_type" in
            "crash")
                for i in {1..3}; do paplay /usr/share/sounds/alsa/Front_Left.wav 2>/dev/null & sleep 0.2; done
                ;;
            "restart")
                paplay /usr/share/sounds/alsa/Front_Left.wav 2>/dev/null &
                ;;
        esac
    elif command -v aplay >/dev/null 2>&1; then
        # ALSA
        case "$alert_type" in
            "crash")
                for i in {1..3}; do aplay /usr/share/sounds/alsa/Front_Left.wav 2>/dev/null & sleep 0.2; done
                ;;
            "restart")
                aplay /usr/share/sounds/alsa/Front_Left.wav 2>/dev/null &
                ;;
        esac
    elif command -v espeak >/dev/null 2>&1; then
        # Text-to-speech como alternativa
        case "$alert_type" in
            "crash")
                espeak "Servidor caído, reiniciando" --speed=200 2>/dev/null &
                ;;
            "restart")
                espeak "Servidor reiniciado" --speed=200 2>/dev/null &
                ;;
        esac
    else
        # Fallback: beep del sistema
        case "$alert_type" in
            "crash")
                for i in {1..3}; do echo -e "\a" && sleep 0.3; done
                ;;
            "restart")
                echo -e "\a"
                ;;
        esac
    fi
}

# Función para logging de eventos de watchdog
log_event() {
    local event_type="$1"
    local service="$2"
    local message="$3"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[$timestamp] [$event_type] $service: $message" >> "$WATCHDOG_LOG"

    # También log de reinicios en archivo separado
    if [[ "$event_type" == "RESTART" ]]; then
        echo "[$timestamp] $service reiniciado automáticamente - $message" >> "$RESTART_LOG"
    fi
}

# Función del watchdog para monitoreo continuo
watchdog_monitor() {
    local check_interval=10  # Verificar cada 10 segundos
    local max_restart_attempts=3
    local restart_cooldown=30  # Esperar 30 segundos entre reintentos

    echo "$$" > "$WATCHDOG_PID_FILE"
    echo "RUNNING" > "$WATCHDOG_STATUS_FILE"

    log_event "START" "WATCHDOG" "Monitoreo iniciado con PID $$"

    local backend_down_count=0
    local frontend_down_count=0
    local last_backend_restart=0
    local last_frontend_restart=0

    while [ -f "$WATCHDOG_STATUS_FILE" ] && [ "$(cat "$WATCHDOG_STATUS_FILE")" = "RUNNING" ]; do
        local current_time=$(date +%s)

        # Verificar Backend
        if ! is_process_running "$BACKEND_PID_FILE" "uvicorn"; then
            backend_down_count=$((backend_down_count + 1))
            log_event "ALERT" "BACKEND" "Servicio caído (intento $backend_down_count)"

            if [ $backend_down_count -eq 1 ]; then
                # Primera detección de caída - sonar alerta
                play_alert_sound "crash"
                echo -e "\n${BRIGHT_RED}${ALERT} $(date '+%H:%M:%S') - BACKEND CAÍDO DETECTADO${NC}" >> "$BACKEND_LOG"
            fi

            # Reiniciar si han pasado suficiente tiempo y no hemos excedido intentos
            if [ $((current_time - last_backend_restart)) -gt $restart_cooldown ] && [ $backend_down_count -le $max_restart_attempts ]; then
                log_event "RESTART" "BACKEND" "Iniciando reinicio automático"
                echo -e "\n${BRIGHT_YELLOW}${RESTART} $(date '+%H:%M:%S') - REINICIO AUTOMÁTICO BACKEND${NC}" >> "$BACKEND_LOG"

                # Reiniciar en background
                (
                    cd "$PROJECT_DIR" || exit 1

                    # Activar entorno virtual si existe
                    [ -f ".venv/bin/activate" ] && source .venv/bin/activate

                    # Iniciar backend
                    nohup python -m uvicorn app.main:app \
                        --reload \
                        --reload-dir ./app \
                        --host "$BACKEND_HOST" \
                        --port "$BACKEND_PORT" \
                        >> "$BACKEND_LOG" 2>&1 &

                    echo "$!" > "$BACKEND_PID_FILE"

                    # Verificar que inició correctamente
                    sleep 5
                    if is_process_running "$BACKEND_PID_FILE" "uvicorn"; then
                        log_event "SUCCESS" "BACKEND" "Reinicio exitoso con PID $(cat "$BACKEND_PID_FILE")"
                        echo -e "\n${BRIGHT_GREEN}${CHECK_MARK} $(date '+%H:%M:%S') - BACKEND REINICIADO EXITOSAMENTE${NC}" >> "$BACKEND_LOG"
                        play_alert_sound "restart"
                        backend_down_count=0
                    else
                        log_event "FAILED" "BACKEND" "Fallo en reinicio automático"
                    fi
                ) &

                last_backend_restart=$current_time
            fi
        else
            backend_down_count=0
        fi

        # Verificar Frontend (similar lógica)
        if ! is_process_running "$FRONTEND_PID_FILE" "node"; then
            frontend_down_count=$((frontend_down_count + 1))
            log_event "ALERT" "FRONTEND" "Servicio caído (intento $frontend_down_count)"

            if [ $frontend_down_count -eq 1 ]; then
                play_alert_sound "crash"
                echo -e "\n${BRIGHT_RED}${ALERT} $(date '+%H:%M:%S') - FRONTEND CAÍDO DETECTADO${NC}" >> "$FRONTEND_LOG"
            fi

            if [ $((current_time - last_frontend_restart)) -gt $restart_cooldown ] && [ $frontend_down_count -le $max_restart_attempts ]; then
                log_event "RESTART" "FRONTEND" "Iniciando reinicio automático"
                echo -e "\n${BRIGHT_YELLOW}${RESTART} $(date '+%H:%M:%S') - REINICIO AUTOMÁTICO FRONTEND${NC}" >> "$FRONTEND_LOG"

                (
                    cd "$PROJECT_DIR/frontend" || exit 1

                    nohup npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" \
                        >> "$FRONTEND_LOG" 2>&1 &

                    echo "$!" > "$FRONTEND_PID_FILE"

                    sleep 8
                    if is_process_running "$FRONTEND_PID_FILE" "node"; then
                        log_event "SUCCESS" "FRONTEND" "Reinicio exitoso con PID $(cat "$FRONTEND_PID_FILE")"
                        echo -e "\n${BRIGHT_GREEN}${CHECK_MARK} $(date '+%H:%M:%S') - FRONTEND REINICIADO EXITOSAMENTE${NC}" >> "$FRONTEND_LOG"
                        play_alert_sound "restart"
                        frontend_down_count=0
                    else
                        log_event "FAILED" "FRONTEND" "Fallo en reinicio automático"
                    fi
                ) &

                last_frontend_restart=$current_time
            fi
        else
            frontend_down_count=0
        fi

        sleep $check_interval
    done

    log_event "STOP" "WATCHDOG" "Monitoreo detenido"
    rm -f "$WATCHDOG_PID_FILE" "$WATCHDOG_STATUS_FILE"
}

# Función para iniciar watchdog
start_watchdog() {
    if [ -f "$WATCHDOG_PID_FILE" ] && ps -p "$(cat "$WATCHDOG_PID_FILE")" > /dev/null 2>&1; then
        echo -e "${YELLOW}${WARNING} Watchdog ya está ejecutándose (PID: $(cat "$WATCHDOG_PID_FILE"))${NC}"
        return 1
    fi

    echo -e "${BRIGHT_GREEN}${WATCHDOG} Iniciando Watchdog para monitoreo automático...${NC}"

    # Crear script temporal simplificado
    cat > /tmp/mestocker_watchdog.sh << 'WATCHDOG_SCRIPT'
#!/bin/bash

# Variables fijas
PROJECT_DIR="/home/admin-jairo/MeStore"
BACKEND_HOST="192.168.1.137"
FRONTEND_HOST="192.168.1.137"
BACKEND_PORT=8000
FRONTEND_PORT=5173
BACKEND_LOG="$PROJECT_DIR/logs/backend.log"
FRONTEND_LOG="$PROJECT_DIR/logs/frontend.log"
WATCHDOG_LOG="$PROJECT_DIR/logs/watchdog.log"
RESTART_LOG="$PROJECT_DIR/logs/restart_history.log"
BACKEND_PID_FILE="/tmp/mestocker_backend.pid"
FRONTEND_PID_FILE="/tmp/mestocker_frontend.pid"
WATCHDOG_PID_FILE="/tmp/mestocker_watchdog.pid"
WATCHDOG_STATUS_FILE="/tmp/mestocker_watchdog_status"

# Cargar configuración si existe
CONFIG_FILE="$PROJECT_DIR/config.env"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

# Crear logs si no existen
mkdir -p "$PROJECT_DIR/logs"
touch "$BACKEND_LOG" "$FRONTEND_LOG" "$WATCHDOG_LOG" "$RESTART_LOG"

# Función para verificar procesos
is_process_running() {
    local pid_file="$1"
    local process_name="$2"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            if ps -p "$pid" -o cmd --no-headers | grep -q "$process_name"; then
                return 0
            fi
        fi
        rm -f "$pid_file"
    fi
    return 1
}

# Función para sonidos
play_alert_sound() {
    local alert_type="$1"
    case "$alert_type" in
        "crash")
            for i in {1..3}; do echo -e "\a"; sleep 0.3; done
            ;;
        "restart")
            echo -e "\a"
            ;;
    esac
}

# Función de logging
log_event() {
    local event_type="$1"
    local service="$2"
    local message="$3"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[$timestamp] [$event_type] $service: $message" >> "$WATCHDOG_LOG"

    if [[ "$event_type" == "RESTART" ]]; then
        echo "[$timestamp] $service reiniciado automáticamente - $message" >> "$RESTART_LOG"
    fi
}

# Inicializar watchdog
echo "$$" > "$WATCHDOG_PID_FILE"
echo "RUNNING" > "$WATCHDOG_STATUS_FILE"

log_event "START" "WATCHDOG" "Monitoreo iniciado con PID $$"

backend_down_count=0
frontend_down_count=0
last_backend_restart=0
last_frontend_restart=0

# Loop principal
while [ -f "$WATCHDOG_STATUS_FILE" ] && [ "$(cat "$WATCHDOG_STATUS_FILE")" = "RUNNING" ]; do
    current_time=$(date +%s)

    # Verificar Backend
    if ! is_process_running "$BACKEND_PID_FILE" "uvicorn"; then
        backend_down_count=$((backend_down_count + 1))
        log_event "ALERT" "BACKEND" "Servicio caído (intento $backend_down_count)"

        if [ $backend_down_count -eq 1 ]; then
            play_alert_sound "crash"
            echo -e "\n🚨 $(date '+%H:%M:%S') - BACKEND CAÍDO DETECTADO" >> "$BACKEND_LOG"
        fi

        # Reiniciar si han pasado 30 segundos y no hemos excedido 3 intentos
        if [ $((current_time - last_backend_restart)) -gt 30 ] && [ $backend_down_count -le 3 ]; then
            log_event "RESTART" "BACKEND" "Iniciando reinicio automático"
            echo -e "\n🔄 $(date '+%H:%M:%S') - REINICIO AUTOMÁTICO BACKEND" >> "$BACKEND_LOG"

            (
                cd "$PROJECT_DIR" || exit 1
                [ -f ".venv/bin/activate" ] && source .venv/bin/activate

                nohup python -m uvicorn app.main:app \
                    --reload \
                    --reload-dir ./app \
                    --host "$BACKEND_HOST" \
                    --port "$BACKEND_PORT" \
                    >> "$BACKEND_LOG" 2>&1 &

                echo "$!" > "$BACKEND_PID_FILE"

                sleep 5
                if is_process_running "$BACKEND_PID_FILE" "uvicorn"; then
                    log_event "SUCCESS" "BACKEND" "Reinicio exitoso con PID $(cat "$BACKEND_PID_FILE")"
                    echo -e "\n✅ $(date '+%H:%M:%S') - BACKEND REINICIADO EXITOSAMENTE" >> "$BACKEND_LOG"
                    play_alert_sound "restart"
                    backend_down_count=0
                else
                    log_event "FAILED" "BACKEND" "Fallo en reinicio automático"
                fi
            ) &

            last_backend_restart=$current_time
        fi
    else
        backend_down_count=0
    fi

    # Verificar Frontend
    if ! is_process_running "$FRONTEND_PID_FILE" "node"; then
        frontend_down_count=$((frontend_down_count + 1))
        log_event "ALERT" "FRONTEND" "Servicio caído (intento $frontend_down_count)"

        if [ $frontend_down_count -eq 1 ]; then
            play_alert_sound "crash"
            echo -e "\n🚨 $(date '+%H:%M:%S') - FRONTEND CAÍDO DETECTADO" >> "$FRONTEND_LOG"
        fi

        if [ $((current_time - last_frontend_restart)) -gt 30 ] && [ $frontend_down_count -le 3 ]; then
            log_event "RESTART" "FRONTEND" "Iniciando reinicio automático"
            echo -e "\n🔄 $(date '+%H:%M:%S') - REINICIO AUTOMÁTICO FRONTEND" >> "$FRONTEND_LOG"

            (
                cd "$PROJECT_DIR/frontend" || exit 1

                nohup npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" \
                    >> "$FRONTEND_LOG" 2>&1 &

                echo "$!" > "$FRONTEND_PID_FILE"

                sleep 8
                if is_process_running "$FRONTEND_PID_FILE" "node"; then
                    log_event "SUCCESS" "FRONTEND" "Reinicio exitoso con PID $(cat "$FRONTEND_PID_FILE")"
                    echo -e "\n✅ $(date '+%H:%M:%S') - FRONTEND REINICIADO EXITOSAMENTE" >> "$FRONTEND_LOG"
                    play_alert_sound "restart"
                    frontend_down_count=0
                else
                    log_event "FAILED" "FRONTEND" "Fallo en reinicio automático"
                fi
            ) &

            last_frontend_restart=$current_time
        fi
    else
        frontend_down_count=0
    fi

    sleep 10
done

# Limpieza final
log_event "STOP" "WATCHDOG" "Monitoreo detenido"
rm -f "$WATCHDOG_PID_FILE" "$WATCHDOG_STATUS_FILE"
WATCHDOG_SCRIPT

    chmod +x /tmp/mestocker_watchdog.sh

    # Ejecutar en background con logging específico
    nohup /tmp/mestocker_watchdog.sh > /home/admin-jairo/MeStore/logs/watchdog.log 2>&1 &
    local watchdog_pid=$!

    sleep 3

    # Verificar que se inició correctamente
    if [ -f "$WATCHDOG_PID_FILE" ] && ps -p "$(cat "$WATCHDOG_PID_FILE")" > /dev/null 2>&1; then
        echo -e "${BRIGHT_GREEN}${CHECK_MARK} Watchdog iniciado exitosamente (PID: $(cat "$WATCHDOG_PID_FILE"))${NC}"
        echo -e "${CYAN}📝 Logs disponibles en: /home/admin-jairo/MeStore/logs/watchdog.log${NC}"
        return 0
    else
        echo -e "${RED}${CROSS_MARK} Error iniciando Watchdog${NC}"

        # Debug: mostrar qué pasó
        echo -e "${YELLOW}Información de debug:${NC}"
        echo "- Script PID original: $watchdog_pid"
        echo "- Archivo PID existe: $([ -f "$WATCHDOG_PID_FILE" ] && echo "Sí" || echo "No")"
        echo "- Archivo status existe: $([ -f "$WATCHDOG_STATUS_FILE" ] && echo "Sí" || echo "No")"

        if [ -f "/home/admin-jairo/MeStore/logs/watchdog.log" ]; then
            echo -e "${YELLOW}Últimas líneas del log:${NC}"
            tail -10 "/home/admin-jairo/MeStore/logs/watchdog.log"
        fi

        return 1
    fi
}

# Función para detener watchdog
stop_watchdog() {
    if [ -f "$WATCHDOG_PID_FILE" ]; then
        local pid=$(cat "$WATCHDOG_PID_FILE")
        echo -e "${YELLOW}${WATCHDOG} Deteniendo Watchdog (PID: $pid)...${NC}"

        # Marcar para detener
        echo "STOPPING" > "$WATCHDOG_STATUS_FILE"

        # Esperar detención grácil
        sleep 2

        # Forzar si es necesario
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid" 2>/dev/null
            sleep 1
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid" 2>/dev/null
            fi
        fi

        rm -f "$WATCHDOG_PID_FILE" "$WATCHDOG_STATUS_FILE" "/tmp/watchdog_temp.sh"
        echo -e "${GREEN}${CHECK_MARK} Watchdog detenido${NC}"
    else
        echo -e "${CYAN}${INFO} Watchdog no estaba ejecutándose${NC}"
    fi
}

# Función para verificar si un proceso está corriendo
is_process_running() {
    local pid_file="$1"
    local process_name="$2"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            # Verificar que el proceso es realmente el que esperamos
            if ps -p "$pid" -o cmd --no-headers | grep -q "$process_name"; then
                return 0  # Proceso corriendo
            fi
        fi
        # PID file existe pero proceso no está corriendo
        rm -f "$pid_file"
    fi
    return 1  # Proceso no corriendo
}

# Función mejorada para matar proceso
kill_process() {
    local pid_file="$1"
    local service_name="$2"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        echo -e "${YELLOW}🛑 Deteniendo $service_name (PID: $pid)...${NC}"

        # Intentar terminar amablemente
        kill "$pid" 2>/dev/null
        sleep 2

        # Verificar si terminó
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚡ Forzando terminación de $service_name...${NC}"
            kill -9 "$pid" 2>/dev/null
            sleep 1
        fi

        rm -f "$pid_file"
        echo -e "${GREEN}✅ $service_name detenido${NC}"
    else
        echo -e "${CYAN}ℹ️ $service_name no estaba corriendo${NC}"
    fi

    # Limpiar procesos zombi y por puerto/nombre
    case "$service_name" in
        "Backend")
            # Matar por nombre de proceso
            pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
            pkill -f "python.*uvicorn" 2>/dev/null || true

            # Matar por puerto si fuser está disponible
            if command -v fuser >/dev/null 2>&1; then
                echo -e "${CYAN}🧹 Limpiando puerto $BACKEND_PORT...${NC}"
                fuser -k $BACKEND_PORT/tcp 2>/dev/null || true
                sleep 1
            fi
            ;;
        "Frontend")
            # Matar por nombre de proceso
            pkill -f "vite.*dev" 2>/dev/null || true
            pkill -f "node.*vite" 2>/dev/null || true

            # Matar por puerto si fuser está disponible
            if command -v fuser >/dev/null 2>&1; then
                echo -e "${CYAN}🧹 Limpiando puerto $FRONTEND_PORT...${NC}"
                fuser -k $FRONTEND_PORT/tcp 2>/dev/null || true
                sleep 1
            fi
            ;;
    esac

    # Limpiar procesos zombi
    echo -e "${CYAN}🧟 Limpiando procesos zombi...${NC}"
    ps aux | awk '$8 ~ /^Z/ { print $2 }' | xargs -r kill -9 2>/dev/null || true
}

# Función mejorada para iniciar backend
start_backend() {
    echo -e "${CYAN}🐍 INICIANDO BACKEND...${NC}"

    # Rotar logs si es necesario
    rotate_logs

    # Verificar puerto disponible
    if ! check_port "$BACKEND_PORT" "Backend"; then
        echo -e "${RED}💥 Abortando inicio del backend${NC}"
        return 1
    fi

    # Verificar directorio
    if [ ! -d "$PROJECT_DIR/app" ]; then
        echo -e "${RED}❌ Error: Directorio app/ no encontrado en $PROJECT_DIR${NC}"
        return 1
    fi

    # Cambiar al directorio del proyecto
    cd "$PROJECT_DIR" || return 1

    # Activar entorno virtual si existe
    if [ -f ".venv/bin/activate" ]; then
        echo -e "${CYAN}🔧 Activando entorno virtual...${NC}"
        source .venv/bin/activate
    else
        echo -e "${YELLOW}⚠️ Entorno virtual no encontrado${NC}"
    fi

    # Verificar dependencias críticas
    echo -e "${CYAN}📦 Verificando dependencias...${NC}"
    python -c "import fastapi, uvicorn" 2>/dev/null || {
        echo -e "${RED}❌ Error: FastAPI/Uvicorn no instalados${NC}"
        return 1
    }

    # Iniciar backend en background con logging
    echo -e "${CYAN}🚀 Iniciando uvicorn en $BACKEND_HOST:$BACKEND_PORT...${NC}"

    nohup python -m uvicorn app.main:app \
        --reload \
        --reload-dir ./app \
        --host "$BACKEND_HOST" \
        --port "$BACKEND_PORT" \
        > "$BACKEND_LOG" 2>&1 &

    local pid=$!
    echo "$pid" > "$BACKEND_PID_FILE"
    echo -e "${GREEN}🆔 PID: $pid${NC}"

    # Health check mejorado
    if health_check "Backend" "http://$BACKEND_HOST:$BACKEND_PORT/health"; then
        echo -e "${GREEN}🌐 URL: http://$BACKEND_HOST:$BACKEND_PORT${NC}"
        echo -e "${GREEN}📚 Docs: http://$BACKEND_HOST:$BACKEND_PORT/docs${NC}"
        echo -e "${CYAN}📋 Mostrando logs en tiempo real (Ctrl+C para menú)...${NC}"
        echo ""
        sleep 1
        show_logs "backend"
        return 0
    else
        echo -e "${RED}💥 Backend falló al iniciar${NC}"
        kill_process "$BACKEND_PID_FILE" "Backend"
        return 1
    fi
}

# Función mejorada para iniciar frontend
start_frontend() {
    echo -e "${CYAN}⚛️ INICIANDO FRONTEND...${NC}"

    # Rotar logs si es necesario
    rotate_logs

    # Verificar puerto disponible
    if ! check_port "$FRONTEND_PORT" "Frontend"; then
        echo -e "${RED}💥 Abortando inicio del frontend${NC}"
        return 1
    fi

    # Verificar directorio frontend
    if [ ! -d "$PROJECT_DIR/frontend" ]; then
        echo -e "${RED}❌ Error: Directorio frontend/ no encontrado${NC}"
        return 1
    fi

    # Cambiar al directorio frontend
    cd "$PROJECT_DIR/frontend" || return 1

    # Verificar package.json
    if [ ! -f "package.json" ]; then
        echo -e "${RED}❌ Error: package.json no encontrado${NC}"
        return 1
    fi

    # Verificar Node.js
    if ! command -v node >/dev/null 2>&1; then
        echo -e "${RED}❌ Error: Node.js no instalado${NC}"
        return 1
    fi

    # Verificar node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${CYAN}📦 Instalando dependencias...${NC}"
        npm install || {
            echo -e "${RED}❌ Error instalando dependencias${NC}"
            return 1
        }
    fi

    # Verificar script dev existe
    if ! npm run dev --dry-run >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️ Script 'dev' no encontrado en package.json${NC}"
    fi

    # Iniciar frontend en background con logging
    echo -e "${CYAN}🚀 Iniciando Vite dev server en $FRONTEND_HOST:$FRONTEND_PORT...${NC}"

    nohup npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" \
        > "$FRONTEND_LOG" 2>&1 &

    local pid=$!
    echo "$pid" > "$FRONTEND_PID_FILE"
    echo -e "${GREEN}🆔 PID: $pid${NC}"

    # Health check mejorado
    if health_check "Frontend" "http://$FRONTEND_HOST:$FRONTEND_PORT"; then
        echo -e "${GREEN}🌐 URL: http://$FRONTEND_HOST:$FRONTEND_PORT${NC}"
        echo -e "${CYAN}📋 Mostrando logs en tiempo real (Ctrl+C para menú)...${NC}"
        echo ""
        sleep 1
        show_logs "frontend"
        return 0
    else
        echo -e "${RED}💥 Frontend falló al iniciar${NC}"
        kill_process "$FRONTEND_PID_FILE" "Frontend"
        return 1
    fi
}

# Función para obtener tiempo de uptime de un proceso
get_process_uptime() {
    local pid_file="$1"
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
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

# Función para crear barra de estado visual
create_status_bar() {
    local service="$1"
    local is_running="$2"
    local pid="$3"
    local url="$4"
    local uptime="$5"

    if [ "$is_running" = "true" ]; then
        echo -e "${BRIGHT_GREEN}┌─ $service ${CHECK_MARK} ACTIVO ─────────────────────────────────────────────┐${NC}"
        echo -e "${GREEN}│ PID: ${WHITE}$pid${GREEN} │ Uptime: ${WHITE}$uptime${GREEN} │ URL: ${BRIGHT_CYAN}$url${GREEN} │${NC}"
        echo -e "${BRIGHT_GREEN}└──────────────────────────────────────────────────────────────────────┘${NC}"
    else
        echo -e "${BRIGHT_RED}┌─ $service ${CROSS_MARK} INACTIVO ──────────────────────────────────────────┐${NC}"
        echo -e "${RED}│ Servicio detenido - Use las opciones del menú para iniciar          │${NC}"
        echo -e "${BRIGHT_RED}└──────────────────────────────────────────────────────────────────────┘${NC}"
    fi
}

# Función mejorada para mostrar estado de servicios
show_status() {
    echo -e "${BRIGHT_CYAN}${LOG} PANEL DE CONTROL - ESTADO DE SERVICIOS${NC}"
    echo ""

    # Backend status
    if is_process_running "$BACKEND_PID_FILE" "uvicorn"; then
        local pid=$(cat "$BACKEND_PID_FILE")
        local uptime=$(get_process_uptime "$BACKEND_PID_FILE")
        local url="http://$BACKEND_HOST:$BACKEND_PORT"
        create_status_bar "🐍 BACKEND API" "true" "$pid" "$url" "$uptime"
        echo -e "${GRAY}   └─ Documentación: ${CYAN}http://$BACKEND_HOST:$BACKEND_PORT/docs${NC}"
    else
        create_status_bar "🐍 BACKEND API" "false" "" "" ""
    fi

    echo ""

    # Frontend status
    if is_process_running "$FRONTEND_PID_FILE" "node"; then
        local pid=$(cat "$FRONTEND_PID_FILE")
        local uptime=$(get_process_uptime "$FRONTEND_PID_FILE")
        local url="http://$FRONTEND_HOST:$FRONTEND_PORT"
        create_status_bar "⚛️  FRONTEND WEB" "true" "$pid" "$url" "$uptime"
    else
        create_status_bar "⚛️  FRONTEND WEB" "false" "" "" ""
    fi

    echo ""
}

# Función para formatear timestamp
format_timestamp() {
    echo "${GRAY}[$(date '+%H:%M:%S')]${NC}"
}

# Función mejorada para mostrar logs en tiempo real con colores y formato
show_logs() {
    local service="$1"

    case "$service" in
        "backend")
            echo -e "${BRIGHT_CYAN}┌─ 🐍 LOGS BACKEND EN TIEMPO REAL ─────────────────────────────────────────────────┐${NC}"
            echo -e "${BRIGHT_CYAN}│ Presiona Ctrl+C para volver al menú                                 │${NC}"
            echo -e "${BRIGHT_CYAN}└──────────────────────────────────────────────────────────────────────────────────┘${NC}"
            echo ""
            tail -f "$BACKEND_LOG" 2>/dev/null | while IFS= read -r line; do
                local timestamp=$(format_timestamp)
                # Colorear logs según contenido con mejor formato
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
            done || echo -e "${RED}${CROSS_MARK} Log no encontrado: $BACKEND_LOG${NC}"
            ;;
        "frontend")
            echo -e "${BRIGHT_CYAN}┌─ ⚛️  LOGS FRONTEND EN TIEMPO REAL ─────────────────────────────────────────────┐${NC}"
            echo -e "${BRIGHT_CYAN}│ Presiona Ctrl+C para volver al menú                                 │${NC}"
            echo -e "${BRIGHT_CYAN}└──────────────────────────────────────────────────────────────────────────────────┘${NC}"
            echo ""
            tail -f "$FRONTEND_LOG" 2>/dev/null | while IFS= read -r line; do
                local timestamp=$(format_timestamp)
                # Colorear logs según contenido con mejor formato
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
            done || echo -e "${RED}${CROSS_MARK} Log no encontrado: $FRONTEND_LOG${NC}"
            ;;
        "both")
            echo -e "${BRIGHT_CYAN}┌─ 📋 LOGS COMBINADOS EN TIEMPO REAL ────────────────────────────────────────────┐${NC}"
            echo -e "${BRIGHT_CYAN}│ Presiona Ctrl+C para volver al menú                                 │${NC}"
            echo -e "${BRIGHT_CYAN}└──────────────────────────────────────────────────────────────────────────────────┘${NC}"
            echo ""
            (
                tail -f "$BACKEND_LOG" 2>/dev/null | while IFS= read -r line; do
                    local timestamp=$(format_timestamp)
                    if [[ "$line" == *"INFO"* ]]; then
                        echo -e "$timestamp ${BRIGHT_GREEN}[🐍 BACKEND]${NC} ${GREEN}$line${NC}"
                    elif [[ "$line" == *"ERROR"* ]]; then
                        echo -e "$timestamp ${BRIGHT_RED}[🐍 BACKEND]${NC} ${RED}$line${NC}"
                    elif [[ "$line" == *"WARNING"* ]]; then
                        echo -e "$timestamp ${BRIGHT_YELLOW}[🐍 BACKEND]${NC} ${YELLOW}$line${NC}"
                    else
                        echo -e "$timestamp ${CYAN}[🐍 BACKEND]${NC} $line"
                    fi
                done &

                tail -f "$FRONTEND_LOG" 2>/dev/null | while IFS= read -r line; do
                    local timestamp=$(format_timestamp)
                    if [[ "$line" == *"✓"* ]] || [[ "$line" == *"ready"* ]]; then
                        echo -e "$timestamp ${BRIGHT_GREEN}[⚛️  FRONTEND]${NC} ${GREEN}$line${NC}"
                    elif [[ "$line" == *"error"* ]]; then
                        echo -e "$timestamp ${BRIGHT_RED}[⚛️  FRONTEND]${NC} ${RED}$line${NC}"
                    elif [[ "$line" == *"warning"* ]]; then
                        echo -e "$timestamp ${BRIGHT_YELLOW}[⚛️  FRONTEND]${NC} ${YELLOW}$line${NC}"
                    else
                        echo -e "$timestamp ${BLUE}[⚛️  FRONTEND]${NC} $line"
                    fi
                done &

                wait
            )
            ;;
    esac
}

# Función para mostrar ayuda
show_help() {
    clear_screen
    echo -e "${BRIGHT_CYAN}┌─ 📚 AYUDA - MESTOCKER PROJECT MANAGER v3.0 ─────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│                                                                       │${NC}"
    echo -e "${CYAN}│ ${BRIGHT_WHITE}ATAJOS DE TECLADO:${NC}                                                  ${CYAN}│${NC}"
    echo -e "${CYAN}│ • Números 1-9: Ejecutar opción correspondiente                       │${NC}"
    echo -e "${CYAN}│ • 's' o 'S': Refrescar estado de servicios                           │${NC}"
    echo -e "${CYAN}│ • 'h' o 'H': Mostrar esta ayuda                                      │${NC}"
    echo -e "${CYAN}│ • '0': Salir y detener todos los servicios                           │${NC}"
    echo -e "${CYAN}│                                                                       │${NC}"
    echo -e "${CYAN}│ ${BRIGHT_WHITE}FUNCIONALIDADES AVANZADAS:${NC}                                         ${CYAN}│${NC}"
    echo -e "${CYAN}│ • Validación automática de puertos ocupados                          │${NC}"
    echo -e "${CYAN}│ • Rotación automática de logs (>10MB)                                │${NC}"
    echo -e "${CYAN}│ • Health checks robustos con 15 reintentos                           │${NC}"
    echo -e "${CYAN}│ • Limpieza de procesos zombi                                         │${NC}"
    echo -e "${CYAN}│ • Configuración externa via config.env                               │${NC}"
    echo -e "${CYAN}│ • Monitoreo en tiempo real con colores                               │${NC}"
    echo -e "${CYAN}│                                                                       │${NC}"
    echo -e "${CYAN}│ ${BRIGHT_WHITE}UBICACIONES DE ARCHIVOS:${NC}                                           ${CYAN}│${NC}"
    echo -e "${CYAN}│ • Proyecto: ${WHITE}$PROJECT_DIR${NC}                      ${CYAN}│${NC}"
    echo -e "${CYAN}│ • Logs: ${WHITE}$LOG_DIR${NC}                           ${CYAN}│${NC}"
    echo -e "${CYAN}│ • PIDs: ${WHITE}/tmp/mestocker_*.pid${NC}                            ${CYAN}│${NC}"
    echo -e "${CYAN}│                                                                       │${NC}"
    echo -e "${CYAN}│ ${BRIGHT_WHITE}URLS DE SERVICIOS:${NC}                                                 ${CYAN}│${NC}"
    echo -e "${CYAN}│ • Backend API: ${BRIGHT_CYAN}http://$BACKEND_HOST:$BACKEND_PORT${NC}                   ${CYAN}│${NC}"
    echo -e "${CYAN}│ • Backend Docs: ${BRIGHT_CYAN}http://$BACKEND_HOST:$BACKEND_PORT/docs${NC}              ${CYAN}│${NC}"
    echo -e "${CYAN}│ • Frontend Web: ${BRIGHT_CYAN}http://$FRONTEND_HOST:$FRONTEND_PORT${NC}                 ${CYAN}│${NC}"
    echo -e "${CYAN}│                                                                       │${NC}"
    echo -e "${BRIGHT_CYAN}└───────────────────────────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    echo -e "${CYAN}${INFO} Presiona Enter para volver al menú principal...${NC}"
    read -r
}

# Función para manejar señal SIGINT (Ctrl+C)
handle_interrupt() {
    echo -e "\n${CYAN}🔄 Regresando al menú...${NC}"
    sleep 1
    show_menu
}

# Función para mostrar menú mejorado
show_menu() {
    # Configurar trap para Ctrl+C
    trap handle_interrupt SIGINT

    while true; do
        clear_screen
        show_status

        echo -e "${BRIGHT_CYAN}🎛️  PANEL DE CONTROL - OPCIONES DISPONIBLES${NC}"
        echo ""
        echo -e "${BRIGHT_GREEN}┌─ GESTIÓN DE SERVICIOS ─────────────────┐${NC}"
        echo -e "${GREEN}│ ${ROCKET} 1  Iniciar Backend                │${NC}"
        echo -e "${GREEN}│ ${ROCKET} 2  Iniciar Frontend               │${NC}"
        echo -e "${YELLOW}│ 🔄 3  Reload Backend                  │${NC}"
        echo -e "${YELLOW}│ 🔄 4  Reload Frontend                 │${NC}"
        echo -e "${RED}│ 🛑 8  Detener Backend                 │${NC}"
        echo -e "${RED}│ 🛑 9  Detener Frontend                │${NC}"
        echo -e "${BRIGHT_GREEN}└─────────────────────────────────────────┘${NC}"
        echo ""
        echo -e "${BRIGHT_BLUE}┌─ MONITOREO Y LOGS ─────────────────────┐${NC}"
        echo -e "${BLUE}│ ${LOG} 5  Ver Logs Backend               │${NC}"
        echo -e "${BLUE}│ ${LOG} 6  Ver Logs Frontend              │${NC}"
        echo -e "${BLUE}│ ${LOG} 7  Ver Logs Combinados            │${NC}"
        echo -e "${PURPLE}│ ${WATCHDOG} w  Iniciar/Detener Watchdog        │${NC}"
        echo -e "${PURPLE}│ 📊 s  Mostrar Estado (refresh)        │${NC}"
        echo -e "${BRIGHT_BLUE}└─────────────────────────────────────────┘${NC}"
        echo ""
        echo -e "${BRIGHT_RED}┌─ SISTEMA ──────────────────────────────┐${NC}"
        echo -e "${WHITE}│ 🚪 0  Salir y Detener Todo            │${NC}"
        echo -e "${WHITE}│ 🆘 h  Mostrar Ayuda                   │${NC}"
        echo -e "${BRIGHT_RED}└─────────────────────────────────────────┘${NC}"
        echo ""
        echo -ne "${BRIGHT_CYAN}💻 Selecciona una opción [0-9,s,w,h]: ${NC}"

        read -r option
        
        case "$option" in
            1)
                echo ""
                echo -e "${BRIGHT_GREEN}${ROCKET} Iniciando Backend...${NC}"
                show_progress 3 "Preparando backend"
                kill_process "$BACKEND_PID_FILE" "Backend"
                start_backend
                ;;
            2)
                echo ""
                echo -e "${BRIGHT_GREEN}${ROCKET} Iniciando Frontend...${NC}"
                show_progress 3 "Preparando frontend"
                kill_process "$FRONTEND_PID_FILE" "Frontend"
                start_frontend
                ;;
            3)
                echo ""
                echo -e "${BRIGHT_YELLOW}🔄 Recargando Backend...${NC}"
                show_progress 2 "Reiniciando servicio"
                kill_process "$BACKEND_PID_FILE" "Backend"
                sleep 1
                start_backend
                ;;
            4)
                echo ""
                echo -e "${BRIGHT_YELLOW}🔄 Recargando Frontend...${NC}"
                show_progress 2 "Reiniciando servicio"
                kill_process "$FRONTEND_PID_FILE" "Frontend"
                sleep 1
                start_frontend
                ;;
            5)
                clear_screen
                show_logs "backend"
                ;;
            6)
                clear_screen
                show_logs "frontend"
                ;;
            7)
                clear_screen
                show_logs "both"
                ;;
            8)
                echo ""
                echo -e "${BRIGHT_RED}🛑 Deteniendo Backend...${NC}"
                kill_process "$BACKEND_PID_FILE" "Backend"
                echo ""
                echo -e "${CYAN}${INFO} Presiona Enter para continuar...${NC}"
                read -r
                ;;
            9)
                echo ""
                echo -e "${BRIGHT_RED}🛑 Deteniendo Frontend...${NC}"
                kill_process "$FRONTEND_PID_FILE" "Frontend"
                echo ""
                echo -e "${CYAN}${INFO} Presiona Enter para continuar...${NC}"
                read -r
                ;;
            s|S)
                # Solo refresh, no hace nada, el bucle se encarga
                ;;
            w|W)
                echo ""
                if [ -f "$WATCHDOG_PID_FILE" ] && ps -p "$(cat "$WATCHDOG_PID_FILE")" > /dev/null 2>&1; then
                    stop_watchdog
                else
                    start_watchdog
                fi
                echo ""
                echo -e "${CYAN}${INFO} Presiona Enter para continuar...${NC}"
                read -r
                ;;
            h|H)
                show_help
                ;;
            0)
                echo ""
                echo -e "${BRIGHT_RED}🛑 Deteniendo todos los servicios...${NC}"
                show_progress 5 "Cerrando servicios"
                stop_watchdog
                kill_process "$BACKEND_PID_FILE" "Backend"
                kill_process "$FRONTEND_PID_FILE" "Frontend"
                echo ""
                echo -e "${BRIGHT_GREEN}👋 ¡Gracias por usar MeStore Manager!${NC}"
                exit 0
                ;;
            *)
                echo ""
                echo -e "${BRIGHT_RED}${CROSS_MARK} Opción inválida. Usa 0-9, s, o h${NC}"
                sleep 2
                ;;
        esac
    done
}

# Función principal
main() {
    # Verificar directorio del proyecto
    if [ ! -d "$PROJECT_DIR" ]; then
        echo -e "${RED}❌ Error: Directorio del proyecto no encontrado: $PROJECT_DIR${NC}"
        exit 1
    fi
    
    # Setup inicial
    setup_logs
    
    # Mostrar menú
    show_menu
}

# Ejecutar función principal
main "$@"
