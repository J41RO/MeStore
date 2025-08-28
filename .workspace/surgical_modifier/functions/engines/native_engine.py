"""
Native Engine - Motor nativo usando functions existentes como fallback.
Encapsula funcionalidad actual del sistema en interface BaseEngine.
"""
from typing import Dict, List, Optional, Any, Union
import re

from .base_engine import (
    BaseEngine, EngineCapability, EngineResult, EngineMatch, 
    OperationType, EngineStatus, register_engine
)
from ..insertion.indentation_detector import detect_indentation
from ..insertion.position_calculator import calculate_position, PositionType
from ..insertion.content_formatter import format_content, ContentType
from ..insertion.context_analyzer import analyze_context
from ..pattern.literal_matcher import LiteralMatcher
from ..pattern.regex_matcher import RegexMatcher

@register_engine("native")
class NativeEngine(BaseEngine):
    """
    Motor nativo que utiliza las functions existentes del sistema.
    Sirve como fallback confiable y referencia para otros engines.
    """
    
    DEFAULT_NAME = "native"
    
    def __init__(self, name: str = "native", version: str = "1.0.0"):
        super().__init__(name, version)
        
        # Definir capacidades del motor nativo
        self._capabilities = {
            EngineCapability.LITERAL_SEARCH,
            EngineCapability.REGEX_SEARCH,
            EngineCapability.MULTILINE_PATTERNS,
            EngineCapability.CONTEXT_AWARE,
            EngineCapability.BATCH_OPERATIONS
        }
        
        # Soporta todos los lenguajes (general purpose)
        self._supported_languages = set()  # Empty = supports all
        
        # Inicializar matchers internos
        self._literal_matcher = LiteralMatcher()
        self._regex_matcher = RegexMatcher()
    
    def _create_engine_match(self, content: str, pattern: str, match_start: int, 
                        match_end: int, line_number: int) -> EngineMatch:
        """Crear EngineMatch desde información de match"""
        lines = content.split('\n')
        
        # Calcular posición en línea
        line_start = sum(len(line) + 1 for line in lines[:line_number-1])
        column_start = match_start - line_start
        column_end = match_end - line_start
        
        # Extraer contexto
        context_before = '\n'.join(lines[max(0, line_number-3):line_number-1])
        context_after = '\n'.join(lines[line_number:min(len(lines), line_number+2)])
        
        return EngineMatch(
            content=content[match_start:match_end],
            start_line=line_number,
            end_line=line_number,  # Simplified - single line matches
            start_column=column_start,
            end_column=column_end,
            context_before=context_before,
            context_after=context_after,
            metadata={
                'engine': self.name,
                'pattern': pattern,
                'match_type': 'native'
            }
        )
    def search(self, content: str, pattern: str, **kwargs) -> EngineResult:
        """
        Buscar patrón usando matchers nativos.
        """
        try:
            use_regex = kwargs.get('use_regex', False)
            case_sensitive = kwargs.get('case_sensitive', True)
            
            matches = []
            
            if use_regex:
                # RegexMatcher devuelve dict con 'matches' key
                self._regex_matcher.set_case_sensitive(case_sensitive)
                regex_result = self._regex_matcher.find_matches(content, pattern)
                
                if regex_result and regex_result.get('success', False):
                    for match_data in regex_result.get('matches', []):
                        line_number = content[:match_data['start']].count('\n') + 1
                        engine_match = self._create_engine_match(
                            content, pattern, match_data['start'], match_data['end'], line_number
                        )
                        matches.append(engine_match)
            else:
                # LiteralMatcher devuelve lista de dicts
                self._literal_matcher.set_case_sensitive(case_sensitive)
                literal_results = self._literal_matcher.find_all(content, pattern)
                
                if literal_results:
                    for match_data in literal_results:
                        line_number = content[:match_data['start']].count('\n') + 1
                        engine_match = self._create_engine_match(
                            content, pattern, match_data['start'], match_data['end'], line_number
                        )
                        matches.append(engine_match)
            
            status = EngineStatus.SUCCESS if matches else EngineStatus.FAILURE
            
            return EngineResult(
                status=status,
                matches=matches,
                operations_count=len(matches),
                metadata={
                    'engine': self.name,
                    'use_regex': use_regex,
                    'case_sensitive': case_sensitive
                }
            )
            
        except Exception as e:
            return EngineResult(
                status=EngineStatus.FAILURE,
                matches=[],
                error_message=f"Search failed: {str(e)}",
                metadata={'engine': self.name}
            )

    def replace(self, content: str, pattern: str, replacement: str, **kwargs) -> EngineResult:
        """
        Reemplazar patrón usando functions nativas.
        """
        try:
            use_regex = kwargs.get('use_regex', False)
            case_sensitive = kwargs.get('case_sensitive', True)
            
            # Buscar matches primero para tracking
            search_result = self.search(content, pattern, 
                                    use_regex=use_regex, 
                                    case_sensitive=case_sensitive)
            
            if not search_result.has_matches:
                return EngineResult(
                    status=EngineStatus.FAILURE,
                    matches=[],
                    error_message=f"Pattern '{pattern}' not found",
                    metadata={'engine': self.name}
                )
            
            # Realizar reemplazo con signature correcta
            if use_regex:
                self._regex_matcher.set_case_sensitive(case_sensitive)
                replace_result = self._regex_matcher.replace_pattern(content, pattern, replacement)
                if isinstance(replace_result, dict):
                    modified_content = replace_result.get('new_text', content)
                else:
                    modified_content = replace_result
            else:
                self._literal_matcher.set_case_sensitive(case_sensitive)
                # CORRECCIÓN FINAL: signature correcta (pattern, replacement, text)
                replace_result = self._literal_matcher.replace_literal(pattern, replacement, content, case_sensitive)
                if isinstance(replace_result, dict):
                    modified_content = replace_result.get('new_text', content)
                    operations_count = replace_result.get('replacements_made', 0)
                else:
                    modified_content = replace_result
                    operations_count = len(search_result.matches)
            
            return EngineResult(
                status=EngineStatus.SUCCESS,
                matches=search_result.matches,
                modified_content=modified_content,
                operations_count=operations_count,
                metadata={
                    'engine': self.name,
                    'use_regex': use_regex,
                    'case_sensitive': case_sensitive
                }
            )
            
        except Exception as e:
            return EngineResult(
                status=EngineStatus.FAILURE,
                matches=[],
                error_message=f"Replace failed: {str(e)}",
                metadata={'engine': self.name}
            )