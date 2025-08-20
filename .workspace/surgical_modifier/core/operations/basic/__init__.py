"""
Surgical Modifier v6.0 - Basic Operations (Integrated)
Basic file operations with full integration and v5.3 compatibility
"""

from .create import (
    CreateOperation, create_operation, 
    create_file, create_file_with_template, create_file_v53
)
from .replace import (
    ReplaceOperation, replace_operation,
    replace_content, replace_content_regex, replace_content_v53
)
from .append import (
    AppendOperation, append_operation,
    append_content, append_with_separator, append_content_v53
)

__all__ = [
    # CREATE operations
    'CreateOperation', 'create_operation', 
    'create_file', 'create_file_with_template', 'create_file_v53',

    # REPLACE operations
    'ReplaceOperation', 'replace_operation',
    'replace_content', 'replace_content_regex', 'replace_content_v53',

    # APPEND operations
    'AppendOperation', 'append_operation',
    'append_content', 'append_with_separator', 'append_content_v53'
]

