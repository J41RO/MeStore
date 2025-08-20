"""
Surgical Modifier v6.0 - Plugin System Foundation
Prepared for future plugin architecture
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

class PluginManager:
    """
    Plugin system foundation for future extensibility
    Will support dynamic loading of operations and extensions
    """
    
    def __init__(self):
        self.plugin_dirs = [
            Path(__file__).parent.parent / "plugins",
            Path.home() / ".surgical_modifier" / "plugins"
        ]
        self.loaded_plugins = {}
        self.available_operations = {}
        
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in plugin directories
        Future: Will auto-load .py files as plugins
        """
        plugins = []
        for plugin_dir in self.plugin_dirs:
            if plugin_dir.exists():
                for plugin_file in plugin_dir.glob("*.py"):
                    if not plugin_file.name.startswith("_"):
                        plugins.append(plugin_file.stem)
        return plugins
        
    def register_operation(self, name: str, operation_class: Any):
        """
        Register a new operation for the CLI system
        Future: Dynamic operation registration
        """
        self.available_operations[name] = operation_class
        
    def get_available_operations(self) -> Dict[str, Any]:
        """
        Get all available operations (built-in + plugins)
        """
        return self.available_operations.copy()
        
    def load_plugin(self, plugin_name: str) -> Optional[Any]:
        """
        Load a specific plugin by name
        Future: Dynamic plugin loading
        """
        # Placeholder for future implementation
        return None

# Global plugin manager instance
plugin_manager = PluginManager()
