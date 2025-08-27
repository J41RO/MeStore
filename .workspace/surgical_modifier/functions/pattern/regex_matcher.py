import re
from typing import List, Dict, Any, Optional, Union, Pattern

class RegexMatcher:
    """Matcher robusto para patrones regex con manejo de errores"""
    
    def __init__(self):
        self._compiled_patterns = {}  # Cache de patrones compilados
        self._last_error = None
    
    def compile_pattern(self, pattern: str, flags: int = 0) -> Optional[Pattern]:
        """Compilar patron regex con cache"""
        cache_key = f"{pattern}:{flags}"
        
        if cache_key in self._compiled_patterns:
            return self._compiled_patterns[cache_key]
        
        try:
            compiled = re.compile(pattern, flags)
            self._compiled_patterns[cache_key] = compiled
            return compiled
        except re.error as e:
            self._last_error = f"Invalid regex pattern: {e}"
            return None
    
    def find_matches(self, pattern: str, text: str, flags: int = 0) -> Dict[str, Any]:
        """Encontrar todas las coincidencias de un patron"""
        compiled_pattern = self.compile_pattern(pattern, flags)
        if not compiled_pattern:
            return {
                'success': False,
                'error': self._last_error,
                'matches': []
            }
        
        try:
            matches = []
            for match in compiled_pattern.finditer(text):
                match_info = {
                    'match': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'groups': match.groups(),
                    'groupdict': match.groupdict()
                }
                matches.append(match_info)
            
            return {
                'success': True,
                'matches': matches,
                'count': len(matches),
                'pattern': pattern
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Match error: {e}",
                'matches': []
            }
    
    def find_single_match(self, pattern: str, text: str, flags: int = 0) -> Dict[str, Any]:
        """Encontrar primera coincidencia con informacion detallada"""
        compiled_pattern = self.compile_pattern(pattern, flags)
        if not compiled_pattern:
            return {'success': False, 'error': self._last_error}
        
        try:
            match = compiled_pattern.search(text)
            if match:
                return {
                    'success': True,
                    'found': True,
                    'match': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'groups': match.groups(),
                    'groupdict': match.groupdict(),
                    'span': match.span()
                }
            else:
                return {
                    'success': True,
                    'found': False,
                    'match': None
                }
        except Exception as e:
            return {'success': False, 'error': f"Search error: {e}"}

    def extract_groups(self, pattern: str, text: str, flags: int = 0) -> Dict[str, Any]:
        """Extraer grupos de captura especificos"""
        result = self.find_single_match(pattern, text, flags)
        
        if not result['success'] or not result.get('found'):
            return result
        
        groups_info = {
            'success': True,
            'numbered_groups': result['groups'],
            'named_groups': result['groupdict'],
            'full_match': result['match']
        }
        
        return groups_info

    def replace_pattern(self, pattern: str, replacement: str, text: str, 
                       count: int = 0, flags: int = 0) -> Dict[str, Any]:
        """Reemplazar coincidencias de patron"""
        compiled_pattern = self.compile_pattern(pattern, flags)
        if not compiled_pattern:
            return {'success': False, 'error': self._last_error}
        
        try:
            new_text = compiled_pattern.sub(replacement, text, count=count)
            replacements_made = len(compiled_pattern.findall(text))
            
            return {
                'success': True,
                'original_text': text,
                'new_text': new_text,
                'replacements_made': replacements_made,
                'pattern': pattern,
                'replacement': replacement
            }
        except Exception as e:
            return {'success': False, 'error': f"Replacement error: {e}"}

    def get_predefined_pattern(self, category: str, pattern_name: str) -> Optional[str]:
        """Obtener patron predefinido por categoria"""
        patterns_map = {
            'python': CodePatterns.PYTHON_PATTERNS,
            'javascript': CodePatterns.JAVASCRIPT_PATTERNS,  
            'universal': CodePatterns.UNIVERSAL_PATTERNS
        }
        
        if category in patterns_map:
            return patterns_map[category].get(pattern_name)
        return None

    def find_code_patterns(self, text: str, language: str = 'python') -> Dict[str, Any]:
        """Encontrar patrones de codigo comunes en texto"""
        if language == 'python':
            patterns = CodePatterns.PYTHON_PATTERNS
        elif language == 'javascript':
            patterns = CodePatterns.JAVASCRIPT_PATTERNS
        else:
            return {'success': False, 'error': f'Unsupported language: {language}'}
        
        results = {'success': True, 'language': language, 'patterns': {}}
        
        for pattern_name, pattern in patterns.items():
            matches = self.find_matches(pattern, text, re.MULTILINE)
            if matches['success']:
                results['patterns'][pattern_name] = matches['matches']
        
        return results
    
class CodePatterns:
    """Patrones regex predefinidos para codigo comun"""
    
    PYTHON_PATTERNS = {
        'function_def': r'def\s+(\w+)\s*\(([^)]*)\)\s*:',
        'class_def': r'class\s+(\w+)(?:\(([^)]*)\))?\s*:',
        'import_statement': r'^(?:from\s+(\S+)\s+)?import\s+(.+)$',
        'variable_assignment': r'(\w+)\s*=\s*(.+)',
        'docstring': r'"""(.*?)"""',
        'comment': r'#(.*)$'
    }
    
    JAVASCRIPT_PATTERNS = {
        'function_def': r'function\s+(\w+)\s*\(([^)]*)\)\s*{',
        'arrow_function': r'(?:const|let|var)\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>\s*{?',
        'class_def': r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{',
        'import_statement': r'import\s+(?:{([^}]+)}|(\w+))\s+from\s+["\']([^"\']+)["\']',
        'variable_declaration': r'(?:const|let|var)\s+(\w+)\s*=\s*(.+)',
        'comment': r'//(.*)$'
    }
    
    UNIVERSAL_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'url': r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
        'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'number': r'-?\d+(?:\.\d+)?',
        'word': r'\b\w+\b'
    }
    
    
    