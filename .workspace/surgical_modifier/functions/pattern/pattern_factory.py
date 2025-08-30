"""
PatternMatcherFactory - Factory para coordinar matchers optimizados con engines
Integra pattern matching con engine selection para optimizaciones automáticas
"""

from typing import Dict, Any, Optional, List, Type
from .base_matcher import BaseMatcher
from .regex_matcher import RegexMatcher
from .literal_matcher import LiteralMatcher
from .fuzzy_matcher import FuzzyMatcher
from .multiline_matcher import MultilineMatcher


class PatternMatcherFactory:
    """
    Factory que coordina pattern matchers con engines automáticamente.
    Selecciona el matcher optimal según pattern type y engine capabilities.
    """
    
    def __init__(self):
        """Inicializa factory con registry de matchers y engines soportados"""
        self._matcher_registry: Dict[str, Type[BaseMatcher]] = {
            'regex': RegexMatcher,
            'literal': LiteralMatcher,
            'fuzzy': FuzzyMatcher,
            'multiline': MultilineMatcher
        }
        
        self._engine_capabilities: Dict[str, List[str]] = {
            'native': ['case_insensitive_native', 'pattern_precompilation'],
            'ast': ['ast_literal_matching', 'function_matching', 'import_matching', 'ast_pattern_matching'],
            'comby': ['structural_matching', 'template_generation']
        }
        
        self._optimal_combinations: Dict[str, Dict[str, str]] = {
            'native': {
                'simple_text': 'literal',
                'complex_patterns': 'regex',
                'approximate': 'fuzzy',
                'multiline_code': 'multiline'
            },
            'ast': {
                'code_structure': 'regex',
                'identifiers': 'literal',
                'function_definitions': 'regex',
                'imports': 'regex'
            },
            'comby': {
                'structural_search': 'regex',
                'template_matching': 'literal',
                'code_patterns': 'regex'
            }
        }
    
    def get_optimized_matcher(self, pattern_type: str, engine_type: str = 'native') -> BaseMatcher:
        """
        Factory method principal - retorna matcher optimizado para engine específico.
        
        Args:
            pattern_type: Tipo de pattern ('literal', 'regex', 'fuzzy', 'multiline')
            engine_type: Tipo de engine ('native', 'ast', 'comby')
            
        Returns:
            Instancia de matcher configurada para el engine especificado
            
        Raises:
            ValueError: Si pattern_type o engine_type no son soportados
        """
        if pattern_type not in self._matcher_registry:
            raise ValueError(f"Unsupported pattern type: {pattern_type}")
            
        if engine_type not in self._engine_capabilities:
            raise ValueError(f"Unsupported engine type: {engine_type}")
        
        # Obtener clase del matcher
        matcher_class = self._matcher_registry[pattern_type]
        
        # Crear instancia con engine_type
        matcher = matcher_class(engine_type=engine_type)
        
        # Configurar capabilities del engine
        capabilities = self._engine_capabilities[engine_type]
        matcher.set_engine_context(engine_type, capabilities)
        
        return matcher
    
    def get_optimal_matcher_for_use_case(self, use_case: str, engine_type: str = 'native') -> BaseMatcher:
        """
        Retorna matcher optimal para un caso de uso específico.
        
        Args:
            use_case: Caso de uso ('simple_text', 'complex_patterns', 'code_structure', etc.)
            engine_type: Tipo de engine
            
        Returns:
            Matcher optimal para el caso de uso y engine
        """
        if engine_type not in self._optimal_combinations:
            engine_type = 'native'  # Fallback por defecto
            
        optimal_pattern_type = self._optimal_combinations[engine_type].get(use_case, 'literal')
        return self.get_optimized_matcher(optimal_pattern_type, engine_type)
    
    def create_engine_coordinated_matcher(self, engine_selector=None) -> BaseMatcher:
        """
        Crea matcher que se coordina automáticamente con EngineSelector.
        
        Args:
            engine_selector: Instancia de EngineSelector (opcional)
            
        Returns:
            Matcher configurado para coordinarse con engine selection
        """
        if engine_selector is None:
            # Usar configuración por defecto si no hay engine selector
            return self.get_optimized_matcher('literal', 'native')
        
        # Detectar engine type del selector
        engine_type = getattr(engine_selector, 'current_engine_type', 'native')
        
        # Crear matcher coordinado
        matcher = self.get_optimized_matcher('regex', engine_type)  # regex es versátil
        
        # Configurar coordinación automática si el engine selector lo soporta
        if hasattr(engine_selector, 'register_matcher'):
            engine_selector.register_matcher(matcher)
        
        return matcher
    
    def get_all_optimized_matchers(self, engine_type: str = 'native') -> Dict[str, BaseMatcher]:
        """
        Retorna todos los matchers optimizados para un engine específico.
        
        Args:
            engine_type: Tipo de engine
            
        Returns:
            Dict con todos los matchers configurados para el engine
        """
        matchers = {}
        for pattern_type in self._matcher_registry:
            try:
                matchers[pattern_type] = self.get_optimized_matcher(pattern_type, engine_type)
            except ValueError:
                continue  # Skip si no es compatible
                
        return matchers
    
    def get_engine_compatibility_matrix(self) -> Dict[str, Any]:
        """
        Retorna matriz de compatibilidad entre engines y matchers.
        
        Returns:
            Dict con información de compatibilidad completa
        """
        matrix = {
            'engines': list(self._engine_capabilities.keys()),
            'pattern_types': list(self._matcher_registry.keys()),
            'capabilities_by_engine': self._engine_capabilities.copy(),
            'optimal_combinations': self._optimal_combinations.copy(),
            'compatibility': {}
        }
        
        # Generar información de compatibilidad
        for engine in matrix['engines']:
            matrix['compatibility'][engine] = {}
            for pattern_type in matrix['pattern_types']:
                try:
                    matcher = self.get_optimized_matcher(pattern_type, engine)
                    matrix['compatibility'][engine][pattern_type] = {
                        'compatible': True,
                        'capabilities': matcher.engine_capabilities,
                        'optimizations_available': len(matcher.engine_capabilities) > 0
                    }
                except ValueError:
                    matrix['compatibility'][engine][pattern_type] = {
                        'compatible': False,
                        'reason': 'Engine not supported'
                    }
        
        return matrix
    
    def register_custom_matcher(self, pattern_type: str, matcher_class: Type[BaseMatcher]) -> None:
        """
        Registra matcher custom en el factory.
        
        Args:
            pattern_type: Identificador para el nuevo tipo de pattern
            matcher_class: Clase del matcher que debe heredar de BaseMatcher
        """
        if not issubclass(matcher_class, BaseMatcher):
            raise TypeError("matcher_class must inherit from BaseMatcher")
            
        self._matcher_registry[pattern_type] = matcher_class
    
    def get_factory_statistics(self) -> Dict[str, Any]:
        """
        Retorna estadísticas del factory y uso de matchers.
        
        Returns:
            Dict con estadísticas completas
        """
        return {
            'total_pattern_types': len(self._matcher_registry),
            'total_engines_supported': len(self._engine_capabilities),
            'pattern_types': list(self._matcher_registry.keys()),
            'engines_supported': list(self._engine_capabilities.keys()),
            'total_combinations': len(self._matcher_registry) * len(self._engine_capabilities),
            'use_cases_supported': sum(len(cases) for cases in self._optimal_combinations.values()),
            'version': '2.0.0'
        }


# Instancia global del factory para uso conveniente
pattern_factory = PatternMatcherFactory()

def get_optimized_matcher(pattern_type: str, engine_type: str = 'native') -> BaseMatcher:
    """
    Función helper para acceso rápido al factory global.
    
    Args:
        pattern_type: Tipo de pattern
        engine_type: Tipo de engine
        
    Returns:
        Matcher optimizado
    """
    return pattern_factory.get_optimized_matcher(pattern_type, engine_type)