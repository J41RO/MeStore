"""Surgical Modifier - Sistema de Modificación Precisa de Código"""
__version__ = "0.1.0"

from . import cli
from . import config
from . import base_coordinator
from . import exceptions

__all__ = ['cli', 'config', 'base_coordinator', 'exceptions']
