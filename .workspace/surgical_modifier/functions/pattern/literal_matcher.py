from typing import List, Dict, Any, Optional, Tuple
import re
import time
from .base_matcher import BaseMatcher


class LiteralMatcher(BaseMatcher):
    """Matcher eficiente para texto literal sin overhead regex"""
    
    def __init__(self, engine_type: Optional[str] = None):
        super().__init__(engine_type)  # Pasar engine_type al BaseMatcher
        self._last_search = None
        self._case_sensitive = False  # Case insensitive por defecto
        self._whole_words = False
        
    # Métodos estándar requeridos por BaseMatcher
    def find(self, text: str, pattern: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Implementación estándar del método find()"""
        case_sensitive = kwargs.get('case_sensitive', self._case_sensitive)
        result = self.find_literal(pattern, text, case_sensitive=case_sensitive)
        if result.get('success') and result.get('found'):
            return self._normalize_result(
                result['matched_text'],
                result['position'],
                result['end_position']
            )
        return None

    def match(self, text: str, pattern: str, **kwargs) -> bool:
        """Implementación estándar del método match()"""
        case_sensitive = kwargs.get('case_sensitive', self._case_sensitive)
        result = self.find_literal(pattern, text, case_sensitive=case_sensitive)
        return result.get('success', False) and result.get('found', False)

    def find_all(self, text: str, pattern: str, **kwargs) -> List[Dict[str, Any]]:
        """Implementación estándar del método find_all()"""
        case_sensitive = kwargs.get('case_sensitive', self._case_sensitive)
        result = self.find_all_literals(pattern, text, case_sensitive=case_sensitive)
        if result.get('success') and result.get('matches'):
            return [
                self._normalize_result(
                    match['matched_text'], 
                    match['position'], 
                    match['end_position']
                )
                for match in result['matches']
            ]
        return []
    
    # Métodos especializados para funcionalidad literal
    def find_literal(self, pattern: str, text: str, case_sensitive: bool = True) -> Dict[str, Any]:
        """Encontrar primera ocurrencia de patron literal"""
        if not pattern:
            return {'success': False, 'error': 'Empty pattern'}
        
        search_text = text if case_sensitive else text.lower()
        search_pattern = pattern if case_sensitive else pattern.lower()
        
        try:
            position = search_text.find(search_pattern)
            
            if position != -1:
                return {
                    'success': True,
                    'found': True,
                    'pattern': pattern,
                    'position': position,
                    'end_position': position + len(pattern),
                    'matched_text': text[position:position + len(pattern)],
                    'case_sensitive': case_sensitive
                }
            else:
                return {
                    'success': True,
                    'found': False,
                    'pattern': pattern,
                    'case_sensitive': case_sensitive
                }
        except Exception as e:
            return {'success': False, 'error': f'Search error: {e}'}
    
    def find_all_literals(self, pattern: str, text: str, case_sensitive: bool = True) -> Dict[str, Any]:
        """Encontrar todas las ocurrencias de patron literal"""
        if not pattern:
            return {'success': False, 'error': 'Empty pattern'}
        
        search_text = text if case_sensitive else text.lower()
        search_pattern = pattern if case_sensitive else pattern.lower()
        
        try:
            matches = []
            start = 0
            
            while True:
                position = search_text.find(search_pattern, start)
                if position == -1:
                    break
                
                match_info = {
                    'position': position,
                    'end_position': position + len(pattern),
                    'matched_text': text[position:position + len(pattern)],
                    'length': len(pattern)
                }
                matches.append(match_info)
                start = position + 1  # Overlap search
            
            return {
                'success': True,
                'pattern': pattern,
                'matches': matches,
                'count': len(matches),
                'case_sensitive': case_sensitive
            }
        except Exception as e:
            return {'success': False, 'error': f'Search error: {e}'}
    
    # ==================== ENGINE-SPECIFIC OPTIMIZATIONS v2.0 ====================

    def _optimize_pattern_for_engine(self, pattern: str) -> str:
        """
        Optimiza pattern según engine capabilities específicas.
        
        Args:
            pattern: Pattern literal original
            
        Returns:
            Pattern optimizado para el engine actual
        """
        if not self._engine_type:
            return pattern
            
        if self._engine_type == 'native':
            return self._optimize_for_native_engine(pattern)
        elif self._engine_type == 'ast':
            return self._optimize_for_ast_engine(pattern)
        elif self._engine_type == 'comby':
            return self._optimize_for_structural_engine(pattern)
        
        return pattern

    def _optimize_for_native_engine(self, pattern: str) -> str:
        """
        Optimizaciones específicas para NativeEngine.
        NativeEngine maneja búsquedas de strings eficientemente.
        """
        # Para native engine, usar pattern tal como está
        # Pero pre-procesar para case sensitivity si el engine lo soporta
        if self.has_engine_capability('case_insensitive_native'):
            return pattern.lower() if not self._case_sensitive else pattern
        return pattern

    def _optimize_for_ast_engine(self, pattern: str) -> str:
        """
        Optimizaciones específicas para AST-based engines.
        AST engines pueden aprovechar estructura del código.
        """
        # AST engine puede beneficiarse de escape de caracteres especiales
        if self.has_engine_capability('ast_literal_matching'):
            # Escapar caracteres que pueden ser problemáticos en AST parsing
            special_chars = ['(', ')', '[', ']', '{', '}', '.', '*', '+', '?', '^', '$', '|', '\\']
            escaped_pattern = pattern
            for char in special_chars:
                if char in pattern:
                    escaped_pattern = escaped_pattern.replace(char, f'\\{char}')
            return escaped_pattern
        return pattern

    def _optimize_for_structural_engine(self, pattern: str) -> str:
        """
        Optimizaciones específicas para structural search engines como Comby.
        """
        if self.has_engine_capability('structural_matching'):
            # Para structural engines, puede ser útil crear templates
            if ' ' in pattern and self.has_engine_capability('template_generation'):
                # Convertir espacios múltiples a templates flexibles
                import re
                normalized = re.sub(r'\s+', ' :[_] ', pattern)
                return normalized
        return pattern

    def find_with_engine_optimization(self, text: str, pattern: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Versión optimizada de find() que aprovecha engine-specific optimizations.
        
        Args:
            text: Texto donde buscar
            pattern: Pattern a buscar
            **kwargs: Argumentos adicionales
            
        Returns:
            Resultado optimizado según el engine configurado
        """
        optimized_pattern = self.get_engine_optimized_pattern(pattern)
        
        # Si el pattern no cambió, usar método estándar
        if optimized_pattern == pattern:
            return self.find(text, pattern, **kwargs)
        
        # Usar pattern optimizado
        case_sensitive = kwargs.get('case_sensitive', self._case_sensitive)
        result = self.find_literal(optimized_pattern, text, case_sensitive=case_sensitive)
        
        if result.get('success') and result.get('found'):
            # Ajustar resultado para mostrar pattern original
            normalized = self._normalize_result(
                result['matched_text'],
                result['position'], 
                result['end_position']
            )
            normalized['original_pattern'] = pattern
            normalized['optimized_pattern'] = optimized_pattern
            normalized['engine_type'] = self._engine_type
            return normalized
        
        return None

    def get_engine_performance_info(self) -> Dict[str, Any]:
        """
        Retorna información de performance según el engine configurado.
        
        Returns:
            Dict con información de capabilities y optimizaciones aplicadas
        """
        return {
            'engine_type': self._engine_type,
            'capabilities': self.engine_capabilities,
            'optimizations_available': {
                'native': ['case_insensitive_native'],
                'ast': ['ast_literal_matching'],
                'comby': ['structural_matching', 'template_generation']
            },
            'pattern_cache_size': len(self._pattern_cache),
            'supported_engines': ['native', 'ast', 'comby']
        }
    
    
    def count_occurrences(self, pattern: str, text: str, case_sensitive: bool = True) -> Dict[str, Any]:
        """Contar ocurrencias de patron literal (mas eficiente que find_all)"""
        if not pattern:
            return {'success': False, 'error': 'Empty pattern'}
        
        search_text = text if case_sensitive else text.lower()
        search_pattern = pattern if case_sensitive else pattern.lower()
        
        try:
            count = search_text.count(search_pattern)
            return {
                'success': True,
                'pattern': pattern,
                'count': count,
                'case_sensitive': case_sensitive
            }
        except Exception as e:
            return {'success': False, 'error': f'Count error: {e}'}
    
    def find_whole_words(self, pattern: str, text: str, case_sensitive: bool = True) -> Dict[str, Any]:
        """Encontrar patron como palabras completas solamente"""
        if not pattern:
            return {'success': False, 'error': 'Empty pattern'}
        
        # Usar regex simple para word boundaries pero mantener eficiencia literal
        word_pattern = r'\b' + re.escape(pattern) + r'\b'
        flags = 0 if case_sensitive else re.IGNORECASE
        
        try:
            matches = []
            for match in re.finditer(word_pattern, text, flags):
                match_info = {
                    'position': match.start(),
                    'end_position': match.end(),
                    'matched_text': match.group(),
                    'length': len(match.group())
                }
                matches.append(match_info)
            
            return {
                'success': True,
                'pattern': pattern,
                'matches': matches,
                'count': len(matches),
                'whole_words_only': True,
                'case_sensitive': case_sensitive
            }
        except Exception as e:
            return {'success': False, 'error': f'Whole words search error: {e}'}

    def replace_literal(self, pattern: str, replacement: str, text: str, 
                       case_sensitive: bool = True, max_replacements: int = -1) -> Dict[str, Any]:
        """Reemplazar ocurrencias literales"""
        if not pattern:
            return {'success': False, 'error': 'Empty pattern'}
        
        try:
            if case_sensitive:
                if max_replacements == -1:
                    new_text = text.replace(pattern, replacement)
                    count = text.count(pattern)
                else:
                    new_text = text.replace(pattern, replacement, max_replacements)
                    count = min(text.count(pattern), max_replacements)
            else:
                # Case insensitive replacement requires regex
                escaped_pattern = re.escape(pattern)
                regex_pattern = re.compile(escaped_pattern, re.IGNORECASE)
                if max_replacements == -1:
                    new_text = regex_pattern.sub(replacement, text)
                    count = len(regex_pattern.findall(text))
                else:
                    new_text = regex_pattern.sub(replacement, text, count=max_replacements)
                    count = min(len(regex_pattern.findall(text)), max_replacements)
            
            return {
                'success': True,
                'original_text': text,
                'new_text': new_text,
                'pattern': pattern,
                'replacement': replacement,
                'replacements_made': count,
                'case_sensitive': case_sensitive
            }
        except Exception as e:
            return {'success': False, 'error': f'Replacement error: {e}'}

    def find_at_boundaries(self, pattern: str, text: str, boundary_type: str = 'line') -> Dict[str, Any]:
        """Encontrar patron en boundaries especificos (start/end line, word, etc)"""
        if not pattern:
            return {'success': False, 'error': 'Empty pattern'}
        
        try:
            matches = []
            
            if boundary_type == 'line':
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    # Start of line
                    if line.startswith(pattern):
                        pos = sum(len(lines[j]) + 1 for j in range(i))  # +1 for \n
                        matches.append({
                            'position': pos,
                            'boundary': 'line_start',
                            'line_number': i + 1,
                            'matched_text': pattern
                        })
                    # End of line
                    if line.endswith(pattern):
                        pos = sum(len(lines[j]) + 1 for j in range(i)) + len(line) - len(pattern)
                        matches.append({
                            'position': pos,
                            'boundary': 'line_end', 
                            'line_number': i + 1,
                            'matched_text': pattern
                        })
            elif boundary_type == 'text':
                # Start of text
                if text.startswith(pattern):
                    matches.append({
                        'position': 0,
                        'boundary': 'text_start',
                        'matched_text': pattern
                    })
                # End of text
                if text.endswith(pattern):
                    matches.append({
                        'position': len(text) - len(pattern),
                        'boundary': 'text_end',
                        'matched_text': pattern
                    })
            
            return {
                'success': True,
                'pattern': pattern,
                'boundary_type': boundary_type,
                'matches': matches,
                'count': len(matches)
            }
        except Exception as e:
            return {'success': False, 'error': f'Boundary search error: {e}'}
    
    def benchmark_vs_regex(self, pattern: str, text: str, iterations: int = 1000) -> Dict[str, Any]:
        """Benchmark literal vs regex matching"""
        try:
            # Benchmark literal matching
            start_time = time.time()
            for _ in range(iterations):
                self.find_literal(pattern, text)
            literal_time = time.time() - start_time

            # Benchmark regex matching usando re nativo (sin dependencia externa)
            escaped_pattern = re.escape(pattern)
            start_time = time.time()
            for _ in range(iterations):
                re.findall(escaped_pattern, text)
            regex_time = time.time() - start_time

            return {
                'success': True,
                'pattern': pattern,
                'iterations': iterations,
                'literal_time': literal_time,
                'regex_time': regex_time,
                'speedup_factor': regex_time / literal_time if literal_time > 0 else float('inf'),
                'literal_faster': literal_time < regex_time
            }
        except Exception as e:
            return {'success': False, 'error': f'Benchmark error: {e}'}

    # Métodos adicionales requeridos por tests
    def find_multiple_patterns(self, patterns: List[str], text: str, **kwargs) -> Dict[str, Any]:
        """Buscar múltiples patrones usando find_all para cada uno"""
        total_matches = 0
        results = {}
        case_sensitive = kwargs.get('case_sensitive', self._case_sensitive)
        
        for pattern in patterns:
            matches = self.find_all(text, pattern, case_sensitive=case_sensitive)
            if matches:
                results[pattern] = matches
                total_matches += len(matches)
        
        return {
            'success': True,
            'patterns_found': list(results.keys()),
            'results': results,
            'total_patterns': len(patterns),
            'found_patterns': len(results),
            'total_matches': total_matches
        }
    
    def get_context_around_match(self, pattern: str, text: str, context_chars: int = 10, **kwargs) -> Dict[str, Any]:
        """Obtener contexto alrededor de una coincidencia"""
        case_sensitive = kwargs.get('case_sensitive', self._case_sensitive)
        matches = self.find_all(text, pattern, case_sensitive=case_sensitive)
        
        if not matches:
            return {
                'success': False,
                'error': 'Pattern not found',
                'pattern': pattern
            }
        
        matches_with_context = []
        for match in matches:
            start = match['start']
            end = match['end']
            
            context_start = max(0, start - context_chars)
            context_end = min(len(text), end + context_chars)
            
            matches_with_context.append({
                'match': match['match'],
                'match_start': start,
                'match_end': end,
                'context': text[context_start:context_end],
                'context_start': context_start,
                'context_end': context_end,
                'before_context': text[context_start:start],
                'after_context': text[end:context_end]
            })
        
        return {
            'success': True,
            'pattern': pattern,
            'matches_with_context': matches_with_context
        }