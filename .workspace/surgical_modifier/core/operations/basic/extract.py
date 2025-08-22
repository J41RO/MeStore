#!/usr/bin/env python3
"""
Basic extraction utilities for Surgical Modifier v6.0

This module contains utility functions for extracting and processing
code patterns that are commonly used across different operations.

Functions:
    extract_line_indentation: Extract indentation from a line
    apply_indentation_to_content: Apply indentation to multi-line content
    extract_v53_arguments: Extract common arguments from v5.3 format
"""

from pathlib import Path
from typing import List, Dict, Any, Optional

# Import from parent operations
try:
    from ..base_operation import (
        BaseOperation,
        OperationContext,
        OperationResult,
        OperationStatus,
        OperationType,
    )
except ImportError:
    from core.operations.base_operation import (
        BaseOperation,
        OperationContext,
        OperationResult,
        OperationStatus,
        OperationType, 
    )

# Module version and metadata
__version__ = "1.0.0"
__author__ = "Surgical Modifier Team"


def extract_line_indentation(line: str) -> str:
    """
    Extract indentation from a line.
    
    Args:
        line (str): The line from which to extract indentation
        
    Returns:
        str: The indentation string (spaces/tabs at the beginning)
        
    Examples:
        >>> extract_line_indentation("    hello world")
        "    "
        >>> extract_line_indentation("\t\tdef function():")
        "\t\t"
        >>> extract_line_indentation("no_indent")
        ""
    """
    if not isinstance(line, str):
        raise ValueError("Input must be a string")
    return line[:len(line) - len(line.lstrip())]


def apply_indentation_to_content(content: str, indentation: str) -> str:
    """
    Apply indentation to content, handling multi-line content.

    Args:
        content (str): The content to indent
        indentation (str): The indentation string to apply

    Returns:
        str: The indented content

    Examples:
        >>> apply_indentation_to_content('line1\\nline2', '  ')
        '  line1\\n  line2'
        >>> apply_indentation_to_content('single', '    ')
        '    single'
        >>> apply_indentation_to_content('line1\\n\\nline3', '\\t')
        '\\tline1\\n\\n\\tline3'
    """
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
    return '\\n'.join(indented_lines)


class ExtractOperation(BaseOperation):
    """Extract operation for pattern extraction and analysis"""
    
    def __init__(self):
        super().__init__(OperationType.EXTRACT, "Extract patterns and code blocks")
        self.description = "Extract patterns, functions, or code blocks from files"
    
    def execute(self, context: OperationContext) -> OperationResult:
        """Execute the extract operation"""
        try:
            target_path = context.target_file
            pattern = context.position_marker
            
            # Validate inputs
            if not target_path:
                return OperationResult(
                    success=False,
                    operation_type=self.operation_type,
                    target_path="",
                    message="Target file path not provided",
                    details={},
                    execution_time=0.0
                )
            
            if not pattern:
                return OperationResult(
                    success=False,
                    operation_type=self.operation_type,
                    target_path="",
                    message="Pattern not provided for extraction",
                    details={},
                    execution_time=0.0
                )
            
            # Check if file exists
            if not Path(target_path).exists():
                return OperationResult(
                    success=False,
                    operation_type=self.operation_type,
                    target_path="",
                    message=f"Target file '{target_path}' does not exist",
                    details={},
                    execution_time=0.0
                )
            
            # Read file content
            with open(target_path, 'r', encoding='utf-8') as file:
                content = file.read()
                lines = content.splitlines()
            
            # Extract matching lines/patterns
            extracted_lines = []
            for i, line in enumerate(lines, 1):
                if pattern in line:
                    extracted_lines.append({
                        'line_number': i,
                        'content': line.strip(),
                        'indentation': extract_line_indentation(line)
                    })
            
            return OperationResult(
                success=True,
                operation_type=self.operation_type,
                target_path=str(target_path),
                message=f"Extracted {len(extracted_lines)} matches from {target_path}",
                details={
                    'extracted_lines': extracted_lines,
                    'total_matches': len(extracted_lines),
                    'pattern': pattern,
                    'file': str(target_path)
                },
                execution_time=0.0
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                operation_type=self.operation_type,
                target_path="",
                message=f"Extract operation failed: {str(e)}",
                details={},
                execution_time=0.0
            )

    def can_rollback(self) -> bool:
        """Extract operations are read-only, no rollback needed"""
        return False
    
    def validate_context(self, context: OperationContext) -> bool:
        """Validate context for extract operation"""
        return bool(context.target_file and context.position_marker)

def extract_operation(file_path, pattern, content, **kwargs):
    """
    Simple wrapper function for extraction operations.
    Follows standard signature: (file_path, pattern, content, **kwargs)
    
    Args:
        file_path: Path to the file to operate on
        pattern: Pattern to search for extraction
        content: Content parameter (for consistency with standard signature)
        **kwargs: Additional options
    
    Returns:
        Extracted content or operation result
    """
    # Implementation using existing ExtractOperation class
    from pathlib import Path
    operation = ExtractOperation()
    return operation.execute(Path(file_path), pattern, **kwargs)

# Alias for consistency
execute = extract_operation