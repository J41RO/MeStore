"""
Surgical Modifier v6.0 - Utils Module
"""

from .logger import logger
from .path_resolver import path_resolver

__all__ = ["logger", "path_resolver"]

# Plugin system (future)
from .plugin_system import plugin_manager

__all__.append('plugin_manager')
