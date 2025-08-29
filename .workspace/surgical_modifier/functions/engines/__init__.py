"""
Engines subsystem - Interface común para motores de modificación de código.
Permite intercambio transparente entre different engines (native, comby, ast-grep).
"""
from .base_engine import BaseEngine, EngineCapability, EngineResult, EngineMatch, EngineStatus
from .native_engine import NativeEngine
from .comby_engine import CombyEngine

__all__ = [
    'BaseEngine',
    'EngineCapability', 
    'EngineResult',
    'EngineMatch',
    'EngineStatus',
    'NativeEngine',
    'CombyEngine'
]