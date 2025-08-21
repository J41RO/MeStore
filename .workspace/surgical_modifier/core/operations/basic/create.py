"""
Create operation implementation for Surgical Modifier v6.0
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.escape_processor import process_content_escapes

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

# Integration imports
try:
    from utils.content_handler import content_handler
    from utils.logger import logger
    from utils.path_resolver import path_resolver

    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    logger = None
    content_handler = None
    path_resolver = None


class CreateOperation(BaseOperation):
    """Create operation for creating new files and directories"""

    def __init__(self):
        super().__init__(OperationType.CREATE)

    def validate_context(self, context: OperationContext) -> bool:
        """Validate that the context is appropriate for create operation"""
        try:
            # Check if target_path is provided
            if not context.target_file:
                return False

            # Check if target_path is valid
            from pathlib import Path

            target_path = Path(context.target_file)

            # Check if parent directory can be created/accessed
            try:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                return True
            except (OSError, PermissionError):
                return False

        except Exception:
            return False

    def can_rollback(self, context: OperationContext) -> bool:
        """Check if the create operation can be rolled back"""
        try:
            # Create operations can be rolled back by deleting the created file
            import os
            from pathlib import Path

            target_path = Path(context.target_file)

            # If file doesn't exist, rollback is not needed
            if not target_path.exists():
                return True

            # If file exists, check if we have permission to delete it
            try:
                # Test write permission on parent directory
                return os.access(target_path.parent, os.W_OK)
            except (OSError, PermissionError):
                return False

        except Exception:
            return False

    def execute(self, context: OperationContext) -> OperationResult:
        """Execute create operation"""
        try:
            target_path = Path(context.target_file)

            # Create parent directories if they don't exist
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Create the file with content
            if context.content:
                target_path.write_text(context.content, encoding="utf-8")
            else:
                target_path.touch()

            return OperationResult(
                success=True,
                operation_type=self.operation_type,
                target_path=str(target_path),
                message=f"File created successfully: {target_path}",
                details={"content_length": len(context.content or "")},
                execution_time=0.0,
            )

        except Exception as e:
            return OperationResult(
                success=False,
                operation_type=self.operation_type,
                target_path=str(context.target_file),
                message=f"Failed to create file: {str(e)}",
                details={"error": str(e)},
                execution_time=0.0,
            )


def create_operation(target_path: str, content: str = "", **kwargs) -> Dict[str, Any]:
    """Main create operation function"""
    operation = CreateOperation()
    context = OperationContext(
        project_root=Path.cwd(),
        target_file=Path(target_path),
        operation_type=OperationType.CREATE,
        content=content,
    )

    result = operation.execute(context)

    return {
        "success": result.success,
        "message": result.message,
        "details": result.details,
        "operation_type": result.operation_type.value,
        "target_path": result.target_path,
    }


def create_file(filepath: str, content: str = "") -> bool:
    """Simple file creation function"""
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Process escape characters before writing
        content = process_content_escapes(content)
        path.write_text(content, encoding="utf-8")
        return True
    except Exception:
        return False


def create_file_with_template(
    filepath: str, template: str, variables: Dict[str, str] = None
) -> bool:
    """Create file with template substitution"""
    try:
        content = template
        if variables:
            for key, value in variables.items():
                content = content.replace(f"{{{key}}}", value)

        return create_file(filepath, content)
    except Exception:
        return False


def create_file_v53(
    filepath: str, content: str = "", backup: bool = True
) -> Dict[str, Any]:
    """v5.3 compatible create function"""
    try:
        path = Path(filepath)

        # Create backup if file exists and backup is requested
        backup_created = False
        if backup and path.exists():
            backup_path = path.with_suffix(path.suffix + ".backup")
            backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            backup_created = True

        # Create the file
        path.parent.mkdir(parents=True, exist_ok=True)
        # Process escape characters before writing
        content = process_content_escapes(content)
        path.write_text(content, encoding="utf-8")

        return {
            "success": True,
            "filepath": str(path),
            "content_length": len(content),
            "backup_created": backup_created,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "filepath": filepath,
            "backup_created": False,
        }


# Export all required functions and classes
__all__ = [
    "CreateOperation",
    "create_operation",
    "create_file",
    "create_file_with_template",
    "create_file_v53",
]
