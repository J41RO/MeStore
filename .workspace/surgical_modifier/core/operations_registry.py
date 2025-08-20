"""
Surgical Modifier v6.0 - Operations Registry System
Dynamic discovery and registration of operations
"""

import importlib
import inspect
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import click

class OperationMeta:
    """Metadata for an operation"""
    def __init__(self, name: str, module_path: str, class_obj: Any, category: str):
        self.name = name
        self.module_path = module_path
        self.class_obj = class_obj
        self.category = category
        self.description = getattr(class_obj, 'description', f'{name} operation')
        self.examples = getattr(class_obj, 'examples', [])

class OperationsRegistry:
    """
    Central registry for all operations with dynamic discovery
    """
    
    def __init__(self):
        self.operations: Dict[str, OperationMeta] = {}
        self.categories = {
            'basic': [],
            'advanced': [],
            'revolutionary': [],
            'ai': [],
            'collaboration': []
        }
        self.click_commands: Dict[str, click.Command] = {}
        
    def discover_operations(self) -> int:
        """
        Discover all operations in the operations directory structure
        Returns: Number of operations discovered
        """
        operations_dir = Path(__file__).parent / 'operations'
        discovered = 0
        
        # Check if operations directory exists
        if not operations_dir.exists():
            return 0
        
        for category_dir in operations_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('_'):
                continue
                
            category = category_dir.name
            discovered += self._discover_category_operations(category_dir, category)
            
        return discovered
    
    def _discover_category_operations(self, category_dir: Path, category: str) -> int:
        """Discover operations in a specific category directory"""
        discovered = 0
        
        for py_file in category_dir.glob('*.py'):
            if py_file.name.startswith('_'):
                continue
                
            operation_name = py_file.stem
            module_path = f'core.operations.{category}.{operation_name}'
            
            try:
                # Dynamic import
                module = importlib.import_module(module_path)
                
                # Look for operation class
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (hasattr(obj, 'execute') and 
                        hasattr(obj, 'name') and 
                        not name.startswith('_')):
                        
                        # Register operation
                        op_meta = OperationMeta(
                            name=getattr(obj, 'name', operation_name),
                            module_path=module_path,
                            class_obj=obj,
                            category=category
                        )
                        
                        self.operations[op_meta.name] = op_meta
                        if category in self.categories:
                            self.categories[category].append(op_meta.name)
                        discovered += 1
                        break
                        
            except ImportError:
                # Operation not implemented yet, skip silently
                continue
            except Exception as e:
                print(f"Warning: Error loading operation {operation_name}: {e}")
                
        return discovered
    
    def create_click_command(self, operation_meta: OperationMeta) -> click.Command:
        """
        Create a Click command from an operation metadata
        """
        def operation_wrapper(*args, **kwargs):
            """Wrapper function for operation execution"""
            try:
                # Create operation instance
                operation = operation_meta.class_obj()
                
                # Execute operation
                result = operation.execute(*args, **kwargs)
                
                # Log success
                print(f"✅ {operation_meta.name} completed successfully")
                return result
                
            except Exception as e:
                print(f"❌ {operation_meta.name} failed: {e}")
                raise click.ClickException(str(e))
        
        # Create Click command
        command = click.command(
            name=operation_meta.name,
            help=operation_meta.description
        )(operation_wrapper)
        
        return command
    
    def register_with_click(self, click_group: click.Group):
        """
        Register all discovered operations as Click commands
        """
        registered = 0
        
        for op_name, op_meta in self.operations.items():
            try:
                command = self.create_click_command(op_meta)
                click_group.add_command(command)
                self.click_commands[op_name] = command
                registered += 1
            except Exception as e:
                print(f"Warning: Failed to register {op_name}: {e}")
                
        return registered
    
    def get_operations_by_category(self, category: str) -> List[str]:
        """Get all operations in a specific category"""
        return self.categories.get(category, [])
    
    def get_operation_info(self, operation_name: str) -> Optional[OperationMeta]:
        """Get detailed information about an operation"""
        return self.operations.get(operation_name)
    
    def list_all_operations(self) -> Dict[str, List[str]]:
        """List all operations organized by category"""
        return {k: v for k, v in self.categories.items() if v}

# Global registry instance
operations_registry = OperationsRegistry()
