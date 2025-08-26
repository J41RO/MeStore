"""
Surgical Modifier v6.0 - BEFORE Operation (Integrated)
Insert content before a specific line/pattern with integration to existing architecture and v5.3 compatibility
"""

import os
import re
from pathlib import Path
# Imports de shared functions
from ...shared_functions.content_processor import detect_pattern_indentation, apply_context_indentation
from ...shared_functions.backup_system import create_automatic_backup, cleanup_old_backups
from ...shared_functions.syntax_validators import validate_python_syntax, validate_javascript_syntax
from typing import List, Optional
import time
import shutil

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

    Inserts content before a specific line/pattern in files, with support for:
    - Integration with existing OperationSpec system
    - v5.3 compatibility layer
    - Pattern matching with regex support
    - Multiple insertion modes
    - Content validation and processing
    - Framework-aware insertions
    - Rollback support through backup system
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


    # ========== INTEGRATION WITH EXISTING ARCHITECTURE ==========

    def _get_operation_specific_arguments(self) -> List["ArgumentSpec"]:
        """
        Define BEFORE-specific arguments for integration with registry.

        Returns:
            List of BEFORE-specific ArgumentSpec
        """
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

    # ========== OPERATION IMPLEMENTATION ==========

    def execute(self, context: OperationContext) -> OperationResult:
        """
        Execute BEFORE operation.

        Args:
            context: OperationContext with target file, pattern, and content

        Returns:
            OperationResult with insertion details
        """
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
                f"Permission denied accessing file: {target_file}",
                self.operation_type,
                str(target_file),
                {"permission_error": str(e)},
            )
        except UnicodeDecodeError as e:
            raise ContentError(
                f"Unable to decode file content: {target_file}",
                self.operation_type,
                str(target_file),
                {"encoding_error": str(e)},
            )
        except Exception as e:
            raise FileSystemError(
                f"Unexpected error during insertion: {target_file}",
                self.operation_type,
                str(target_file),
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
        """
        Perform the actual content insertion before pattern.

        Args:
            content: Original file content
            pattern: Pattern to search for
            insertion: Content to insert
            regex_mode: Use regex matching
            case_sensitive: Case sensitive matching
            first_match_only: Insert before first match only
            preserve_indentation: Preserve indentation of target line

        Returns:
            Dictionary with insertion results
        """
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
                    try:
                        content_to_insert = insertion
                    except:
                        content_to_insert = insertion

                    # Preserve indentation if requested
                    if preserve_indentation:
                        indentation = self._get_line_indentation(line)
                        content_to_insert = self._apply_indentation(
                            content_to_insert, indentation
                        )

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

    def _apply_indentation(self, content: str, indentation: str) -> str:
        """Apply indentation to content, handling multi-line content."""
        if not indentation:
            return content

        lines = content.splitlines()
        indented_lines = []

        for i, line in enumerate(lines):
            if i == 0:
                # First line gets the base indentation
                indented_lines.append(indentation + line)
            else:
                # Subsequent lines get additional indentation if not empty
                if line.strip():
                    indented_lines.append(indentation + line)
                else:
                    indented_lines.append(line)

        return "\n".join(indented_lines)

    def validate_context(self, context: OperationContext) -> List[str]:
        """
        Validate BEFORE operation context.

        Args:
            context: OperationContext to validate

        Returns:
            List of validation error messages
        """
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
        """
        BEFORE operations support rollback by restoring original content.

        Returns:
            True (BEFORE always supports rollback)
        """
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
        """
        v5.3 compatible BEFORE insertion method.

        Args:
            file_path: Path to file to modify
            pattern: Pattern to search for
            content: Content to insert before pattern
            regex_mode: Use regex matching
            **kwargs: Additional arguments

        Returns:
            OperationResult with v5.3 compatibility
        """
        arguments = {
            "target_file": file_path,
            "content": content,
            "position_marker": pattern,
            "regex_mode": regex_mode,
            **kwargs,
        }

        return self.execute_v53_compatible(arguments)

    def rollback_before(self, target_file: Path) -> bool:
        """
        Rollback BEFORE operation by restoring original content.

        Args:
            target_file: File to restore

        Returns:
            True if rollback successful, False otherwise
        """
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
    """
    Convenience function to insert content before a pattern.

    Args:
        target_file: Path to file to modify
        pattern: Pattern to search for
        content: Content to insert before pattern
        **kwargs: Additional context parameters

    Returns:
        OperationResult with insertion details
    """
    operation = BeforeOperation()
    context = operation.prepare_context(
        target_file, content, position_marker=pattern, **kwargs
    )
    return operation.execute_with_logging(context)

def insert_before_regex(
    target_file: str, pattern: str, content: str, **kwargs
) -> OperationResult:
    """
    Convenience function to insert content before a regex pattern.

    Args:
        target_file: Path to file to modify
        pattern: Regex pattern to search for
        content: Content to insert before pattern
        **kwargs: Additional context parameters

    Returns:
        OperationResult with insertion details
    """
    kwargs["regex_mode"] = True
    return insert_before(target_file, pattern, content, **kwargs)


