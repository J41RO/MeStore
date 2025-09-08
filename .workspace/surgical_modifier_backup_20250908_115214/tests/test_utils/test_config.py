import pytest
import os
from pathlib import Path
from unittest.mock import patch

class TestConfig:
    """Tests unitarios para config.py"""
    
    def test_can_import_config(self):
        """Test que el módulo config se puede importar"""
        import surgical_modifier.config as config
        assert hasattr(config, 'DEFAULT_CONFIG')
        assert hasattr(config, 'PROJECT_ROOT')
        assert config.DEFAULT_CONFIG is not None
        assert config.PROJECT_ROOT is not None
    
    def test_default_config_structure(self):
        """Test estructura de DEFAULT_CONFIG"""
        import surgical_modifier.config as config
        default_config = config.DEFAULT_CONFIG
        
        # Verificar campos obligatorios
        required_fields = [
            "version", "backup_enabled", "verbose", "dry_run",
            "max_backup_files", "backup_retention_days", "supported_extensions",
            "excluded_dirs", "log_level", "max_file_size_mb"
        ]
        
        for field in required_fields:
            assert field in default_config
    
    def test_project_root_is_path(self):
        """Test que PROJECT_ROOT es un Path válido"""
        import surgical_modifier.config as config
        project_root = config.PROJECT_ROOT
        
        assert isinstance(project_root, Path)
        assert project_root.exists()
    
    def test_config_dir_setup(self):
        """Test configuración de directorios"""
        import surgical_modifier.config as config
        
        config_dir = config.CONFIG_DIR
        backup_dir = config.BACKUP_DIR
        project_root = config.PROJECT_ROOT
        
        assert isinstance(config_dir, Path)
        assert isinstance(backup_dir, Path)
        assert config_dir == project_root / "config"
    
    def test_supported_extensions(self):
        """Test extensiones soportadas"""
        import surgical_modifier.config as config
        
        extensions = config.DEFAULT_CONFIG["supported_extensions"]
        assert isinstance(extensions, list)
        assert ".py" in extensions
        assert ".js" in extensions
        assert ".json" in extensions
    
    def test_excluded_dirs(self):
        """Test directorios excluidos"""
        import surgical_modifier.config as config
        
        excluded = config.DEFAULT_CONFIG["excluded_dirs"]
        assert isinstance(excluded, list)
        assert "__pycache__" in excluded
        assert ".git" in excluded
        assert "node_modules" in excluded
    
    def test_default_values(self):
        """Test valores por defecto"""
        import surgical_modifier.config as config
        default_config = config.DEFAULT_CONFIG
        
        assert default_config["version"] == "0.1.0"
        assert default_config["backup_enabled"] == True
        assert default_config["verbose"] == False
        assert default_config["dry_run"] == False
        assert default_config["log_level"] == "INFO"
        assert isinstance(default_config["max_backup_files"], int)
        assert isinstance(default_config["backup_retention_days"], int)
    
    def test_constants_exist(self):
        """Test que las constantes básicas existen"""
        import surgical_modifier.config as config
        
        assert hasattr(config, 'LOG_LEVEL')
        assert hasattr(config, 'MAX_FILE_SIZE')
        assert hasattr(config, 'ENCODING')
    
    def test_functions_exist(self):
        """Test que las funciones de configuración existen"""
        import surgical_modifier.config as config
        
        assert hasattr(config, 'get_coordinator_config')
        assert callable(config.get_coordinator_config)
        assert hasattr(config, 'validate_config')
        assert callable(config.validate_config)
        assert hasattr(config, 'get_full_config')
        assert callable(config.get_full_config)
