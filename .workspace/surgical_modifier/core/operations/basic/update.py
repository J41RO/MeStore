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
    def _detect_format_simple(self, file_path: str) -> str:
        """Simple format detection"""
        if file_path.endswith('.json'):
            return 'json'
        elif file_path.endswith(('.yaml', '.yml')):
            return 'yaml'
        elif file_path.endswith('.py'):
            return 'python'
        else:
            return 'text'
    
    def _update_json_simple(self, lines: list, pattern: str, content: str) -> tuple:
        """Simple JSON update with type preservation"""
        updated_lines = []
        updates_made = 0
        for line in lines:
            if pattern in line:
                # For JSON with numeric values, remove quotes from replacement
                if ':' in pattern and ':' in content:
                    pattern_val = pattern.split(':')[1].strip()
                    content_val = content.split(':')[1].strip()
                    
                    # If original was numeric, keep new value numeric
                    if pattern_val.isdigit():
                        clean_val = content_val.strip('"').strip("'")
                        if clean_val.isdigit():
                            final_content = pattern.split(':')[0] + ': ' + clean_val
                        else:
                            final_content = content
                    else:
                        final_content = content
                else:
                    final_content = content
                    
                updated_line = line.replace(pattern, final_content)
                updated_lines.append(updated_line)
                updates_made += 1
            else:
                updated_lines.append(line)
        return updated_lines, updates_made

    def _detect_format(self, file_path: str) -> str:
        """Detect file format based on extension and content"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == '.json':
            return 'json'
        elif ext in ['.yaml', '.yml']:
            return 'yaml'
        elif ext == '.py':
            return 'python'
        else:
            # Try to detect by content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content.startswith(('{', '[')):
                        return 'json'
                    elif any(line.strip().endswith(':') for line in content.split('\n')[:10]):
                        return 'yaml'
                    else:
                        return 'text'
            except:
                return 'text'

    def _validate_type_consistency(self, original_value: str, new_value: str) -> str:
        """Validate and convert types to maintain consistency"""
        # Extract actual values
        orig_clean = original_value.strip()
        new_clean = new_value.strip().strip('"').strip("'")
        
        # For numeric values (detect by content)
        if orig_clean.isdigit():
            try:
                return str(int(new_clean))
            except ValueError:
                return new_value
                
        # For boolean values
        if orig_clean.lower() in ['true', 'false']:
            if new_clean.lower() in ['true', 'false']:
                return new_clean.lower()
            return new_value
            
        # For float values
        try:
            float(orig_clean)
            try:
                return str(float(new_clean))
            except ValueError:
                return new_value
        except ValueError:
            pass
        
        return new_value

    def _parse_with_preservation(self, file_path: str, pattern: str, new_content: str) -> tuple:
        """Parse file preserving comments and formatting"""
        format_type = self._detect_format(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
            lines = [line + '\n' for line in file_content.splitlines()]
        
        if format_type == 'json':
            return self._update_json_with_types(lines, pattern, new_content)
        else:
            # Default processing
            updated_lines = []
            updates_made = 0
            for line in lines:
                if pattern in line:
                    updated_line = line.replace(pattern, new_content)
                    updated_lines.append(updated_line)
                    updates_made += 1
                else:
                    updated_lines.append(line)
            return updated_lines, updates_made

    def _update_json_with_types(self, lines: list, pattern: str, content: str) -> tuple:
        """Update JSON with automatic type validation and conversion"""
        updated_lines = []
        updates_made = 0
        
        for line in lines:
            if pattern in line:
                # For JSON patterns with key:value structure
                if ':' in pattern and ':' in content:
                    # Extract original and new values
                    pattern_parts = pattern.split(':')
                    content_parts = content.split(':')
                    
                    if len(pattern_parts) >= 2 and len(content_parts) >= 2:
                        original_val = pattern_parts[1].strip()
                        new_val = content_parts[1].strip()
                        
                        # Apply type validation - remove quotes from both values
                        original_clean = original_val.strip().strip('"').strip("'")
                        new_clean = new_val.strip().strip('"').strip("'")
                        
                        validated_val = self._validate_type_consistency(original_clean, new_clean)
                        
                        # Reconstruct the pattern with validated value (no quotes for numbers)
                        key_part = pattern_parts[0]
                        validated_pattern = key_part + ': ' + validated_val
                        
                        updated_line = line.replace(pattern, validated_pattern)
                    else:
                        updated_line = line.replace(pattern, content)
                else:
                    updated_line = line.replace(pattern, content)
                    
                updated_lines.append(updated_line)
                updates_made += 1
            else:
                updated_lines.append(line)
                
        return updated_lines, updates_made
    
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

def update_operation(file_path, pattern, content, **kwargs):
    """
    Simple wrapper function for update operations.
    Follows standard signature: (file_path, pattern, content, **kwargs)
    
    Args:
        file_path: Path to the file to operate on
        pattern: Pattern to search for update
        content: New content to update with
        **kwargs: Additional options
    
    Returns:
        Update operation result
    """
    # Implementation using existing UpdateOperation class
    from pathlib import Path
    operation = UpdateOperation()
    return operation.execute(Path(file_path), pattern, content, **kwargs)

# Alias for consistency
execute = update_operation