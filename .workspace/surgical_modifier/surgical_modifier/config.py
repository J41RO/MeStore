"""
Configuración centralizada para Surgical Modifier CLI
Sistema de logging y configuraciones por defecto.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any
import yaml

# Configuración por defecto
DEFAULT_CONFIG = {
    'backup': {
        'enabled': True,
        'max_backups': 10,
        'cleanup_old': True
    },
    'logging': {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    },
    'operations': {
        'preserve_permissions': True,
        'preserve_line_endings': True,
        'default_encoding': 'utf-8'
    }
}


def get_config(config_path: str = None) -> Dict[str, Any]:
    """
    Obtener configuración del sistema.
    
    Args:
        config_path: Ruta opcional al archivo de configuración
        
    Returns:
        Diccionario con configuración completa
    """
    config = DEFAULT_CONFIG.copy()
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    config.update(user_config)
        except Exception as e:
            logging.warning(f"Error cargando configuración personalizada: {e}")
    
    return config


def setup_logging(verbose: bool = False):
    """
    Configurar sistema de logging.
    
    Args:
        verbose: Si True, usar nivel DEBUG
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Crear logger específico para surgical_modifier
    logger = logging.getLogger('surgical_modifier')
    logger.setLevel(level)
    
    return logger


def get_project_root() -> Path:
    """Obtener directorio raíz del proyecto."""
    return Path(__file__).parent


def get_config_dir() -> Path:
    """Obtener directorio de configuraciones."""
    return get_project_root() / 'config'


def get_templates_dir() -> Path:
    """Obtener directorio de templates."""
    return get_config_dir() / 'templates'