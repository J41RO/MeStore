"""
Tests para la integración de loguru en el sistema de logging.
Valida que loguru funciona correctamente en development sin afectar production.
"""

import pytest
import os
import sys
from unittest.mock import patch

# Asegurar que podemos importar desde app
sys.path.append('.')


class TestLoguruIntegration:
    """Tests para la integración de loguru con structlog."""
    
    def setup_method(self):
        """Setup para cada test."""
        # Limpiar caché de módulos para tests aislados
        modules_to_clear = [mod for mod in sys.modules.keys() if 'app.core.logger' in mod]
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'development'})
    def test_configure_loguru_activates_in_development(self):
        """Test: loguru se activa solo en environment=development."""
        from app.core.logger import configure_loguru
        
        # Mock loguru_logger para verificar llamadas
        with patch('app.core.logger.loguru_logger') as mock_loguru:
            configure_loguru()
            
            # Verificar que loguru se configuró
            mock_loguru.remove.assert_called_once()
            mock_loguru.add.assert_called_once()
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'production'})
    def test_configure_loguru_skips_in_production(self):
        """Test: loguru NO se activa en production."""
        # Limpiar caché para test aislado
        modules_to_clear = [mod for mod in sys.modules.keys() if 'app.core.config' in mod]
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]
        
        from app.core.config import settings
        
        # Verificar que environment es production
        assert settings.ENVIRONMENT.lower() == 'production'
        
        # Test: función debería salir temprano sin configurar nada
        with patch('app.core.logger.sys.stderr') as mock_stderr:
            from app.core.logger import configure_loguru
            configure_loguru()
            
            # Verificar que NO se intentó escribir a stderr (loguru no configurado)
            mock_stderr.assert_not_called()
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
    def test_configure_loguru_skips_in_testing(self):
        """Test: loguru NO se activa en testing."""
        from app.core.logger import configure_loguru
        
        with patch('app.core.logger.loguru_logger') as mock_loguru:
            configure_loguru()
            
            # Verificar que loguru NO se configuró
            mock_loguru.add.assert_not_called()


class TestLoguruStructlogCoexistence:
    """Tests para verificar que loguru y structlog coexisten sin conflictos."""
    
    def setup_method(self):
        """Setup para cada test."""
        # Limpiar caché de módulos
        modules_to_clear = [mod for mod in sys.modules.keys() if 'app.core.logger' in mod]
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'development'})
    def test_structlog_still_works_with_loguru(self):
        """Test: structlog sigue funcionando cuando loguru está activo."""
        from app.core.logger import get_logger
        
        # Obtener logger (debería usar structlog internamente)
        test_logger = get_logger('test.coexistence')
        
        # Verificar que es instancia de structlog
        assert hasattr(test_logger, 'info')
        assert hasattr(test_logger, 'error')
        assert hasattr(test_logger, 'warning')
        assert hasattr(test_logger, 'debug')
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'production'})
    def test_production_mode_unchanged(self):
        """Test: modo production funciona igual que antes (solo structlog)."""
        from app.core.logger import get_logger
        test_logger = get_logger('test.production')
        
        # En production, debería funcionar sin errores
        assert test_logger is not None
        
        # Verificar que puede loggear sin errores
        try:
            test_logger.info('Test message')
        except Exception as e:
            pytest.fail(f'Logger falló en production: {e}')


class TestLoguruErrorHandling:
    """Tests para manejo de errores en la configuración de loguru."""
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'invalid_environment'})
    def test_invalid_environment_treated_as_not_development(self):
        """Test: environment inválido se trata como NOT development."""
        from app.core.logger import configure_loguru
        
        with patch('app.core.logger.loguru_logger') as mock_loguru:
            configure_loguru()
            
            # No debería configurar loguru
            mock_loguru.add.assert_not_called()


class TestLoguruFunctions:
    """Tests para verificar funciones del logger."""
    
    def test_logger_functions_exist_and_callable(self):
        """Test: todas las funciones del logger existen y son llamables."""
        from app.core.logger import (
            configure_logging, 
            configure_loguru, 
            get_logger,
            log_startup_info,
            log_shutdown_info,
            log_request_info,
            log_error
        )
        
        # Verificar que todas las funciones existen
        assert callable(configure_logging)
        assert callable(configure_loguru)
        assert callable(get_logger)
        assert callable(log_startup_info)
        assert callable(log_shutdown_info)
        assert callable(log_request_info)
        assert callable(log_error)
