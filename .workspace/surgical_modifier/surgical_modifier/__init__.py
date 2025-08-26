"""
Surgical Modifier - Sistema de Modificación Precisa de Código
Módulo principal con entry points y configuración.
"""

__version__ = "0.1.0"
__author__ = "Admin Jairo"
__description__ = "Sistema de Modificación Precisa de Código con CLI y coordinadores especializados"

# Imports principales disponibles para importación externa
from .config import get_config, setup_logging
from .cli import main

# Metadata del módulo
__all__ = [
    'get_config',
    'setup_logging', 
    'main',
    '__version__',
    '__author__',
    '__description__'
]
