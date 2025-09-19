#!/bin/bash
# Log Rotator - Mantiene logs por 7 días y limpia archivos antiguos
# v1.0 - Rotación automática con backup

PROJECT_DIR="/home/admin-jairo/MeStore"
LOGS_DIR="$PROJECT_DIR/logs"
BACKUP_DIR="$LOGS_DIR/backups"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_rotator() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] LOG-ROTATOR: $1${NC}"
}

rotate_logs() {
    log_rotator "🔄 Iniciando rotación de logs..."

    # Crear directorio de backups si no existe
    mkdir -p "$BACKUP_DIR"

    local rotated=0
    local cleaned=0

    # Lista de logs a rotar
    local logs=(
        "backend.log"
        "frontend.log"
        "backend_daemon.log"
        "frontend_daemon.log"
        "backend_watchdog.log"
        "frontend_watchdog.log"
        "status.log"
        "health_monitor.log"
    )

    # Rotar cada log si existe y tiene contenido
    for log_file in "${logs[@]}"; do
        local log_path="$LOGS_DIR/$log_file"

        if [ -f "$log_path" ] && [ -s "$log_path" ]; then
            local backup_name="${log_file%.log}_$(date '+%Y%m%d_%H%M%S').log"
            local backup_path="$BACKUP_DIR/$backup_name"

            # Mover log actual a backup
            mv "$log_path" "$backup_path"

            # Crear nuevo log vacío
            touch "$log_path"

            # Comprimir backup para ahorrar espacio
            gzip "$backup_path"

            log_rotator "📦 Rotado: $log_file → ${backup_name}.gz"
            rotated=$((rotated + 1))
        fi
    done

    # Limpiar backups antiguos (más de 7 días)
    local old_backups=$(find "$BACKUP_DIR" -name "*.log.gz" -mtime +7 2>/dev/null)
    if [ -n "$old_backups" ]; then
        echo "$old_backups" | while read -r backup; do
            rm -f "$backup"
            log_rotator "🗑️ Eliminado backup antiguo: $(basename "$backup")"
            cleaned=$((cleaned + 1))
        done
    fi

    # Limpiar logs huérfanos (archivos .log que no están en la lista)
    find "$LOGS_DIR" -maxdepth 1 -name "*.log" -mtime +1 2>/dev/null | while read -r orphan; do
        local basename_orphan=$(basename "$orphan")
        local is_known=false

        for known_log in "${logs[@]}"; do
            if [ "$basename_orphan" = "$known_log" ]; then
                is_known=true
                break
            fi
        done

        if [ "$is_known" = false ]; then
            rm -f "$orphan"
            log_rotator "🧹 Eliminado log huérfano: $basename_orphan"
            cleaned=$((cleaned + 1))
        fi
    done

    log_rotator "✅ Rotación completa: $rotated rotados, $cleaned limpiados"
}

get_log_stats() {
    echo -e "${GREEN}=== ESTADÍSTICAS DE LOGS ===${NC}"

    # Stats de logs actuales
    echo -e "${YELLOW}Logs actuales:${NC}"
    if [ -d "$LOGS_DIR" ]; then
        find "$LOGS_DIR" -maxdepth 1 -name "*.log" -exec ls -lh {} \; | while read -r line; do
            echo "  $line"
        done
    fi

    # Stats de backups
    echo -e "${YELLOW}Backups (últimos 7 días):${NC}"
    if [ -d "$BACKUP_DIR" ]; then
        local backup_count=$(find "$BACKUP_DIR" -name "*.log.gz" | wc -l)
        local backup_size=$(find "$BACKUP_DIR" -name "*.log.gz" -exec du -ch {} + 2>/dev/null | tail -n1 | cut -f1)
        echo "  Archivos: $backup_count"
        echo "  Tamaño total: ${backup_size:-0}"
    fi

    # Uso de disco del directorio logs
    echo -e "${YELLOW}Uso de disco logs/:${NC}"
    du -sh "$LOGS_DIR" 2>/dev/null || echo "  No disponible"
}

setup_cron() {
    log_rotator "⏰ Configurando rotación automática diaria..."

    # Agregar cron job si no existe
    local cron_job="0 2 * * * $PROJECT_DIR/log_rotator.sh rotate >/dev/null 2>&1"
    local cron_exists=$(crontab -l 2>/dev/null | grep -F "$PROJECT_DIR/log_rotator.sh")

    if [ -z "$cron_exists" ]; then
        (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
        log_rotator "✅ Cron job agregado: rotación diaria a las 2:00 AM"
    else
        log_rotator "ℹ️ Cron job ya existe"
    fi
}

remove_cron() {
    log_rotator "⏰ Removiendo rotación automática..."

    local temp_cron=$(mktemp)
    crontab -l 2>/dev/null | grep -v "$PROJECT_DIR/log_rotator.sh" > "$temp_cron"
    crontab "$temp_cron"
    rm -f "$temp_cron"

    log_rotator "✅ Cron job removido"
}

case "$1" in
    rotate)
        rotate_logs
        ;;
    stats)
        get_log_stats
        ;;
    setup-cron)
        setup_cron
        ;;
    remove-cron)
        remove_cron
        ;;
    *)
        echo "Uso: $0 {rotate|stats|setup-cron|remove-cron}"
        echo ""
        echo "  rotate      - Rotar logs y limpiar backups antiguos"
        echo "  stats       - Mostrar estadísticas de logs"
        echo "  setup-cron  - Configurar rotación automática diaria"
        echo "  remove-cron - Remover rotación automática"
        exit 1
        ;;
esac
