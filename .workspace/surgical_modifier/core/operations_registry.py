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

        # Discover operations in basic category
        basic_dir = operations_dir / 'basic'
        if basic_dir.exists():
            discovered += self._discover_category_operations(basic_dir, 'basic')

        # Discover operations in advanced category
        advanced_dir = operations_dir / 'advanced'
        if advanced_dir.exists():
            discovered += self._discover_category_operations(advanced_dir, 'advanced')

        return discovered

    def _discover_category_operations(self, category_dir: Path, category: str) -> int:
        """Discover operations in a specific category directory"""
        discovered = 0
        
        for py_file in category_dir.glob('*.py'):
            if py_file.name.startswith('__'):
                continue
                
            module_name = py_file.stem
            try:
                # Import the module
                module_path = f'core.operations.{category}.{module_name}'
                module = importlib.import_module(module_path)
                
                # Look for operation classes
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if name.endswith('Operation') and hasattr(obj, 'execute'):
                        operation_name = name.lower().replace('operation', '')
                        
                        # Create operation metadata
                        operation_meta = OperationMeta(
                            name=operation_name,
                            module_path=module_path,
                            class_obj=obj,
                            category=category
                        )
                        
                        # Register the operation
                        self.operations[operation_name] = operation_meta
                        self.categories[category].append(operation_name)
                        discovered += 1
                        
            except Exception as e:
                # Skip modules that can't be imported
                continue
                
        return discovered

    def get_operation(self, name: str) -> Optional[OperationMeta]:
        """Get operation metadata by name"""
        return self.operations.get(name)

    def list_operations(self) -> List[str]:
        """List all registered operation names"""
        return list(self.operations.keys())

    def get_categories(self) -> Dict[str, List[str]]:
        """Get operations organized by category"""
        return self.categories.copy()
        



# ========== INTEGRATION WITH BASEOPERATION PATTERN ==========

from typing import Type, Dict, Any, Optional, List

class BaseOperationRegistry:
    """
    Enhanced registry supporting BaseOperation pattern alongside existing system
    """

    def __init__(self):
        self.base_operations: Dict[str, 'BaseOperation'] = {}
        self.operation_specs: Dict[str, 'OperationSpec'] = {}

    def register_base_operation(self, operation: 'BaseOperation') -> None:
        """Register a BaseOperation instance"""
        operation_name = operation.operation_name
        self.base_operations[operation_name] = operation

        # Also register its OperationSpec if available
        operation_spec = operation.get_operation_spec()
        if operation_spec:
            self.operation_specs[operation_name] = operation_spec

    def get_base_operation(self, operation_name: str) -> Optional['BaseOperation']:
        """Get registered BaseOperation by name"""
        return self.base_operations.get(operation_name)

    def list_base_operations(self) -> List[str]:
        """List all registered BaseOperation names"""
        return list(self.base_operations.keys())

# Enhanced operations registry with BaseOperation support
def enhance_operations_registry(registry_instance):
    """Add BaseOperation support to existing registry"""
    registry_instance.base_registry = BaseOperationRegistry()

    def register_base_operation(operation):
        registry_instance.base_registry.register_base_operation(operation)

    def list_all_operations():
        return {
            'base_operations': registry_instance.base_registry.list_base_operations(),
            'legacy_operations': list(registry_instance.operations.keys())
        }

    def get_operation_info(name: str):
        # Check BaseOperation first
        base_op = registry_instance.base_registry.get_base_operation(name)
        if base_op:
            return {
                'type': 'base_operation',
                'name': base_op.operation_name,
                'operation_type': base_op.operation_type.value,
                'description': base_op.get_description(),
                'supports_rollback': base_op.can_rollback()
            }
        return None

    # Attach methods
    registry_instance.register_base_operation = register_base_operation
    registry_instance.list_all_operations = list_all_operations
    registry_instance.get_operation_info = get_operation_info

    # Auto-register all BaseOperations
    try:
        from .operations.basic.create import create_operation
        from .operations.basic.replace import replace_operation  
        from .operations.basic.append import append_operation

        registry_instance.register_base_operation(create_operation)
        registry_instance.register_base_operation(replace_operation)
        registry_instance.register_base_operation(append_operation)

        # Register advanced operations
        from .operations.basic.after import after_operation
        from .operations.basic.before import before_operation
        registry_instance.register_base_operation(after_operation)
        registry_instance.register_base_operation(before_operation)
    except ImportError:
        pass

    return registry_instance


# Create enhanced global instance
operations_registry = OperationsRegistry()
# Auto-discover operations when registry is created
operations_registry.discover_operations()
# enhanced_operations_registry = enhance_operations_registry(operations_registry)# [CÓDIGO DE INTEGRACIÓN QUE PROPORCIONÉ]
