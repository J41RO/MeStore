from typing import Dict, Any, Optional, List
from pathlib import Path
import logging


class ResponseBuilder:
    """Builder para construcción de respuestas estructuradas CREATE"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def build_success_response(self, file_path: str, content: str, backup_result: Dict[str, Any], 
                              parent_result: Dict[str, Any], verification: Dict[str, Any], 
                              phases_completed: List[str], template_used: Optional[str] = None) -> Dict[str, Any]:
        """Construir respuesta exitosa completa con todos los detalles"""
        path_obj = Path(file_path)
        
        response = {
            'success': True,
            'file_path': file_path,
            'absolute_path': str(path_obj.absolute()),
            'content_length': len(content),
            'template_used': template_used,
            'backup_created': backup_result.get('created', False),
            'parent_dirs_created': parent_result.get('created', False),
            'verification': verification,
            'phases_completed': phases_completed
        }
        
        # Agregar información adicional de backup si existe
        if backup_result.get('backup_path'):
            response['backup_path'] = backup_result['backup_path']
        
        # Agregar warnings si existen en verification
        if verification.get('warning'):
            response['warnings'] = [verification['warning']]
        
        self.logger.info(f"Success response built for: {file_path}")
        return response
    
    def build_error_response(self, error: str, details: Any, phase: str, 
                           file_path: Optional[str] = None) -> Dict[str, Any]:
        """Construir respuesta de error estructurada"""
        response = {
            'success': False,
            'error': error,
            'details': details,
            'phase': phase
        }
        
        if file_path:
            response['file_path'] = file_path
            response['absolute_path'] = str(Path(file_path).absolute())
        
        self.logger.error(f"Error response built: {error} in phase {phase}")
        return response
    
    def build_workflow_error_response(self, error: str, exception_details: Dict[str, Any], 
                                    phase: str, file_path: str, 
                                    phases_completed: List[str]) -> Dict[str, Any]:
        """Construir respuesta de error de workflow con contexto completo"""
        response = {
            'success': False,
            'error': error,
            'details': exception_details,
            'phase': phase,
            'file_path': file_path,
            'absolute_path': str(Path(file_path).absolute()),
            'phases_completed': phases_completed,
            'failed_at_phase': phase
        }
        
        self.logger.error(f"Workflow error response built: {error}")
        return response
    
    def build_validation_error_response(self, validation_type: str, errors: List[str], 
                                      file_path: str, phase: str) -> Dict[str, Any]:
        """Construir respuesta específica para errores de validación"""
        response = {
            'success': False,
            'error': f'{validation_type} validation failed',
            'details': {
                'validation_type': validation_type,
                'errors': errors,
                'file_path': file_path
            },
            'phase': phase,
            'file_path': file_path
        }
        
        self.logger.warning(f"Validation error response: {validation_type} failed for {file_path}")
        return response
    
    def build_partial_success_response(self, file_path: str, content: str, 
                                     completed_phases: List[str], 
                                     warnings: List[str]) -> Dict[str, Any]:
        """Construir respuesta para éxito parcial con warnings"""
        path_obj = Path(file_path)
        
        response = {
            'success': True,
            'file_path': file_path,
            'absolute_path': str(path_obj.absolute()),
            'content_length': len(content),
            'phases_completed': completed_phases,
            'warnings': warnings,
            'partial_success': True
        }
        
        self.logger.warning(f"Partial success response built for: {file_path} with {len(warnings)} warnings")
        return response
    
    def enhance_response_with_metadata(self, response: Dict[str, Any], 
                                     metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enhancer respuesta con metadata adicional"""
        enhanced = response.copy()
        
        if 'timing' in metadata:
            enhanced['timing'] = metadata['timing']
        
        if 'performance' in metadata:
            enhanced['performance'] = metadata['performance']
        
        if 'debug_info' in metadata and metadata.get('debug_mode'):
            enhanced['debug_info'] = metadata['debug_info']
        
        return enhanced