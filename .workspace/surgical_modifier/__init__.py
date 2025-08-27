#!/usr/bin/env python3
"""
Surgical Modifier - Herramienta de modificación quirúrgica de archivos
Sistema robusto de modificación de código con detección inteligente de patrones.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configuración del logger
logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = "Surgical Modifier Team"
__description__ = "Herramienta de modificación quirúrgica de archivos"

# Importar excepciones desde nuestro módulo exceptions.py
try:
    from .exceptions import (
        SurgicalModifierError,
        InvalidPatternError,
        FileNotFoundError as SurgicalFileNotFoundError,
        PermissionError as SurgicalPermissionError,
        ValidationError,
        ConfigurationError
    )
except ImportError:
    # Fallback: importación directa
    from exceptions import (
        SurgicalModifierError,
        InvalidPatternError,
        FileNotFoundError as SurgicalFileNotFoundError,
        PermissionError as SurgicalPermissionError,
        ValidationError,
        ConfigurationError
    )

# Importar componentes principales
try:
    from .functions.pattern.regex_matcher import RegexMatcher
    from .functions.pattern.literal_matcher import LiteralMatcher  
    from .functions.pattern.fuzzy_matcher import FuzzyMatcher
    from .functions.pattern.multiline_matcher import MultilineMatcher
except ImportError:
    # Fallback: importación directa
    from functions.pattern.regex_matcher import RegexMatcher
    from functions.pattern.literal_matcher import LiteralMatcher
    from functions.pattern.fuzzy_matcher import FuzzyMatcher
    from functions.pattern.multiline_matcher import MultilineMatcher

# Hacer disponibles las clases principales
__all__ = [
    'SurgicalModifierError',
    'InvalidPatternError', 
    'SurgicalFileNotFoundError',
    'SurgicalPermissionError',
    'ValidationError',
    'ConfigurationError',
    'RegexMatcher',
    'LiteralMatcher',
    'FuzzyMatcher',
    'MultilineMatcher'
]

def get_version():
    """Obtener versión del paquete"""
    return __version__

def get_logger():
    """Obtener logger configurado"""
    return logger
