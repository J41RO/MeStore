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

    def detect_type_change(self, old_content: str, new_content: str) -> Dict[str, Any]:
        """Detectar cambios de tipos básicos entre versiones"""
        changes = {
            'detected': False,
            'changes': [],
            'incompatibilities': []
        }
        
        # Patrones para detectar cambios de tipos básicos
        type_patterns = [
            (r'(\w+):\s*string', r'(\w+):\s*number', 'string', 'number'),
            (r'(\w+):\s*number', r'(\w+):\s*string', 'number', 'string'),
            (r'(\w+):\s*boolean', r'(\w+):\s*(string|number)', 'boolean', 'primitive'),
            (r'(\w+):\s*(string|number)', r'(\w+):\s*boolean', 'primitive', 'boolean'),
            (r'(\w+):\s*(\w+)\[\]', r'(\w+):\s*(\w+)', 'array', 'single'),
            (r'(\w+):\s*(\w+)', r'(\w+):\s*(\w+)\[\]', 'single', 'array')
        ]
        
        for old_pattern, new_pattern, old_type, new_type in type_patterns:
            old_matches = re.finditer(old_pattern, old_content)
            new_matches = re.finditer(new_pattern, new_content)
            
            old_props = {match.group(1): (old_type, match.group(0)) for match in old_matches}
            new_props = {match.group(1): (new_type, match.group(0)) for match in new_matches}
            
            # Detectar cambios
            for prop_name in old_props:
                if prop_name in new_props and old_props[prop_name][0] != new_props[prop_name][0]:
                    changes['detected'] = True
                    change_info = {
                        'property': prop_name,
                        'old_type': old_props[prop_name][0],
                        'new_type': new_props[prop_name][0],
                        'old_declaration': old_props[prop_name][1],
                        'new_declaration': new_props[prop_name][1]
                    }
                    changes['changes'].append(change_info)
                    
                    # Detectar incompatibilidades potenciales
                    incompatibility = self._analyze_type_incompatibility(old_content, new_content, prop_name, old_props[prop_name][0], new_props[prop_name][0])
                    if incompatibility:
                        changes['incompatibilities'].append(incompatibility)
        
        return changes

    def detect_prop_compatibility(self, old_content: str, new_content: str) -> Dict[str, Any]:
        """Detectar cambios en propiedades opcionales vs requeridas"""
        compatibility = {
            'detected': False,
            'optional_to_required': [],
            'required_to_optional': []
        }
        
        # Detectar cambios de propiedades opcionales
        prop_pattern = r'(\w+)(\?)?:\s*(\w+)'
        
        old_props = {}
        for match in re.finditer(prop_pattern, old_content):
            prop_name = match.group(1)
            is_optional = match.group(2) == '?'
            prop_type = match.group(3)
            old_props[prop_name] = {'optional': is_optional, 'type': prop_type}
        
        new_props = {}
        for match in re.finditer(prop_pattern, new_content):
            prop_name = match.group(1)
            is_optional = match.group(2) == '?'
            prop_type = match.group(3)
            new_props[prop_name] = {'optional': is_optional, 'type': prop_type}
        
        # Detectar cambios en opcionalidad
        for prop_name in old_props:
            if prop_name in new_props:
                old_optional = old_props[prop_name]['optional']
                new_optional = new_props[prop_name]['optional']
                
                if old_optional and not new_optional:
                    compatibility['detected'] = True
                    warning_msg = 'Property ' + prop_name + ' changed from optional to required - may break existing code'
                    compatibility['optional_to_required'].append({
                        'property': prop_name,
                        'type': old_props[prop_name]['type'],
                        'warning': warning_msg
                    })
                elif not old_optional and new_optional:
                    compatibility['detected'] = True
                    info_msg = 'Property ' + prop_name + ' changed from required to optional - generally safe'
                    compatibility['required_to_optional'].append({
                        'property': prop_name,
                        'type': old_props[prop_name]['type'],
                        'info': info_msg
                    })
        
        return compatibility

    def validate_type_compatibility(self, old_content: str, new_content: str) -> Dict[str, Any]:
        """Validación completa de compatibilidad de tipos"""
        result = {
            'compatible': True,
            'warnings': [],
            'errors': [],
            'suggestions': []
        }
        
        # Detectar cambios de tipos
        type_changes = self.detect_type_change(old_content, new_content)
        if type_changes['detected']:
            result['compatible'] = False
            
            for change in type_changes['changes']:
                warning_msg = 'Type change detected: ' + change['property'] + ' from ' + change['old_type'] + ' to ' + change['new_type']
                result['warnings'].append(warning_msg)
            
            for incompatibility in type_changes['incompatibilities']:
                result['errors'].append(incompatibility['error'])
                if 'suggestion' in incompatibility:
                    result['suggestions'].append(incompatibility['suggestion'])
        
        # Detectar cambios de propiedades opcionales
        prop_changes = self.detect_prop_compatibility(old_content, new_content)
        if prop_changes['detected']:
            for change in prop_changes['optional_to_required']:
                result['warnings'].append(change['warning'])
            
            for change in prop_changes['required_to_optional']:
                result['warnings'].append(change['info'])
        
        return result

    def _analyze_type_incompatibility(self, old_content: str, new_content: str, prop_name: str, old_type: str, new_type: str) -> Optional[Dict[str, str]]:
        """Analizar incompatibilidades específicas entre tipos"""
        
        # Buscar valores asignados a la propiedad
        assignment_pattern = prop_name + r':\s*(.+?)(?=[,}}\n])'
        
        assignments = re.finditer(assignment_pattern, old_content)
        
        for assignment in assignments:
            value = assignment.group(1).strip()
            
            # Detectar incompatibilidades comunes
            if old_type == 'number' and new_type == 'string':
                if value.isdigit() or '.' in value:
                    error_msg = 'Value ' + value + ' for ' + prop_name + ' is numeric but new type is string'
                    suggestion_msg = 'Consider changing ' + value + ' to "' + value + '" to match string type'
                    return {
                        'error': error_msg,
                        'suggestion': suggestion_msg
                    }
            
            elif old_type == 'string' and new_type == 'number':
                if value.startswith('"') or value.startswith("'"):
                    clean_value = value.strip('"').strip("'")
                    error_msg = 'Value ' + value + ' for ' + prop_name + ' is string but new type is number'
                    suggestion_msg = 'Consider changing ' + value + ' to numeric value like ' + clean_value
                    return {
                        'error': error_msg,
                        'suggestion': suggestion_msg
                    }
            
            elif old_type == 'single' and new_type == 'array':
                error_msg = 'Value ' + value + ' for ' + prop_name + ' is single value but new type expects array'
                suggestion_msg = 'Consider changing ' + value + ' to [' + value + '] to match array type'
                return {
                    'error': error_msg,
                    'suggestion': suggestion_msg
                }
            
            elif old_type == 'array' and new_type == 'single':
                if '[' in value and ']' in value:
                    error_msg = 'Value ' + value + ' for ' + prop_name + ' is array but new type expects single value'
                    suggestion_msg = 'Consider extracting single element from array or changing type back to array'
                    return {
                        'error': error_msg,
                        'suggestion': suggestion_msg
                    }
        
        return None
        
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