#!/usr/bin/env python3
"""
Update operation implementation for Surgical Modifier v6.0
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    # Fallback imports for standalone usage
    from core.operations.base_operation import (
        BaseOperation,
        OperationContext,
        OperationResult,
        OperationStatus,
        OperationType,
    )


class UpdateOperation(BaseOperation):
    """Update operation for modifying existing file content"""
    
    def __init__(self):
        super().__init__(OperationType.UPDATE, "Update existing file content")
        self.description = "Update existing content in files based on patterns"
    
    def execute(self, context: OperationContext) -> OperationResult:
        """Execute the update operation"""
        try:
            target_path = context.target_file
            pattern = context.position_marker
            content = context.content
            
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
                    message="Pattern not provided for update",
                    details={},
                    execution_time=0.0
                )
            
            if content is None:
                return OperationResult(
                    success=False,
                    operation_type=self.operation_type,
                    target_path="",
                    message="Content not provided for update",
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
                file_content = file.read()
                lines = file_content.splitlines()
            
            # Find and update matching lines
            updated_lines = []
            updates_made = 0
            
            for line in lines:
                if pattern in line:
                    # Update the line by replacing the pattern with new content
                    updated_line = line.replace(pattern, content)
                    updated_lines.append(updated_line)
                    updates_made += 1
                else:
                    updated_lines.append(line)
            
            if updates_made == 0:
                return OperationResult(
                    success=False,
                    operation_type=self.operation_type,
                    target_path="",
                    message=f"Pattern '{pattern}' not found in file '{target_path}'",
                    details={},
                    execution_time=0.0
                )
            
            # Write updated content back to file
            updated_content = '\n'.join(updated_lines)
            with open(target_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            
            return OperationResult(
                success=True,
                operation_type=self.operation_type,
                target_path=str(target_path),
                message=f"Updated {updates_made} occurrences in {target_path}",
                details={
                    'updates_made': updates_made,
                    'pattern': pattern,
                    'new_content': content,
                    'file': str(target_path)
                },
                execution_time=0.0
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                operation_type=self.operation_type,
                target_path="",
                message=f"Update operation failed: {str(e)}",
                details={},
                execution_time=0.0
            )

    def can_rollback(self) -> bool:
        """Update operations modify files, rollback supported"""
        return True
    
    def validate_context(self, context: OperationContext) -> bool:
        """Validate context for update operation"""
        return bool(context.target_file and context.position_marker and context.content is not None)