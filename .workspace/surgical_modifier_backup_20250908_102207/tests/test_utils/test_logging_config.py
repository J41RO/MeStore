import pytest
import logging
import tempfile
from pathlib import Path

class TestLoggingConfig:
    """Tests unitarios para logging_config"""
    
    def test_can_import_logging_config(self):
        """Test que el módulo se puede importar"""
        import surgical_modifier.logging_config as logging_config
        assert hasattr(logging_config, 'setup_logging')
        assert hasattr(logging_config, 'get_logger')
    
    def test_setup_logging_basic(self):
        """Test configuración básica de logging"""
        import surgical_modifier.logging_config as logging_config
        
        logger = logging_config.setup_logging()
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "surgical_modifier"
    
    def test_get_logger_function(self):
        """Test función get_logger"""
        import surgical_modifier.logging_config as logging_config
        
        logger = logging_config.get_logger("test_module")
        assert logger is not None
        assert "surgical_modifier.test_module" in logger.name
    
    def test_default_logger_exists(self):
        """Test que DEFAULT_LOGGER existe"""
        import surgical_modifier.logging_config as logging_config
        
        assert hasattr(logging_config, 'DEFAULT_LOGGER')
        assert isinstance(logging_config.DEFAULT_LOGGER, logging.Logger)
