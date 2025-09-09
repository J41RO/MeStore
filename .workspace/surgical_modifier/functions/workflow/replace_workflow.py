from typing import Dict, Any, Optional
import logging
from pathlib import Path
from functions.debugging.context_extractor import ContextExtractor
from functions.debugging.pattern_suggester import PatternSuggester
from functions.response.response_builder import ResponseBuilder
from functions.validation.js_ts_validator import JsTsValidator
from functions.analysis.structural_analyzer import StructuralAnalyzer
from functions.typescript.syntax_validator import TypeScriptSyntaxValidator

class ReplaceWorkflow:
    """Workflow handler para operaciones REPLACE - maneja secuencia y lógica de negocio"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.js_ts_validator = JsTsValidator()
        self.structural_analyzer = StructuralAnalyzer()
        self.typescript_validator = TypeScriptSyntaxValidator()
        self.context_extractor = ContextExtractor()
        self.pattern_suggester = PatternSuggester()
        self.response_builder = ResponseBuilder()
    
    def _detect_optimal_matcher_type(self, pattern: str, content: str, current_type: str) -> str:
        """Detecta automáticamente el tipo de matcher óptimo basado en el patrón y contenido"""
        # Si ya está especificado explícitamente, respetarlo
        if current_type and current_type != 'literal':
            return current_type
            
        # Detectar casos que necesitan fuzzy matching automático
        needs_fuzzy = False
        
        # 1. Patrón con espacios que podrían variar
        if ' ' in pattern:
            pattern_compact = pattern.replace(' ', '')
            if pattern_compact in content.replace(' ', ''):
                needs_fuzzy = True
                
        # 2. Propiedades de objetos JavaScript/TypeScript
        if ':' in pattern and '{' in content:
            needs_fuzzy = True
            
        # 3. Patrones con quotes que podrían diferir
        if ('"' in pattern and "'" in content) or ("'" in pattern and '"' in content):
            needs_fuzzy = True
            
        return 'fuzzy' if needs_fuzzy else 'literal'
    
    def execute_sequence(self, file_path: str, pattern: str, replacement: str,
                        pattern_factory=None, backup_manager=None, reader=None, 
                        writer=None, validator=None, dry_run=False, **kwargs) -> Dict[str, Any]:
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
            # SMART MATCHING: Detectar automáticamente cuándo usar fuzzy matching
            smart_matcher_type = self._detect_optimal_matcher_type(pattern, original_content, kwargs.get('matcher_type'))
            if smart_matcher_type != kwargs.get('matcher_type', 'literal'):
                self.logger.info(f"Smart matching detected: switching from 'literal' to '{smart_matcher_type}' for pattern '{pattern}'")
            matcher_type = smart_matcher_type  # usar smart matching automático
            matcher = pattern_factory.get_optimized_matcher(matcher_type)
            # Ajustar threshold para fuzzy matching cuando es seleccionado por smart matching
            if matcher_type == 'fuzzy':
                match_result = matcher.find_all(original_content, pattern, threshold=0.6)
            else:
                match_result = matcher.find_all(original_content, pattern)
            
            # FALLBACK AUTOMÁTICO: Si matching exacto falla, intentar fuzzy matching
            if not match_result and (matcher_type == 'literal' or matcher_type == 'fuzzy'):
                self.logger.info(f"Exact matching failed for pattern '{pattern}', attempting fuzzy fallback")
                fuzzy_matcher = pattern_factory.get_optimized_matcher('fuzzy')
                fuzzy_result = fuzzy_matcher.find_all(original_content, pattern, threshold=0.6)
                if fuzzy_result:
                    self.logger.info(f"Fuzzy matching successful with {len(fuzzy_result)} matches")
                    match_result = fuzzy_result
                    matcher = fuzzy_matcher  # Usar fuzzy matcher para el replacement también
                    matcher_type = 'fuzzy'  # Actualizar tipo para lógica posterior
                else:
                    self.logger.info("Fuzzy matching also failed")
                    # FALLBACK MANUAL: Cuando FuzzyMatcher falla completamente
                    manual_result = self._manual_fuzzy_matching(original_content, pattern)
                    if manual_result:
                        self.logger.info(f"Manual matching successful for pattern '{pattern}'")
                        match_result = [manual_result]
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
                    # Generar sugerencias inteligentes usando PatternSuggester mejorado
                    suggestions = {
                        'similar_patterns': self.pattern_suggester.suggest_patterns(file_content, pattern)
                    }
                    
                    # Agregar logging de sugerencias automáticas
                    if suggestions['similar_patterns']:
                        self.logger.info(f"Generated {len(suggestions['similar_patterns'])} intelligent suggestions for pattern '{pattern}'")
                    
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

                # Validar compatibilidad de tipos TypeScript si es archivo TS
                if file_path.endswith('.ts') or file_path.endswith('.tsx'):
                    ts_validation = self._validate_typescript_types(original_content, new_content, file_path)
                    
                    # Si hay warnings de tipos, agregarlos al resultado
                    if ts_validation['warnings']:
                        validation_warnings = ts_validation['warnings']
                        self.logger.warning('TypeScript type compatibility warnings detected')
                        for warning in validation_warnings:
                            self.logger.warning('  - ' + warning)
                    
                    # Si hay errores críticos de tipos, detener el proceso
                    if ts_validation['errors']:
                        validation_errors = ts_validation['errors'] 
                        error_message = 'TypeScript type incompatibilities detected: ' + str(len(validation_errors)) + ' errors'
                        self.logger.error(error_message)
                        for error in validation_errors:
                            self.logger.error('  - ' + error)
                        
                        # Mostrar sugerencias si están disponibles
                        if ts_validation['suggestions']:
                            self.logger.warning('Suggested fixes:')
                            for suggestion in ts_validation['suggestions']:
                                self.logger.warning('  + ' + suggestion)
                        
                        return self._build_error_response(
                            error_message,
                            validation_errors,
                            phases_completed,
                            backup_path
                        )
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
            if dry_run:
                # Modo dry-run: No escribir archivo, solo retornar preview info
                self.logger.info(f'DRY-RUN MODE: Skipping file write for {file_path}')
                phases_completed.append('dry_run_preview')
                return self._build_dry_run_response(
                    file_path, original_content, new_content, matches_found
                )
            
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


    def _validate_typescript_types(self, original_content: str, new_content: str, file_path: str) -> Dict[str, Any]:
        """Validar compatibilidad de tipos TypeScript entre contenido original y nuevo"""
        try:
            # Solo validar archivos TypeScript
            if not (file_path.endswith('.ts') or file_path.endswith('.tsx')):
                return {'valid': True, 'warnings': [], 'errors': [], 'suggestions': []}
            
            # Usar TypeScriptSyntaxValidator para validar compatibilidad
            validation_result = self.typescript_validator.validate_type_compatibility(original_content, new_content)
            
            # Formatear resultado para el workflow
            return {
                'valid': validation_result['compatible'],
                'warnings': validation_result['warnings'],
                'errors': validation_result['errors'],
                'suggestions': validation_result['suggestions']
            }
            
        except Exception as e:
            self.logger.warning('Error en validacion TypeScript: ' + str(e))
            # En caso de error, no bloquear el workflow
            return {'valid': True, 'warnings': [], 'errors': [], 'suggestions': []}


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


    def _build_dry_run_response(self, file_path: str, original_content: str, 
                               new_content: str, matches_found: int) -> Dict[str, Any]:
        """Construir respuesta para modo dry-run con información de preview"""
        return {
            'success': True,
            'dry_run': True,
            'message': f'DRY-RUN: Preview generated for {file_path}',
            'file_path': file_path,
            'matches_count': matches_found,
            'original_content': original_content,
            'new_content': new_content,
            'phases_completed': ['file_validation', 'backup_creation', 'content_reading', 
                               'pattern_matching', 'content_replacement', 'dry_run_preview'],
            'preview_available': True
        }

    def _manual_fuzzy_matching(self, content: str, pattern: str) -> dict:
        """Fallback manual cuando FuzzyMatcher falla"""
        # Caso 1: Diferencias de espaciado
        pattern_no_spaces = pattern.replace(' ', '')
        content_lines = content.split('\n')
        
        for i, line in enumerate(content_lines):
            line_no_spaces = line.replace(' ', '')
            if pattern_no_spaces in line_no_spaces:
                # Encontrar posición real en el contenido original
                # Buscar la posición exacta del patrón en la línea original
                # Buscar 'prop:value' exacto en la línea 
                start_in_line = line.find('prop:value')
                if start_in_line == -1:
                    # Fallback: buscar sin espacios pero con contexto
                    for k in range(len(line) - len(pattern_no_spaces) + 1):
                        if line[k:k+len(pattern_no_spaces)] == pattern_no_spaces:
                            start_in_line = k
                            break
                if start_in_line == -1:  # Si no encuentra exacto, buscar aproximado
                    for j in range(len(line) - len(pattern_no_spaces) + 1):
                        if line[j:j+len(pattern_no_spaces)].replace(' ', '') == pattern_no_spaces:
                            start_in_line = j
                            break
                
                if start_in_line != -1:
                    return {
                        'match': pattern_no_spaces,
                        'start': start_in_line,
                        'end': start_in_line + len(pattern_no_spaces),
                        'groups': []
                    }
        return None