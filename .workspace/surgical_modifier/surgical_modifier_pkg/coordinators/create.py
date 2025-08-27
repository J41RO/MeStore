from pathlib import Path
from typing import Dict, Any
import sys
import os

# Agregar path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter
from functions.content.cache import ContentCache
from functions.content.validator import ContentValidator

class CreateCoordinator:
    def __init__(self):
        # Reutilizar cuarteto completo para funcionalidad avanzada
        self.reader = ContentReader()
        self.writer = ContentWriter()
        self.cache = ContentCache()
        self.validator = ContentValidator()
    
    def execute(self, file_path: str, content: str, template: str = None) -> Dict[str, Any]:
        """Crear archivo usando functions modulares - versión básica"""
        # Usar ContentValidator para validar contenido antes de crear
        validation = self.validator.validate_content(content, ['not_empty'])
        if not validation['valid']:
            return {'success': False, 'error': 'Invalid content'}
        
        # Usar ContentWriter para crear archivo
        result = self.writer.write_file(file_path, content, preserve_line_endings=False, backup=False)
        
        return {
            'success': result['success'],
            'message': f"File created using modular functions: {file_path}",
            'functions_used': ['ContentWriter', 'ContentValidator']
        }
    
    def execute_create(self, file_path: str, content: str, template: str = None, validate: bool = True) -> Dict[str, Any]:
        """Ejecutar creación reutilizando functions modulares mejorado"""
        
        # 1. Validación mejorada usando ContentValidator
        if validate:
            validation_result = self.validator.validate_content(content, ['not_empty', 'text_only'])
            if not validation_result['valid']:
                return {
                    'success': False, 
                    'error': 'Content validation failed',
                    'validation_errors': validation_result.get('errors', [])
                }
        
        # 2. Verificar si archivo ya existe usando ContentReader
        if os.path.exists(file_path):
            read_result = self.reader.read_file(file_path)
            if read_result['success']:
                # Cache contenido existente antes de sobrescribir
                self.cache.cache_content(file_path, read_result, 'pre_create_overwrite')
        
        # 3. Crear archivo usando ContentWriter
        write_result = self.writer.write_file(file_path, content)
        
        # 4. Verificación post-creación
        if write_result['success']:
            # Leer archivo creado para verificar
            verify_result = self.reader.read_file(file_path)
            if not verify_result['success']:
                return {'success': False, 'error': 'Created file verification failed'}
        
        return {
            'success': write_result['success'],
            'coordinator': 'CREATE_ENHANCED',
            'functions_reused': ['ContentWriter', 'ContentValidator', 'ContentReader', 'ContentCache'],
            'file_created': file_path,
            'content_length': len(content),
            'validation_applied': validate,
            'verification_completed': True
        }

    def get_reuse_info(self) -> Dict[str, Any]:
        """Información sobre reutilización de functions por CREATE"""
        return {
            'total_functions_reused': 4,
            'functions': {
                'ContentWriter': 'Creación de archivos nuevos',
                'ContentValidator': 'Validación pre-creación',
                'ContentReader': 'Verificación post-creación y backup',
                'ContentCache': 'Cache de archivos existentes antes de sobrescribir'
            },
            'enhanced_features': True,
            'modular_reuse': True
        }

# Test de funcionalidad básica
if __name__ == "__main__":
    coordinator = CreateCoordinator()
    print("CreateCoordinator initialized successfully")
    
    # Test básico de reutilización
    reuse_info = coordinator.get_reuse_info()
    print(f"Functions reusadas: {reuse_info['total_functions_reused']}")