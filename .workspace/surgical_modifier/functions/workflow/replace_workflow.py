from typing import Dict, Any, Optional
import logging
from pathlib import Path
from functions.debugging.context_extractor import ContextExtractor
from functions.debugging.pattern_suggester import PatternSuggester
from functions.response.response_builder import ResponseBuilder
from functions.validation.js_ts_validator import JsTsValidator
from functions.analysis.structural_analyzer import StructuralAnalyzer

class ReplaceWorkflow:
    """Workflow handler para operaciones REPLACE - maneja secuencia y lógica de negocio"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.js_ts_validator = JsTsValidator()
        self.structural_analyzer = StructuralAnalyzer()
        self.context_extractor = ContextExtractor()
        self.pattern_suggester = PatternSuggester()
        self.response_builder = ResponseBuilder()
    
    def execute_sequence(self, file_path: str, pattern: str, replacement: str,
                        pattern_factory=None, backup_manager=None, reader=None, 
                        writer=None, validator=None, **kwargs) -> Dict[str, Any]:
        """Ejecutar secuencia completa del workflow REPLACE con manejo de errores"""
        self.logger.info(f"Starting REPLACE workflow for: {file_path}")
        phases_completed = []
        backup_path = None
        
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
                backup_created = True
                phases_completed.append('backup_creation')
                self.logger.info(f"Backup created: {backup_path}")
            except Exception as e:
                self.logger.error(f"Backup creation failed: {str(e)}")
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

            # FASE 3.5: Análisis estructural preventivo (opcional)
            skip_structural = kwargs.get('skip_structural_analysis', False)
            if not skip_structural:
                self.logger.info('Ejecutando análisis estructural preventivo...')
                try:
                    analysis_result = self.structural_analyzer.analyze_before_modification(
                        file_path, 
                        original_content,
                        ['syntax', 'duplicates']
                    )
                    phases_completed.append('structural_analysis')
                    
                    # Procesar problemas encontrados
                    if analysis_result.has_issues:
                        critical_issues = analysis_result.get_critical_issues()
                        warnings = analysis_result.get_warnings()
                        
                        # Si hay errores críticos, detener modificación
                        if critical_issues:
                            self.logger.warning(f'Análisis preventivo detectó {len(critical_issues)} problemas críticos')
                            return self._build_structural_warning_response(
                                critical_issues, warnings, phases_completed, backup_path
                            )
                        
                        # Si solo hay advertencias, continuar pero reportar
                        if warnings:
                            self.logger.info(f'Análisis preventivo detectó {len(warnings)} advertencias')
                            # Las advertencias se incluirán en la respuesta final
                    
                except Exception as e:
                    self.logger.warning(f'Error en análisis estructural: {str(e)}')
                    # No detener el flujo por errores de análisis
            else:
                self.logger.info('Análisis estructural omitido (--skip-structural-analysis)')
            
            # FASE 4: Pattern matching
            # Selección dinámica de matcher basada en parámetros
            matcher_type = kwargs.get('matcher_type', 'literal')  # default literal
            matcher = pattern_factory.get_optimized_matcher(matcher_type)
            match_result = matcher.find_all(original_content, pattern)
            phases_completed.append('pattern_matching')
            
            if not match_result:
                # Generar error contextual usando nuevo sistema
                try:
                    # Obtener contenido del archivo para contexto
                    file_result = reader.read_file(file_path)
                    file_content = file_result.get('content', '') if isinstance(file_result, dict) else str(file_result)
                    
                    # Extraer contexto detallado
                    pattern_context = self.context_extractor.extract_pattern_context(
                        file_path, pattern, kwargs.get('regex', False)
                    )
                    
                    # Generar sugerencias
                    suggestions = self.context_extractor.suggest_alternatives(file_path, pattern)
                    
                    # Usar nuevo ResponseBuilder para error contextual
                    if kwargs.get('verbose', False):
                        debug_info = {
                            'file_analysis': self.context_extractor.analyze_file_structure(file_path),
                            'pattern_context': pattern_context,
                            'match_attempt_details': match_result
                        }
                        return self.response_builder.build_verbose_error_response(
                            f"Pattern '{pattern}' not found in {file_path}",
                            file_path, pattern, debug_info, 
                            suggestions.get('similar_patterns', [])
                        )
                    else:
                        return self.response_builder.build_pattern_mismatch_response(
                            pattern, file_path, file_content,
                            suggestions.get('similar_patterns', [])
                        )
                        
                except Exception as context_error:
                    # Fallback al error simple si el contexto falla
                    self.logger.error(f"Context extraction failed: {context_error}")
                    return {
                        'success': False,
                        'error': 'Pattern not found',
                        'pattern': pattern,
                        'file_path': file_path,
                        'phases_completed': phases_completed,
                        'context_error': str(context_error)
                    }
            
            # FASE 5: Realizar replacement
            # Usar método apropiado según el tipo de matcher
            if matcher_type == 'regex':
                replace_result = matcher.replace_pattern(pattern, replacement, original_content)
            else:
                replace_result = matcher.replace_literal(pattern, replacement, original_content)
            new_content = replace_result.get("new_text", original_content)
            phases_completed.append('content_replacement')
            
            # FASE 6.5: Validación de sintaxis JS/TS (si aplica) - ANTES de escribir
            if self._is_js_ts_file(file_path) and not kwargs.get('force', False):
                validation_result = self._validate_js_ts_syntax(new_content, file_path)
                if not validation_result['valid']:
                    self.logger.error(f"Sintaxis JS/TS inválida después del reemplazo: {validation_result['errors']}")
                    # No necesitamos rollback aquí porque aún no hemos escrito el archivo
                    return {
                        'success': False,
                        'error': f"Sintaxis JS/TS inválida: {'; '.join(validation_result['errors'])}",
                        'rollback_applied': False,
                        'file_path': file_path,
                        'validation_errors': validation_result['errors'],
                        'phases_completed': phases_completed
                    }
                else:
                    self.logger.info("Validación JS/TS pasó correctamente")
            elif self._is_js_ts_file(file_path) and kwargs.get('force', False):
                self.logger.warning(f"FORCE MODE: Skipping JS/TS validation for {file_path}")
            
            # FASE 6: Escribir nuevo contenido (solo si validación pasó)
            write_result = writer.write_file(file_path, new_content)
            phases_completed.append('content_writing')
            if not write_result.get('success', False):
                # Si falla la escritura, el archivo original sigue intacto
                return self._build_error_response(
                    'File writing failed',
                    write_result.get('errors', []),
                    'content_writing'
                )
            
            # FASE 7: Validación final
            validation_result = validator.validate_file(file_path, ["not_empty", "text_only"])
            phases_completed.append('final_validation')
            
            # Si llegamos aquí, todo fue exitoso
            matches_count = len(match_result)
            self.logger.info(f"REPLACE workflow completed successfully. Matches: {matches_count}")
            
            return {
                'success': True,
                'file_path': file_path,
                'pattern': pattern,
                'replacement': replacement,
                'matches_found': matches_count,
                'matches_count': matches_count,  # Alias para compatibilidad
                'backup_created': backup_path,
                'backup_path': backup_path,
                'phases_completed': phases_completed,
                'validation': validation_result
            }
            
        except Exception as e:
            self.logger.error(f"REPLACE workflow failed: {str(e)}")
            
            # Rollback automático si algo falló después de escribir
            if backup_path and 'content_writing' in phases_completed:
                try:
                    backup_manager.restore_backup(file_path, backup_path)
                    self.logger.info(f"Emergency rollback applied: {file_path} restored from backup")
                    rollback_applied = True
                except Exception as rollback_error:
                    self.logger.error(f"Emergency rollback failed: {str(rollback_error)}")
                    rollback_applied = False
            else:
                rollback_applied = False
            
            return self._build_error_response(
                f'Workflow execution failed: {str(e)}',
                [str(e)],
                'workflow_execution',
                phases_completed,
                rollback_applied=rollback_applied
            )
    
    def _build_error_response(self, message: str, errors: list, 
                             failed_phase: str, phases_completed: list = None,
                             rollback_applied: bool = False) -> Dict[str, Any]:
        """Construir respuesta de error estandarizada"""
        return {
            'success': False,
            'error': message,
            'errors': errors,
            'failed_phase': failed_phase,
            'phases_completed': phases_completed or [],
            'rollback_applied': rollback_applied
        }

    def _is_js_ts_file(self, file_path: str) -> bool:
        """Verifica si el archivo es JavaScript o TypeScript."""
        js_ts_extensions = ['.js', '.jsx', '.ts', '.tsx']
        return any(file_path.endswith(ext) for ext in js_ts_extensions)
    
    def _validate_js_ts_syntax(self, content: str, file_path: str) -> Dict[str, Any]:
        """Valida sintaxis JS/TS del contenido."""
        try:
            file_extension = Path(file_path).suffix
            errors = self.js_ts_validator.get_syntax_errors(content, file_extension)
            return {
                'valid': len(errors) == 0,
                'errors': errors
            }
        except Exception as e:
            self.logger.error(f"Error en validación JS/TS: {e}")
            return {
                'valid': True,  # En caso de error del validador, no bloquear
                'errors': []
            }


    def _build_structural_warning_response(self, critical_issues, warnings, phases_completed, backup_path):
        """Construye respuesta cuando se detectan problemas estructurales"""
        response_data = {
            'success': False,
            'operation': 'replace',
            'structural_analysis': {
                'critical_issues': len(critical_issues),
                'warnings': len(warnings),
                'details': []
            },
            'phases_completed': phases_completed,
            'backup_path': backup_path,
            'message': 'Modificación bloqueada por problemas estructurales críticos'
        }
        
        # Agregar detalles de problemas críticos
        for issue in critical_issues:
            response_data['structural_analysis']['details'].append({
                'type': issue.type,
                'severity': issue.severity,
                'file': issue.file_path,
                'line': issue.line_number,
                'message': issue.message
            })
        
        # Agregar advertencias
        for warning in warnings:
            response_data['structural_analysis']['details'].append({
                'type': warning.type,
                'severity': warning.severity,
                'file': warning.file_path,
                'line': warning.line_number,
                'message': warning.message
            })
        
        return response_data