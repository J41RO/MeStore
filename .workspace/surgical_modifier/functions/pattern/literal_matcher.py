from typing import List, Dict, Any, Optional, Tuple
import re
import time
# imports existentes...
from .base_matcher import BaseMatcher
class LiteralMatcher(BaseMatcher):
    """Matcher eficiente para texto literal sin overhead regex"""
    
    def __init__(self):
        super().__init__()
        self._last_search = None  
        self._case_sensitive = False  # Cambiar a False por defecto
        self._whole_words = False
        
    # Herencia de BaseMatcher - métodos estándar requeridos
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
                # Case insensitive replacement requires more work
            
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
        import time
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