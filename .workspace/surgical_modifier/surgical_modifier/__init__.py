"""Surgical Modifier - Sistema de Modificación Precisa de Código."""

__version__ = "0.1.0"
__author__ = "Admin Jairo"
__description__ = (
    "Sistema de Modificación Precisa de Código con coordinadores especializados"
)

# Importaciones explícitas para asegurar disponibilidad de módulos
from . import config
from . import logging_config
from .base_coordinator import BaseCoordinator
from .exceptions import (
    SurgicalModifierError, CoordinatorError, ValidationError,
    BackupError, FileOperationError, PatternMatchError, ConfigurationError
)

# Hacer disponibles los componentes principales
__all__ = [
    'config',
    'logging_config', 
    'BaseCoordinator',
    'SurgicalModifierError', 'CoordinatorError', 'ValidationError',
    'BackupError', 'FileOperationError', 'PatternMatchError', 'ConfigurationError'
]
