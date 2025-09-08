from typing import Dict, Any, Optional
import logging
from pathlib import Path


class CreateWorkflow:
    """Workflow handler para operaciones CREATE - maneja secuencia y lógica de negocio"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def execute_sequence(self, file_path: str, content: str = None, template: str = None, 
                        path_checker=None, template_generator=None, backup_manager=None, 
                        writer=None, validator=None, **kwargs) -> Dict[str, Any]:
        """Ejecutar secuencia completa del workflow CREATE con manejo de errores"""
        
        self.logger.info(f"Starting CREATE workflow for: {file_path}")
        phases_completed = []
        
        try:
            # FASE 1: Validación de ruta
            path_validation = path_checker.validate_path(file_path)
            phases_completed.append('path_validation')
            if not path_validation.get('success', False):
                return self._build_error_response(
                    'Path validation failed',
                    path_validation.get('errors', []),
                    'path_validation'
                )
            
            # FASE 2: Verificación de permisos
            permissions = path_checker.check_permissions(file_path)
            phases_completed.append('permissions')
            if not permissions.get('can_create', False):
                return self._build_error_response(
                    'Insufficient permissions',
                    permissions,
                    'permissions'
                )
            
            # FASE 3: Crear directorios padres
            parent_result = path_checker.ensure_parent_dirs(file_path)
            phases_completed.append('parent_dirs')
            if not parent_result.get('success', False):
                return self._build_error_response(
                    'Failed to create parent directories',
                    parent_result.get('errors', []),
                    'parent_dirs'
                )
            
            # FASE 4: Generación de contenido
            final_content = self._generate_content(file_path, content, template, template_generator)
            phases_completed.append('content_generation')
            
            # FASE 5: Manejo de backup
            backup_result = self._handle_backup(file_path, backup_manager)
            phases_completed.append('backup')
            
            # FASE 6: Validación de contenido
            content_validation = validator.validate_content(final_content, [])
            phases_completed.append('content_validation')
            if not content_validation.get('valid', False):
                return self._build_error_response(
                    'Content validation failed',
                    content_validation.get('errors', []),
                    'content_validation'
                )
            
            # FASE 7: Escritura del archivo
            write_result = writer.write_file(file_path, final_content)
            phases_completed.append('write')
            if not write_result.get('success', False):
                return self._build_error_response(
                    'File write failed',
                    write_result.get('error', 'Unknown write error'),
                    'write'
                )
            
            # FASE 8: Verificación final
            verification = self._verify_creation(file_path, final_content, validator)
            phases_completed.append('verification')
            
            # Construir respuesta exitosa
            return self._build_success_response(
                file_path, final_content, backup_result, 
                parent_result, verification, phases_completed
            )
            
        except Exception as e:
            self.logger.error(f"CREATE workflow failed: {str(e)}")
            return self._build_error_response(
                f'Workflow execution failed: {str(e)}',
                {'exception': str(e)},
                f'workflow_error_after_{phases_completed[-1] if phases_completed else "start"}'
            )
    
    def _generate_content(self, file_path: str, content: str = None, template: str = None, 
                         template_generator=None) -> str:
        """Generar contenido final usando template_generator"""
        if content:
            return content
        if template:
            return template_generator.generate_template(template, file_path=file_path)
        return template_generator.get_template_for_extension(file_path)
    
    def _handle_backup(self, file_path: str, backup_manager) -> Dict[str, Any]:
        """Manejar backup usando backup_manager"""
        path_obj = Path(file_path)
        if path_obj.exists():
            try:
                backup_path = backup_manager.create_snapshot(file_path)
                return {'created': True, 'backup_path': backup_path, 'success': True}
            except Exception as e:
                return {'created': False, 'error': f'Backup failed: {str(e)}', 'success': False}
        return {'created': False, 'reason': 'File does not exist', 'success': True}
    
    def _verify_creation(self, file_path: str, expected_content: str, validator) -> Dict[str, Any]:
        """Verificar creación exitosa del archivo"""
        try:
            path_obj = Path(file_path)
            if not path_obj.exists():
                return {
                    'verified': False,
                    'error': 'File was not created',
                    'checks': ['existence']
                }
            
            # Verificar contenido
            with open(file_path, 'r', encoding='utf-8') as f:
                actual_content = f.read()
            
            content_match = expected_content.strip() in actual_content
            
            verification_result = {
                'verified': True,
                'file_exists': True,
                'content_written': content_match,
                'file_size': path_obj.stat().st_size,
                'checks': ['existence', 'content', 'size']
            }
            
            if not content_match:
                verification_result['warning'] = 'Content may have been modified by template generation'
            
            return verification_result
            
        except Exception as e:
            return {
                'verified': False,
                'error': f'Verification failed: {str(e)}',
                'checks': ['existence']
            }
    
    def _build_error_response(self, error: str, details: Any, phase: str) -> Dict[str, Any]:
        """Construir respuesta de error estructurada"""
        return {
            'success': False,
            'error': error,
            'details': details,
            'phase': phase
        }
    
    def _build_success_response(self, file_path: str, content: str, backup_result: Dict,
                               parent_result: Dict, verification: Dict, 
                               phases_completed: list) -> Dict[str, Any]:
        """Construir respuesta exitosa completa"""
        path_obj = Path(file_path)
        
        return {
            'success': True,
            'file_path': file_path,
            'absolute_path': str(path_obj.absolute()),
            'content_length': len(content),
            'template_used': None,  # Será actualizado por coordinator
            'backup_created': backup_result.get('created', False),
            'parent_dirs_created': parent_result.get('created', False),
            'verification': verification,
            'phases_completed': phases_completed
        }