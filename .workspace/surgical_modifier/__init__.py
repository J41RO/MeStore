"""
Surgical Modifier v6.0 - The most complete code modification tool in the world
"""

__version__ = "6.0.0"
__author__ = "Surgical Modifier Team"
__description__ = "The most complete code modification tool in the world"

# Import main utilities for easy access
from .utils import logger, path_resolver

__all__ = ["logger", "path_resolver", "__version__", "__author__", "__description__"]
