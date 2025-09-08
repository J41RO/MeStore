"""
Context Analyzer - Analizador de contexto para inserción inteligente de código.
Combina indentación, posición y formateo para análisis contextual completo.
"""
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from enum import Enum
import re

from .indentation_detector import detect_indentation, IndentationInfo
from .position_calculator import calculate_position, InsertionPosition, PositionType
from .content_formatter import format_content, FormattedContent, ContentType

class ContextType(Enum):
    FUNCTION_BODY = "function_body"
    CLASS_BODY = "class_body"
    MODULE_LEVEL = "module_level"
    BLOCK_STATEMENT = "block_statement"
    IMPORT_SECTION = "import_section"
    UNKNOWN = "unknown"

@dataclass
class ContextAnalysis:
    context_type: ContextType
    indentation_level: int
    surrounding_code: Dict[str, str]
    suggested_indentation: str
    insertion_hints: List[str]
    compatibility_score: float

class ContextAnalyzer:
    def __init__(self):
        self.context_patterns = {
            ContextType.FUNCTION_BODY: [
                r'^\s*def\s+\w+\([^)]*\).*:',
                r'^\s*async\s+def\s+\w+\([^)]*\).*:'
            ],
            ContextType.CLASS_BODY: [
                r'^\s*class\s+\w+.*:'
            ],
            ContextType.IMPORT_SECTION: [
                r'^\s*(?:from|import)\s+',
                r'^\s*#.*import'
            ]
        }
    
    def analyze_context(self, content: str, target_pattern: str, position_type: PositionType = PositionType.AFTER) -> ContextAnalysis:
        """Analiza el contexto completo para inserción inteligente."""
        # Detectar indentación
        indentation_info = detect_indentation(content)
        
        # Calcular posición
        insertion_pos = calculate_position(content, target_pattern, position_type, indentation_info)
        
        # Analizar contexto específico
        context_type = self._detect_context_type(content, insertion_pos.line_number)
        surrounding_code = self._extract_surrounding_code(content, insertion_pos.line_number)
        
        # Generar sugerencias
        suggested_indentation = self._calculate_suggested_indentation(
            context_type, insertion_pos.column, indentation_info
        )
        
        insertion_hints = self._generate_insertion_hints(context_type, surrounding_code)
        compatibility_score = self._calculate_compatibility_score(context_type, surrounding_code)
        
        return ContextAnalysis(
            context_type=context_type,
            indentation_level=insertion_pos.column,
            surrounding_code=surrounding_code,
            suggested_indentation=suggested_indentation,
            insertion_hints=insertion_hints,
            compatibility_score=compatibility_score
        )
    
    def _detect_context_type(self, content: str, line_number: int) -> ContextType:
        """Detecta el tipo de contexto basado en el contenido circundante."""
        lines = content.split('\n')
        if line_number >= len(lines):
            return ContextType.UNKNOWN
        
        # Analizar líneas anteriores para determinar contexto
        for i in range(max(0, line_number - 5), line_number + 1):
            if i >= len(lines):
                continue
            line = lines[i]
            
            # Verificar patrones de contexto
            for context_type, patterns in self.context_patterns.items():
                for pattern in patterns:
                    if re.match(pattern, line):
                        return context_type
        
        # Análisis por ubicación en el archivo
        if line_number < 10:
            return ContextType.IMPORT_SECTION
        
        return ContextType.MODULE_LEVEL
    
    def _extract_surrounding_code(self, content: str, line_number: int) -> Dict[str, str]:
        """Extrae código circundante para análisis contextual."""
        lines = content.split('\n')
        start = max(0, line_number - 3)
        end = min(len(lines), line_number + 4)
        
        return {
            'before': '\n'.join(lines[start:line_number]),
            'current': lines[line_number] if line_number < len(lines) else '',
            'after': '\n'.join(lines[line_number + 1:end])
        }
    
    def _calculate_suggested_indentation(self, context_type: ContextType, current_indent: int, indent_info: IndentationInfo) -> str:
        """Calcula la indentación sugerida basada en el contexto."""
        if context_type == ContextType.FUNCTION_BODY:
            # Dentro de función, incrementar indentación
            # Usar atributos correctos de FileIndentationStats
            char = '\t' if indent_info.dominant_type.value == 'tabs' else ' '
            return char * (indent_info.dominant_size + current_indent)
        elif context_type == ContextType.CLASS_BODY:
            # Dentro de clase, usar indentación de clase + un nivel
            char = '\t' if indent_info.dominant_type.value == 'tabs' else ' '
            return char * (indent_info.dominant_size + current_indent)
        else:
            # Nivel de módulo o desconocido, usar indentación actual
            char = '\t' if indent_info.dominant_type.value == 'tabs' else ' '
            return char * current_indent
    
    def _generate_insertion_hints(self, context_type: ContextType, surrounding_code: Dict[str, str]) -> List[str]:
        """Genera sugerencias para la inserción basada en el contexto."""
        hints = []
        
        if context_type == ContextType.FUNCTION_BODY:
            hints.append("Inserción dentro de función - considerar indentación apropiada")
            hints.append("Verificar que el código mantenga la lógica de la función")
        elif context_type == ContextType.CLASS_BODY:
            hints.append("Inserción dentro de clase - puede requerir self parameter")
            hints.append("Considerar si es método o atributo de clase")
        elif context_type == ContextType.IMPORT_SECTION:
            hints.append("Inserción en sección de imports - ordenar alfabéticamente")
            hints.append("Agrupar imports por tipo (stdlib, third-party, local)")
        else:
            hints.append("Inserción a nivel de módulo - verificar orden lógico")
        
        return hints
    
    def _calculate_compatibility_score(self, context_type: ContextType, surrounding_code: Dict[str, str]) -> float:
        """Calcula un score de compatibilidad para la inserción."""
        base_score = 0.7
        
        # Ajustar score basado en contexto
        if context_type == ContextType.UNKNOWN:
            base_score -= 0.2
        elif context_type in [ContextType.FUNCTION_BODY, ContextType.CLASS_BODY]:
            base_score += 0.1
        
        # Verificar consistencia del código circundante
        before_lines = surrounding_code['before'].split('\n')
        after_lines = surrounding_code['after'].split('\n')
        
        if len(before_lines) > 0 and len(after_lines) > 0:
            base_score += 0.1
        
        return min(1.0, max(0.0, base_score))


def analyze_context(content: str, target_pattern: str, position_type: Union[PositionType, str] = PositionType.AFTER) -> ContextAnalysis:
    """
    Función de conveniencia para análisis contextual.
    
    Args:
        content: Contenido del archivo
        target_pattern: Patrón objetivo
        position_type: Tipo de posición
    
    Returns:
        ContextAnalysis con análisis completo
    """
    if isinstance(position_type, str):
        position_type = PositionType(position_type.lower())
    
    analyzer = ContextAnalyzer()
    return analyzer.analyze_context(content, target_pattern, position_type)