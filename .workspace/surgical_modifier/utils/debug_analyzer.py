import re
import os
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from utils import logger

class PatternDebugger:
    """
    Analizador de debug para troubleshooting step-by-step de patrones.
    
    Proporciona análisis detallado de matching de patrones, visualización
    de regex y diagnóstico de fallos en operaciones de matching.
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.debug_results = []
    
    def debug_pattern_matching(self, file_path: str, pattern: str, 
                             content_preview: bool = True, 
                             max_preview_lines: int = 10) -> Dict[str, Any]:
        """
        Analiza step-by-step el proceso de matching de patrones.
        
        Args:
            file_path: Ruta del archivo a analizar
            pattern: Patrón a buscar (puede ser regex)
            content_preview: Si mostrar preview del contenido
            max_preview_lines: Máximo líneas de preview
            
        Returns:
            Dict con análisis completo del matching
        """
        debug_info = {
            'file_path': file_path,
            'pattern': pattern,
            'file_exists': False,
            'content_lines': 0,
            'matches_found': [],
            'regex_analysis': {},
            'preview_lines': [],
            'errors': []
        }
        
        try:
            # Verificar existencia del archivo
            if not os.path.exists(file_path):
                debug_info['errors'].append(f"File not found: {file_path}")
                return debug_info
            
            debug_info['file_exists'] = True
            
            # Leer contenido
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                debug_info['content_lines'] = len(lines)
                
                if content_preview:
                    debug_info['preview_lines'] = lines[:max_preview_lines]
            
            # Análisis de regex
            debug_info['regex_analysis'] = self._analyze_regex_pattern(pattern)
            
            # Buscar matches
            matches = list(re.finditer(pattern, content, re.MULTILINE))
            for i, match in enumerate(matches):
                match_info = {
                    'match_number': i + 1,
                    'start_pos': match.start(),
                    'end_pos': match.end(),
                    'matched_text': match.group(0),
                    'line_number': content[:match.start()].count('\n') + 1,
                    'groups': match.groups() if match.groups() else []
                }
                debug_info['matches_found'].append(match_info)
            
            if self.verbose:
                self._log_debug_results(debug_info)
            
        except re.error as e:
            debug_info['errors'].append(f"Regex error: {str(e)}")
        except Exception as e:
            debug_info['errors'].append(f"General error: {str(e)}")
        
        self.debug_results.append(debug_info)
        return debug_info
    
    def analyze_pattern_failures(self, file_path: str, pattern: str, 
                               expected_matches: int = None) -> Dict[str, Any]:
        """
        Diagnostica por qué fallan los patrones de matching.
        
        Args:
            file_path: Archivo donde buscar
            pattern: Patrón que falla
            expected_matches: Número esperado de matches
            
        Returns:
            Análisis de por qué falla el patrón
        """
        analysis = {
            'pattern': pattern,
            'failure_reasons': [],
            'suggestions': [],
            'alternative_patterns': []
        }
        
        debug_result = self.debug_pattern_matching(file_path, pattern, content_preview=True)
        
        if debug_result['errors']:
            analysis['failure_reasons'].extend(debug_result['errors'])
            return analysis
        
        matches_count = len(debug_result['matches_found'])
        
        # Analizar por qué no hay matches o hay menos de los esperados
        if matches_count == 0:
            analysis['failure_reasons'].append("No matches found")
            analysis['suggestions'].extend([
                "Check if pattern is case-sensitive",
                "Try escaping special characters",
                "Verify the pattern syntax",
                "Check if content actually contains expected text"
            ])
            
            # Sugerir patrones alternativos
            analysis['alternative_patterns'] = self._suggest_alternative_patterns(pattern)
        
        elif expected_matches and matches_count < expected_matches:
            analysis['failure_reasons'].append(
                f"Found {matches_count} matches but expected {expected_matches}"
            )
            analysis['suggestions'].append("Pattern might be too restrictive")
        
        return analysis
    
    def _analyze_regex_pattern(self, pattern: str) -> Dict[str, Any]:
        """Analiza estructura del patrón regex."""
        analysis = {
            'pattern': pattern,
            'is_valid': True,
            'special_chars': [],
            'groups': 0,
            'flags_suggested': []
        }
        
        try:
            # Compilar para verificar validez
            compiled = re.compile(pattern)
            analysis['groups'] = compiled.groups
            
            # Detectar caracteres especiales
            special_chars = ['.', '*', '+', '?', '^', '$', '\\', '|', '[', ']', '(', ')', '{', '}']
            analysis['special_chars'] = [c for c in special_chars if c in pattern]
            
            # Sugerir flags si es necesario
            if any(c.isupper() for c in pattern):
                analysis['flags_suggested'].append('re.IGNORECASE for case-insensitive matching')
            
            if '\\n' in pattern or '\n' in pattern:
                analysis['flags_suggested'].append('re.MULTILINE for multiline matching')
                
        except re.error as e:
            analysis['is_valid'] = False
            analysis['error'] = str(e)
        
        return analysis
    
    def _suggest_alternative_patterns(self, original_pattern: str) -> List[str]:
        """Sugiere patrones alternativos basados en el original."""
        alternatives = []
        
        # Versión case-insensitive
        alternatives.append(f"(?i){original_pattern}")
        
        # Versión con espacios opcionales
        spaced_pattern = original_pattern.replace(' ', r'\s*')
        if spaced_pattern != original_pattern:
            alternatives.append(spaced_pattern)
        
        # Versión más permisiva (escapar caracteres especiales)
        escaped = re.escape(original_pattern)
        if escaped != original_pattern:
            alternatives.append(escaped)
        
        return alternatives[:3]  # Máximo 3 alternativas
    
    def _log_debug_results(self, debug_info: Dict[str, Any]) -> None:
        """Log resultados de debug con formato rico."""
        logger.info(f"🔍 Pattern Debug Analysis")
        logger.info(f"File: {debug_info['file_path']}")
        logger.info(f"Pattern: {debug_info['pattern']}")
        logger.info(f"Matches found: {len(debug_info['matches_found'])}")
        
        if debug_info['regex_analysis']['special_chars']:
            logger.info(f"Special chars: {', '.join(debug_info['regex_analysis']['special_chars'])}")
        
        if debug_info['errors']:
            for error in debug_info['errors']:
                logger.warning(f"Error: {error}")