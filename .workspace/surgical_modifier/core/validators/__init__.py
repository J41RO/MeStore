"""
Módulo de validadores de integridad estructural.

Proporciona validación automática de código Python antes y después
de operaciones de modificación, con capacidades de rollback automático.
"""

from .structural_validator import StructuralValidator
from .rollback_manager import RollbackManager
from .integration_validator import (
    validate_structural_integrity,
    StructuralIntegrityError,
    manual_structural_validation
)

__all__ = [
    'StructuralValidator',
    'RollbackManager', 
    'validate_structural_integrity',
    'StructuralIntegrityError',
    'manual_structural_validation'
]

# Información del módulo
__version__ = '1.0.0'
__author__ = 'Surgical Modifier Team'
__description__ = 'Sistema de validación de integridad estructural para código Python'