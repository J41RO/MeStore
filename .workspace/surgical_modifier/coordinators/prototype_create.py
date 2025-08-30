from typing import Dict, Any
import sys, os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from functions.content.writer import ContentWriter
from functions.content.validator import ContentValidator
from functions.engines.selector import get_best_engine
from functions.engines.base_engine import EngineCapability

class CreateCoordinatorPrototype:
    """Prototipo del Coordinador CREATE usando functions content con engine selector"""
    
    def __init__(self):
        # Reutilizar functions modulares
        self.writer = ContentWriter()
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
            
    def execute(self, file_path: str, content: str) -> Dict[str, Any]:
        """Ejecutar creación con engine selector y fallback a functions"""
        
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
                        'coordinator': 'CREATE_PROTOTYPE_ENGINE',
                        'engine_used': selected_engine.__class__.__name__,
                        'fallback_used': False
                    }
                else:
                    self.logger.warning(f"Engine {selected_engine.__class__.__name__} failed, falling back to functions")
            except Exception as e:
                self.logger.warning(f"Engine operation failed: {e}, falling back to functions")
        
        # Fallback a functions content (código original)
        # Validar usando ContentValidator
        validation = self.validator.validate_content(content, ['not_empty'])
        if not validation['valid']:
            return {'success': False, 'error': 'Invalid content'}
            
        # Crear usando ContentWriter
        result = self.writer.write_file(file_path, content)
        
        return {
            'success': result['success'],
            'coordinator': 'CREATE (prototype)',
            'functions_reused': ['ContentWriter', 'ContentValidator'],
            'functions_used': ['ContentWriter', 'ContentValidator'],
            'engine_used': None,
            'fallback_used': True
        }

    def execute_create(self, file_path: str, content: str) -> Dict[str, Any]:
        """Método execute_create para compatibilidad con tests"""
        return self.execute(file_path, content)
