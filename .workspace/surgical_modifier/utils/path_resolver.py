"""
Surgical Modifier v6.0 - Global Path Resolver
Resolve paths from anywhere in the system
"""

import os
import sys
from pathlib import Path

class GlobalPathResolver:
    """Resolve paths globally from any working directory"""
    
    def __init__(self):
        self.cache = {}
        
    def resolve(self, path_str):
        """
        Resolve path string to absolute path
        Works from any current working directory
        """
        if path_str in self.cache:
            return self.cache[path_str]
            
        path = Path(path_str)
        
        # If already absolute, return as is
        if path.is_absolute():
            resolved = path
        else:
            # Try relative to current working directory
            resolved = Path.cwd() / path
            
        # Cache and return
        self.cache[path_str] = resolved
        return resolved
        
    def exists(self, path_str):
        """Check if path exists"""
        return self.resolve(path_str).exists()
        
    def is_file(self, path_str):
        """Check if path is a file"""
        return self.resolve(path_str).is_file()
        
    def is_dir(self, path_str):
        """Check if path is a directory"""
        return self.resolve(path_str).is_dir()

# Global resolver instance
path_resolver = GlobalPathResolver()
