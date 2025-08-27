# Crear functions/pattern/fuzzy_matcher.py con:
import difflib
from typing import List, Dict, Any, Optional, Tuple
from .base_matcher import BaseMatcher
class FuzzyMatcher(BaseMatcher):
    """Matcher aproximado usando algoritmos de similaridad"""
    
    def __init__(self, default_threshold: float = 0.6):
        self.default_threshold = default_threshold
        self._similarity_cache = {}  # Cache resultados similaridad
        super().__init__()
    
    # Métodos estándar requeridos por BaseMatcher
    def find(self, text: str, pattern: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Implementación estándar del método find()"""
        threshold = kwargs.get('threshold', self.default_threshold)
        result = self.find_fuzzy_match(pattern, text, threshold)
        if result.get('success') and result.get('found'):
            return self._normalize_result(
                result['match'],  # Es string directamente
                result['position'],
                result['position'] + len(result['match'])  # Calcular end
            )
        return None
    
    def match(self, text: str, pattern: str, **kwargs) -> bool:
        """Implementación estándar del método match()"""
        threshold = kwargs.get('threshold', self.default_threshold)
        result = self.find_fuzzy_match(pattern, text, threshold)
        return result.get('success', False)
    
    def find_all(self, text: str, pattern: str, **kwargs) -> List[Dict[str, Any]]:
        """Implementación estándar del método find_all()"""
        threshold = kwargs.get('threshold', self.default_threshold)
        result = self.find_all_fuzzy_matches(pattern, text, threshold)
        if result.get('success') and result.get('matches'):
            return [
                self._normalize_result(
                    match['match'],
                    match['position'],
                    match['position'] + len(match['match'])
                )
                for match in result['matches']
            ]
        return []
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcular similaridad entre dos textos (0.0 - 1.0)"""
        if not text1 or not text2:
            return 0.0
        
        # Use cache for identical comparisons
        cache_key = f"{text1}|{text2}"
        if cache_key in self._similarity_cache:
            return self._similarity_cache[cache_key]
        
        # Calculate similarity using SequenceMatcher
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
        self._similarity_cache[cache_key] = similarity
        return similarity
    
    def find_fuzzy_match(self, pattern: str, text: str, threshold: float = None) -> Dict[str, Any]:
        """Encontrar mejor match aproximado de patron en texto"""
        if not pattern:
            return {'success': False, 'error': 'Empty pattern'}
        
        threshold = threshold or self.default_threshold
        
        try:
            # Split text into words for word-level matching
            words = text.split()
            best_match = None
            best_similarity = 0.0
            best_position = -1
            
            # Check each word
            for i, word in enumerate(words):
                similarity = self.calculate_similarity(pattern.lower(), word.lower())
                if similarity >= threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_match = word
                    # Calculate position in original text
                    position = sum(len(words[j]) + 1 for j in range(i))
                    best_position = position
            
            # Also check substrings if no word match found
            if best_match is None:
                pattern_len = len(pattern)
                for i in range(len(text) - pattern_len + 1):
                    substring = text[i:i + pattern_len]
                    similarity = self.calculate_similarity(pattern.lower(), substring.lower())
                    if similarity >= threshold and similarity > best_similarity:
                        best_similarity = similarity
                        best_match = substring
                        best_position = i
            
            if best_match:
                return {
                    'success': True,
                    'found': True,
                    'pattern': pattern,
                    'match': best_match,
                    'position': best_position,
                    'similarity': best_similarity,
                    'threshold': threshold
                }
            else:
                return {
                    'success': True,
                    'found': False,
                    'pattern': pattern,
                    'threshold': threshold
                }
        
        except Exception as e:
            return {'success': False, 'error': f'Fuzzy match error: {e}'}
    
    def find_all_fuzzy_matches(self, pattern: str, text: str, threshold: float = None) -> Dict[str, Any]:
        """Encontrar todos los matches aproximados"""
        if not pattern:
            return {'success': False, 'error': 'Empty pattern'}
        
        threshold = threshold or self.default_threshold
        
        try:
            matches = []
            words = text.split()
            
            # Check each word
            for i, word in enumerate(words):
                similarity = self.calculate_similarity(pattern.lower(), word.lower())
                if similarity >= threshold:
                    position = sum(len(words[j]) + 1 for j in range(i))
                    match_info = {
                        'match': word,
                        'position': position,
                        'end_position': position + len(word),
                        'similarity': similarity,
                        'type': 'word_match'
                    }
                    matches.append(match_info)
            
            return {
                'success': True,
                'pattern': pattern,
                'matches': matches,
                'count': len(matches),
                'threshold': threshold
            }
        
        except Exception as e:
            return {'success': False, 'error': f'Fuzzy matches error: {e}'}
        
        # Agregar a FuzzyMatcher (maximo 35 lineas):
    def get_close_matches(self, pattern: str, candidates: List[str], 
                        n: int = 5, cutoff: float = 0.6) -> Dict[str, Any]:
        """Obtener matches cercanos de una lista de candidatos"""
        if not pattern or not candidates:
            return {'success': False, 'error': 'Empty pattern or candidates'}
        
        try:
            # Use difflib.get_close_matches with custom scoring
            close_matches = difflib.get_close_matches(pattern, candidates, n=n, cutoff=cutoff)
            
            # Add similarity scores
            matches_with_scores = []
            for match in close_matches:
                similarity = self.calculate_similarity(pattern, match)
                matches_with_scores.append({
                    'match': match,
                    'similarity': similarity,
                    'original_index': candidates.index(match) if match in candidates else -1
                })
            
            # Sort by similarity (highest first)
            matches_with_scores.sort(key=lambda x: x['similarity'], reverse=True)
            
            return {
                'success': True,
                'pattern': pattern,
                'matches': matches_with_scores,
                'count': len(matches_with_scores),
                'cutoff': cutoff
            }
        
        except Exception as e:
            return {'success': False, 'error': f'Close matches error: {e}'}

    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calcular distancia Levenshtein (edit distance)"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    def similarity_detailed(self, text1: str, text2: str) -> Dict[str, Any]:
        """Analisis detallado de similaridad entre textos"""
        if not text1 or not text2:
            return {'success': False, 'error': 'Empty texts'}
        
        try:
            # Multiple similarity metrics
            seq_matcher = difflib.SequenceMatcher(None, text1, text2)
            ratio = seq_matcher.ratio()
            
            # Levenshtein-based similarity
            edit_distance = self.levenshtein_distance(text1, text2)
            max_len = max(len(text1), len(text2))
            edit_similarity = 1 - (edit_distance / max_len) if max_len > 0 else 1.0
            
            # Character-level analysis
            matching_blocks = seq_matcher.get_matching_blocks()
            total_matching_chars = sum(block.size for block in matching_blocks)
            
            # Word-level analysis
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            common_words = words1.intersection(words2)
            total_words = words1.union(words2)
            word_similarity = len(common_words) / len(total_words) if total_words else 0
            
            return {
                'success': True,
                'text1': text1,
                'text2': text2,
                'sequence_ratio': ratio,
                'edit_distance': edit_distance,
                'edit_similarity': edit_similarity,
                'matching_chars': total_matching_chars,
                'word_similarity': word_similarity,
                'common_words': list(common_words),
                'overall_score': (ratio + edit_similarity + word_similarity) / 3
            }
        
        except Exception as e:
            return {'success': False, 'error': f'Detailed similarity error: {e}'}
            
            # Agregar metodos contextuales y optimizaciones (maximo 30 lineas):
    def fuzzy_search_in_lines(self, pattern: str, lines: List[str], 
                            threshold: float = None) -> Dict[str, Any]:
        """Busqueda fuzzy en lista de lineas con contexto"""
        if not pattern or not lines:
            return {'success': False, 'error': 'Empty pattern or lines'}
        
        threshold = threshold or self.default_threshold
        
        try:
            matches = []
            for line_num, line in enumerate(lines, 1):
                line_matches = self.find_all_fuzzy_matches(pattern, line, threshold)
                if line_matches['success'] and line_matches['matches']:
                    for match in line_matches['matches']:
                        match_with_context = {
                            'line_number': line_num,
                            'line_content': line,
                            'match_info': match,
                            'context': line.strip()
                        }
                        matches.append(match_with_context)
            
            return {
                'success': True,
                'pattern': pattern,
                'matches': matches,
                'lines_searched': len(lines),
                'lines_with_matches': len(set(match['line_number'] for match in matches)),
                'threshold': threshold
            }
        
        except Exception as e:
            return {'success': False, 'error': f'Line search error: {e}'}

    def suggest_corrections(self, pattern: str, text: str, max_suggestions: int = 5) -> Dict[str, Any]:
        """Sugerir correcciones para patron no encontrado"""
        if not pattern:
            return {'success': False, 'error': 'Empty pattern'}
        
        try:
            # Extract unique words from text
            words = list(set(text.lower().split()))
            
            # Find close matches with lower threshold for suggestions
            suggestions = self.get_close_matches(pattern.lower(), words, 
                                            n=max_suggestions, cutoff=0.3)
            
            if suggestions['success'] and suggestions['matches']:
                # Add context for each suggestion
                enhanced_suggestions = []
                for suggestion in suggestions['matches'][:max_suggestions]:
                    # Find original case version in text
                    original_word = suggestion['match']
                    for word in text.split():
                        if word.lower() == original_word:
                            original_word = word
                            break
                    
                    enhanced_suggestions.append({
                        'suggestion': original_word,
                        'similarity': suggestion['similarity'],
                        'reason': self._get_suggestion_reason(pattern, original_word)
                    })
                
                return {
                    'success': True,
                    'pattern': pattern,
                    'suggestions': enhanced_suggestions,
                    'count': len(enhanced_suggestions)
                }
            else:
                return {
                    'success': True,
                    'pattern': pattern,
                    'suggestions': [],
                    'count': 0
                }
        
        except Exception as e:
            return {'success': False, 'error': f'Suggestions error: {e}'}

    def _get_suggestion_reason(self, pattern: str, suggestion: str) -> str:
        """Generar razon para sugerencia"""
        distance = self.levenshtein_distance(pattern.lower(), suggestion.lower())
        if distance == 1:
            return "Similar spelling (1 character difference)"
        elif distance == 2:
            return "Similar spelling (2 character difference)"
        elif pattern.lower() in suggestion.lower() or suggestion.lower() in pattern.lower():
            return "Partial match"
        else:
            return f"Approximate match (edit distance: {distance})"

    def benchmark_fuzzy_performance(self, patterns: List[str], text: str) -> Dict[str, Any]:
        """Benchmark performance fuzzy matching"""
        import time
        
        try:
            results = []
            total_start = time.time()
            
            for pattern in patterns:
                start_time = time.time()
                result = self.find_fuzzy_match(pattern, text)
                end_time = time.time()
                
                results.append({
                    'pattern': pattern,
                    'found': result.get('found', False),
                    'similarity': result.get('similarity', 0.0),
                    'time_ms': (end_time - start_time) * 1000
                })
            
            total_time = time.time() - total_start
            
            return {
                'success': True,
                'results': results,
                'total_patterns': len(patterns),
                'total_time_ms': total_time * 1000,
                'average_time_ms': (total_time * 1000) / len(patterns) if patterns else 0,
                'cache_hits': len(self._similarity_cache)
            }
        
        except Exception as e:
            return {'success': False, 'error': f'Benchmark error: {e}'}