"""
🚀 CodeCraft Ultimate v6.0 - Configuración Global
"""

import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuración global del sistema"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.config_file = ".codecraft.toml"
        self.backup_dir = ".codecraft_backups"
        
        # Configuraciones por defecto
        self.default_config = {
            'general': {
                'output_format': 'structured',
                'backup_enabled': True,
                'verbose': False,
                'auto_format': True
            },
            'analysis': {
                'complexity_threshold': 10,
                'security_level': 'medium',
                'include_metrics': True,
                'performance_checks': True
            },
            'generation': {
                'default_test_framework': 'pytest',
                'template_directory': './templates',
                'auto_format': True,
                'include_docs': True
            },
            'ai_integration': {
                'enable_suggestions': True,
                'context_window': 1000,
                'max_suggestions': 3,
                'auto_explain': False
            },
            'operations': {
                'create_backups': True,
                'verify_syntax': True,
                'run_tests': False,
                'git_integration': True
            },
            'refactoring': {
                'safe_mode': True,
                'run_tests_after': True,
                'create_backup': True,
                'verify_references': True
            }
        }
    
    def get(self, key: str, default=None) -> Any:
        """Obtener valor de configuración"""
        keys = key.split('.')
        value = self.default_config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return default
    
    def load_from_file(self, config_path: str = None) -> Dict[str, Any]:
        """Cargar configuración desde archivo"""
        if config_path is None:
            config_path = os.path.join(self.project_root, self.config_file)
        
        if not os.path.exists(config_path):
            return self.default_config
        
        try:
            import toml
            with open(config_path, 'r') as f:
                file_config = toml.load(f)
            
            # Merge con configuración por defecto
            merged_config = self.default_config.copy()
            self._deep_merge(merged_config, file_config)
            return merged_config
            
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            return self.default_config
    
    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """Merge profundo de diccionarios"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value


# Instancia global
config = Config()