"""
Surgical Modifier v6.0 - BEFORE Operation (Refactorizada)
Insert content before a specific line/pattern - LIMPIADA DE DUPLICACIONES
"""

import os
import re
from pathlib import Path
from typing import List, Optional
import time
import shutil

# IMPORTS CENTRALIZADOS - NO DUPLICAR IMPLEMENTACIONES
from ...shared_functions.content_processor import detect_pattern_indentation, apply_context_indentation
from ...shared_functions.backup_system import create_automatic_backup, cleanup_old_backups
from ...shared_functions.syntax_validators import validate_python_syntax, validate_javascript_syntax

from utils.escape_processor import process_content_escapes

from ..base_operation import (
    ArgumentSpec,
    BaseOperation,
    ContentError,
    FileSystemError,
    OperationContext,
    OperationResult,
    OperationType,
    ValidationError,
)

try:
    from utils.logger import logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    logger = None

def before_operation(file_path: str, pattern: str, content: str, **kwargs):
    """Simple before operation function - no classes"""
    try:
        # Leer archivo
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()

        # Buscar patrón e insertar antes
        if pattern in file_content:
            # Insertar contenido antes del patrón
            new_content = file_content.replace(pattern, content + pattern)

            # Escribir archivo modificado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return {
                'success': True,
                'message': f'Inserted content before pattern in {file_path}',
                'file_path': file_path
            }
        else:
            return {
                'success': False,
                'error': f'Pattern not found in {file_path}',
                'file_path': file_path
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'file_path': file_path
        }

# Alias for consistency
execute = before_operation

class BeforeOperation(BaseOperation):
    """
    BEFORE operation implementation with full integration.
    REFACTORIZADA: Eliminadas ~300 líneas de duplicaciones
    """

    def __init__(self):
        super().__init__(OperationType.BEFORE, "before")
        self.inserted_content = {}  # Track inserted content for rollback

    def prepare_context(self, target_file, content=None, **kwargs):
        """Override prepare_context to ensure content is properly handled for BEFORE operation."""
        from pathlib import Path
        
        # Ensure target_file is a Path object
        if isinstance(target_file, str):
            target_file = Path(target_file)
        
        # Create context using parent method
        context = super().prepare_context(target_file, None, **kwargs)
        
        # CORRECCIÓN: Establecer content correctamente
        context.content = content if content is not None else ""
        
        return context

    def _get_operation_specific_arguments(self) -> List["ArgumentSpec"]:
        """Define BEFORE-specific arguments for integration with registry."""
        if not hasattr(self, "_ArgumentSpec_available"):
            try:
                from ..base_operation import ArgumentSpec
                self._ArgumentSpec_available = True
            except ImportError:
                self._ArgumentSpec_available = False
                return []

        if not self._ArgumentSpec_available:
            return []

        from ..base_operation import ArgumentSpec

        return [
            ArgumentSpec(
                name="pattern",
                type=str,
                required=True,
                help="Pattern/line to search for to insert content before",
                example="def function_name",
            ),
            ArgumentSpec(
                name="content",
                type=str,
                required=True,
                help="Content to insert before the pattern",
                example="    # This is a comment",
            ),
            ArgumentSpec(
                name="regex_mode",
                type=bool,
                required=False,
                default=False,
                help="Use regex pattern matching",
                example="false",
            ),
            ArgumentSpec(
                name="case_sensitive",
                type=bool,
                required=False,
                default=True,
                help="Case sensitive pattern matching",
                example="true",
            ),
            ArgumentSpec(
                name="first_match_only",
                type=bool,
                required=False,
                default=True,
                help="Insert before first match only",
                example="true",
            ),
            ArgumentSpec(
                name="preserve_indentation",
                type=bool,
                required=False,
                default=True,
                help="Preserve indentation of the target line",
                example="true",
            ),
        ]

    def get_description(self) -> str:
        """Get BEFORE operation description."""
        return "Insert content before a specific line or pattern in files"

    def get_examples(self) -> List[str]:
        """Get BEFORE operation examples."""
        return [
            "surgical-modifier before --target-file models.py --pattern 'class User:' --content '# User model definition'",
            "surgical-modifier before --target-file views.py --pattern 'return render' --content '    # Process data before rendering'",
            "surgical-modifier before --target-file app.js --pattern 'export default' --content '// Export component' --regex-mode",
        ]

    def execute(self, context: OperationContext) -> OperationResult:
        """Execute BEFORE operation."""
        target_file = None  # Ensure target_file is always defined
        try:
            target_file = context.target_file
            pattern = (
                context.arguments.get("pattern", context.position_marker)
                if context.arguments
                else context.position_marker
            )
            content = context.content or ""

            # Validate inputs
            if not pattern:
                return OperationResult(
                    success=False,
                    operation_type=self.operation_type,
                    target_path=str(target_file),
                    message="Pattern is required for BEFORE operation",
                    details={"missing_pattern": True},
                    execution_time=0.0,
                    operation_name=self.operation_name,
                )

            # Check if file exists
            if not target_file.exists():
                return OperationResult(
                    success=False,
                    operation_type=self.operation_type,
                    target_path=str(target_file),
                    message=f"Target file does not exist: {target_file}",
                    details={"file_not_found": True},
                    execution_time=0.0,
                    operation_name=self.operation_name,
                )

            # Read current file content
            with open(target_file, "r", encoding="utf-8") as f:
                original_content = f.read()

            # Get insertion options
            regex_mode = (
                context.arguments.get("regex_mode", False)
                if context.arguments
                else False
            )
            case_sensitive = (
                context.arguments.get("case_sensitive", True)
                if context.arguments
                else True
            )
            first_match_only = (
                context.arguments.get("first_match_only", True)
                if context.arguments
                else True
            )
            preserve_indentation = (
                context.arguments.get("preserve_indentation", True)
                if context.arguments
                else True
            )

            # Perform insertion
            insertion_result = self._perform_before_insertion(
                original_content,
                pattern,
                content,
                regex_mode,
                case_sensitive,
                first_match_only,
                preserve_indentation,
            )

            if not insertion_result["success"]:
                return OperationResult(
                    success=False,
                    operation_type=self.operation_type,
                    target_path=str(target_file),
                    message=insertion_result["message"],
                    details=insertion_result["details"],
                    execution_time=0.0,
                    operation_name=self.operation_name,
                )

            new_content = insertion_result["new_content"]
            insertions_made = insertion_result["insertions_made"]

            # Write updated content to file
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(new_content)

            # Track insertion for potential rollback
            self.inserted_content[str(target_file)] = {
                "original_content": original_content,
                "pattern": pattern,
                "content": content,
                "insertions_made": insertions_made,
                "insertion_positions": insertion_result.get("insertion_positions", []),
            }

            return OperationResult(
                success=True,
                operation_type=self.operation_type,
                target_path=str(target_file),
                message=f"Successfully inserted content before {insertions_made} occurrence(s) in {target_file}",
                details={
                    "pattern": pattern,
                    "content": content,
                    "insertions_made": insertions_made,
                    "regex_mode": regex_mode,
                    "case_sensitive": case_sensitive,
                    "first_match_only": first_match_only,
                    "preserve_indentation": preserve_indentation,
                    "original_length": len(original_content),
                    "new_length": len(new_content),
                },
                execution_time=0.0,  # Will be set by base class
                content_processed=new_content,
                operation_name=self.operation_name,
            )
        except PermissionError as e:
            raise FileSystemError(
                f"Permission denied accessing file: {target_file if target_file is not None else '<unknown>'}",
                self.operation_type,
                str(target_file) if target_file is not None else "<unknown>",
                {"permission_error": str(e)},
            )
        except UnicodeDecodeError as e:
            raise ContentError(
                f"Unable to decode file content: {target_file if target_file is not None else '<unknown>'}",
                self.operation_type,
                str(target_file) if target_file is not None else "<unknown>",
                {"encoding_error": str(e)},
            )
        except Exception as e:
            raise FileSystemError(
                f"Unexpected error during insertion: {target_file if target_file is not None else '<unknown>'}",
                self.operation_type,
                str(target_file) if target_file is not None else "<unknown>",
                {"unexpected_error": str(e)},
            )
            

    def _perform_before_insertion(
        self,
        content: str,
        pattern: str,
        insertion: str,
        regex_mode: bool,
        case_sensitive: bool,
        first_match_only: bool,
        preserve_indentation: bool,
    ) -> dict:
        """Perform the actual content insertion before pattern."""
        try:
            lines = content.splitlines(keepends=True)
            new_lines = []
            insertions_made = 0
            insertion_positions = []

            for i, line in enumerate(lines):
                # Check if this line matches the pattern
                if self._line_matches_pattern(
                    line, pattern, regex_mode, case_sensitive
                ):
                    # Prepare content to insert
                    content_to_insert = insertion

                    # Preserve indentation if requested - USA SHARED FUNCTION
                    if preserve_indentation:
                        indentation = self._get_line_indentation(line)
                        content_to_insert = apply_context_indentation(content_to_insert, len(indentation))

                    # Ensure content ends with newline for proper line separation
                    if not content_to_insert.endswith("\n"):
                        content_to_insert += "\n"

                    # Insert the content before this line
                    new_lines.append(content_to_insert)
                    insertions_made += 1
                    insertion_positions.append(i + 1)  # Line number (1-based)

                    # Add the original line
                    new_lines.append(line)

                    # If first match only, add remaining lines and break
                    if first_match_only:
                        new_lines.extend(lines[i + 1 :])
                        break
                else:
                    # Add the original line
                    new_lines.append(line)

            if insertions_made == 0:
                return {
                    "success": False,
                    "message": f"Pattern not found: '{pattern}'",
                    "details": {"pattern_not_found": True, "pattern": pattern},
                }

            new_content = "".join(new_lines)

            return {
                "success": True,
                "new_content": new_content,
                "insertions_made": insertions_made,
                "insertion_positions": insertion_positions,
                "details": {
                    "pattern": pattern,
                    "insertion": insertion,
                    "regex_mode": regex_mode,
                    "case_sensitive": case_sensitive,
                    "first_match_only": first_match_only,
                    "preserve_indentation": preserve_indentation,
                },
            }

        except re.error as e:
            return {
                "success": False,
                "message": f"Invalid regex pattern: {e}",
                "details": {"regex_error": str(e), "pattern": pattern},
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Insertion failed: {e}",
                "details": {"insertion_error": str(e)},
            }

    def _line_matches_pattern(
        self, line: str, pattern: str, regex_mode: bool, case_sensitive: bool
    ) -> bool:
        """Check if a line matches the given pattern."""
        if regex_mode:
            flags = 0 if case_sensitive else re.IGNORECASE
            return bool(re.search(pattern, line, flags))
        else:
            search_line = line if case_sensitive else line.lower()
            search_pattern = pattern if case_sensitive else pattern.lower()
            return search_pattern in search_line

    def _get_line_indentation(self, line: str) -> str:
        """Extract indentation from a line."""
        return line[: len(line) - len(line.lstrip())]

    def validate_context(self, context: OperationContext) -> List[str]:
        """Validate BEFORE operation context."""
        errors = []

        # Validate target file
        if not context.target_file:
            errors.append("Target file path is required")
        else:
            if not context.target_file.exists():
                errors.append(f"Target file does not exist: {context.target_file}")
            elif not os.access(context.target_file, os.R_OK):
                errors.append(f"Target file is not readable: {context.target_file}")
            elif not os.access(context.target_file, os.W_OK):
                errors.append(f"Target file is not writable: {context.target_file}")

        # Validate pattern
        pattern = (
            context.arguments.get("pattern", context.position_marker)
            if context.arguments
            else context.position_marker
        )
        if not pattern:
            errors.append("Pattern is required for BEFORE operation")

        # Validate content
        if not context.content:
            errors.append("Content to insert is required")

        # Validate regex pattern if regex mode is enabled
        regex_mode = (
            context.arguments.get("regex_mode", False) if context.arguments else False
        )
        if regex_mode and pattern:
            try:
                re.compile(pattern)
            except re.error as e:
                errors.append(f"Invalid regex pattern '{pattern}': {e}")

        return errors

    def can_rollback(self) -> bool:
        """BEFORE operations support rollback by restoring original content."""
        return True

    # ========== v5.3 COMPATIBILITY METHODS ==========

    def insert_before_v53(
        self,
        file_path: str,
        pattern: str,
        content: str,
        regex_mode: bool = False,
        **kwargs,
    ) -> OperationResult:
        """v5.3 compatible BEFORE insertion method."""
        arguments = {
            "target_file": file_path,
            "content": content,
            "position_marker": pattern,
            "regex_mode": regex_mode,
            **kwargs,
        }

        return self.execute_v53_compatible(arguments)

    def rollback_before(self, target_file: Path) -> bool:
        """Rollback BEFORE operation by restoring original content."""
        try:
            target_str = str(target_file)

            if target_str not in self.inserted_content:
                if LOGGING_AVAILABLE and logger:
                    logger.warning(
                        f"No insertion record found for rollback: {target_file}"
                    )
                return False

            insertion_record = self.inserted_content[target_str]
            original_content = insertion_record["original_content"]

            # Restore original content
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(original_content)

            # Remove from tracking
            del self.inserted_content[target_str]

            if LOGGING_AVAILABLE and logger:
                logger.success(f"BEFORE rollback successful: restored {target_file}")
            return True

        except Exception as e:
            if LOGGING_AVAILABLE and logger:
                logger.error(f"BEFORE rollback failed: {e}")
            return False

# ========== CONVENIENCE FUNCTIONS ==========

def insert_before(
    target_file: str, pattern: str, content: str, **kwargs
) -> OperationResult:
    """Convenience function to insert content before a pattern."""
    operation = BeforeOperation()
    context = operation.prepare_context(
        target_file, content, position_marker=pattern, **kwargs
    )
    return operation.execute_with_logging(context)

def insert_before_regex(
    target_file: str, pattern: str, content: str, **kwargs
) -> OperationResult:
    """Convenience function to insert content before a regex pattern."""
    kwargs["regex_mode"] = True
    return insert_before(target_file, pattern, content, **kwargs)

# v5.3 Compatibility functions
def insert_before_v53(
    file_path: str, pattern: str, content: str, regex_mode: bool = False, **kwargs
) -> OperationResult:
    """v5.3 compatible BEFORE insertion function."""
    operation = BeforeOperation()
    return operation.insert_before_v53(
        file_path, pattern, content, regex_mode, **kwargs
    )

# FUNCIONES ENHANCED SIMPLIFICADAS - UTILIZAN SHARED_FUNCTIONS
def enhanced_before_operation(file_path: str, pattern: str, content: str, preserve_indentation: bool = True):
    """BEFORE mejorada con preservación de indentación - USA SHARED_FUNCTIONS"""
    try:
        # Leer contenido original
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        lines = original_content.split('\n')
        
        # Buscar patrón y detectar indentación - USA SHARED_FUNCTION
        for i, line in enumerate(lines):
            if pattern in line:
                if preserve_indentation:
                    # Detectar indentación del contexto - USA SHARED_FUNCTION
                    base_indent = detect_pattern_indentation(original_content, pattern)
                    # Aplicar indentación al nuevo contenido - USA SHARED_FUNCTION
                    formatted_content = apply_context_indentation(content, base_indent)
                else:
                    formatted_content = content
                
                # Insertar ANTES de la línea encontrada
                if '\n' in formatted_content:
                    new_lines = formatted_content.split('\n')
                    for j, new_line in enumerate(new_lines):
                        lines.insert(i + j, new_line)
                else:
                    lines.insert(i, formatted_content)
                break
        
        # Escribir archivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return {
            'success': True,
            'message': f"Content inserted before pattern in {file_path}",
            'file_path': file_path,
            'indentation_preserved': preserve_indentation
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'file_path': file_path
        }


def enhanced_before_operation_with_backup(file_path: str, pattern: str, content: str, auto_backup: bool = True):
    """BEFORE con backup automático integrado - USA SHARED_FUNCTIONS"""
    backup_path = None
    
    try:
        # 1. Crear backup automático - USA SHARED_FUNCTION
        if auto_backup:
            backup_path = create_automatic_backup(file_path)
        
        # 2. Ejecutar inserción mejorada
        result = enhanced_before_operation(file_path, pattern, content)
        
        if result.get('success'):
            # 3. Limpiar backups antiguos - USA SHARED_FUNCTION
            if auto_backup:
                cleanup_old_backups(file_path)
            
            # 4. Añadir info de backup al resultado
            result['backup_created'] = backup_path
            result['auto_backup'] = auto_backup
        
        return result
        
    except Exception as e:
        # 5. Rollback automático si algo falló
        if backup_path and Path(backup_path).exists():
            import shutil
            shutil.copy2(backup_path, file_path)
            return {
                'success': False,
                'error': str(e),
                'rollback_applied': True,
                'backup_restored_from': backup_path
            }
        raise e


def enhanced_before_operation_with_validation(file_path: str, pattern: str, content: str, validate: bool = True):
    """BEFORE con validación sintáctica - USA SHARED_FUNCTIONS"""
    backup_path = None
    
    try:
        # 1. Backup automático - USA SHARED_FUNCTION
        backup_path = create_automatic_backup(file_path)
        
        # 2. Ejecutar inserción con backup
        result = enhanced_before_operation_with_backup(file_path, pattern, content, auto_backup=False)
        
        if not result.get('success'):
            return result
        
        # 3. Validación sintáctica - USA SHARED_FUNCTIONS
        if validate:
            with open(file_path, 'r', encoding='utf-8') as f:
                new_content = f.read()
            
            if file_path.endswith('.py'):
                validate_python_syntax(new_content)
            elif file_path.endswith(('.js', '.ts')):
                validate_javascript_syntax(new_content)
        
        # 4. Éxito - limpiar backup - USA SHARED_FUNCTION
        cleanup_old_backups(file_path)
        
        result['validated'] = validate
        result['backup_created'] = backup_path
        
        return result
        
    except Exception as e:
        # 5. Rollback automático por error de validación
        if backup_path and Path(backup_path).exists():
            import shutil
            shutil.copy2(backup_path, file_path)
        
        return {
            'success': False,
            'error': str(e),
            'rollback_applied': True,
            'validation_failed': True
        }