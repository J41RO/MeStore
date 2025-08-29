"""
Engine Selector - Lógica de auto-selección de engines.
Selecciona automáticamente el mejor engine basado en criterios como tipo de operación,
capacidades requeridas, lenguaje de programación, y disponibilidad.
"""
from typing import List, Dict, Optional, Any, Union
from enum import Enum
import logging
import re
from dataclasses import dataclass

from .base_engine import BaseEngine, EngineCapability, EngineRegistry

# AGREGAR TODO EL CÓDIGO DE COMPLEJIDAD AQUÍ:

class ComplexityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ComplexityMetrics:
    lines_count: int = 0
    nesting_depth: int = 0
    complex_patterns: int = 0
    function_count: int = 0
    class_count: int = 0
    lambda_count: int = 0
    complexity_score: float = 0.0

class ComplexityAnalyzer:
    """Analyzer for content and operation complexity"""
    
    def __init__(self):
        self.complex_patterns = [
            r'lambda\s+.*?:',  # Lambda functions
            r'list\s*\(.*?for.*?in.*?\)',  # List comprehensions
            r'dict\s*\(.*?for.*?in.*?\)',  # Dict comprehensions
            r'async\s+def',  # Async functions
            r'try\s*:.*?except',  # Try-except blocks
            r'with\s+.*?as\s+.*?:',  # Context managers
            r'@\w+',  # Decorators
            r'yield\s+',  # Generators
            r'class\s+\w+.*?\(.*?\):',  # Class inheritance
        ]
    
    def analyze_content_complexity(self, content: str) -> ComplexityLevel:
        """Analyze the complexity of given content"""
        if not content or not content.strip():
            return ComplexityLevel.LOW
            
        metrics = self._calculate_metrics(content)
        complexity_score = self._calculate_complexity_score(metrics)
        
        if complexity_score >= 80:
            return ComplexityLevel.CRITICAL
        elif complexity_score >= 60:
            return ComplexityLevel.HIGH
        elif complexity_score >= 30:
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.LOW
    
    def analyze_operation_complexity(self, operation_type: str, content: str = "") -> ComplexityLevel:
        """Analyze complexity based on operation type and content"""
        # Base complexity by operation type
        operation_complexity = {
            'literal_search': 10,
            'regex_search': 30,
            'structural_search': 50,
            'batch_operations': 70,
            'insert_before': 25,
            'insert_after': 25,
            'extract': 40,
            'transform': 60
        }
        
        base_score = operation_complexity.get(operation_type, 20)
        
        # Adjust based on content if provided
        if content:
            content_level = self.analyze_content_complexity(content)
            content_multiplier = {
                ComplexityLevel.LOW: 1.0,
                ComplexityLevel.MEDIUM: 1.3,
                ComplexityLevel.HIGH: 1.6,
                ComplexityLevel.CRITICAL: 2.0
            }
            base_score *= content_multiplier[content_level]
        
        if base_score >= 80:
            return ComplexityLevel.CRITICAL
        elif base_score >= 60:
            return ComplexityLevel.HIGH
        elif base_score >= 30:
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.LOW
    
    def _calculate_metrics(self, content: str) -> ComplexityMetrics:
        """Calculate detailed complexity metrics"""
        lines = content.split('\n')
        metrics = ComplexityMetrics()
        
        metrics.lines_count = len([line for line in lines if line.strip()])
        metrics.nesting_depth = self._calculate_nesting_depth(content)
        metrics.complex_patterns = self._count_complex_patterns(content)
        metrics.function_count = len(re.findall(r'def\s+\w+', content))
        metrics.class_count = len(re.findall(r'class\s+\w+', content))
        metrics.lambda_count = len(re.findall(r'lambda\s+.*?:', content))
        
        metrics.complexity_score = self._calculate_complexity_score(metrics)
        return metrics
    
    def _calculate_nesting_depth(self, content: str) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        current_depth = 0
        
        for line in content.split('\n'):
            stripped = line.strip()
            if not stripped:
                continue
                
            # Count indentation
            indent = len(line) - len(line.lstrip())
            current_depth = indent // 4  # Assuming 4-space indentation
            max_depth = max(max_depth, current_depth)
            
        return max_depth
    
    def _count_complex_patterns(self, content: str) -> int:
        """Count complex patterns in content"""
        count = 0
        for pattern in self.complex_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            count += len(matches)
        return count
    
    def _calculate_complexity_score(self, metrics: ComplexityMetrics) -> float:
        """Calculate overall complexity score"""
        score = 0
        
        # Lines contribution (logarithmic scale)
        if metrics.lines_count > 0:
            import math
            score += min(20, math.log(metrics.lines_count) * 5)
        
        # Nesting depth (exponential impact)
        score += metrics.nesting_depth ** 1.5 * 8
        
        # Complex patterns (linear impact)
        score += metrics.complex_patterns * 5
        
        # Functions and classes
        score += metrics.function_count * 3
        score += metrics.class_count * 8
        score += metrics.lambda_count * 4
        
        metrics.complexity_score = score
        return score

# DESPUÉS CONTINÚA CON logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

class SelectionCriteria(Enum):
    """Criterios para selección de engines"""
    CAPABILITY_MATCH = "capability_match"
    LANGUAGE_SUPPORT = "language_support"  
    PERFORMANCE = "performance"
    AVAILABILITY = "availability"
    OPERATION_TYPE = "operation_type"


class EngineSelector:
    """
    Selector automático de engines basado en criterios específicos.
    
    Analiza los engines disponibles y selecciona el más apropiado según:
    - Capacidades requeridas
    - Tipo de operación
    - Lenguaje de programación 
    - Disponibilidad de herramientas externas
    """
    
    def __init__(self):
        """Inicializar selector con configuración por defecto"""
        self._engine_priorities = {
                # Prioridades por tipo de operación (mayor número = mayor prioridad)
                'structural_search': {'comby': 3, 'ast': 2, 'native': 1},
                'literal_search': {'native': 3, 'comby': 2, 'ast': 1},
                'regex_search': {'native': 3, 'comby': 2, 'ast': 1},
                'batch_operations': {'native': 3, 'comby': 2, 'ast': 1},
                # Nuevos tipos de operación expandidos
                'insert_before': {'comby': 3, 'ast': 2, 'native': 1},
                'insert_after': {'comby': 3, 'ast': 2, 'native': 1},
                'extract': {'ast': 3, 'comby': 2, 'native': 1},
                'transform': {'comby': 3, 'ast': 2, 'native': 1}
            }
            
            # Contexto inteligente por lenguaje
        self._language_priorities = {
                'python': {'ast': 1.2, 'comby': 1.1, 'native': 1.0},
                'javascript': {'comby': 1.2, 'ast': 1.1, 'native': 1.0},
                'typescript': {'comby': 1.2, 'ast': 1.1, 'native': 1.0},
                'java': {'comby': 1.2, 'ast': 1.0, 'native': 0.9},
                'c++': {'comby': 1.1, 'ast': 1.0, 'native': 1.0},
                'c#': {'comby': 1.1, 'ast': 1.0, 'native': 0.9}
            }
    
    def select_best_engine(
        self,
        operation_type: str,
        capabilities_needed: List[Union[EngineCapability, str]],
        language: Optional[str] = None,
        content: Optional[str] = None,
        complexity_level: Optional[ComplexityLevel] = None,
        **kwargs
    ) -> BaseEngine:
        """
        Seleccionar el mejor engine para una operación específica.
        
        Args:
            operation_type: Tipo de operación ('search', 'replace', etc.)
            capabilities_needed: Lista de capacidades requeridas
            language: Lenguaje de programación (opcional)
            content: Contenido a procesar (opcional, para análisis contextual)
            **kwargs: Parámetros adicionales para criterios específicos
            
        Returns:
            Instancia del engine más apropiado
            
        Raises:
            ValueError: Si no se encuentra engine apropiado
        """
        # Normalizar capabilities a enum si vienen como strings
        normalized_capabilities = self._normalize_capabilities(capabilities_needed)
        
        # Análisis automático de complejidad si se proporciona contenido
        if content and complexity_level is None:
            analyzer = ComplexityAnalyzer()
            complexity_level = analyzer.analyze_content_complexity(content)
            logger.info(f"Complejidad detectada automáticamente: {complexity_level.value}")
        
        # Auto-detectar tipo de operación si no se especifica explícitamente
        if operation_type == 'auto' and content:
            analyzer = ComplexityAnalyzer() if 'analyzer' not in locals() else analyzer
            operation_type = self._detect_operation_type(content, normalized_capabilities)
            logger.info(f"Tipo de operación detectado automáticamente: {operation_type}")
        
        # Obtener engines candidatos que tengan las capacidades requeridas
        candidate_engines = self._get_engines_by_capability(normalized_capabilities)
        
        if not candidate_engines:
            logger.warning(f"No se encontraron engines con capacidades {capabilities_needed}. Usando NativeEngine como fallback.")
            return EngineRegistry.get_engine('native')
        
        # Rankear engines por prioridad y criterios
        ranked_engines = self._rank_engines(
            candidate_engines,
            operation_type,
            normalized_capabilities,
            language,
            complexity_level
)
        
        # Seleccionar el mejor engine disponible
        selected_engine_name = ranked_engines[0]['name']
        
        logger.info(f"Engine seleccionado: {selected_engine_name} para operación '{operation_type}' con capacidades {[c.value for c in normalized_capabilities]}")
        
        return EngineRegistry.get_engine(selected_engine_name)
    
    def _normalize_capabilities(self, capabilities: List[Union[EngineCapability, str]]) -> List[EngineCapability]:
        """Convertir lista mixta de capabilities a enum EngineCapability"""
        normalized = []
        for cap in capabilities:
            if isinstance(cap, str):
                try:
                    normalized.append(EngineCapability(cap))
                except ValueError:
                    logger.warning(f"Capacidad desconocida: {cap}")
            elif isinstance(cap, EngineCapability):
                normalized.append(cap)
        return normalized
    
    def _get_engines_by_capability(self, required_capabilities: List[EngineCapability]) -> List[Dict[str, Any]]:
        """
        Filtrar engines que tengan todas las capacidades requeridas.
        
        Returns:
            Lista de diccionarios con info de engines candidatos
        """
        candidate_engines = []
        
        for engine_name, engine_class in EngineRegistry._engines.items():
            try:
                # Crear instancia temporal para verificar capacidades
                engine_instance = engine_class()
                # Usar property capabilities en lugar de get_capabilities()
                engine_capabilities = engine_instance.capabilities
                
                # Verificar si el engine tiene todas las capacidades requeridas
                if all(cap in engine_capabilities for cap in required_capabilities):
                    candidate_engines.append({
                        'name': engine_name,
                        'class': engine_class,
                        'capabilities': engine_capabilities,
                        'available': self._check_engine_availability(engine_name, engine_instance)
                    })
                    
            except Exception as e:
                logger.warning(f"Error evaluando engine {engine_name}: {e}")
                continue
        
        return candidate_engines
    
    def _rank_engines(
        self,
        candidate_engines: List[Dict[str, Any]],
        operation_type: str,
        capabilities: List[EngineCapability],
        language: Optional[str] = None,
        complexity_level: Optional[ComplexityLevel] = None
    ) -> List[Dict[str, Any]]:
        """
        Rankear engines candidatos por prioridad y criterios.
        
        Returns:
            Lista de engines ordenados por ranking (mejor primero)
        """
        # Asignar scores a cada engine
        for engine in candidate_engines:
            score = 0
            engine_name = engine['name']
            
            # Score base por disponibilidad
            if engine['available']:
                score += 100
            else:
                score += 10  # Penalidad por no disponible pero no eliminatorio
            
            # Score por prioridad del tipo de operación
            primary_capability = self._get_primary_capability(capabilities)
            if primary_capability in self._engine_priorities:
                priority_map = self._engine_priorities[primary_capability]
                score += priority_map.get(engine_name, 0) * 10
                
                # Score por nivel de complejidad
            if complexity_level:
                complexity_bonus = self._calculate_complexity_bonus(
                    engine_name, complexity_level, operation_type
                )
                score += complexity_bonus
                
                # Bonus por contexto inteligente de lenguaje
            if language and language.lower() in self._language_priorities:
                lang_multiplier = self._language_priorities[language.lower()].get(
                    engine_name, 1.0
                )
                language_bonus = int((lang_multiplier - 1.0) * 100)
                score += language_bonus
            
            # Bonus por capacidades específicas de lenguaje si se especifica
            if language and EngineCapability.LANGUAGE_SPECIFIC in engine['capabilities']:
                score += 5
            
            engine['score'] = score
        
        # Ordenar por score descendente
        ranked_engines = sorted(candidate_engines, key=lambda x: x['score'], reverse=True)
        
        return ranked_engines
    
    def _get_primary_capability(self, capabilities: List[EngineCapability]) -> str:
        """Determinar la capacidad primaria para priorización"""
        capability_priorities = {
            EngineCapability.STRUCTURAL_SEARCH: 'structural_search',
            EngineCapability.AST_AWARE: 'structural_search', 
            EngineCapability.REGEX_SEARCH: 'regex_search',
            EngineCapability.LITERAL_SEARCH: 'literal_search',
            EngineCapability.BATCH_OPERATIONS: 'batch_operations'
        }
        
        # Buscar primera capacidad que tengamos mapeada
        for cap in capabilities:
            if cap in capability_priorities:
                return capability_priorities[cap]
        
        return 'literal_search'  # Default
    
    def _calculate_complexity_bonus(self, engine_name: str, complexity_level: ComplexityLevel, operation_type: str) -> int:
        """Calculate complexity-based bonus for engine selection"""
        # Define engine power levels (higher = more powerful/slower)
        engine_power = {
            'ast_engine': 90,      # Most powerful for complex operations
            'regex_engine': 70,    # Good for pattern matching
            'native_engine': 50,   # Balanced
            'literal_engine': 30,  # Fast but basic
        }
        
        # Define complexity requirements
        complexity_requirements = {
            ComplexityLevel.CRITICAL: 80,
            ComplexityLevel.HIGH: 60,
            ComplexityLevel.MEDIUM: 40,
            ComplexityLevel.LOW: 20
        }
        
        engine_power_level = engine_power.get(engine_name, 50)
        required_power = complexity_requirements[complexity_level]
        
        # Bonus calculation:
        # - High complexity: favor powerful engines
        # - Low complexity: favor fast engines
        if complexity_level in [ComplexityLevel.HIGH, ComplexityLevel.CRITICAL]:
            # High complexity: bonus for powerful engines
            if engine_power_level >= required_power:
                return 25  # Strong bonus for capable engines
            else:
                return -10  # Penalty for underpowered engines
        else:
            # Low/Medium complexity: bonus for balanced/fast engines
            if engine_power_level <= required_power + 20:
                return 15  # Bonus for not overkill
            else:
                return 5   # Small bonus for powerful engines (still works)
    
    def _detect_operation_type(self, content: str, capabilities: List[EngineCapability]) -> str:
        """Auto-detect operation type based on content and capabilities"""
        # Analyze content patterns
        has_regex_patterns = bool(re.search(r'[.*+?^${}()|[\]\\]', content))
        has_complex_structures = bool(re.search(r'(class|def|if|for|while|try)', content))
        has_imports = bool(re.search(r'(import|from.*import)', content))
        
        # Decision logic based on capabilities and content
        if EngineCapability.STRUCTURAL_SEARCH in capabilities:
            if has_complex_structures or has_imports:
                return 'structural_search'
            elif has_regex_patterns:
                return 'regex_search'
            else:
                return 'literal_search'
        elif EngineCapability.REGEX_SEARCH in capabilities:
            return 'regex_search' if has_regex_patterns else 'literal_search'
        elif EngineCapability.BATCH_OPERATIONS in capabilities:
            return 'batch_operations'
        else:
            return 'literal_search'
    
    def _check_engine_availability(self, engine_name: str, engine_instance: BaseEngine) -> bool:
        """
        Verificar si un engine está realmente disponible.
        
        Algunos engines pueden requerir herramientas externas (como ast-grep).
        """
        try:
            # Para engines que requieren herramientas externas, verificar disponibilidad
            if hasattr(engine_instance, 'is_available'):
                return engine_instance.is_available()
            return True
        except Exception:
            return False


# Función de conveniencia para uso directo
def get_best_engine(
    operation_type: str,
    capabilities_needed: List[Union[EngineCapability, str]],
    language: Optional[str] = None,
    **kwargs
) -> BaseEngine:
    """
    Función de conveniencia para obtener el mejor engine.
    
    Wrapper simple sobre EngineSelector.select_best_engine()
    """
    selector = EngineSelector()
    return selector.select_best_engine(
        operation_type=operation_type,
        capabilities_needed=capabilities_needed,
        language=language,
        **kwargs
    )