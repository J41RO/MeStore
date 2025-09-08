"""
TypeScript Interface Manager
============================
Gestión especializada de interfaces TypeScript
"""

import re
from typing import Dict, Any, List, Optional, Tuple

class InterfaceManager:
    """Gestor especializado para interfaces TypeScript"""
    
    def __init__(self):
        """Inicializar gestor de interfaces"""
        self.interface_pattern = r'interface\s+([A-Z][a-zA-Z0-9_]*)\s*{([^}]*?)}'
        
    def create_interface(self, name: str, properties: Dict[str, str]) -> str:
        """Crear interface TypeScript con propiedades"""
        
        if not name[0].isupper():
            raise ValueError(f'Interface name should use PascalCase: {name}')
            
        if not properties:
            raise ValueError('Interface cannot be empty')
            
        interface_lines = [f'interface {name} {{']
        
        for prop_name, prop_type in properties.items():
            if not self._is_valid_property_name(prop_name):
                raise ValueError(f'Invalid property name: {prop_name}')
                
            if not self._is_valid_type(prop_type):
                raise ValueError(f'Invalid type for property {prop_name}: {prop_type}')
                
            interface_lines.append(f'  {prop_name}: {prop_type};')
            
        interface_lines.append('}')
        
        return '\n'.join(interface_lines)
        
    def add_property_to_interface(self, interface_code: str, prop_name: str, prop_type: str, optional: bool = False) -> str:
        """Agregar propiedad a interface existente"""
        
        if not self._is_valid_property_name(prop_name):
            raise ValueError(f'Invalid property name: {prop_name}')
            
        if not self._is_valid_type(prop_type):
            raise ValueError(f'Invalid type: {prop_type}')
            
        # Buscar la interface en el código
        match = re.search(self.interface_pattern, interface_code, re.DOTALL)
        if not match:
            raise ValueError('No interface found in provided code')
            
        interface_name = match.group(1)
        interface_body = match.group(2)
        
        # Crear nueva propiedad
        optional_marker = '?' if optional else ''
        new_property = f'  {prop_name}{optional_marker}: {prop_type};'
        
        # Insertar propiedad antes del cierre
        updated_body = interface_body.rstrip()
        if updated_body and not updated_body.endswith('\n'):
            updated_body += '\n'
        updated_body += new_property
        
        # Reconstruir interface
        new_interface = f'interface {interface_name} {{\n{updated_body}\n}}'
        
        return interface_code.replace(match.group(0), new_interface)
        
    def update_interface_property(self, interface_code: str, prop_name: str, new_type: str) -> str:
        """Actualizar tipo de propiedad existente"""
        
        if not self._is_valid_type(new_type):
            raise ValueError(f'Invalid type: {new_type}')
            
        # Buscar y actualizar la propiedad específica
        # Escapar caracteres especiales en prop_name para regex seguro
        escaped_prop_name = re.escape(prop_name)
        prop_pattern = f'({escaped_prop_name})(\\?)?:\\s*([^;]+);'
        
        def replace_property(match):
            prop_name_match = match.group(1)
            optional_marker = match.group(2) or ''
            return f'{prop_name_match}{optional_marker}: {new_type};'
            
        updated_code = re.sub(prop_pattern, replace_property, interface_code)
        
        if updated_code == interface_code:
            raise ValueError(f'Property {prop_name} not found in interface')
            
        return updated_code
        
    def extract_interfaces(self, content: str) -> List[Dict[str, Any]]:
        """Extraer todas las interfaces del contenido"""
        interfaces = []
        
        matches = re.finditer(self.interface_pattern, content, re.DOTALL)
        for match in matches:
            interface_name = match.group(1)
            interface_body = match.group(2)
            
            properties = self._parse_interface_properties(interface_body)
            
            interfaces.append({
                'name': interface_name,
                'properties': properties,
                'full_text': match.group(0),
                'start_pos': match.start(),
                'end_pos': match.end()
            })
            
        return interfaces
        
    def _parse_interface_properties(self, body: str) -> List[Dict[str, Any]]:
        """Parsear propiedades de interface"""
        properties = []
        lines = [line.strip() for line in body.split('\n') if line.strip()]
        
        for line in lines:
            if ':' not in line:
                continue
                
            # Parsear propiedad
            prop_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)(\?)?:\s*(.+?);?$', line.strip())
            if prop_match:
                prop_name = prop_match.group(1)
                is_optional = prop_match.group(2) == '?'
                prop_type = prop_match.group(3).strip().rstrip(';')
                
                properties.append({
                    'name': prop_name,
                    'type': prop_type,
                    'optional': is_optional,
                    'line': line
                })
                
        return properties
        
    def find_interface_by_name(self, content: str, interface_name: str) -> Optional[Dict[str, Any]]:
        """Buscar interface específica por nombre"""
        interfaces = self.extract_interfaces(content)
        
        for interface in interfaces:
            if interface['name'] == interface_name:
                return interface
                
        return None
        
    def _is_valid_property_name(self, name: str) -> bool:
        """Validar nombre de propiedad"""
        return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name) is not None
        
    def _is_valid_type(self, type_str: str) -> bool:
        """Validar tipo TypeScript"""
        type_str = type_str.strip()
        
        # Tipos básicos
        basic_types = ['string', 'number', 'boolean', 'void', 'any', 'unknown', 'never', 'object']
        if type_str in basic_types:
            return True
            
        # Union types
        if '|' in type_str:
            return all(self._is_valid_type(t.strip()) for t in type_str.split('|'))
            
        # Array types
        if type_str.endswith('[]'):
            return self._is_valid_type(type_str[:-2])
            
        # Generic types
        if '<' in type_str and '>' in type_str:
            return True
            
        # Custom types (PascalCase)
        if type_str[0].isupper():
            return True
            
        # Function types
        if '=>' in type_str:
            return True
            
        return False
