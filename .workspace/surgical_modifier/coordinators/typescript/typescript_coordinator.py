"""
Coordinador TypeScript Especializado
====================================
Maneja archivos .ts puros (sin React)
Separación clara de TypeScriptReactCoordinator
"""

from typing import Dict, Any, List, Optional
import os
import json
from pathlib import Path

class TypeScriptCoordinator:
    """Coordinador especializado para TypeScript puro (sin React)"""
    
    def __init__(self):
        """Inicializar coordinador con functions TypeScript específicas"""
        self.technology = 'typescript'
        self.file_extensions = ['.ts']  # Solo .ts, NO .tsx
        
        # Functions específicas TypeScript se cargarán cuando estén disponibles
        self.syntax_validator = None
        self.interface_manager = None  
        self.import_resolver = None
        
    def can_handle(self, file_path: str) -> bool:
        """Verifica si este coordinador puede manejar el archivo"""
        return file_path.endswith('.ts') and not file_path.endswith('.tsx')
        
    def validate_typescript_syntax(self, content: str) -> Dict[str, Any]:
        """Validación básica de sintaxis TypeScript"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validaciones básicas TypeScript
        if 'interface ' in content and not content.strip().endswith('}'):
            validation_result['errors'].append('Interface declaration seems incomplete')
            validation_result['valid'] = False
            
        if ': ' in content and not any(ts_type in content for ts_type in ['string', 'number', 'boolean', 'any', 'void']):
            validation_result['warnings'].append('Type annotations detected but no common types found')
            
        return validation_result
        
    def execute_create(self, file_path: str, content: str, **kwargs) -> Dict[str, Any]:
        """Crear archivo TypeScript con validación específica"""
        
        # Validar contenido TypeScript antes de crear
        validation = self.validate_typescript_syntax(content)
        if not validation['valid']:
            return {
                'success': False,
                'error': f'TypeScript validation failed: {validation["errors"]}',
                'file_path': file_path
            }
            
        # Crear archivo (implementación básica)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return {
                'success': True,
                'message': f'TypeScript file created: {file_path}',
                'file_path': file_path,
                'validation': validation
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create TypeScript file: {str(e)}',
                'file_path': file_path
            }
            
    def execute_replace(self, file_path: str, old_content: str, new_content: str, **kwargs) -> Dict[str, Any]:
        """Reemplazar contenido con validación TypeScript"""
        
        try:
            # Leer archivo actual
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
                
            # Realizar reemplazo
            if old_content not in current_content:
                return {
                    'success': False,
                    'error': f'Pattern not found: {old_content}',
                    'file_path': file_path
                }
                
            updated_content = current_content.replace(old_content, new_content)
            
            # Validar contenido resultante
            validation = self.validate_typescript_syntax(updated_content)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': f'TypeScript validation failed after replacement: {validation["errors"]}',
                    'file_path': file_path
                }
                
            # Escribir archivo actualizado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            return {
                'success': True,
                'message': f'TypeScript content replaced in: {file_path}',
                'file_path': file_path,
                'validation': validation
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to replace content in TypeScript file: {str(e)}',
                'file_path': file_path
            }
            
    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Ejecutar operación específica TypeScript"""
        
        operations = {
            'create': self.execute_create,
            'replace': self.execute_replace
        }
        
        if operation not in operations:
            return {
                'success': False,
                'error': f'Operation not supported by TypeScriptCoordinator: {operation}',
                'supported_operations': list(operations.keys())
            }
            
        return operations[operation](**kwargs)
        
    def get_info(self) -> Dict[str, Any]:
        """Información del coordinador TypeScript"""
        return {
            'name': 'TypeScriptCoordinator',
            'technology': self.technology,
            'file_extensions': self.file_extensions,
            'description': 'Coordinador especializado para TypeScript puro (sin React)',
            'features': [
                'Validación sintaxis TypeScript',
                'Creación de archivos .ts',
                'Reemplazo con validación',
                'Separación clara de React'
            ]
        }
