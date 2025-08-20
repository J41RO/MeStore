"""
Example plugin for Surgical Modifier v6.0
Demonstrates future plugin architecture
"""

class ExampleOperation:
    """
    Example operation plugin
    Future: All plugins will implement this interface
    """
    
    name = "example"
    description = "Example operation for plugin system demonstration"
    
    def execute(self, *args, **kwargs):
        """Execute the operation"""
        return "Example plugin executed successfully!"
        
    def validate(self, *args, **kwargs):
        """Validate operation parameters"""
        return True

# Plugin registration (future)
def register_plugin(plugin_manager):
    """Register this plugin with the system"""
    plugin_manager.register_operation("example", ExampleOperation)
