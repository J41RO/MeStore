"""
AST Engine - Wrapper para herramienta ast-grep de búsqueda basada en AST.

Este engine proporciona capacidades avanzadas de análisis sintáctico estructural
utilizando la herramienta externa ast-grep para búsquedas y reemplazos basados
en Abstract Syntax Trees.

Dependencias:
    - ast-grep: Herramienta externa de búsqueda estructural basada en AST
    
Capacidades:
    - AST_AWARE: Análisis consciente de la estructura sintáctica
    - STRUCTURAL_SEARCH: Búsqueda basada en patrones estructurales
    - LANGUAGE_SPECIFIC: Soporte para lenguajes específicos
"""

import subprocess
import json
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from .base_engine import BaseEngine, EngineMatch, EngineResult, EngineStatus, register_engine
from .base_engine import EngineCapability


logger = logging.getLogger(__name__)


@register_engine("ast-grep")
class AstEngine(BaseEngine):
    """
    Engine que utiliza ast-grep para búsqueda y reemplazo basado en AST.
    
    ast-grep es una herramienta que permite realizar búsquedas estructurales
    en código fuente utilizando Abstract Syntax Trees, proporcionando mayor
    precisión que las búsquedas basadas en texto.
    
    Ejemplos de uso:
        # Buscar todas las funciones con nombre específico
        pattern = "$FUNC($$ARGS)"
        result = engine.search(content, pattern)
        
        # Reemplazar patrones estructurales
        result = engine.replace(content, "$OLD_FUNC($$ARGS)", "$NEW_FUNC($$ARGS)")
    """
    
    def __init__(self):
        """Initialize AST Engine con verificación de disponibilidad de ast-grep."""
        super().__init__(name="ast-grep")
        
        # Asignar capabilities después de la inicialización base
        self._capabilities = {
            EngineCapability.AST_AWARE,
            EngineCapability.STRUCTURAL_SEARCH,
            EngineCapability.LANGUAGE_SPECIFIC
        }
        
        # Verificar disponibilidad de ast-grep al inicializar
        self._ast_grep_available = self._check_ast_grep_available()
        
        if not self._ast_grep_available:
            logger.warning("ast-grep tool not available. AstEngine will return NOT_SUPPORTED status.")
    
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
    
    def _search_impl(self, content: str, pattern: str, **kwargs) -> EngineResult:
        """
        Buscar coincidencias usando ast-grep.
        
        Args:
            content: Contenido del archivo donde buscar
            pattern: Patrón de búsqueda estructural de ast-grep
            **kwargs: Argumentos adicionales (language, etc.)
            
        Returns:
            EngineResult: Resultado con matches encontrados y estado
        """
        if not self._ast_grep_available:
            logger.warning("ast-grep not available, returning empty results")
            return EngineResult(
                status=EngineStatus.NOT_SUPPORTED,
                matches=[],
                error_message="ast-grep no está instalado en el sistema"
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
                    status=EngineStatus.ERROR,
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
                        status=EngineStatus.ERROR,
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
                status=EngineStatus.ERROR,
                matches=[],
                error_message="ast-grep search timed out"
            )
        except Exception as e:
            logger.error(f"Unexpected error in ast-grep search: {e}")
            return EngineResult(
                status=EngineStatus.ERROR,
                matches=[],
                error_message=f"Unexpected error in ast-grep search: {e}"
            )
    
    def _replace_impl(self, content: str, pattern: str, replacement: str, **kwargs) -> EngineResult:
        """
        Realizar reemplazo usando ast-grep.
        
        Args:
            content: Contenido original del archivo
            pattern: Patrón de búsqueda estructural
            replacement: Patrón de reemplazo
            **kwargs: Argumentos adicionales (language, etc.)
            
        Returns:
            EngineResult: Resultado con contenido modificado y estadísticas
        """
        if not self._ast_grep_available:
            logger.warning("ast-grep not available")
            return EngineResult(
                status=EngineStatus.NOT_SUPPORTED,
                matches=[],
                modified_content=content,
                error_message="ast-grep no está instalado en el sistema"
            )
        
        try:
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
                    status=EngineStatus.ERROR,
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
                operations_count=operations_count
            )
            
        except subprocess.TimeoutExpired:
            logger.error("ast-grep replace timed out")
            return EngineResult(
                status=EngineStatus.ERROR,
                matches=[],
                modified_content=content,
                error_message="ast-grep replace timed out"
            )
        except Exception as e:
            logger.error(f"Unexpected error in ast-grep replace: {e}")
            return EngineResult(
                status=EngineStatus.ERROR,
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
        # Intentar parsear el formato más común
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