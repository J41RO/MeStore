"""
Configuración del sistema Surgical Modifier
"""

from pathlib import Path
import os

# Configuración del proyecto
PROJECT_ROOT = Path(__file__).parent
CONFIG_DIR = PROJECT_ROOT / "config"
LOGS_DIR = PROJECT_ROOT / "logs"
BACKUP_DIR = PROJECT_ROOT / "backups"

# Configuración por defecto
DEFAULT_CONFIG = {
    "version": "0.1.0",
    "backup_enabled": True,
    "verbose": False,
    "dry_run": False,
    "max_backup_files": 10,
    "backup_retention_days": 30,
    "logging_level": "INFO",
    "supported_extensions": [".py", ".js", ".ts", ".json", ".yaml", ".yml"],
    "excluded_dirs": ["__pycache__", ".git", "node_modules", ".pytest_cache"],
    "max_file_size_mb": 10,
    "log_level": "INFO",
    "encoding": "utf-8",
    "technology_mapping": {
        ".py": "python",
        ".tsx": "typescript_react", 
        ".ts": "typescript",
        ".jsx": "javascript_react",
        ".js": "javascript",
        ".vue": "vue",
        ".svelte": "svelte"
    }
}

# Constantes requeridas por los tests
LOG_LEVEL = DEFAULT_CONFIG["log_level"]

# Extensiones soportadas
SUPPORTED_EXTENSIONS = DEFAULT_CONFIG["supported_extensions"]

# Directorios excluidos  
EXCLUDED_DIRS = DEFAULT_CONFIG["excluded_dirs"]

def get_config():
    """Obtener configuración actual"""
    return DEFAULT_CONFIG.copy()

def update_config(updates):
    """Actualizar configuración"""
    DEFAULT_CONFIG.update(updates)
    return DEFAULT_CONFIG

def get_coordinator_config():
    """Obtener configuración para coordinadores"""
    return {
        "max_retries": 3,
        "timeout": 30,
        "log_level": LOG_LEVEL
    }

# Constante adicional requerida por tests
MAX_FILE_SIZE = DEFAULT_CONFIG["max_file_size_mb"] * 1024 * 1024  # En bytes

def validate_config(config_dict=None):
    """Validar configuración del sistema"""
    if config_dict is None:
        config_dict = DEFAULT_CONFIG
    
    required_fields = [
        "version", "backup_enabled", "verbose", "dry_run",
        "max_backup_files", "backup_retention_days", "supported_extensions",
        "excluded_dirs", "log_level", "max_file_size_mb"
    ]
    
    for field in required_fields:
        if field not in config_dict:
            raise ValueError(f"Missing required config field: {field}")
    
    return True

# Constante ENCODING requerida por tests
ENCODING = DEFAULT_CONFIG["encoding"]

def get_full_config():
    """Obtener configuración completa del sistema"""
    return {
        **DEFAULT_CONFIG,
        "project_root": str(PROJECT_ROOT),
        "config_dir": str(CONFIG_DIR),
        "logs_dir": str(LOGS_DIR),
        "backup_dir": str(BACKUP_DIR)
    }
