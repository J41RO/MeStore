#!/bin/bash
# ~/scripts/project_manager_v2.sh
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Gestor de Proyecto Completo v2.0
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: project_manager_v2.sh
# Propósito: Gestión completa de backend y frontend con menú interactivo
# Funcionalidades: Inicio/parada automática, reload, logging, detección de procesos
# v2.0: Menú unificado CYAN, logs automáticos, colores verde/rojo en logs
#
# ---------------------------------------------------------------------------------------------

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Variables globales
PROJECT_DIR="/home/admin-jairo/MeStore"
BACKEND_PORT=8000
FRONTEND_PORT=5173
BACKEND_HOST="192.168.1.137"
FRONTEND_HOST="localhost"

# PID files para tracking
BACKEND_PID_FILE="/tmp/mestocker_backend.pid"
FRONTEND_PID_FILE="/tmp/mestocker_frontend.pid"

# Log files
LOG_DIR="$PROJECT_DIR/logs"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

# Función para limpiar pantalla
clear_screen() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    🏗️ MESTOCKER PROJECT MANAGER v2.0          ║${NC}"
    echo -e "${CYAN}║                        Gestión Completa Optimizada            ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Función para crear directorio de logs
setup_logs() {
    mkdir -p "$LOG_DIR"
    touch "$BACKEND_LOG" "$FRONTEND_LOG"
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

# Función para matar proceso
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
    
    # Buscar y matar procesos adicionales por puerto/nombre
    case "$service_name" in
        "Backend")
            pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
            pkill -f "python.*uvicorn" 2>/dev/null || true
            ;;
        "Frontend")
            pkill -f "vite.*dev" 2>/dev/null || true
            pkill -f "node.*vite" 2>/dev/null || true
            ;;
    esac
}

# Función para iniciar backend
start_backend() {
    echo -e "${CYAN}🐍 INICIANDO BACKEND...${NC}"
    
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
    
    # Esperar a que inicie
    echo -e "${CYAN}⏱️ Esperando inicio del backend...${NC}"
    for i in {1..10}; do
        if curl -s "http://$BACKEND_HOST:$BACKEND_PORT/health" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend iniciado exitosamente!${NC}"
            echo -e "${GREEN}🌐 URL: http://$BACKEND_HOST:$BACKEND_PORT${NC}"
            echo -e "${GREEN}📚 Docs: http://$BACKEND_HOST:$BACKEND_PORT/docs${NC}"
            echo -e "${GREEN}🆔 PID: $pid${NC}"
            echo -e "${CYAN}📋 Mostrando logs en tiempo real (Ctrl+C para menú)...${NC}"
            echo ""
            sleep 1
            show_logs "backend"
            return 0
        fi
        sleep 1
        echo -ne "${CYAN}.${NC}"
    done
    
    echo -e "\n${RED}❌ Backend no respondió en tiempo esperado${NC}"
    return 1
}

# Función para iniciar frontend
start_frontend() {
    echo -e "${CYAN}⚛️ INICIANDO FRONTEND...${NC}"
    
    # Verificar directorio frontend
    if [ ! -d "$PROJECT_DIR/frontend" ]; then
        echo -e "${RED}❌ Error: Directorio frontend/ no encontrado${NC}"
        return 1
    fi
    
    # Cambiar al directorio frontend
    cd "$PROJECT_DIR/frontend" || return 1
    
    # Verificar node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${CYAN}📦 Instalando dependencias...${NC}"
        npm install || {
            echo -e "${RED}❌ Error instalando dependencias${NC}"
            return 1
        }
    fi
    
    # Verificar package.json
    if [ ! -f "package.json" ]; then
        echo -e "${RED}❌ Error: package.json no encontrado${NC}"
        return 1
    fi
    
    # Iniciar frontend en background con logging
    echo -e "${CYAN}🚀 Iniciando Vite dev server en $FRONTEND_HOST:$FRONTEND_PORT...${NC}"
    
    nohup npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" \
        > "$FRONTEND_LOG" 2>&1 &
    
    local pid=$!
    echo "$pid" > "$FRONTEND_PID_FILE"
    
    # Esperar a que inicie
    echo -e "${CYAN}⏱️ Esperando inicio del frontend...${NC}"
    for i in {1..15}; do
        if curl -s "http://$FRONTEND_HOST:$FRONTEND_PORT" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Frontend iniciado exitosamente!${NC}"
            echo -e "${GREEN}🌐 URL: http://$FRONTEND_HOST:$FRONTEND_PORT${NC}"
            echo -e "${GREEN}🆔 PID: $pid${NC}"
            echo -e "${CYAN}📋 Mostrando logs en tiempo real (Ctrl+C para menú)...${NC}"
            echo ""
            sleep 1
            show_logs "frontend"
            return 0
        fi
        sleep 1
        echo -ne "${CYAN}.${NC}"
    done
    
    echo -e "\n${RED}❌ Frontend no respondió en tiempo esperado${NC}"
    return 1
}

# Función para mostrar estado de servicios
show_status() {
    echo -e "${CYAN}📊 ESTADO DE SERVICIOS:${NC}"
    echo ""
    
    # Backend status
    if is_process_running "$BACKEND_PID_FILE" "uvicorn"; then
        local pid=$(cat "$BACKEND_PID_FILE")
        echo -e "${GREEN}🐍 Backend: ✅ CORRIENDO (PID: $pid)${NC}"
        echo -e "${GREEN}   URL: http://$BACKEND_HOST:$BACKEND_PORT${NC}"
        echo -e "${GREEN}   Docs: http://$BACKEND_HOST:$BACKEND_PORT/docs${NC}"
    else
        echo -e "${RED}🐍 Backend: ❌ DETENIDO${NC}"
    fi
    
    echo ""
    
    # Frontend status
    if is_process_running "$FRONTEND_PID_FILE" "node"; then
        local pid=$(cat "$FRONTEND_PID_FILE")
        echo -e "${GREEN}⚛️ Frontend: ✅ CORRIENDO (PID: $pid)${NC}"
        echo -e "${GREEN}   URL: http://$FRONTEND_HOST:$FRONTEND_PORT${NC}"
    else
        echo -e "${RED}⚛️ Frontend: ❌ DETENIDO${NC}"
    fi
    
    echo ""
}

# Función para mostrar logs en tiempo real con colores
show_logs() {
    local service="$1"
    
    case "$service" in
        "backend")
            echo -e "${CYAN}📋 LOGS BACKEND (Ctrl+C para volver al menú):${NC}"
            echo ""
            tail -f "$BACKEND_LOG" 2>/dev/null | while IFS= read -r line; do
                # Colorear logs según contenido
                if [[ "$line" == *"INFO"* ]]; then
                    echo -e "${GREEN}$line${NC}"
                elif [[ "$line" == *"ERROR"* ]] || [[ "$line" == *"error"* ]]; then
                    echo -e "${RED}$line${NC}"
                elif [[ "$line" == *"WARNING"* ]] || [[ "$line" == *"warning"* ]]; then
                    echo -e "${YELLOW}$line${NC}"
                else
                    echo "$line"
                fi
            done || echo "Log no encontrado"
            ;;
        "frontend")
            echo -e "${CYAN}📋 LOGS FRONTEND (Ctrl+C para volver al menú):${NC}"
            echo ""
            tail -f "$FRONTEND_LOG" 2>/dev/null | while IFS= read -r line; do
                # Colorear logs según contenido
                if [[ "$line" == *"✓"* ]] || [[ "$line" == *"ready"* ]] || [[ "$line" == *"compiled"* ]]; then
                    echo -e "${GREEN}$line${NC}"
                elif [[ "$line" == *"error"* ]] || [[ "$line" == *"Error"* ]] || [[ "$line" == *"✗"* ]]; then
                    echo -e "${RED}$line${NC}"
                elif [[ "$line" == *"warning"* ]] || [[ "$line" == *"Warning"* ]]; then
                    echo -e "${YELLOW}$line${NC}"
                else
                    echo "$line"
                fi
            done || echo "Log no encontrado"
            ;;
        "both")
            echo -e "${CYAN}📋 LOGS COMBINADOS (Ctrl+C para volver al menú):${NC}"
            echo ""
            (
                tail -f "$BACKEND_LOG" 2>/dev/null | while IFS= read -r line; do
                    if [[ "$line" == *"INFO"* ]]; then
                        echo -e "${CYAN}[BACKEND]${NC} ${GREEN}$line${NC}"
                    elif [[ "$line" == *"ERROR"* ]]; then
                        echo -e "${CYAN}[BACKEND]${NC} ${RED}$line${NC}"
                    else
                        echo -e "${CYAN}[BACKEND]${NC} $line"
                    fi
                done &
                
                tail -f "$FRONTEND_LOG" 2>/dev/null | while IFS= read -r line; do
                    if [[ "$line" == *"✓"* ]] || [[ "$line" == *"ready"* ]]; then
                        echo -e "${BLUE}[FRONTEND]${NC} ${GREEN}$line${NC}"
                    elif [[ "$line" == *"error"* ]]; then
                        echo -e "${BLUE}[FRONTEND]${NC} ${RED}$line${NC}"
                    else
                        echo -e "${BLUE}[FRONTEND]${NC} $line"
                    fi
                done &
                
                wait
            )
            ;;
    esac
}

# Función para manejar señal SIGINT (Ctrl+C)
handle_interrupt() {
    echo -e "\n${CYAN}🔄 Regresando al menú...${NC}"
    sleep 1
    show_menu
}

# Función para mostrar menú
show_menu() {
    # Configurar trap para Ctrl+C
    trap handle_interrupt SIGINT
    
    while true; do
        clear_screen
        show_status
        
        echo -e "${CYAN}📋 OPCIONES DISPONIBLES:${NC}"
        echo ""
        echo -e "${CYAN}1️⃣  Iniciar Backend${NC}"
        echo -e "${CYAN}2️⃣  Iniciar Frontend${NC}"
        echo -e "${CYAN}3️⃣  Reload Backend${NC}"
        echo -e "${CYAN}4️⃣  Reload Frontend${NC}"
        echo -e "${CYAN}5️⃣  Ver Logs Backend${NC}"
        echo -e "${CYAN}6️⃣  Ver Logs Frontend${NC}"
        echo -e "${CYAN}7️⃣  Ver Logs Combinados${NC}"
        echo -e "${CYAN}8️⃣  Detener Backend${NC}"
        echo -e "${CYAN}9️⃣  Detener Frontend${NC}"
        echo -e "${CYAN}0️⃣  Salir${NC}"
        echo ""
        echo -ne "${CYAN}Selecciona una opción [0-9]: ${NC}"
        
        read -r option
        
        case "$option" in
            1)
                echo ""
                kill_process "$BACKEND_PID_FILE" "Backend"
                start_backend
                # Los logs se muestran automáticamente
                ;;
            2)
                echo ""
                kill_process "$FRONTEND_PID_FILE" "Frontend"
                start_frontend
                # Los logs se muestran automáticamente
                ;;
            3)
                echo ""
                echo -e "${CYAN}🔄 Reloading Backend...${NC}"
                kill_process "$BACKEND_PID_FILE" "Backend"
                sleep 1
                start_backend
                # Los logs se muestran automáticamente
                ;;
            4)
                echo ""
                echo -e "${CYAN}🔄 Reloading Frontend...${NC}"
                kill_process "$FRONTEND_PID_FILE" "Frontend"
                sleep 1
                start_frontend
                # Los logs se muestran automáticamente
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
                kill_process "$BACKEND_PID_FILE" "Backend"
                echo ""
                echo -e "${CYAN}Presiona Enter para continuar...${NC}"
                read -r
                ;;
            9)
                echo ""
                kill_process "$FRONTEND_PID_FILE" "Frontend"
                echo ""
                echo -e "${CYAN}Presiona Enter para continuar...${NC}"
                read -r
                ;;
            0)
                echo ""
                echo -e "${CYAN}🛑 Deteniendo todos los servicios...${NC}"
                kill_process "$BACKEND_PID_FILE" "Backend"
                kill_process "$FRONTEND_PID_FILE" "Frontend"
                echo ""
                echo -e "${GREEN}👋 ¡Hasta luego!${NC}"
                exit 0
                ;;
            *)
                echo ""
                echo -e "${RED}❌ Opción inválida. Intenta de nuevo.${NC}"
                sleep 1
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
