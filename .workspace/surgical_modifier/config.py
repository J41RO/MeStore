"""Configuración centralizada de Surgical Modifier."""

import os

# Configuración por defecto
DEFAULT_CONFIG = {
    "backup_enabled": True,
    "verbose": False,
    "dry_run": False,
}

# Variables de entorno
BACKUP_DIR = os.getenv("SURGICAL_BACKUP_DIR", ".backup")
LOG_LEVEL = os.getenv("SURGICAL_LOG_LEVEL", "INFO")
