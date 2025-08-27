"""
Pattern Matching Module - Sistema unificado de matchers independientes

Este módulo proporciona matchers especializados para diferentes tipos de búsqueda:
- RegexMatcher: Patrones regex robustos
- LiteralMatcher: Búsqueda literal eficiente  
- FuzzyMatcher: Coincidencias aproximadas
- MultilineMatcher: Patrones multilínea

Todos los matchers implementan interface común BaseMatcher con métodos:
- find(): Encuentra primera coincidencia
- match(): Verifica existencia de coincidencia
- find_all(): Encuentra todas las coincidencias
"""

from typing import List
# IMPORTS RELATIVOS CORRECTOS:
from .base_matcher import BaseMatcher, MatcherCombiner
from .regex_matcher import RegexMatcher
from .literal_matcher import LiteralMatcher
from .fuzzy_matcher import FuzzyMatcher
from .multiline_matcher import MultilineMatcher

# Export público de todas las clases
__all__ = [
    'BaseMatcher',
    'MatcherCombiner', 
    'RegexMatcher',
    'LiteralMatcher',
    'FuzzyMatcher',
    'MultilineMatcher'
]

# Versión del módulo
__version__ = '1.0.0'

def create_combined_matcher(*matchers) -> MatcherCombiner:
    """
    Helper function para crear un combinador con múltiples matchers.
    
    Args:
        *matchers: Instancias de matchers a combinar
        
    Returns:
        MatcherCombiner configurado con los matchers especificados
        
    Example:
        >>> regex = RegexMatcher()
        >>> literal = LiteralMatcher()
        >>> combined = create_combined_matcher(regex, literal)
        >>> result = combined.find_any(text, [pattern1, pattern2])
    """
    if not matchers:
        # Crear instancias por defecto de todos los matchers
        matchers = [
            RegexMatcher(),
            LiteralMatcher(), 
            FuzzyMatcher(),
            MultilineMatcher()
        ]
    return MatcherCombiner(list(matchers))

def get_all_matchers() -> List[BaseMatcher]:
    """
    Retorna lista con instancias de todos los matchers disponibles.
    
    Returns:
        Lista de instancias de todos los matchers implementados
    """
    return [
        RegexMatcher(),
        LiteralMatcher(),
        FuzzyMatcher(), 
        MultilineMatcher()
    ]