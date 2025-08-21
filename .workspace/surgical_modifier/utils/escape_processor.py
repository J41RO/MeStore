#!/usr/bin/env python3
"""
EscapeProcessor - Procesador especializado para casos complejos de escape.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any

try:
    from utils.logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class EscapeProcessor:
    """Procesador especializado para casos complejos de escape."""
    
    def __init__(self):
        """Inicializa el EscapeProcessor."""
        self.logger = logger
        self._setup_advanced_patterns()
        self.logger.info("EscapeProcessor inicializado correctamente")
    
    def _setup_advanced_patterns(self):
        """Configura patrones avanzados."""
        self.advanced_patterns = {
            "double_escape": re.compile(r"\\\\\\\\([nrtbf])"),
            "malformed_unicode": re.compile(r"\\u([0-9a-fA-F]{1,3})(?![0-9a-fA-F])"),
            "broken_json_escape": re.compile(r'\\"'),
            "incorrect_newlines": re.compile(r"\\n"),
        }
        
        self.correction_config = {
            "preserve_original": True,
            "log_corrections": True,
            "max_iterations": 3,
        }

    def fix_escape_issues(self, content: str, issue_type: str) -> str:
        """
        Corrige problemas específicos de escape no manejados por el sistema básico.
        
        Args:
            content: Contenido con problemas de escape
            issue_type: Tipo de problema ('double_escape', 'malformed_unicode', etc.)
            
        Returns:
            Contenido corregido
        """
        if not content or not issue_type:
            return content
            
        original_content = content
        corrections_made = 0
        
        try:
            if issue_type == 'double_escape':
                # Corregir escape doble: \\\\n → \\n
                content = self.advanced_patterns['double_escape'].sub(r'\\\\\\1', content)
                corrections_made += 1
                
            elif issue_type == 'malformed_unicode':
                # Corregir Unicode malformado: \\u12 → \\u0012
                def fix_unicode(match):
                    hex_val = match.group(1)
                    return f'\\\\u{hex_val.zfill(4)}'
                content = self.advanced_patterns['malformed_unicode'].sub(fix_unicode, content)
                corrections_made += 1
                
            elif issue_type == 'broken_json_escape':
                # Corregir escape JSON roto: \\\" → \"
                content = self.advanced_patterns['broken_json_escape'].sub('\"', content)
                corrections_made += 1
                
            elif issue_type == 'incorrect_newlines':
                # Corregir newlines incorrectos: \\n → \\n
                content = self.advanced_patterns['incorrect_newlines'].sub('\\n', content)
                corrections_made += 1
                
            if self.correction_config['log_corrections'] and corrections_made > 0:
                self.logger.info(f'fix_escape_issues: {corrections_made} correcciones aplicadas para {issue_type}')
                
            return content
            
        except Exception as e:
            self.logger.error(f'Error en fix_escape_issues: {e}')
            return original_content if self.correction_config['preserve_original'] else content

    def analyze_escape_patterns(self, content: str) -> dict:
        """Analiza patrones de escape en contenido."""
        analysis = {
            'total_escapes': 0,
            'escape_types': {},
            'problematic_sequences': []
        }
        
        if not content:
            return analysis
            
        try:
            # Contar diferentes tipos de escape
            for pattern_name, pattern in self.advanced_patterns.items():
                matches = pattern.findall(content)
                if matches:
                    analysis['escape_types'][pattern_name] = len(matches)
                    analysis['total_escapes'] += len(matches)
                    
            # Detectar secuencias problemáticas
            if '\\\\\\\\' in content:
                analysis['problematic_sequences'].append('double_backslash')
            if '\\\\\"' in content and '\"' in content:
                analysis['problematic_sequences'].append('mixed_quotes')
                
            return analysis
            
        except Exception as e:
            self.logger.error(f'Error en analyze_escape_patterns: {e}')
            return analysis

    def validate_escape_integrity(self, content: str) -> dict:
        """Valida integridad de secuencias de escape."""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        if not content:
            return validation
            
        try:
            # Validar pares de comillas
            quote_count = content.count('"')
            escaped_quote_count = content.count('\\"')
            if (quote_count - escaped_quote_count) % 2 != 0:
                validation['is_valid'] = False
                validation['errors'].append('unmatched_quotes')
                
            # Validar secuencias Unicode
            unicode_pattern = re.compile(r'\\u[0-9a-fA-F]{4}')
            malformed_unicode = re.compile(r'\\u[0-9a-fA-F]{1,3}(?![0-9a-fA-F])')
            
            if malformed_unicode.search(content):
                validation['warnings'].append('malformed_unicode_sequences')
                
            return validation
            
        except Exception as e:
            self.logger.error(f'Error en validate_escape_integrity: {e}')
            validation['is_valid'] = False
            validation['errors'].append(f'validation_error: {str(e)}')
            return validation

    def suggest_escape_corrections(self, content: str) -> list:
        """Sugiere correcciones automáticas para problemas de escape."""
        suggestions = []
        
        if not content:
            return suggestions
            
        try:
            analysis = self.analyze_escape_patterns(content)
            
            # Sugerir correcciones basadas en análisis
            if 'double_escape' in analysis['escape_types']:
                suggestions.append({
                    'issue': 'double_escape',
                    'description': 'Escape doble detectado',
                    'correction': 'fix_escape_issues(content, "double_escape")'
                })
                
            if 'malformed_unicode' in analysis['escape_types']:
                suggestions.append({
                    'issue': 'malformed_unicode', 
                    'description': 'Secuencias Unicode malformadas',
                    'correction': 'fix_escape_issues(content, "malformed_unicode")'
                })
                
            if 'double_backslash' in analysis['problematic_sequences']:
                suggestions.append({
                    'issue': 'normalize_needed',
                    'description': 'Normalización de secuencias requerida',
                    'correction': 'normalize_escape_sequences(content)'
                })
                
            return suggestions
            
        except Exception as e:
            self.logger.error(f'Error en suggest_escape_corrections: {e}')
            return suggestions

    def normalize_escape_sequences(self, content: str) -> str:
        """Normaliza secuencias inconsistentes de escape."""
        if not content:
            return content
            
        try:
            normalized = content
            
            # Normalizar backslashes múltiples
            normalized = re.sub(r'\\{3,}', '\\\\', normalized)
            
            # Normalizar comillas escape
            normalized = re.sub(r'\\{2,}"', '\\"', normalized)
            
            # Normalizar secuencias de control
            control_chars = {'n': '\n', 't': '\t', 'r': '\r', 'b': '\b', 'f': '\f'}
            for char, replacement in control_chars.items():
                pattern = f'\\\\{char}'
                normalized = normalized.replace(pattern, replacement)
                
            if self.correction_config['log_corrections']:
                if normalized != content:
                    self.logger.info('normalize_escape_sequences: Secuencias normalizadas')
                    
            return normalized
            
        except Exception as e:
            self.logger.error(f'Error en normalize_escape_sequences: {e}')
            return content if self.correction_config['preserve_original'] else content


    def integrate_with_content_handler(self) -> dict:
        """Integra con ExtremeContentHandler para casos complejos."""
        integration_info = {
            'compatible': False,
            'handler_available': False,
            'integration_methods': []
        }

        try:
            from utils.content_handler import ExtremeContentHandler
            integration_info['handler_available'] = True
            integration_info['compatible'] = True

            # Métodos de integración disponibles
            integration_info['integration_methods'] = [
                'enhanced_escape_processing',
                'fallback_to_extreme_handler',
                'combined_pattern_detection'
            ]

            self.logger.info('Integración con ExtremeContentHandler exitosa')
            return integration_info

        except ImportError as e:
            self.logger.warning(f'ExtremeContentHandler no disponible: {e}')
            integration_info['handler_available'] = False
            return integration_info
        except Exception as e:
            self.logger.error(f'Error en integración: {e}')
            return integration_info