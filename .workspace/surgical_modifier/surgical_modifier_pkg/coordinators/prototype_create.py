from typing import Dict, Any
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from functions.content.writer import ContentWriter
from functions.content.validator import ContentValidator

class CreateCoordinatorPrototype:
    """Prototipo del Coordinador CREATE usando functions content"""
    
    def __init__(self):
        # Reutilizar functions modulares
        self.writer = ContentWriter()
        self.validator = ContentValidator()
    
    def execute_create(self, file_path: str, content: str, template: str = None) -> Dict[str, Any]:
        # 1. Validar contenido antes de crear
        validation = self.validator.validate_content(content, ['not_empty'])
        if not validation['valid']:
            return {'success': False, 'error': 'Content validation failed'}
        
        # 2. Crear archivo con ContentWriter
        result = self.writer.write_file(file_path, content, backup=False)
        
        return {
            'success': result['success'],
            'coordinator': 'CREATE (prototype)',
            'functions_reused': ['ContentWriter', 'ContentValidator']
        }