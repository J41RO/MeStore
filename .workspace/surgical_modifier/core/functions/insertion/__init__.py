# Insertion module initialization
"""
Módulo de inserción consolidado.
Contiene lógica compartida para operaciones before y after.
"""

from .insertion_engine import (
    handle_insertion,
    detect_pattern_indentation,
    apply_context_indentation,
    line_matches_pattern
)

__all__ = [
    'handle_insertion',
    'detect_pattern_indentation',
    'apply_context_indentation',
    'line_matches_pattern'
]
