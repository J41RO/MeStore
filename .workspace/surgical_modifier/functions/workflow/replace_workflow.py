from typing import Dict, Any, Optional
import logging
from pathlib import Path

class ReplaceWorkflow:
    """Workflow handler para operaciones REPLACE - maneja secuencia y lógica de negocio"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def execute_sequence(self, file_path: str, pattern: str, replacement: str,
                        pattern_factory=None, backup_manager=None, reader=None, 
                        writer=None, validator=None, **kwargs) -> Dict[str, Any]:
        """Ejecutar secuencia completa del workflow REPLACE con manejo de errores"""
        self.logger.info(f"Starting REPLACE workflow for: {file_path}")
        phases_completed = []
        
        try:
            # FASE 1: Validación de archivo existente
            if not Path(file_path).exists():
                return self._build_error_response(
                    f'File does not exist: {file_path}\n\nExamples:\n  python3 cli.py replace file.txt old new\n  python3 cli.py replace old new file.txt',
                    [f'Cannot replace in non-existent file: {file_path}'],
                    'file_validation'
                )
            phases_completed.append('file_validation')
            
            # FASE 2: Crear backup antes del cambio
            try:
                backup_path = backup_manager.create_snapshot(file_path, "replace")
                phases_completed.append('backup_creation')
            except Exception as e:
                return self._build_error_response(
                    'Backup creation failed',
                    [f'Backup error: {str(e)}'],
                    'backup_creation'
                )
            
            # FASE 3: Leer contenido actual
            content_result = reader.read_file(file_path)
            phases_completed.append('content_reading')
            if not content_result.get('success', False):
                return self._build_error_response(
                    'File reading failed',
                    content_result.get('errors', []),
                    'content_reading'
                )
            
            original_content = content_result.get('content', '')
            
            # FASE 4: Pattern matching
            # Selección dinámica de matcher basada en parámetros
            matcher_type = kwargs.get('matcher_type', 'literal')  # default literal
            matcher = pattern_factory.get_optimized_matcher(matcher_type)
            match_result = matcher.find_all(original_content, pattern)
            phases_completed.append('pattern_matching')
            
            if not match_result:
                return {
                    'success': False,
                    'error': 'Pattern not found',
                    'pattern': pattern,
                    'file_path': file_path,
                    'phases_completed': phases_completed
                }
            
            # FASE 5: Realizar replacement
            # Usar método apropiado según el tipo de matcher
            if matcher_type == 'regex':
                replace_result = matcher.replace_pattern(pattern, replacement, original_content)
            else:
                replace_result = matcher.replace_literal(pattern, replacement, original_content)
            new_content = replace_result.get("new_text", original_content)
            phases_completed.append('content_replacement')
            
            # FASE 6: Escribir nuevo contenido
            write_result = writer.write_file(file_path, new_content)
            phases_completed.append('content_writing')
            if not write_result.get('success', False):
                return self._build_error_response(
                    'File writing failed',
                    write_result.get('errors', []),
                    'content_writing'
                )
            
            # FASE 7: Validación final
            validation_result = validator.validate_file(file_path, ["not_empty", "text_only"])
            phases_completed.append('final_validation')
            
            return {
                'success': True,
                'file_path': file_path,
                'pattern': pattern,
                'replacement': replacement,
                'matches_found': len(match_result),
                'backup_created': backup_path,
                'phases_completed': phases_completed,
                'validation': validation_result
            }
            
        except Exception as e:
            self.logger.error(f"REPLACE workflow failed: {str(e)}")
            return self._build_error_response(
                f'Workflow execution failed: {str(e)}',
                [str(e)],
                'workflow_execution',
                phases_completed
            )
    
    def _build_error_response(self, message: str, errors: list, 
                             failed_phase: str, phases_completed: list = None) -> Dict[str, Any]:
        """Construir respuesta de error estandarizada"""
        return {
            'success': False,
            'error': message,
            'errors': errors,
            'failed_phase': failed_phase,
            'phases_completed': phases_completed or []
        }