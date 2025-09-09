import re
from typing import List, Dict, Any, Optional, Union, Pattern
from .base_matcher import BaseMatcher
import string

class RegexMatcher(BaseMatcher):
    """Matcher robusto para patrones regex con manejo de errores y auto-escape"""
    
    def __init__(self, engine_type: Optional[str] = None):
        self._compiled_patterns = {}  # Cache de patrones compilados
        self._last_error = None
        super().__init__(engine_type)  # Pasar engine_type al BaseMatcher
    
    def _detect_literal_pattern(self, pattern: str) -> bool:
        """Detectar si un pattern es texto literal (no regex)"""
        # Caracteres especiales de regex que indican pattern complejo
        regex_chars = set('[]()|*+?{}^$\\.')
        
        # Si contiene caracteres especiales comunes de regex, es regex
        special_count = sum(1 for char in pattern if char in regex_chars)
        
        # Si tiene más de 2 caracteres especiales o contiene anchors, es regex
        if special_count > 2 or pattern.startswith('^') or pattern.endswith('$'):
            return False
            
        # Si solo tiene curly braces aislados, probablemente es JSX literal
        if '{' in pattern and '}' in pattern and special_count <= 2:
            return True
            
        # Si no tiene caracteres especiales, es literal
        return special_count == 0
    
    # Métodos estándar requeridos por BaseMatcher
    def find(self, text: str, pattern: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Implementación estándar del método find()"""
        flags = kwargs.get('flags', 0)
        result = self.find_single_match(pattern, text, flags)
        if result.get('success') and result.get('found'):
            return self._normalize_result(
                result['match'],  # Es un string directamente
                result['start'],
                result['end'],
                list(result.get('groups', []))
            )
        return None
    
    def match(self, text: str, pattern: str, **kwargs) -> bool:
        """Implementación estándar del método match()"""
        flags = kwargs.get('flags', 0)
        result = self.find_single_match(pattern, text, flags)
        return result.get('success', False) and result.get('found', False)
        
    def find_all(self, text: str, pattern: str, **kwargs) -> List[Dict[str, Any]]:
        """Implementación estándar del método find_all()"""
        flags = kwargs.get('flags', 0)
        result = self.find_matches(pattern, text, flags)
        if result.get('success') and result.get('matches'):
            return [
                self._normalize_result(
                    match_obj.group(0) if hasattr(match_obj, 'group') else str(match_obj),
                    match_obj.start() if hasattr(match_obj, 'start') else 0,
                    match_obj.end() if hasattr(match_obj, 'end') else 0,
                    list(match_obj.groups()) if hasattr(match_obj, 'groups') else []
                )
                for match_obj in result['matches']
            ]
        return []
    
    def compile_pattern(self, pattern: str, flags: int = 0) -> Optional[Pattern]:
        """Compilar patron con auto-escape para texto literal"""
        cache_key = f"{pattern}:{flags}"
        
        if cache_key in self._compiled_patterns:
            return self._compiled_patterns[cache_key]
        
        # Detectar si es literal y aplicar escape automático
        if self._detect_literal_pattern(pattern):
            escaped_pattern = re.escape(pattern)
        else:
            escaped_pattern = pattern
            
        try:
            compiled = re.compile(escaped_pattern, flags)
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
    
    # ==================== ENGINE-SPECIFIC OPTIMIZATIONS v2.0 ====================

    def _optimize_pattern_for_engine(self, pattern: str) -> str:
        """
        Optimiza regex pattern según engine capabilities específicas.
        
        Args:
            pattern: Pattern regex original
            
        Returns:
            Pattern optimizado para el engine actual
        """
        if not self._engine_type:
            return pattern
            
        if self._engine_type == 'comby':
            return self._optimize_for_comby_engine(pattern)
        elif self._engine_type == 'ast':
            return self._optimize_for_ast_engine(pattern)
        elif self._engine_type == 'native':
            return self._optimize_for_native_engine(pattern)
        
        return pattern

    def _optimize_for_comby_engine(self, pattern: str) -> str:
        """
        Optimizaciones específicas para CombyEngine con structural search capabilities.
        Convierte regex patterns a structural templates cuando es posible.
        """
        if not self.has_engine_capability('structural_matching'):
            return pattern
            
        # Convertir patrones regex comunes a templates estructurales
        optimized = pattern
        
        # Convertir \w+ a :[identifier] para nombres/identificadores
        if self.has_engine_capability('template_generation'):
            import re
            # Patrones comunes que se pueden convertir a templates estructurales
            optimizations = [
                (r'\\w+', ':[identifier]'),
                (r'\\d+', ':[number]'),
                (r'[a-zA-Z_][a-zA-Z0-9_]*', ':[name]'),
                (r'\\s*=\\s*', ' = '),  # Normalizar espacios alrededor de asignaciones
                (r'\\s*{\\s*', ' { '),  # Normalizar espacios alrededor de llaves
            ]
            
            for regex_pattern, template in optimizations:
                if re.search(regex_pattern, optimized):
                    optimized = re.sub(regex_pattern, template, optimized)
        
        return optimized

    def _optimize_for_ast_engine(self, pattern: str) -> str:
        """
        Optimizaciones específicas para AST-based engines.
        Adapta patterns para trabajar mejor con estructura de AST.
        """
        if self.has_engine_capability('ast_pattern_matching'):
            # Para AST engines, convertir algunos patterns a búsquedas más estructurales
            import re
            optimized = pattern
            
            # Optimizar patrones que buscan definiciones de funciones
            if 'def' in pattern and self.has_engine_capability('function_matching'):
                # Convertir regex de función a pattern más específico para AST
                optimized = re.sub(r'def\s+(\w+)', r'def :[function_name]', optimized)
            
            # Optimizar patrones de imports
            if 'import' in pattern and self.has_engine_capability('import_matching'):
                optimized = re.sub(r'from\s+(\w+)\s+import', r'from :[module] import', optimized)
                
            return optimized
        
        return pattern

    def _optimize_for_native_engine(self, pattern: str) -> str:
        """
        Optimizaciones específicas para NativeEngine.
        Mantiene regex patterns pero puede aplicar optimizaciones de performance.
        """
        # Para native engine, aplicar optimizaciones de performance estándar
        optimized = pattern
        
        # Pre-compilar patrones frecuentes si el engine lo soporta
        if self.has_engine_capability('pattern_precompilation'):
            # El pattern se mantiene igual, pero se marca para pre-compilación
            cache_key = f"precompiled:{self._engine_type}:{pattern}"
            if cache_key not in self._compiled_patterns:
                try:
                    self._compiled_patterns[cache_key] = re.compile(pattern)
                except re.error:
                    pass  # Si no se puede compilar, usar pattern original
        
        return optimized

    def _translate_pattern_for_engine(self, pattern: str) -> Dict[str, Any]:
        """
        Traduce pattern regex a formato específico del engine con metadata.
        
        Args:
            pattern: Pattern regex original
            
        Returns:
            Dict con pattern traducido y metadata de traducción
        """
        optimized_pattern = self.get_engine_optimized_pattern(pattern)
        
        translation_info = {
            'original_pattern': pattern,
            'optimized_pattern': optimized_pattern,
            'engine_type': self._engine_type,
            'optimizations_applied': [],
            'structural_elements': []
        }
        
        # Detectar qué optimizaciones se aplicaron
        if optimized_pattern != pattern:
            if ':[' in optimized_pattern:
                translation_info['optimizations_applied'].append('template_conversion')
                translation_info['structural_elements'] = [
                    elem for elem in optimized_pattern.split() if ':[' in elem
                ]
            
            if self._engine_type == 'comby':
                translation_info['optimizations_applied'].append('structural_matching')
            elif self._engine_type == 'ast':
                translation_info['optimizations_applied'].append('ast_optimization')
        
        return translation_info

    def find_with_structural_optimization(self, text: str, pattern: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Versión optimizada de find() que aprovecha structural search capabilities.
        
        Args:
            text: Texto donde buscar
            pattern: Pattern a buscar
            **kwargs: Argumentos adicionales
            
        Returns:
            Resultado optimizado con información de traducción
        """
        translation_info = self._translate_pattern_for_engine(pattern)
        optimized_pattern = translation_info['optimized_pattern']
        
        # Si el pattern fue optimizado para structural matching, usar lógica especial
        if 'structural_matching' in translation_info['optimizations_applied']:
            # Para structural patterns, usar find normal pero con metadata adicional
            flags = kwargs.get('flags', 0)
            result = self.find_single_match(optimized_pattern, text, flags)
            
            if result.get('success') and result.get('found'):
                normalized = self._normalize_result(
                    result['match'],
                    result['start'],
                    result['end'],
                    list(result.get('groups', []))
                )
                # Agregar información de optimización
                normalized.update({
                    'translation_info': translation_info,
                    'engine_optimized': True
                })
                return normalized
        
        # Para otros casos, usar método estándar
        return self.find(text, optimized_pattern, **kwargs)

    def get_pattern_cache_info(self) -> Dict[str, Any]:
        """
        Retorna información sobre el cache de patterns optimizados por engine.
        
        Returns:
            Dict con estadísticas de cache y optimizaciones por engine
        """
        cache_stats = {
            'total_patterns_cached': len(self._compiled_patterns),
            'engine_type': self._engine_type,
            'capabilities': self.engine_capabilities,
            'cache_by_engine': {}
        }
        
        # Analizar cache por engine
        for cache_key in self._compiled_patterns.keys():
            if ':' in cache_key:
                parts = cache_key.split(':')
                if len(parts) >= 2:
                    engine_part = parts[1] if parts[0] == 'precompiled' else 'general'
                    cache_stats['cache_by_engine'].setdefault(engine_part, 0)
                    cache_stats['cache_by_engine'][engine_part] += 1
        
        return cache_stats
    
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