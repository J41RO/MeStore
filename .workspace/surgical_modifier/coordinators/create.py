from pathlib import Path
from typing import Dict, Any
import sys
import os
import logging

# Agregar path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter
from functions.content.cache import ContentCache
from functions.content.validator import ContentValidator
from functions.engines.selector import get_best_engine
from functions.engines.base_engine import EngineCapability

class CreateCoordinator:
    def __init__(self):
        # Reutilizar cuarteto completo para funcionalidad avanzada
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
            # Capacidades requeridas para operación de creación
            required_capabilities = [EngineCapability.CREATE, EngineCapability.WRITE]
            
            # Si se especifica archivo, agregar capacidad específica del lenguaje
            if file_path:
                if file_path.endswith('.py'):
                    required_capabilities.append(EngineCapability.PYTHON_SUPPORT)
                elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    required_capabilities.append(EngineCapability.JAVASCRIPT_SUPPORT)
            
            # Derivar language de file_path  
            language = None
            if file_path.endswith('.py'):
                language = 'python'
            elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                language = 'javascript'

            # Obtener mejor engine usando selector
            best_engine = get_best_engine(
                operation_type=operation_type,
                capabilities_needed=required_capabilities,  # Cambio: required_capabilities -> capabilities_needed
                language=language  # Cambio: file_path -> language derivado
)
            
            return best_engine
            
        except Exception as e:
            # Fallback a functions content si engine selector falla
            self.logger.warning(f"Engine selector failed: {e}, using functions fallback")
            return None
    
    def execute(self, file_path: str, content: str, template: str = None) -> Dict[str, Any]:
        """Crear archivo usando engine selector con fallback a functions modulares"""
        
        # Seleccionar engine óptimo para operación de creación
        selected_engine = self._get_engine_for_operation("create", file_path)
        
        # Si hay engine disponible, usar para operación
        if selected_engine:
            try:
                # Usar engine selector para la operación de creación
                result = selected_engine.create(file_path, content)
                if result.success:
                    self.logger.info(f"File created successfully using {selected_engine.__class__.__name__}")
                    return {
                        'success': True,
                        'message': f"File created using engine selector: {file_path}",
                        'engine_used': selected_engine.__class__.__name__,
                        'fallback_used': False
                    }
                else:
                    self.logger.warning(f"Engine {selected_engine.__class__.__name__} failed, falling back to functions")
            except Exception as e:
                self.logger.warning(f"Engine operation failed: {e}, falling back to functions")
        
        # Fallback a functions content (mantener código existente)
        # Usar ContentValidator para validar contenido antes de crear
        validation = self.validator.validate_content(content, ['not_empty'])
        if not validation['valid']:
            return {'success': False, 'error': 'Invalid content'}
        
        # Usar ContentWriter para crear archivo
        result = self.writer.write_file(file_path, content, preserve_line_endings=False, backup=False)
        
        return {
            'success': result['success'],
            'message': f"File created using modular functions: {file_path}",
            'functions_used': ['ContentWriter', 'ContentValidator'],
            'engine_used': None,
            'fallback_used': True
        }
    
    def execute_create(self, file_path: str, content: str, template: str = None, validate: bool = True) -> Dict[str, Any]:
        """Ejecutar creación con engine selector y functions modulares mejorado"""
        
        # Seleccionar engine óptimo para operación de creación
        selected_engine = self._get_engine_for_operation("create", file_path)
        
        # Si hay engine disponible, usar para operación
        if selected_engine:
            try:
                # Validación usando ContentValidator antes de engine
                if validate:
                    validation_result = self.validator.validate_content(content, ['not_empty', 'text_only'])
                    if not validation_result['valid']:
                        return {
                            'success': False, 
                            'error': 'Content validation failed',
                            'validation_errors': validation_result.get('errors', [])
                        }
                
                # Usar engine selector para la operación de creación
                result = selected_engine.create(file_path, content)
                if result.success:
                    self.logger.info(f"File created successfully using {selected_engine.__class__.__name__}")
                    return {
                        'success': True,
                        'coordinator': 'CREATE_ENHANCED_ENGINE',
                        'engine_used': selected_engine.__class__.__name__,
                        'file_created': file_path,
                        'content_length': len(content),
                        'validation_applied': validate,
                        'fallback_used': False
                    }
                else:
                    self.logger.warning(f"Engine {selected_engine.__class__.__name__} failed, falling back to functions")
            except Exception as e:
                self.logger.warning(f"Engine operation failed: {e}, falling back to functions")
        
        # Fallback a functions content (código original mejorado)
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
            'verification_completed': True,
            'engine_used': None,
            'fallback_used': True
        }

    def get_reuse_info(self) -> Dict[str, Any]:
        """Información sobre reutilización de functions por CREATE con engine selector"""
        return {
            'total_functions_reused': 4,
            'functions': {
                'ContentWriter': 'Creación de archivos nuevos (fallback)',
                'ContentValidator': 'Validación pre-creación',
                'ContentReader': 'Verificación post-creación y backup',
                'ContentCache': 'Cache de archivos existentes antes de sobrescribir'
            },
            'engine_selector_integrated': True,
            'engine_selector_method': '_get_engine_for_operation',
            'enhanced_features': True,
            'modular_reuse': True,
            'fallback_strategy': 'Functions content si engine falla'
        }

# Test de funcionalidad básica
if __name__ == "__main__":
    coordinator = CreateCoordinator()
    print("CreateCoordinator initialized successfully with engine selector")
    
    # Test básico de reutilización
    reuse_info = coordinator.get_reuse_info()
    print(f"Functions reusadas: {reuse_info['total_functions_reused']}")
    print(f"Engine selector integrado: {reuse_info['engine_selector_integrated']}")