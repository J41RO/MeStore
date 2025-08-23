"""
Surgical Modifier v6.0 - APPEND Operation (Integrated)
Append content to existing files with integration to existing architecture and v5.3 compatibility
"""

import os
from typing import List, Optional
from pathlib import Path
from utils.escape_processor import process_content_escapes

from ..base_operation import (
    BaseOperation, OperationType, OperationContext, OperationResult,
    ValidationError, FileSystemError, ArgumentSpec
)

try:
    from utils.logger import logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    logger = None

def append_operation(file_path: str, pattern: str, content: str, **kwargs):
    """Simple append operation function - follows standard signature (file_path, pattern, content, **kwargs)"""
    try:
        # Agregar contenido al final del archivo
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'success': True,
            'message': f'Appended content to {file_path}',
            'file_path': file_path
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'file_path': file_path
        }

class AppendOperation(BaseOperation):
    """
    APPEND operation implementation with full integration.
    
    Appends content to the end of existing files, with support for:
    - Integration with existing OperationSpec system
    - v5.3 compatibility layer
    - Automatic newline handling
    - Content validation and processing
    - Framework-aware appending
    - Rollback support through backup system
    """
    
    def __init__(self):
        super().__init__(OperationType.APPEND, "append")
        self.appended_content = {}  # Track appended content for rollback
    
    # ========== INTEGRATION WITH EXISTING ARCHITECTURE ==========
    
    def _get_operation_specific_arguments(self) -> List['ArgumentSpec']:
        """
        Define APPEND-specific arguments for integration with registry.
        
        Returns:
            List of APPEND-specific ArgumentSpec
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
                name="content",
                type=str,
                required=True,
                help="Content to append to the file",
                example="def new_function(): pass"
            ),
            ArgumentSpec(
                name="add_newline",
                type=bool,
                required=False,
                default=True,
                help="Add newline before appended content if file doesn't end with one",
                example="true"
            ),
            ArgumentSpec(
                name="separator",
                type=str,
                required=False,
                default="",
                help="Separator to add before appended content",
                example="\\n\\n# New section\\n"
            )
        ]
    
    def get_description(self) -> str:
        """Get APPEND operation description."""
        return "Append content to the end of existing files"
    
    def get_examples(self) -> List[str]:
        """Get APPEND operation examples."""
        return [
            "surgical-modifier append --target-file utils.py --content 'def helper(): pass'",
            "surgical-modifier append --target-file config.py --content 'FEATURE_FLAG = True' --separator '\\n\\n'",
            "surgical-modifier append --target-file script.js --content 'console.log(\"Done\");' --add-newline false"
        ]
    
    # ========== OPERATION IMPLEMENTATION ==========
    
    def execute(self, context: OperationContext) -> OperationResult:
        """
        Execute APPEND operation.
        
        Args:
            context: OperationContext with target file and content to append
            
        Returns:
            OperationResult with append details
        """
        try:
            target_file = context.target_file
            content = context.content or ""
            
            # Check if file exists
            if not target_file.exists():
                return OperationResult(
                    success=False,
                    operation_type=self.operation_type,
                    file_path=str(target_file),
                    message=f"Target file does not exist: {target_file}",
                    details={'file_not_found': True},
                    execution_time=0.0,
                    operation_name=self.operation_name
                )
            
            # Read current file content
            with open(target_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Get append options
            add_newline = context.arguments.get('add_newline', True) if context.arguments else True
            separator = context.arguments.get('separator', '') if context.arguments else ''
            
            # Prepare content to append
            content_to_append = self._prepare_append_content(
                original_content, content, add_newline, separator
            )
            
            # Create new content
            new_content = original_content + content_to_append
            
            # Write updated content to file
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Track appended content for potential rollback
            self.appended_content[str(target_file)] = {
                'original_content': original_content,
                'appended_content': content_to_append,
                'append_length': len(content_to_append)
            }
            
            return OperationResult(
                success=True,
                operation_type=self.operation_type,
                file_path=str(target_file),
                message=f"Successfully appended {len(content_to_append)} characters to {target_file}",
                details={
                    'content_appended': content,
                    'separator_used': separator,
                    'newline_added': add_newline,
                    'original_length': len(original_content),
                    'new_length': len(new_content),
                    'appended_length': len(content_to_append)
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
            raise FileSystemError(
                f"Unable to decode file content: {target_file}",
                self.operation_type,
                str(target_file),
                {'encoding_error': str(e)}
            )
        except Exception as e:
            raise FileSystemError(
                f"Unexpected error during append: {target_file}",
                self.operation_type,
                str(target_file),
                {'unexpected_error': str(e)}
            )
    
    def _process_escape_characters(self, content: str) -> str:
        """
        Process escape characters in content to convert them to actual characters.
        
        Args:
            content: Content that may contain escape sequences
            
        Returns:
            Content with escape sequences converted to actual characters
        """
        if not content:
            return content
            
        # Replace common escape sequences - using raw strings to avoid issues
        processed_content = content.replace('\\n', '\n')   # \n -> actual newline
        processed_content = processed_content.replace('\\t', '\t')   # \t -> actual tab  
        processed_content = processed_content.replace('\\r', '\r')   # \r -> carriage return
        processed_content = processed_content.replace('\\\\', '\\')  # \\ -> single backslash
        
        return processed_content

    def _prepare_append_content(self, original_content: str, content: str, 
                              add_newline: bool, separator: str) -> str:
        """
        Prepare content to be appended with proper formatting.
        
        Args:
            original_content: Current file content
            content: Content to append
            add_newline: Whether to add newline if file doesn't end with one
            separator: Separator to add before content
            
        Returns:
            Formatted content ready to append
        """
        result = ""
        
        # Add newline if file doesn't end with one and add_newline is True
        if add_newline and original_content and not original_content.endswith('\n'):
            result += '\n'
        
        # Add separator if specified
        if separator:
            result += separator
        
        # Add the actual content (with escape processing)
        try:
            processed_content = process_content_escapes(content)
        except:
            processed_content = content
        result += processed_content
        
        return result
    
    def validate_context(self, context: OperationContext) -> List[str]:
        """
        Validate APPEND operation context.
        
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
        
        # Validate content
        if not context.content:
            errors.append("Content to append is required")
        
        # Validate content encoding
        if hasattr(context, 'validate_content') and context.validate_content and context.content:
            try:
                context.content.encode('utf-8')
            except UnicodeEncodeError:
                errors.append("Content contains characters that cannot be encoded in UTF-8")
        
        return errors
    
    def can_rollback(self) -> bool:
        """
        APPEND operations support rollback by restoring original content.
        
        Returns:
            True (APPEND always supports rollback)
        """
        return True
    
    # ========== v5.3 COMPATIBILITY METHODS ==========
    
    def append_content_v53(self, file_path: str, content: str, 
                          add_newline: bool = True, **kwargs) -> OperationResult:
        """
        v5.3 compatible APPEND content method.
        
        Args:
            file_path: Path to file to modify
            content: Content to append
            add_newline: Add newline before content if needed
            **kwargs: Additional arguments
            
        Returns:
            OperationResult with v5.3 compatibility
        """
        arguments = {
            'target_file': file_path,
            'content': content,
            'add_newline': add_newline,
            **kwargs
        }
        
        return self.execute_v53_compatible(arguments)
    
    def rollback_append(self, target_file: Path) -> bool:
        """
        Rollback APPEND operation by restoring original content.
        
        Args:
            target_file: File to restore
            
        Returns:
            True if rollback successful, False otherwise
        """
        try:
            target_str = str(target_file)
            
            if target_str not in self.appended_content:
                if LOGGING_AVAILABLE and logger:
                    logger.warning(f"No append record found for rollback: {target_file}")
                return False
            
            append_record = self.appended_content[target_str]
            original_content = append_record['original_content']
            
            # Restore original content
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Remove from tracking
            del self.appended_content[target_str]
            
            if LOGGING_AVAILABLE and logger:
                logger.success(f"APPEND rollback successful: restored {target_file}")
            return True
                
        except Exception as e:
            if LOGGING_AVAILABLE and logger:
                logger.error(f"APPEND rollback failed: {e}")
            return False

# ========== CONVENIENCE FUNCTIONS ==========

def append_content(target_file: str, content: str, **kwargs) -> OperationResult:
    """
    Convenience function to append content to a file.
    
    Args:
        target_file: Path to file to modify
        content: Content to append
        **kwargs: Additional context parameters
        
    Returns:
        OperationResult with append details
    """
    operation = AppendOperation()
    context = operation.prepare_context(target_file, content, **kwargs)
    return operation.execute_with_logging(context)

def append_with_separator(target_file: str, content: str, separator: str = "\n\n", **kwargs) -> OperationResult:
    """
    Convenience function to append content with a separator.
    
    Args:
        target_file: Path to file to modify
        content: Content to append
        separator: Separator to add before content
        **kwargs: Additional context parameters
        
    Returns:
        OperationResult with append details
    """
    kwargs['separator'] = separator
    return append_content(target_file, content, **kwargs)

# v5.3 Compatibility functions
def append_content_v53(file_path: str, content: str, 
                      add_newline: bool = True, **kwargs) -> OperationResult:
    """
    v5.3 compatible APPEND content function.
    
    Args:
        file_path: Path to file to modify
        content: Content to append
        add_newline: Add newline before content if needed
        **kwargs: Additional arguments
        
    Returns:
        OperationResult with v5.3 compatibility
    """
    operation = AppendOperation()
    return operation.append_content_v53(file_path, content, add_newline, **kwargs)
# Alias for consistency
execute = append_operation