"""Configuración centralizada de Surgical Modifier."""

import os
from pathlib import Path
from typing import Any, Dict

# Directorio base del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
BACKUP_DIR = Path(os.getenv("SURGICAL_BACKUP_DIR", PROJECT_ROOT / ".backup"))

# Configuración por defecto
DEFAULT_CONFIG: Dict[str, Any] = {
    "version": "0.1.0",
    "backup_enabled": True,
    "verbose": False,
    "dry_run": False,
    "max_backup_files": 50,
    "backup_retention_days": 30,
    "supported_extensions": [
        ".py", ".js", ".ts", ".jsx", ".tsx", 
        ".html", ".css", ".scss", ".json", 
        ".md", ".txt", ".yaml", ".yml"
    ],
    "excluded_dirs": [
        "__pycache__", ".git", ".venv", "venv", 
        "node_modules", ".pytest_cache", "dist", "build"
    ],
    "log_level": "INFO",
    "max_file_size_mb": 10,
    "encoding": "utf-8"
}

# Variables de entorno
LOG_LEVEL = os.getenv("SURGICAL_LOG_LEVEL", DEFAULT_CONFIG["log_level"])
MAX_FILE_SIZE = int(os.getenv("SURGICAL_MAX_FILE_SIZE", str(DEFAULT_CONFIG["max_file_size_mb"])))
ENCODING = os.getenv("SURGICAL_ENCODING", DEFAULT_CONFIG["encoding"])

# Configuraciones por coordinador
COORDINATOR_CONFIG: Dict[str, Dict[str, Any]] = {
    "create": {
        "default_permissions": 0o644,
        "create_dirs": True,
        "overwrite_existing": False
    },
    "replace": {
        "match_case": True,
        "use_regex": False,
        "backup_before_replace": True
    },
    "before": {
        "preserve_indentation": True,
        "add_newline": True
    },
    "after": {
        "preserve_indentation": True,
        "add_newline": True
    },
    "explore": {
        "max_depth": 10,
        "include_metrics": True,
        "analyze_dependencies": False
    }
}


def get_coordinator_config(coordinator_name: str) -> Dict[str, Any]:
    """Obtener configuración específica de un coordinador."""
    return COORDINATOR_CONFIG.get(coordinator_name, {})


def validate_config() -> bool:
    """Validar que la configuración es correcta."""
    try:
        # Validar directorios necesarios
        if not BACKUP_DIR.parent.exists():
            return False
            
        # Validar configuraciones básicas
        if not isinstance(DEFAULT_CONFIG["max_backup_files"], int):
            return False
            
        return True
    except Exception:
        return False


def get_full_config() -> Dict[str, Any]:
    """Obtener configuración completa del sistema."""
    return {
        "default": DEFAULT_CONFIG,
        "coordinators": COORDINATOR_CONFIG,
        "paths": {
            "project_root": str(PROJECT_ROOT),
            "config_dir": str(CONFIG_DIR),
            "backup_dir": str(BACKUP_DIR)
        },
        "environment": {
            "log_level": LOG_LEVEL,
            "max_file_size": MAX_FILE_SIZE,
            "encoding": ENCODING
        }
    }
