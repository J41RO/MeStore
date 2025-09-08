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


    def build_context_error_response(self, error: str, file_path: str, pattern: str, 
                                   line_number: Optional[int] = None, 
                                   surrounding_context: Optional[str] = None,
                                   file_content_sample: Optional[str] = None) -> Dict[str, Any]:
        """Construir respuesta de error con contexto del archivo"""
        response = {
            'success': False,
            'error': error,
            'error_type': 'context_error',
            'details': {
                'pattern_searched': pattern,
                'file_path': file_path,
                'absolute_path': str(Path(file_path).absolute()),
                'line_number': line_number,
                'surrounding_context': surrounding_context,
                'file_content_sample': file_content_sample
            },
            'phase': 'pattern_matching'
        }
        
        self.logger.error(f"Context error response built: {error} for pattern '{pattern}' in {file_path}")
        return response

    def build_pattern_mismatch_response(self, pattern: str, file_path: str, 
                                      file_content: str, suggestions: List[str] = None) -> Dict[str, Any]:
        """Construir respuesta específica para patterns no encontrados"""
        content_lines = file_content.split('\n')
        response = {
            'success': False,
            'error': f"Pattern '{pattern}' not found in file",
            'error_type': 'pattern_mismatch',
            'details': {
                'pattern_searched': pattern,
                'file_path': file_path,
                'absolute_path': str(Path(file_path).absolute()),
                'total_lines': len(content_lines),
                'file_size': len(file_content),
                'suggestions': suggestions or [],
                'first_few_lines': content_lines[:5] if content_lines else []
            },
            'phase': 'pattern_matching'
        }
        
        self.logger.error(f"Pattern mismatch response built: '{pattern}' not found in {file_path}")
        return response

    def build_verbose_error_response(self, error: str, file_path: str, pattern: str,
                                   debug_info: Dict[str, Any], suggestions: List[str] = None) -> Dict[str, Any]:
        """Construir respuesta de error con máximo detalle para debugging"""
        response = {
            'success': False,
            'error': error,
            'error_type': 'verbose_error',
            'details': {
                'pattern_searched': pattern,
                'file_path': file_path,
                'absolute_path': str(Path(file_path).absolute()),
                'debug_info': debug_info,
                'suggestions': suggestions or [],
                'troubleshooting_tips': [
                    f"Check if pattern '{pattern}' exists with different case",
                    f"Verify file '{file_path}' contains expected content",
                    "Consider using --regex flag for pattern matching",
                    "Use --preview flag to see what would be matched"
                ]
            },
            'phase': 'pattern_matching'
        }
        
        self.logger.error(f"Verbose error response built: {error} for pattern '{pattern}'")
        return response