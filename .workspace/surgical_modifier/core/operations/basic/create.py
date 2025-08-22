#!/usr/bin/env python3
"""
Create operation implementation for Surgical Modifier v6.0
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
        super().__init__(OperationType.CREATE, "Create files and directories")
        
    def execute(self, context: OperationContext) -> OperationResult:
        """Execute the create operation"""
        try:
            target_path = context.target_file
            
            # Validate target path
            if not target_path:
                return OperationResult(
                    success=False,
                    operation_type=self.operation_type,
                    error="Target file path not provided",
                    target_path=""
                )
            
            # Create parent directories if they don't exist
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create the file with content
            if context.content:
                # Use ContentHandler v5.3 for proper escape processing
                from utils.content_handler import create_content_handler
                handler = create_content_handler(context.content, str(target_path), "create")
                processed_content, temp_file = handler.get_safe_content()
                target_path.write_text(processed_content, encoding="utf-8")
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
                error=f"Create operation failed: {str(e)}",
                target_path=str(context.target_file) if context.target_file else "",
                details={"error": str(e)},
                execution_time=0.0,
            )

def create_operation(file_path: str, pattern: str, content: str = "", **kwargs) -> Dict[str, Any]:

    """Simple create operation function - no classes"""
    try:
        # Crear directorio padre si no existe
        parent_dir = os.path.dirname(file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        # Escribir contenido al archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'success': True, 
            'message': f'File {file_path} created successfully',
            'target_path': file_path,
            'content_length': len(content)
        }
    except Exception as e:
        return {
            'success': False, 
            'error': str(e),
            'target_path': target_path
        }

def create_file(filepath: str, content: str = "") -> bool:
    """Simple file creation function"""
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use ContentHandler v5.3 for proper escape processing
        try:
            from utils.content_handler import create_content_handler
            handler = create_content_handler(content, filepath, "create")
            processed_content, temp_file = handler.get_safe_content()
            path.write_text(processed_content, encoding="utf-8")
        except ImportError:
            # Fallback si content_handler no está disponible
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
        backup_created = False
        
        # Create backup if file exists and backup is requested
        if backup and path.exists():
            backup_path = Path(f"{filepath}.backup")
            backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            backup_created = True
        
        # Create the file
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use ContentHandler v5.3 for proper escape processing
        try:
            from utils.content_handler import create_content_handler
            handler = create_content_handler(content, str(path), "create")
            processed_content, temp_file = handler.get_safe_content()
            path.write_text(processed_content, encoding="utf-8")
        except ImportError:
            # Fallback si content_handler no está disponible
            path.write_text(content, encoding="utf-8")
            processed_content = content
        
        return {
            "success": True,
            "filepath": str(path),
            "content_length": len(processed_content),
            "backup_created": backup_created,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "filepath": filepath,
        }
# Alias for consistency
execute = create_operation