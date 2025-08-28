"""
Engines subsystem - Interface común para motores de modificación de código.
Permite intercambio transparente entre different engines (native, comby, ast-grep).
"""
from .base_engine import BaseEngine, EngineCapability, EngineResult

__all__ = [
    'BaseEngine',
    'EngineCapability', 
    'EngineResult'
]