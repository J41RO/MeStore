from typing import Dict, List, Any
import re
import logging

class JSXParser:
    """Parser especializado para manipulación segura de JSX"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def parse_jsx_elements(self, jsx_code: str) -> List[Dict[str, Any]]:
        """Parsea elementos JSX y retorna estructura"""
        elements = []
        jsx_pattern = r'<(\w+)([^>]*)>(.*?)</\1>'
        matches = re.finditer(jsx_pattern, jsx_code, re.DOTALL)
        
        for match in matches:
            element = {
                'tag': match.group(1),
                'attributes': self._parse_attributes(match.group(2)),
                'content': match.group(3).strip(),
                'full_match': match.group(0)
            }
            elements.append(element)
            
        return elements
    
    def _parse_attributes(self, attr_string: str) -> Dict[str, str]:
        """Parsea atributos JSX"""
        attributes = {}
        attr_pattern = r'(\w+)=\{([^}]+)\}|(\w+)="([^"]+)"'
        matches = re.finditer(attr_pattern, attr_string)
        
        for match in matches:
            if match.group(1):  # Attribute with {}
                attributes[match.group(1)] = match.group(2)
            elif match.group(3):  # Attribute with ""
                attributes[match.group(3)] = match.group(4)
                
        return attributes
        
    def validate_jsx_syntax(self, jsx_code: str) -> bool:
        """Valida sintaxis básica de JSX"""
        try:
            # Verificaciones básicas de JSX
            open_tags = jsx_code.count('<')
            close_tags = jsx_code.count('>')
            return open_tags == close_tags
        except Exception as e:
            self.logger.error(f'Error validating JSX: {e}')
            return False

    
    def detect_incomplete_fragments(self, jsx_code: str) -> List[str]:
        """Detecta fragmentos JSX incompletos"""
        errors = []
        
        # Detectar elementos sin cierre apropiado
        unclosed_pattern = r'<(\w+)(?:[^>]*>)(?!.*</\1>)'
        unclosed_matches = re.finditer(unclosed_pattern, jsx_code, re.DOTALL)
        
        for match in unclosed_matches:
            tag = match.group(1)
            # Verificar que no sea un tag auto-cerrado
            full_match = match.group(0)
            if not full_match.endswith('/>'):
                errors.append(f"Elemento JSX incompleto: <{tag}> sin cierre apropiado")
        
        return errors

    
    def _has_valid_conditional_structure(self, conditional_text: str) -> bool:
        """Verifica si un condicional tiene estructura válida"""
        try:
            # Verificar que después de && hay un elemento JSX válido
            parts = conditional_text.split('&&')
            if len(parts) != 2:
                return False
            
            # La parte después de && debe contener JSX válido
            jsx_part = parts[1].strip()
            return jsx_part.startswith('<') and ('>' in jsx_part)
        except:
            return False
    
    def _has_valid_mapping_structure(self, mapping_text: str) -> bool:
        """Verifica si un mapeo tiene estructura válida"""
        try:
            # Verificar que contiene => y JSX de retorno
            if '=>' not in mapping_text:
                return False
            
            # Verificar que después de => hay JSX válido  
            arrow_parts = mapping_text.split('=>')
            if len(arrow_parts) < 2:
                return False
            
            jsx_return = arrow_parts[-1].strip()
            return jsx_return.startswith('<') and ('>' in jsx_return)
        except:
            return False
    
    def validate_jsx_advanced(self, jsx_code: str) -> Dict[str, Any]:
        """Validación JSX avanzada que combina todas las detecciones"""
        all_errors = []
        
        # Ejecutar todas las validaciones
        all_errors.extend(self.detect_incomplete_fragments(jsx_code))
        all_errors.extend(self.detect_malformed_conditionals(jsx_code))
        all_errors.extend(self.detect_incomplete_mappings(jsx_code))
        
        return {
            'valid': len(all_errors) == 0,
            'errors': all_errors,
            'error_count': len(all_errors)
        }

    
    def detect_malformed_conditionals(self, jsx_code: str) -> List[str]:
        """Detecta condicionales JSX malformados"""
        errors = []
        
        # Detectar condicionales && sin cierre apropiado
        conditional_pattern = r'\{[^}]*&&[^}]*\}'
        conditionals = re.finditer(conditional_pattern, jsx_code)
        
        for match in conditionals:
            conditional_text = match.group(0)
            # Verificar si tiene estructura válida
            if '&&' in conditional_text and not self._has_valid_conditional_structure(conditional_text):
                errors.append(f"Condicional JSX malformado: {conditional_text}")
        
        return errors
    
    def detect_incomplete_mappings(self, jsx_code: str) -> List[str]:
        """Detecta mapeos JSX incompletos"""
        errors = []
        
        # Detectar .map() sin cierre apropiado
        mapping_pattern = r'\{[^}]*\.map\([^}]*\)'
        mappings = re.finditer(mapping_pattern, jsx_code)
        
        for match in mappings:
            mapping_text = match.group(0)
            # Verificar si tiene estructura válida de retorno
            if '.map(' in mapping_text and not self._has_valid_mapping_structure(mapping_text):
                errors.append(f"Mapeo JSX incompleto: {mapping_text}")
        
        return errors