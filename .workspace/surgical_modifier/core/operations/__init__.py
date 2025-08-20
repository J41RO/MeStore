"""
Surgical Modifier v6.0 - Operations Module (Integrated)
Modular operation implementations with existing architecture integration
"""

from .base_operation import (
    BaseOperation, OperationType, OperationStatus,
    OperationResult, OperationContext,
    OperationError, ValidationError, ContentError, FileSystemError
)

from .basic import (
    CreateOperation, create_operation,
    create_file, create_file_with_template, create_file_v53,
    ReplaceOperation, replace_operation,
    replace_content, replace_content_regex, replace_content_v53,
    AppendOperation, append_operation,
    append_content, append_with_separator, append_content_v53
)

__all__ = [
    # Base classes
    'BaseOperation', 'OperationType', 'OperationStatus',
    'OperationResult', 'OperationContext',
    'OperationError', 'ValidationError', 'ContentError', 'FileSystemError',
    
    # Basic operations
    'CreateOperation', 'create_operation',
    'create_file', 'create_file_with_template', 'create_file_v53',
    'ReplaceOperation', 'replace_operation',
    'replace_content', 'replace_content_regex', 'replace_content_v53',
    'AppendOperation', 'append_operation',
    'append_content', 'append_with_separator', 'append_content_v53'
]

