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
