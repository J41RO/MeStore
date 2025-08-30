# Crear coordinators/prototype_replace.py
from typing import Dict, Any
import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter
from functions.content.cache import ContentCache
from functions.content.validator import ContentValidator
from functions.engines.selector import get_best_engine
from functions.engines.base_engine import EngineCapability

class ReplaceCoordinatorPrototype:
    """Prototipo coordinador REPLACE que demuestra reutilización del cuarteto content con engine selector"""
    
    def __init__(self):
        # Reutilizar TODO el cuarteto content
        self.reader = ContentReader()
        self.writer = ContentWriter()
        self.cache = ContentCache()
        self.validator = ContentValidator()
        self.logger = logging.getLogger(__name__)

    def _get_engine_for_operation(self, operation_type: str, file_path: str = None) -> Any:
        """
        Selecciona el mejor engine para la operación específica.
        Mantiene functions content como soporte, usa engine selector para modificaciones.
        """
        try:
            # Capacidades requeridas para operación de replace/search
            required_capabilities = [EngineCapability.REPLACE, EngineCapability.SEARCH]
            
            # Si se especifica archivo, agregar capacidad específica del lenguaje
            if file_path:
                if file_path.endswith('.py'):
                    required_capabilities.append(EngineCapability.PYTHON_SUPPORT)
                elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    required_capabilities.append(EngineCapability.JAVASCRIPT_SUPPORT)
            
            # Obtener mejor engine usando selector
            best_engine = get_best_engine(
                operation_type=operation_type,
                required_capabilities=required_capabilities,
                file_path=file_path
            )
            
            return best_engine
            
        except Exception as e:
            # Fallback a functions content si engine selector falla
            self.logger.warning(f"Engine selector failed: {e}, using functions fallback")
            return None

    def execute_replace(self, file_path: str, pattern: str, replacement: str) -> Dict[str, Any]:
        """Ejecutar reemplazo con engine selector y fallback a functions modulares"""
        
        # Seleccionar engine óptimo para operación de reemplazo
        selected_engine = self._get_engine_for_operation("replace", file_path)
        
        # Si hay engine disponible, usar para operación
        if selected_engine:
            try:
                # Usar engine selector para la operación de reemplazo
                result = selected_engine.replace(file_path, pattern, replacement)
                if result.success:
                    self.logger.info(f"Replace completed successfully using {selected_engine.__class__.__name__}")
                    return {
                        'success': True,
                        'coordinator': 'REPLACE_PROTOTYPE_ENGINE',
                        'engine_used': selected_engine.__class__.__name__,
                        'pattern_replaced': pattern,
                        'replacement_applied': replacement,
                        'fallback_used': False
                    }
                else:
                    self.logger.warning(f"Engine {selected_engine.__class__.__name__} failed, falling back to functions")
            except Exception as e:
                self.logger.warning(f"Engine operation failed: {e}, falling back to functions")

        # Fallback a functions content (código original)
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
            'replacement_applied': replacement,
            'engine_used': None,
            'fallback_used': True
        }

    def get_reuse_info(self) -> Dict[str, Any]:
        """Información sobre reutilización de functions con engine selector"""
        return {
            'total_functions_reused': 4,
            'functions': {
                'ContentReader': 'Leer archivos existentes (fallback)',
                'ContentWriter': 'Escribir archivos modificados (fallback)',
                'ContentCache': 'Cache de contenido original',
                'ContentValidator': 'Validación pre y post modificación'
            },
            'engine_selector_integrated': True,
            'engine_selector_method': '_get_engine_for_operation',
            'modular_design': True,
            'independent_functions': True,
            'fallback_strategy': 'Functions content si engine falla'
        }