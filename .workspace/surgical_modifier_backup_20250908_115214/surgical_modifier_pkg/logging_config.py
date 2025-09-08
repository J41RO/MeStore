"""
Configuración de logging para Surgical Modifier
"""

import logging
import sys
from pathlib import Path

# Logger por defecto
DEFAULT_LOGGER = logging.getLogger("surgical_modifier")

def setup_logging(level="INFO"):
    """Configurar logging básico"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return DEFAULT_LOGGER

def get_logger(name=None):
    """Obtener logger configurado con prefijo surgical_modifier"""
    if name:
        full_name = f"surgical_modifier.{name}"
        return logging.getLogger(full_name)
    return DEFAULT_LOGGER

# Configurar logging por defecto
setup_logging()
