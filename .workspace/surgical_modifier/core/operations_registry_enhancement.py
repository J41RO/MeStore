"""
Enhanced Operations Registry - Correction for missing _auto_discover_operations
"""

from typing import Type, Dict, Any, Optional, List
from .operations.base_operation import BaseOperation, OperationType

class BaseOperationRegistry:
    """
    Enhanced registry supporting BaseOperation pattern alongside existing system
    """
    
    def __init__(self):
        self.base_operations: Dict[str, BaseOperation] = {}
        self.operation_specs: Dict[str, 'OperationSpec'] = {}
    
    def register_base_operation(self, operation: BaseOperation) -> None:
        """
        Register a BaseOperation instance.
        
        Args:
            operation: BaseOperation instance to register
        """
        operation_name = operation.operation_name
        self.base_operations[operation_name] = operation
        
        # Also register its OperationSpec if available
        operation_spec = operation.get_operation_spec()
        if operation_spec:
            self.operation_specs[operation_name] = operation_spec
        
        # Log registration
        try:
            from utils.logger import logger
            logger.info(f"Registered BaseOperation: {operation_name}")
        except ImportError:
            pass
    
    def get_base_operation(self, operation_name: str) -> Optional[BaseOperation]:
        """
        Get registered BaseOperation by name.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            BaseOperation instance or None if not found
        """
        return self.base_operations.get(operation_name)
    
    def execute_base_operation(self, operation_name: str, 
                             arguments: Dict[str, Any]) -> Optional['OperationResult']:
        """
        Execute a registered BaseOperation with v5.3 compatible arguments.
        
        Args:
            operation_name: Name of the operation to execute
            arguments: Arguments dictionary (v5.3 format)
            
        Returns:
            OperationResult or None if operation not found
        """
        operation = self.get_base_operation(operation_name)
        if not operation:
            return None
        
        return operation.execute_v53_compatible(arguments)
    
    def list_base_operations(self) -> List[str]:
        """
        List all registered BaseOperation names.
        
        Returns:
            List of operation names
        """
        return list(self.base_operations.keys())
    
    def get_operation_statistics(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a BaseOperation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Statistics dictionary or None if operation not found
        """
        operation = self.get_base_operation(operation_name)
        if not operation:
            return None
        
        return operation.get_statistics()

# Enhanced operations registry with corrected initialization
def create_enhanced_registry(base_registry_instance):
    """
    Create enhanced operations registry by adding BaseOperation support
    to existing registry instance.
    
    Args:
        base_registry_instance: Existing operations registry instance
        
    Returns:
        Enhanced registry with BaseOperation support
    """
    
    # Add BaseOperation support to existing registry
    base_registry_instance.base_registry = BaseOperationRegistry()
    
    # Add new methods to existing registry
    def register_base_operation(operation: BaseOperation):
        """Register BaseOperation (new method)"""
        base_registry_instance.base_registry.register_base_operation(operation)
    
    def get_base_operation(name: str) -> Optional[BaseOperation]:
        """Get BaseOperation (new method)"""
        return base_registry_instance.base_registry.get_base_operation(name)
    
    def execute_operation_enhanced(name: str, arguments: Dict[str, Any]) -> Optional['OperationResult']:
        """
        Execute operation with unified interface.
        
        Tries BaseOperation first, then falls back to existing system.
        """
        # Try BaseOperation first
        result = base_registry_instance.base_registry.execute_base_operation(name, arguments)
        if result:
            return result
        
        # Fall back to existing system
        operation_meta = base_registry_instance.get_operation(name)
        if operation_meta:
            # Execute using existing system
            # This would need to be implemented based on existing execution logic
            pass
        
        return None
    
    def list_all_operations() -> Dict[str, List[str]]:
        """
        List all operations from both systems.
        
        Returns:
            Dictionary with 'base_operations' and 'legacy_operations' lists
        """
        return {
            'base_operations': base_registry_instance.base_registry.list_base_operations(),
            'legacy_operations': list(base_registry_instance.operations.keys())
        }
    
    def get_operation_info_enhanced(name: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive information about an operation.
        
        Args:
            name: Operation name
            
        Returns:
            Operation information dictionary
        """
        # Check BaseOperation first
        base_op = base_registry_instance.base_registry.get_base_operation(name)
        if base_op:
            return {
                'type': 'base_operation',
                'name': base_op.operation_name,
                'operation_type': base_op.operation_type.value,
                'description': base_op.get_description(),
                'category': base_op.get_category(),
                'examples': base_op.get_examples(),
                'supports_rollback': base_op.can_rollback(),
                'statistics': base_op.get_statistics(),
                'argument_specs': [
                    {
                        'name': spec.name,
                        'type': spec.type.__name__,
                        'required': spec.required,
                        'default': spec.default,
                        'help': spec.help
                    }
                    for spec in base_op.get_argument_specs()
                ] if hasattr(base_op, 'get_argument_specs') else []
            }
        
        # Check legacy operation
        legacy_op = base_registry_instance.get_operation(name)
        if legacy_op:
            return {
                'type': 'legacy_operation',
                'name': legacy_op.name,
                'description': legacy_op.description,
                'category': legacy_op.category,
                'module_path': legacy_op.module_path
            }
        
        return None
    
    def register_builtin_base_operations():
        """Register built-in BaseOperation implementations"""
        try:
            # Register CREATE operation
            from .operations.basic.create import create_operation
            base_registry_instance.base_registry.register_base_operation(create_operation)
            
            # Future operations will be registered here
            # from .operations.basic.replace import replace_operation
            # base_registry_instance.base_registry.register_base_operation(replace_operation)
            
        except ImportError as e:
            # Log import issues but don't fail
            try:
                from utils.logger import logger
                logger.warning(f"Could not register some BaseOperations: {e}")
            except ImportError:
                pass
    
    # Attach new methods to existing registry
    base_registry_instance.register_base_operation = register_base_operation
    base_registry_instance.get_base_operation = get_base_operation
    base_registry_instance.execute_operation_enhanced = execute_operation_enhanced
    base_registry_instance.list_all_operations = list_all_operations
    base_registry_instance.get_operation_info_enhanced = get_operation_info_enhanced
    base_registry_instance.register_builtin_base_operations = register_builtin_base_operations
    
    # Register built-in operations
    register_builtin_base_operations()
    
    return base_registry_instance

# Export functions for easy access
def get_operation_info(name: str, registry_instance) -> Optional[Dict[str, Any]]:
    """Get information about an operation"""
    return registry_instance.get_operation_info_enhanced(name)

def execute_operation(name: str, arguments: Dict[str, Any], registry_instance) -> Optional['OperationResult']:
    """Execute an operation"""
    return registry_instance.execute_operation_enhanced(name, arguments)

def list_operations(registry_instance) -> Dict[str, List[str]]:
    """List all available operations"""
    return registry_instance.list_all_operations()
