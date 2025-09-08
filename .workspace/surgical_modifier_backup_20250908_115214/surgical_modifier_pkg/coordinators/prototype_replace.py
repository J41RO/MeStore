# Crear coordinators/prototype_replace.py
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter
from functions.content.cache import ContentCache
from functions.content.validator import ContentValidator

class ReplaceCoordinatorPrototype:
    """Prototipo coordinador REPLACE que demuestra reutilización del cuarteto content"""
    
    def __init__(self):
        # Reutilizar TODO el cuarteto content
        self.reader = ContentReader()
        self.writer = ContentWriter()
        self.cache = ContentCache()
        self.validator = ContentValidator()
    
    def execute_replace(self, file_path: str, pattern: str, replacement: str) -> Dict[str, Any]:
        """Ejecutar reemplazo reutilizando functions modulares"""
        
        # 1. Leer archivo original usando ContentReader
        read_result = self.reader.read_file(file_path)
        if not read_result['success']:
            return {'success': False, 'error': 'Failed to read file'}
        
        # 2. Cache contenido original usando ContentCache
        self.cache.cache_content(file_path, read_result, 'pre_replace')
        
        # 3. Validar contenido original usando ContentValidator
        validation = self.validator.validate_content(read_result['content'], ['not_empty', 'text_only'])
        if not validation['valid']:
            return {'success': False, 'error': 'Original content invalid'}
        
        # 4. Aplicar reemplazo
        new_content = read_result['content'].replace(pattern, replacement)
        
        # 5. Validar contenido modificado usando ContentValidator
        new_validation = self.validator.validate_content(new_content, ['not_empty'])
        if not new_validation['valid']:
            return {'success': False, 'error': 'Replaced content invalid'}
        
        # 6. Escribir resultado usando ContentWriter
        write_result = self.writer.write_file(file_path, new_content)
        
        return {
            'success': write_result['success'],
            'coordinator': 'REPLACE_PROTOTYPE',
            'functions_reused': ['ContentReader', 'ContentWriter', 'ContentCache', 'ContentValidator'],
            'cuarteto_completo': True,
            'pattern_replaced': pattern,
            'replacement_applied': replacement
        }
    
    def get_reuse_info(self) -> Dict[str, Any]:
        """Información sobre reutilización de functions"""
        return {
            'total_functions_reused': 4,
            'functions': {
                'ContentReader': 'Leer archivos existentes',
                'ContentWriter': 'Escribir archivos modificados',
                'ContentCache': 'Cache de contenido original',
                'ContentValidator': 'Validación pre y post modificación'
            },
            'modular_design': True,
            'independent_functions': True
        }