"""
🚀 CodeCraft Ultimate v6.0 - Plugin System
Extensible plugin architecture for custom operations
"""

import os
import sys
import importlib
import importlib.util
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
import logging


class BasePlugin(ABC):
    """Base class for all CodeCraft plugins"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description"""
        pass
    
    @property
    def supported_operations(self) -> List[str]:
        """List of operations this plugin supports"""
        return []
    
    @property
    def supported_file_types(self) -> List[str]:
        """List of file types this plugin supports"""
        return []
    
    @abstractmethod
    def execute(self, operation: str, context: Any, **kwargs) -> Dict[str, Any]:
        """Execute plugin operation"""
        pass
    
    def validate(self, operation: str, context: Any, **kwargs) -> List[str]:
        """Validate operation before execution"""
        return []
    
    def get_suggestions(self, context: Any) -> List[str]:
        """Get operation suggestions for current context"""
        return []


class PluginRegistry:
    """Registry for managing plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.operation_handlers: Dict[str, List[BasePlugin]] = {}
        self.file_type_handlers: Dict[str, List[BasePlugin]] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_plugin(self, plugin: BasePlugin) -> None:
        """Register a plugin"""
        try:
            self.plugins[plugin.name] = plugin
            
            # Register operation handlers
            for operation in plugin.supported_operations:
                if operation not in self.operation_handlers:
                    self.operation_handlers[operation] = []
                self.operation_handlers[operation].append(plugin)
            
            # Register file type handlers
            for file_type in plugin.supported_file_types:
                if file_type not in self.file_type_handlers:
                    self.file_type_handlers[file_type] = []
                self.file_type_handlers[file_type].append(plugin)
            
            self.logger.info(f"Registered plugin: {plugin.name} v{plugin.version}")
        
        except Exception as e:
            self.logger.error(f"Failed to register plugin {plugin.name}: {e}")
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get plugin by name"""
        return self.plugins.get(name)
    
    def get_plugins_for_operation(self, operation: str) -> List[BasePlugin]:
        """Get plugins that support an operation"""
        return self.operation_handlers.get(operation, [])
    
    def get_plugins_for_file_type(self, file_type: str) -> List[BasePlugin]:
        """Get plugins that support a file type"""
        return self.file_type_handlers.get(file_type, [])
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all registered plugins"""
        return [
            {
                'name': plugin.name,
                'version': plugin.version,
                'description': plugin.description,
                'operations': plugin.supported_operations,
                'file_types': plugin.supported_file_types
            }
            for plugin in self.plugins.values()
        ]


class PluginSystem:
    """Main plugin system manager"""
    
    def __init__(self, plugin_dir: Optional[str] = None):
        self.registry = PluginRegistry()
        self.plugin_dirs = []
        self.logger = logging.getLogger(__name__)
        
        # Add default plugin directory
        default_plugin_dir = Path(__file__).parent.parent / "plugins"
        self.plugin_dirs.append(str(default_plugin_dir))
        
        # Add custom plugin directory if provided
        if plugin_dir:
            self.plugin_dirs.append(plugin_dir)
        
        # Load all plugins
        self.load_plugins()
    
    def load_plugins(self) -> None:
        """Load all plugins from plugin directories"""
        for plugin_dir in self.plugin_dirs:
            self._load_plugins_from_directory(plugin_dir)
    
    def _load_plugins_from_directory(self, directory: str) -> None:
        """Load plugins from a specific directory"""
        if not os.path.exists(directory):
            self.logger.warning(f"Plugin directory not found: {directory}")
            return
        
        self.logger.info(f"Loading plugins from: {directory}")
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            if os.path.isfile(item_path) and item.endswith('.py') and not item.startswith('__'):
                self._load_plugin_file(item_path)
            
            elif os.path.isdir(item_path) and not item.startswith('__'):
                # Look for __init__.py in subdirectory
                init_file = os.path.join(item_path, '__init__.py')
                if os.path.exists(init_file):
                    self._load_plugin_file(init_file)
    
    def _load_plugin_file(self, file_path: str) -> None:
        """Load a plugin from a Python file"""
        try:
            # Get module name from file path
            module_name = Path(file_path).stem
            if module_name == '__init__':
                module_name = Path(file_path).parent.name
            
            # Load module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None:
                self.logger.error(f"Could not load spec for {file_path}")
                return
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find plugin classes in module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                if (isinstance(attr, type) and 
                    issubclass(attr, BasePlugin) and 
                    attr is not BasePlugin):
                    
                    # Create plugin instance
                    plugin_instance = attr()
                    self.registry.register_plugin(plugin_instance)
        
        except Exception as e:
            self.logger.error(f"Failed to load plugin from {file_path}: {e}")
    
    def execute_plugin_operation(
        self, 
        operation: str, 
        context: Any, 
        file_type: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Execute operation using appropriate plugin"""
        
        # Get plugins for operation
        operation_plugins = self.registry.get_plugins_for_operation(operation)
        
        # Filter by file type if provided
        if file_type:
            file_type_plugins = self.registry.get_plugins_for_file_type(file_type)
            # Get intersection of operation and file type plugins
            candidates = [p for p in operation_plugins if p in file_type_plugins]
        else:
            candidates = operation_plugins
        
        if not candidates:
            self.logger.debug(f"No plugins found for operation: {operation}")
            return None
        
        # Use first available plugin (could be improved with priority system)
        plugin = candidates[0]
        
        try:
            # Validate operation
            validation_errors = plugin.validate(operation, context, **kwargs)
            if validation_errors:
                return {
                    'success': False,
                    'errors': validation_errors,
                    'plugin': plugin.name
                }
            
            # Execute operation
            result = plugin.execute(operation, context, **kwargs)
            result['plugin'] = plugin.name
            
            return result
        
        except Exception as e:
            self.logger.error(f"Plugin {plugin.name} failed to execute {operation}: {e}")
            return {
                'success': False,
                'errors': [str(e)],
                'plugin': plugin.name
            }
    
    def get_suggestions(self, context: Any) -> List[str]:
        """Get operation suggestions from all plugins"""
        suggestions = []
        
        for plugin in self.registry.plugins.values():
            try:
                plugin_suggestions = plugin.get_suggestions(context)
                suggestions.extend(plugin_suggestions)
            except Exception as e:
                self.logger.error(f"Plugin {plugin.name} failed to provide suggestions: {e}")
        
        return suggestions
    
    def list_available_operations(self) -> Dict[str, List[str]]:
        """List all available operations by plugin"""
        operations = {}
        
        for plugin in self.registry.plugins.values():
            operations[plugin.name] = plugin.supported_operations
        
        return operations
    
    def get_plugin_info(self) -> List[Dict[str, Any]]:
        """Get information about all loaded plugins"""
        return self.registry.list_plugins()