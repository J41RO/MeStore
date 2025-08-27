from typing import List, Dict, Any, Optional, Tuple
import re
import time

class LiteralMatcher:
    """Matcher eficiente para texto literal sin overhead regex"""
    
    def __init__(self):
        self._last_search = None  # Cache ultima busqueda
        self._case_sensitive = True
        self._whole_words = False
    
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
        try:
            from functions.pattern.regex_matcher import RegexMatcher
            regex_matcher = RegexMatcher()
            
            # Benchmark literal matching
            start_time = time.time()
            for _ in range(iterations):
                self.find_literal(pattern, text)
            literal_time = time.time() - start_time
            
            # Benchmark regex matching  
            start_time = time.time()
            for _ in range(iterations):
                regex_matcher.find_matches(re.escape(pattern), text)
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

    def find_multiple_patterns(self, patterns: List[str], text: str, case_sensitive: bool = True) -> Dict[str, Any]:
        """Encontrar multiples patrones literales en una pasada"""
        if not patterns:
            return {'success': False, 'error': 'No patterns provided'}
        
        try:
            results = {}
            all_matches = []
            
            for pattern in patterns:
                pattern_result = self.find_all_literals(pattern, text, case_sensitive)
                if pattern_result['success']:
                    results[pattern] = pattern_result
                    # Add pattern info to each match
                    for match in pattern_result['matches']:
                        match['pattern'] = pattern
                        all_matches.append(match)
            
            # Sort all matches by position
            all_matches.sort(key=lambda x: x['position'])
            
            return {
                'success': True,
                'patterns': patterns,
                'individual_results': results,
                'all_matches': all_matches,
                'total_matches': len(all_matches),
                'case_sensitive': case_sensitive
            }
        except Exception as e:
            return {'success': False, 'error': f'Multiple patterns error: {e}'}

    def get_context_around_match(self, pattern: str, text: str, context_chars: int = 20) -> Dict[str, Any]:
        """Obtener contexto alrededor de matches para preview"""
        result = self.find_all_literals(pattern, text)
        if not result['success'] or not result['matches']:
            return result
        
        try:
            matches_with_context = []
            for match in result['matches']:
                start_pos = match['position']
                end_pos = match['end_position']
                
                # Context boundaries
                context_start = max(0, start_pos - context_chars)
                context_end = min(len(text), end_pos + context_chars)
                
                context_info = {
                    'match': match,
                    'context': text[context_start:context_end],
                    'context_start': context_start,
                    'context_end': context_end,
                    'match_in_context_start': start_pos - context_start,
                    'match_in_context_end': end_pos - context_start
                }
                matches_with_context.append(context_info)
            
            result['matches_with_context'] = matches_with_context
            return result
        except Exception as e:
            return {'success': False, 'error': f'Context error: {e}'}
    