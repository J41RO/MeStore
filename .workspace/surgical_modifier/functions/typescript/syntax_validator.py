"""
TypeScript Syntax Validator
===========================
Validación específica para sintaxis TypeScript
"""

import re
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class TypeScriptSyntaxValidator:
    """Validador especializado para sintaxis TypeScript"""
    
    def __init__(self):
        """Inicializar validador TypeScript"""
        self.typescript_keywords = [
            'interface', 'type', 'enum', 'namespace', 'module',
            'declare', 'abstract', 'implements', 'extends',
            'public', 'private', 'protected', 'readonly',
            'static', 'async', 'await'
        ]
        
        self.typescript_types = [
            'string', 'number', 'boolean', 'void', 'any', 'unknown',
            'never', 'object', 'undefined', 'null', 'bigint', 'symbol'
        ]
        
    def validate_typescript_syntax(self, content: str) -> Dict[str, Any]:
        """Validar sintaxis TypeScript completa"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'typescript_features': []
        }
        
        # Detectar características TypeScript
        if 'interface ' in content:
            result['typescript_features'].append('interfaces')
            interface_errors = self._validate_interfaces(content)
            result['errors'].extend(interface_errors)
            
        if 'type ' in content and '=' in content:
            result['typescript_features'].append('type_aliases')
            type_errors = self._validate_type_aliases(content)
            result['errors'].extend(type_errors)
            
        if ': ' in content:
            result['typescript_features'].append('type_annotations')
            annotation_errors = self._validate_type_annotations(content)
            result['errors'].extend(annotation_errors)
            
        if 'import ' in content:
            result['typescript_features'].append('imports')
            import_warnings = self._validate_imports(content)
            result['warnings'].extend(import_warnings)
            
        # Marcar como inválido si hay errores
        if result['errors']:
            result['valid'] = False
            
        return result
        
    def _validate_interfaces(self, content: str) -> List[str]:
        """Validar interfaces TypeScript"""
        errors = []
        
        # Buscar declaraciones de interface
        interface_pattern = r'interface\s+([A-Z][a-zA-Z0-9_]*)\s*{([^}]*?)}'
        interfaces = re.finditer(interface_pattern, content, re.DOTALL)
        
        for match in interfaces:
            interface_name = match.group(1)
            interface_body = match.group(2).strip()
            
            # Validar naming convention (PascalCase)
            if not interface_name[0].isupper():
                errors.append(f'Interface {interface_name} should use PascalCase naming')
                
            # Validar que no esté vacía
            if not interface_body:
                errors.append(f'Interface {interface_name} is empty')
                
            # Validar propiedades
            if interface_body:
                prop_errors = self._validate_interface_properties(interface_body, interface_name)
                errors.extend(prop_errors)
                
        return errors
        
    def _validate_interface_properties(self, body: str, interface_name: str) -> List[str]:
        """Validar propiedades de interface"""
        errors = []
        
        # Limpiar y procesar cada línea individualmente  
        clean_body = body.strip()
        if not clean_body:
            return errors
            
        # Separar por punto y coma para manejar múltiples propiedades en una línea
        statements = [stmt.strip() for stmt in clean_body.replace('\n', ';').split(';') if stmt.strip()]
        
        for statement in statements:
            if ':' not in statement:
                continue
                
            # Validar sintaxis de propiedad individual
            prop_pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)(\?)?\s*:\s*([a-zA-Z_][a-zA-Z0-9_\[\]\|\s\'"<>]+)$'
            match = re.match(prop_pattern, statement.strip())
            
            if not match:
                errors.append(f'Invalid property syntax in {interface_name}: {statement}')
            else:
                prop_name = match.group(1)
                is_optional = match.group(2) == '?'
                prop_type = match.group(3).strip()
                
                # Validar tipo básico (implementación simplificada)
                basic_types = ['string', 'number', 'boolean', 'any', 'void', 'object']
                if prop_type not in basic_types and not prop_type[0].isupper():
                    errors.append(f'Invalid type in {interface_name}.{prop_name}: {prop_type}')
                        
        return errors
        
    def _validate_type_aliases(self, content: str) -> List[str]:
        """Validar type aliases TypeScript"""
        errors = []
        
        # Buscar declaraciones de type
        type_pattern = r'type\s+([A-Z][a-zA-Z0-9_]*)\s*=\s*(.+?);'
        types = re.finditer(type_pattern, content)
        
        for match in types:
            type_name = match.group(1)
            type_definition = match.group(2).strip()
            
            # Validar naming convention
            if not type_name[0].isupper():
                errors.append(f'Type {type_name} should use PascalCase naming')
                
            # Validar definición no vacía
            if not type_definition:
                errors.append(f'Type {type_name} has empty definition')
                
        return errors
        
    def _validate_type_annotations(self, content: str) -> List[str]:
        """Validar anotaciones de tipo"""
        errors = []
        
        # Buscar anotaciones de tipo específicamente (variable: Type = value)
        annotation_pattern = r'\b\w+\s*:\s*([A-Za-z_][A-Za-z0-9_\[\]\|<>\s]*?)\s*='
        annotations = re.finditer(annotation_pattern, content)
        
        for match in annotations:
            type_annotation = match.group(1).strip()
            
            if not self._is_valid_type(type_annotation):
                errors.append(f'Invalid type annotation: {type_annotation}')
                
        return errors
        
    def _validate_imports(self, content: str) -> List[str]:
        """Validar imports TypeScript"""
        warnings = []
        
        # Buscar imports
        import_lines = [line for line in content.split('\n') if line.strip().startswith('import ')]
        
        for import_line in import_lines:
            # Verificar imports con alias @/
            if '@/' in import_line:
                warnings.append(f'Import with alias detected: {import_line.strip()}')
                
            # Verificar imports relativos
            if '../' in import_line or './' in import_line:
                warnings.append(f'Relative import detected: {import_line.strip()}')
                
        return warnings
        
    def _is_valid_type(self, type_str: str) -> bool:
        """Verificar si un string representa un tipo TypeScript válido"""
        type_str = type_str.strip()
        
        # Tipos básicos
        if type_str in self.typescript_types:
            return True
            
        # Union types
        if '|' in type_str:
            return all(self._is_valid_type(t.strip()) for t in type_str.split('|'))
            
        # Array types
        if type_str.endswith('[]'):
            return self._is_valid_type(type_str[:-2])
            
        # Generic types
        if '<' in type_str and '>' in type_str:
            base_type = type_str.split('<')[0]
            return base_type in ['Array', 'Promise', 'Map', 'Set'] or base_type[0].isupper()
            
        # Custom types (PascalCase)
        if type_str[0].isupper():
            return True
            
        # Function types
        if '=>' in type_str:
            return True
            
        return False
        
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validar archivo TypeScript completo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            result = self.validate_typescript_syntax(content)
            result['file_path'] = file_path
            
            return result
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Failed to read file: {str(e)}'],
                'warnings': [],
                'typescript_features': [],
                'file_path': file_path
            }
