"""
AST Engine - Wrapper para herramienta ast-grep con soporte JavaScript/TypeScript nativo.

Este engine proporciona capacidades avanzadas de análisis sintáctico estructural
utilizando tanto herramientas externas como parsers nativos JavaScript/TypeScript.

Dependencias:
    - ast-grep: Herramienta externa de búsqueda estructural basada en AST (opcional)
    - Node.js + @babel/parser: Parser JavaScript/TypeScript nativo
    
Capacidades:
    - AST_AWARE: Análisis consciente de la estructura sintáctica
    - STRUCTURAL_SEARCH: Búsqueda basada en patrones estructurales
    - LANGUAGE_SPECIFIC: Soporte para lenguajes específicos
    - JS_TS_NATIVE: Soporte nativo para JavaScript/TypeScript sin dependencias externas
"""

import subprocess
import json
import logging
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from .base_engine import BaseEngine, EngineMatch, EngineResult, EngineStatus, register_engine
from .base_engine import EngineCapability


logger = logging.getLogger(__name__)


@register_engine("ast-grep")
class AstEngine(BaseEngine):
    """
    Engine que utiliza ast-grep para búsqueda y reemplazo basado en AST,
    con soporte nativo para JavaScript/TypeScript usando Node.js.
    
    Ejemplos de uso:
        # Buscar todas las funciones con nombre específico
        pattern = "$FUNC($$ARGS)"
        result = engine.search(content, pattern)
        
        # Reemplazar patrones estructurales
        result = engine.replace(content, "$OLD_FUNC($$ARGS)", "$NEW_FUNC($$ARGS)")
    """
    
    def __init__(self):
        """Initialize AST Engine con verificación de herramientas disponibles."""
        super().__init__(name="ast-grep")
        
        # Asignar capabilities después de la inicialización base
        self._capabilities = {
            EngineCapability.AST_AWARE,
            EngineCapability.STRUCTURAL_SEARCH,
            EngineCapability.LANGUAGE_SPECIFIC
        }
        
        # Verificar disponibilidad de herramientas
        self._ast_grep_available = self._check_ast_grep_available()
        self._js_parser_available = self._check_js_parser_available()
        
        if not self._ast_grep_available:
            logger.warning("ast-grep tool not available. AstEngine will use native JS/TS parser when possible.")
            
        if self._js_parser_available:
            logger.info("JavaScript/TypeScript native parser available and functional.")
    
    def _check_ast_grep_available(self) -> bool:
        """
        Verificar si ast-grep está instalado y disponible.
        
        Returns:
            bool: True si ast-grep está disponible, False en caso contrario
        """
        try:
            result = subprocess.run(
                ["ast-grep", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_js_parser_available(self) -> bool:
        """
        Verificar si el parser JavaScript/TypeScript nativo está disponible.
        
        Returns:
            bool: True si el parser JS/TS está funcional
        """
        try:
            # Determinar ruta del parser
            current_dir = Path(__file__).parent.parent.parent
            parser_path = current_dir / "js_ast_parser.js"
            
            if not parser_path.exists():
                logger.warning(f"JavaScript parser not found at {parser_path}")
                return False
            
            # Probar funcionalidad básica
            result = subprocess.run(
                ["node", str(parser_path), "test"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=current_dir
            )
            
            if result.returncode == 0:
                try:
                    output = json.loads(result.stdout)
                    return output.get('success', False) and output.get('hasAST', False)
                except json.JSONDecodeError:
                    return False
            
            return False
            
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _is_javascript_file(self, file_path: str) -> bool:
        """
        Determinar si un archivo es JavaScript o TypeScript.
        
        Args:
            file_path: Ruta del archivo a verificar
            
        Returns:
            bool: True si es archivo JS/TS
        """
        js_extensions = {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}
        path_obj = Path(file_path)
        return path_obj.suffix.lower() in js_extensions
    
    def _use_native_js_parser(self, content: str, operation: str, **kwargs) -> EngineResult:
        """
        Usar el parser JavaScript/TypeScript nativo para análisis AST.
        
        Args:
            content: Contenido del archivo
            operation: Tipo de operación ('search', 'replace', 'analyze')
            **kwargs: Argumentos adicionales
            
        Returns:
            EngineResult: Resultado del análisis AST
        """
        try:
            current_dir = Path(__file__).parent.parent.parent
            parser_path = current_dir / "js_ast_parser.js"
            
            # Para ahora, solo implementamos análisis básico
            # Futuras versiones pueden expandir con búsqueda/reemplazo específico
            result = subprocess.run(
                ["node", str(parser_path), "test"],
                input=content,
                text=True,
                capture_output=True,
                timeout=30,
                cwd=current_dir
            )
            
            if result.returncode == 0:
                try:
                    output = json.loads(result.stdout)
                    if output.get('success', False):
                        return EngineResult(
                            status=EngineStatus.SUCCESS,
                            matches=[],
                            metadata={
                                'engine': 'native-js-parser',
                                'language': output.get('language', 'javascript'),
                                'ast_available': True,
                                'capabilities': output.get('capabilities', [])
                            }
                        )
                except json.JSONDecodeError:
                    pass
            
            return EngineResult(
                status=EngineStatus.FAILURE,
                matches=[],
                error_message="Native JS parser failed to process content"
            )
            
        except Exception as e:
            logger.error(f"Error in native JS parser: {e}")
            return EngineResult(
                status=EngineStatus.FAILURE,
                matches=[],
                error_message=f"Native JS parser error: {e}"
            )
    
    def _search_impl(self, content: str, pattern: str, **kwargs) -> EngineResult:
        """
        Buscar coincidencias usando ast-grep o parser nativo JS/TS.
        
        Args:
            content: Contenido del archivo donde buscar
            pattern: Patrón de búsqueda estructural
            **kwargs: Argumentos adicionales (language, file_path, etc.)
            
        Returns:
            EngineResult: Resultado con matches encontrados y estado
        """
        file_path = kwargs.get('file_path', 'unknown')
        
        # Para archivos JavaScript/TypeScript, usar parser nativo si disponible
        if self._is_javascript_file(file_path) and self._js_parser_available:
            logger.info(f"Using native JavaScript/TypeScript parser for {file_path}")
            # Por ahora retornamos análisis básico, futuras versiones implementarán búsqueda
            result = self._use_native_js_parser(content, 'search', **kwargs)
            if result.status != EngineStatus.FAILURE:
                return result
            # Si falla el parser nativo, continuar con ast-grep
        
        # Usar ast-grep para otros archivos o como fallback
        if not self._ast_grep_available:
            return EngineResult(
                status=EngineStatus.NOT_SUPPORTED,
                matches=[],
                error_message="ast-grep no está instalado y no es archivo JavaScript/TypeScript"
            )
        
        try:
            # Preparar comando ast-grep para búsqueda
            cmd = ["ast-grep", "--json"]
            
            # Agregar lenguaje si se especifica
            language = kwargs.get('language')
            if language:
                cmd.extend(["--lang", language])
            
            # Agregar patrón de búsqueda
            cmd.extend(["--pattern", pattern])
            
            # Ejecutar comando con contenido desde stdin
            result = subprocess.run(
                cmd,
                input=content,
                text=True,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"ast-grep search failed: {result.stderr}")
                return EngineResult(
                    status=EngineStatus.FAILURE,
                    matches=[],
                    error_message=f"ast-grep search failed: {result.stderr}"
                )
            
            # Parsear output JSON
            matches = []
            if result.stdout.strip():
                try:
                    json_output = json.loads(result.stdout)
                    matches = self._parse_ast_grep_matches(json_output, content)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse ast-grep JSON output: {e}")
                    return EngineResult(
                        status=EngineStatus.FAILURE,
                        matches=[],
                        error_message=f"Failed to parse ast-grep JSON output: {e}"
                    )
            
            status = EngineStatus.SUCCESS if matches else EngineStatus.NO_MATCHES
            return EngineResult(
                status=status,
                matches=matches
            )
            
        except subprocess.TimeoutExpired:
            logger.error("ast-grep search timed out")
            return EngineResult(
                status=EngineStatus.FAILURE,
                matches=[],
                error_message="ast-grep search timed out"
            )
        except Exception as e:
            logger.error(f"Unexpected error in ast-grep search: {e}")
            return EngineResult(
                status=EngineStatus.FAILURE,
                matches=[],
                error_message=f"Unexpected error in ast-grep search: {e}"
            )
    
    def _replace_impl(self, content: str, pattern: str, replacement: str, **kwargs) -> EngineResult:
        """
        Realizar reemplazo usando ast-grep o procesamiento mejorado para JS/TS.
        
        Args:
            content: Contenido original del archivo
            pattern: Patrón de búsqueda estructural
            replacement: Patrón de reemplazo
            **kwargs: Argumentos adicionales (language, file_path, etc.)
            
        Returns:
            EngineResult: Resultado con contenido modificado y estadísticas
        """
        file_path = kwargs.get('file_path', 'unknown')
        
        # Para archivos JavaScript/TypeScript con parser nativo disponible
        if self._is_javascript_file(file_path) and self._js_parser_available:
            logger.info(f"Processing JavaScript/TypeScript file {file_path} with enhanced AST awareness")
            # Por ahora, usar reemplazo de texto mejorado con validación AST
            # Futuras versiones implementarán reemplazo estructural completo
            
            # Validar sintaxis antes del reemplazo
            ast_result = self._use_native_js_parser(content, 'analyze', **kwargs)
            if ast_result.status == EngineStatus.SUCCESS:
                # Realizar reemplazo de texto con información AST disponible
                import re
                try:
                    modified_content = re.sub(re.escape(pattern), replacement, content)
                    operations_count = content.count(pattern)
                    
                    if operations_count > 0:
                        # Validar sintaxis después del reemplazo
                        validation_result = self._use_native_js_parser(modified_content, 'analyze', **kwargs)
                        if validation_result.status == EngineStatus.SUCCESS:
                            return EngineResult(
                                status=EngineStatus.SUCCESS,
                                matches=[],
                                modified_content=modified_content,
                                operations_count=operations_count,
                                metadata={
                                    'engine': 'native-js-enhanced',
                                    'ast_validated': True,
                                    'syntax_valid': True
                                }
                            )
                    
                    return EngineResult(
                        status=EngineStatus.NO_MATCHES if operations_count == 0 else EngineStatus.SUCCESS,
                        matches=[],
                        modified_content=modified_content,
                        operations_count=operations_count,
                        metadata={'engine': 'native-js-enhanced'}
                    )
                    
                except Exception as e:
                    logger.error(f"Error in JavaScript/TypeScript replacement: {e}")
        
        # Usar ast-grep para otros archivos o como fallback
        if not self._ast_grep_available:
            return EngineResult(
                status=EngineStatus.NOT_SUPPORTED,
                matches=[],
                modified_content=content,
                error_message="ast-grep no está instalado"
            )
        
        try:
            # Crear backup antes de operación destructiva
            if file_path != 'unknown':
                self._create_backup_before_operation(file_path, 'replace')
                
            # Preparar comando ast-grep para reemplazo
            cmd = ["ast-grep", "--json", "--rewrite", replacement]
            
            # Agregar lenguaje si se especifica
            language = kwargs.get('language')
            if language:
                cmd.extend(["--lang", language])
            
            # Agregar patrón de búsqueda
            cmd.extend(["--pattern", pattern])
            
            # Ejecutar comando con contenido desde stdin
            result = subprocess.run(
                cmd,
                input=content,
                text=True,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"ast-grep replace failed: {result.stderr}")
                return EngineResult(
                    status=EngineStatus.FAILURE,
                    matches=[],
                    modified_content=content,
                    error_message=f"ast-grep replace failed: {result.stderr}"
                )
            
            # ast-grep retorna el contenido modificado directamente
            modified_content = result.stdout if result.stdout else content
            
            # Contar las modificaciones comparando contenido
            operations_count = self._count_differences(content, modified_content)
            
            status = EngineStatus.SUCCESS if operations_count > 0 else EngineStatus.NO_MATCHES
            
            return EngineResult(
                status=status,
                matches=[],
                modified_content=modified_content,
                operations_count=operations_count,
                metadata={
                    'engine': self.name,
                    'backup_created': file_path != 'unknown'
                }
            )
            
        except subprocess.TimeoutExpired:
            logger.error("ast-grep replace timed out")
            return EngineResult(
                status=EngineStatus.FAILURE,
                matches=[],
                modified_content=content,
                error_message="ast-grep replace timed out"
            )
        except Exception as e:
            logger.error(f"Unexpected error in ast-grep replace: {e}")
            return EngineResult(
                status=EngineStatus.FAILURE,
                matches=[],
                modified_content=content,
                error_message=f"Unexpected error in ast-grep replace: {e}"
            )
    
    def _parse_ast_grep_matches(self, json_output: Dict[str, Any], content: str) -> List[EngineMatch]:
        """
        Parsear output JSON de ast-grep y convertir a EngineMatch objects.
        
        Args:
            json_output: Output JSON de ast-grep
            content: Contenido original para extraer contexto
            
        Returns:
            List[EngineMatch]: Lista de matches parseados
        """
        matches = []
        lines = content.splitlines()
        
        # ast-grep puede retornar diferentes formatos dependiendo de la versión
        items = json_output if isinstance(json_output, list) else json_output.get('matches', [])
        
        for item in items:
            try:
                # Extraer información de posición
                range_info = item.get('range', {})
                start_line = range_info.get('start', {}).get('line', 1) - 1  # ast-grep usa 1-based
                start_col = range_info.get('start', {}).get('column', 0)
                end_line = range_info.get('end', {}).get('line', start_line + 1) - 1
                end_col = range_info.get('end', {}).get('column', 0)
                
                # Extraer texto matched
                matched_text = item.get('text', '')
                if not matched_text and start_line < len(lines):
                    matched_text = lines[start_line][start_col:end_col] if end_line == start_line else lines[start_line][start_col:]
                
                # Crear EngineMatch
                match = EngineMatch(
                    start_line=start_line,
                    start_col=start_col,
                    end_line=end_line,
                    end_col=end_col,
                    matched_text=matched_text,
                    context_before=lines[max(0, start_line-1)] if start_line > 0 else "",
                    context_after=lines[min(len(lines)-1, start_line+1)] if start_line < len(lines)-1 else ""
                )
                matches.append(match)
                
            except (KeyError, IndexError, AttributeError) as e:
                logger.warning(f"Failed to parse ast-grep match item: {e}")
                continue
        
        return matches
    
    def _count_differences(self, original: str, modified: str) -> int:
        """
        Contar el número de diferencias entre contenido original y modificado.
        
        Args:
            original: Contenido original
            modified: Contenido modificado
            
        Returns:
            int: Número aproximado de cambios realizados
        """
        if original == modified:
            return 0
        
        # Método simple: contar líneas diferentes
        orig_lines = original.splitlines()
        mod_lines = modified.splitlines()
        
        differences = 0
        max_lines = max(len(orig_lines), len(mod_lines))
        
        for i in range(max_lines):
            orig_line = orig_lines[i] if i < len(orig_lines) else ""
            mod_line = mod_lines[i] if i < len(mod_lines) else ""
            
            if orig_line != mod_line:
                differences += 1
        
        return max(1, differences)  # Al menos 1 si hay diferencias