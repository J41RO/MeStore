import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Callable, Any
from .reader import ContentReader

class ContentValidator:
    def __init__(self):
        self.reader = ContentReader()
        self.validators = {
            'not_empty': self._validate_not_empty,
            'text_only': self._validate_text_only,
            'json_format': self._validate_json_format,
            'max_size': self._validate_max_size,
            'min_lines': self._validate_min_lines
        }
    
    def _validate_not_empty(self, content: str, **kwargs) -> Dict[str, Union[bool, str]]:
        """Validar que contenido no este vacio"""
        stripped = content.strip()
        return {
            'valid': len(stripped) > 0,
            'message': 'Content is empty' if len(stripped) == 0 else 'Content is not empty'
        }

    def _validate_text_only(self, content: str, **kwargs) -> Dict[str, Union[bool, str]]:
        """Validar que contenido sea solo texto (sin caracteres binarios)"""
        try:
            # Intentar encode/decode como texto
            content.encode('utf-8')
            # Verificar caracteres de control (excepto \n, \r, \t)
            control_chars = [c for c in content if ord(c) < 32 and c not in '\n\r\t']
            has_control = len(control_chars) > 0
            
            return {
                'valid': not has_control,
                'message': f'Found {len(control_chars)} control characters' if has_control else 'Text only content'
            }
        except UnicodeEncodeError:
            return {'valid': False, 'message': 'Content contains non-text characters'}

    def _validate_json_format(self, content: str, **kwargs) -> Dict[str, Union[bool, str]]:
        """Validar formato JSON valido"""
        try:
            json.loads(content)
            return {'valid': True, 'message': 'Valid JSON format'}
        except json.JSONDecodeError as e:
            return {'valid': False, 'message': f'Invalid JSON: {str(e)}'}

    def _validate_max_size(self, content: str, max_size: int = 1048576, **kwargs) -> Dict[str, Union[bool, str]]:
        """Validar tamano maximo contenido"""
        size_bytes = len(content.encode('utf-8'))
        return {
            'valid': size_bytes <= max_size,
            'message': f'Size {size_bytes} bytes, limit {max_size} bytes'
        }

    def _validate_min_lines(self, content: str, min_lines: int = 1, **kwargs) -> Dict[str, Union[bool, str]]:
        """Validar minimo numero de lineas"""
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        return {
            'valid': len(non_empty_lines) >= min_lines,
            'message': f'Has {len(non_empty_lines)} non-empty lines, minimum {min_lines}'
        }

    def validate_file(self, file_path: str, rules: List[str], rule_params: Optional[Dict] = None) -> Dict[str, Any]:
        """Validar archivo contra conjunto de reglas"""
        file_path = str(Path(file_path).resolve())
        rule_params = rule_params or {}
        
        # Leer archivo
        read_result = self.reader.read_file(file_path)
        if not read_result['success']:
            return {
                'valid': False,
                'error': f'Could not read file: {read_result.get("error", "Unknown error")}',
                'results': {}
            }
        
        content = read_result['content']
        results = {}
        overall_valid = True
        
        # Aplicar cada regla
        for rule in rules:
            if rule in self.validators:
                params = rule_params.get(rule, {})
                rule_result = self.validators[rule](content, **params)
                results[rule] = rule_result
                if not rule_result['valid']:
                    overall_valid = False
            else:
                results[rule] = {'valid': False, 'message': f'Unknown rule: {rule}'}
                overall_valid = False
        
        return {
            'valid': overall_valid,
            'file_path': file_path,
            'encoding': read_result['encoding_info']['encoding'],
            'results': results
        }

    def validate_content(self, content: str, rules: List[str], rule_params: Optional[Dict] = None) -> Dict[str, Any]:
        """Validar contenido directo contra reglas"""
        rule_params = rule_params or {}
        results = {}
        overall_valid = True
        
        for rule in rules:
            if rule in self.validators:
                params = rule_params.get(rule, {})
                rule_result = self.validators[rule](content, **params)
                results[rule] = rule_result
                if not rule_result['valid']:
                    overall_valid = False
            else:
                results[rule] = {'valid': False, 'message': f'Unknown rule: {rule}'}
                overall_valid = False
        
        return {'valid': overall_valid, 'results': results}

    def add_custom_validator(self, name: str, validator_func: Callable) -> bool:
        """Agregar validador personalizado"""
        if callable(validator_func):
            self.validators[name] = validator_func
            return True
        return False

    def get_available_validators(self) -> List[str]:
        """Obtener lista validadores disponibles"""
        return list(self.validators.keys())

    def validate_batch(self, file_paths: List[str], rules: List[str], rule_params: Optional[Dict] = None) -> Dict[str, Any]:
        """Validar multiples archivos con mismas reglas"""
        results = {}
        summary = {'total': len(file_paths), 'valid': 0, 'invalid': 0, 'errors': 0}
        
        for file_path in file_paths:
            try:
                result = self.validate_file(file_path, rules, rule_params)
                results[file_path] = result
                
                if result['valid']:
                    summary['valid'] += 1
                else:
                    if 'error' in result:
                        summary['errors'] += 1
                    else:
                        summary['invalid'] += 1
            except Exception as e:
                results[file_path] = {'valid': False, 'error': str(e)}
                summary['errors'] += 1
        
        return {'results': results, 'summary': summary}