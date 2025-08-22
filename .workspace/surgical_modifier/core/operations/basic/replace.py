"""
Surgical Modifier v6.0 - REPLACE Operation (Integrated)
Replace content in existing files with integration to existing architecture and v5.3 compatibility
"""

import os
import re
from typing import List, Optional
from pathlib import Path

from ..base_operation import (
    BaseOperation, OperationType, OperationContext, OperationResult,
    ValidationError, FileSystemError, ContentError, ArgumentSpec
)

try:
    from utils.logger import logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    logger = None

def replace_operation(file_path: str, pattern: str, content: str, **kwargs):
    """Simple replace operation function - no classes"""
    try:
        # Leer archivo
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Realizar reemplazo
        if pattern in content:
            new_content = content.replace(pattern, replacement)

            # Escribir archivo modificado
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return {
                'success': True,
                'message': f'Replaced pattern in {target_path}',
                'target_path': target_path
            }
        else:
            return {
                'success': False,
                'error': f'Pattern not found in {target_path}',
                'target_path': target_path
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'target_path': target_path
        }

class ReplaceOperation(BaseOperation):
    """
    REPLACE operation implementation with full integration.
    
    Replaces existing content in files with new content, with support for:
    - Integration with existing OperationSpec system
    - v5.3 compatibility layer
    - Pattern matching with regex support
    - Content validation and processing
    - Framework-aware replacements
    - Rollback support through backup system
    """
    
    def __init__(self):
        super().__init__(OperationType.REPLACE, "replace")
        self.replaced_patterns = {}  # Track replaced content for rollback
    
    # ========== INTEGRATION WITH EXISTING ARCHITECTURE ==========
    
    def _get_operation_specific_arguments(self) -> List['ArgumentSpec']:
        """
        Define REPLACE-specific arguments for integration with registry.
        
        Returns:
            List of REPLACE-specific ArgumentSpec
        """
        if not hasattr(self, '_ArgumentSpec_available'):
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
                help="Pattern to search for and replace",
                example="def old_function"
            ),
            ArgumentSpec(
                name="replacement",
                type=str,
                required=True,
                help="Content to replace the pattern with",
                example="def new_function"
            ),
            ArgumentSpec(
                name="regex_mode",
                type=bool,
                required=False,
                default=False,
                help="Use regex pattern matching",
                example="false"
            ),
            ArgumentSpec(
                name="case_sensitive",
                type=bool,
                required=False,
                default=True,
                help="Case sensitive pattern matching",
                example="true"
            ),
            ArgumentSpec(
                name="max_replacements",
                type=int,
                required=False,
                default=-1,
                help="Maximum number of replacements (-1 for all)",
                example="1"
            )
        ]
    
    def get_description(self) -> str:
        """Get REPLACE operation description."""
        return "Replace existing content in files with new content"
    
    def get_examples(self) -> List[str]:
        """Get REPLACE operation examples."""
        return [
            "surgical-modifier replace --target-file models.py --pattern 'old_function' --replacement 'new_function'",
            "surgical-modifier replace --target-file config.py --pattern 'DEBUG = False' --replacement 'DEBUG = True'",
            "surgical-modifier replace --target-file app.js --pattern 'function.*calculate' --replacement 'function newCalculate' --regex-mode"
        ]
    
    # ========== OPERATION IMPLEMENTATION ==========
    
    def execute(self, context: OperationContext) -> OperationResult:
        """
        Execute REPLACE operation.
        
        Args:
            context: OperationContext with target file, pattern, and replacement
            
        Returns:
            OperationResult with replacement details
        """
        try:
            target_file = context.target_file
            pattern = context.arguments.get('pattern', context.position_marker) if context.arguments else context.position_marker
            replacement = context.content or ""
            
            # Validate inputs
            if not pattern:
                return OperationResult(
                    success=False,
                    operation_type=self.operation_type,
                    target_path=str(target_file),
                    message="Pattern is required for REPLACE operation",
                    details={'missing_pattern': True},
                    execution_time=0.0,
                    operation_name=self.operation_name
                )
            
            # Check if file exists
            if not target_file.exists():
                return OperationResult(
                    success=False,
                    operation_type=self.operation_type,
                    target_path=str(target_file),
                    message=f"Target file does not exist: {target_file}",
                    details={'file_not_found': True},
                    execution_time=0.0,
                    operation_name=self.operation_name
                )
            
            # Read current file content
            with open(target_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Get replacement options
            regex_mode = context.arguments.get('regex_mode', False) if context.arguments else False
            case_sensitive = context.arguments.get('case_sensitive', True) if context.arguments else True
            max_replacements = context.arguments.get('max_replacements', -1) if context.arguments else -1
            
            # Perform replacement
            replacement_result = self._perform_replacement(
                original_content, pattern, replacement, 
                regex_mode, case_sensitive, max_replacements
            )
            
            if not replacement_result['success']:
                return OperationResult(
                    success=False,
                    operation_type=self.operation_type,
                    target_path=str(target_file),
                    message=replacement_result['message'],
                    details=replacement_result['details'],
                    execution_time=0.0,
                    operation_name=self.operation_name
                )
            
            new_content = replacement_result['new_content']
            replacements_made = replacement_result['replacements_made']
            
            # Write updated content to file
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Track replacement for potential rollback
            self.replaced_patterns[str(target_file)] = {
                'original_content': original_content,
                'pattern': pattern,
                'replacement': replacement,
                'replacements_made': replacements_made
            }
            
            return OperationResult(
                success=True,
                operation_type=self.operation_type,
                target_path=str(target_file),
                message=f"Successfully replaced {replacements_made} occurrence(s) in {target_file}",
                details={
                    'pattern': pattern,
                    'replacement': replacement,
                    'replacements_made': replacements_made,
                    'regex_mode': regex_mode,
                    'case_sensitive': case_sensitive,
                    'original_length': len(original_content),
                    'new_length': len(new_content)
                },
                execution_time=0.0,  # Will be set by base class
                content_processed=new_content,
                operation_name=self.operation_name
            )
            
        except PermissionError as e:
            raise FileSystemError(
                f"Permission denied accessing file: {target_file}",
                self.operation_type,
                str(target_file),
                {'permission_error': str(e)}
            )
        except UnicodeDecodeError as e:
            raise ContentError(
                f"Unable to decode file content: {target_file}",
                self.operation_type,
                str(target_file),
                {'encoding_error': str(e)}
            )
        except Exception as e:
            raise FileSystemError(
                f"Unexpected error during replacement: {target_file}",
                self.operation_type,
                str(target_file),
                {'unexpected_error': str(e)}
            )
    
    def _perform_replacement(self, content: str, pattern: str, replacement: str,
                           regex_mode: bool, case_sensitive: bool, max_replacements: int) -> dict:
        """
        Perform the actual content replacement.
        
        Args:
            content: Original file content
            pattern: Pattern to search for
            replacement: Replacement content
            regex_mode: Use regex matching
            case_sensitive: Case sensitive matching
            max_replacements: Maximum replacements to make
            
        Returns:
            Dictionary with replacement results
        """
        try:
            if regex_mode:
                # Use regex replacement
                flags = 0 if case_sensitive else re.IGNORECASE
                if max_replacements == -1:
                    new_content = re.sub(pattern, replacement, content, flags=flags)
                    # Count replacements by comparing with original
                    replacements_made = len(re.findall(pattern, content, flags=flags))
                else:
                    new_content = re.sub(pattern, replacement, content, count=max_replacements, flags=flags)
                    replacements_made = min(max_replacements, len(re.findall(pattern, content, flags=flags)))
            else:
                # Use string replacement
                search_pattern = pattern if case_sensitive else pattern.lower()
                search_content = content if case_sensitive else content.lower()
                
                # Count occurrences
                occurrences = search_content.count(search_pattern)
                
                if occurrences == 0:
                    return {
                        'success': False,
                        'message': f"Pattern not found: '{pattern}'",
                        'details': {'pattern_not_found': True, 'pattern': pattern}
                    }
                
                # Perform replacement
                if max_replacements == -1:
                    new_content = content.replace(pattern, replacement)
                    replacements_made = occurrences
                else:
                    new_content = content.replace(pattern, replacement, max_replacements)
                    replacements_made = min(max_replacements, occurrences)
            
            return {
                'success': True,
                'new_content': new_content,
                'replacements_made': replacements_made,
                'details': {
                    'pattern': pattern,
                    'replacement': replacement,
                    'regex_mode': regex_mode,
                    'case_sensitive': case_sensitive
                }
            }
            
        except re.error as e:
            return {
                'success': False,
                'message': f"Invalid regex pattern: {e}",
                'details': {'regex_error': str(e), 'pattern': pattern}
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Replacement failed: {e}",
                'details': {'replacement_error': str(e)}
            }
    
    def validate_context(self, context: OperationContext) -> List[str]:
        """
        Validate REPLACE operation context.
        
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
        pattern = context.arguments.get('pattern', context.position_marker) if context.arguments else context.position_marker
        if not pattern:
            errors.append("Pattern is required for REPLACE operation")
        
        # Validate replacement content
        if context.content is None:
            errors.append("Replacement content is required")
        
        # Validate regex pattern if regex mode is enabled
        regex_mode = context.arguments.get('regex_mode', False) if context.arguments else False
        if regex_mode and pattern:
            try:
                re.compile(pattern)
            except re.error as e:
                errors.append(f"Invalid regex pattern '{pattern}': {e}")
        
        return errors
    
    def can_rollback(self) -> bool:
        """
        REPLACE operations support rollback by restoring original content.
        
        Returns:
            True (REPLACE always supports rollback)
        """
        return True
    
    # ========== v5.3 COMPATIBILITY METHODS ==========
    
    def replace_content_v53(self, file_path: str, pattern: str, replacement: str, 
                           regex_mode: bool = False, **kwargs) -> OperationResult:
        """
        v5.3 compatible REPLACE content method.
        
        Args:
            file_path: Path to file to modify
            pattern: Pattern to search for
            replacement: Content to replace with
            regex_mode: Use regex matching
            **kwargs: Additional arguments
            
        Returns:
            OperationResult with v5.3 compatibility
        """
        arguments = {
            'target_file': file_path,
            'content': replacement,
            'position_marker': pattern,
            'regex_mode': regex_mode,
            **kwargs
        }
        
        return self.execute_v53_compatible(arguments)
    
    def rollback_replace(self, target_file: Path) -> bool:
        """
        Rollback REPLACE operation by restoring original content.
        
        Args:
            target_file: File to restore
            
        Returns:
            True if rollback successful, False otherwise
        """
        try:
            target_str = str(target_file)
            
            if target_str not in self.replaced_patterns:
                if LOGGING_AVAILABLE and logger:
                    logger.warning(f"No replacement record found for rollback: {target_file}")
                return False
            
            replacement_record = self.replaced_patterns[target_str]
            original_content = replacement_record['original_content']
            
            # Restore original content
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Remove from tracking
            del self.replaced_patterns[target_str]
            
            if LOGGING_AVAILABLE and logger:
                logger.success(f"REPLACE rollback successful: restored {target_file}")
            return True
                
        except Exception as e:
            if LOGGING_AVAILABLE and logger:
                logger.error(f"REPLACE rollback failed: {e}")
            return False

# ========== CONVENIENCE FUNCTIONS ==========

def replace_content(target_file: str, pattern: str, replacement: str, **kwargs) -> OperationResult:
    """
    Convenience function to replace content in a file.
    
    Args:
        target_file: Path to file to modify
        pattern: Pattern to search for
        replacement: Content to replace with
        **kwargs: Additional context parameters
        
    Returns:
        OperationResult with replacement details
    """
    operation = ReplaceOperation()
    context = operation.prepare_context(
        target_file, replacement, 
        position_marker=pattern, 
        **kwargs
    )
    return operation.execute_with_logging(context)

def replace_content_regex(target_file: str, pattern: str, replacement: str, **kwargs) -> OperationResult:
    """
    Convenience function to replace content using regex.
    
    Args:
        target_file: Path to file to modify
        pattern: Regex pattern to search for
        replacement: Content to replace with
        **kwargs: Additional context parameters
        
    Returns:
        OperationResult with replacement details
    """
    kwargs['regex_mode'] = True
    return replace_content(target_file, pattern, replacement, **kwargs)

# v5.3 Compatibility functions
def replace_content_v53(file_path: str, pattern: str, replacement: str, 
                       regex_mode: bool = False, **kwargs) -> OperationResult:
    """
    v5.3 compatible REPLACE content function.
    
    Args:
        file_path: Path to file to modify
        pattern: Pattern to search for
        replacement: Content to replace with
        regex_mode: Use regex matching
        **kwargs: Additional arguments
        
    Returns:
        OperationResult with v5.3 compatibility
    """
    operation = ReplaceOperation()
    return operation.replace_content_v53(file_path, pattern, replacement, regex_mode, **kwargs)
# Alias for consistency
execute = replace_operation
