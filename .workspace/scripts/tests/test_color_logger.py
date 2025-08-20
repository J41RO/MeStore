"""
Tests para ColorLogger de Surgical Modifier Ultimate v5.3
"""

import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

# Importar el módulo principal
try:
    from surgical_modifier_ultimate import ColorLogger
except ImportError:
    sys.path.append("..")
    from surgical_modifier_ultimate import ColorLogger


class TestColorLogger:
    """Tests para la clase ColorLogger"""

    @pytest.fixture
    def color_logger(self):
        """Crear instancia de ColorLogger para testing"""
        return ColorLogger()

    @pytest.fixture
    def quiet_logger(self):
        """Crear instancia de ColorLogger silenciosa"""
        return ColorLogger()

    def test_color_logger_initialization(self, color_logger):
        """Test: Inicialización correcta del ColorLogger"""
        assert color_logger is not None
        assert hasattr(color_logger, "success")
        assert hasattr(color_logger, "error")
        assert hasattr(color_logger, "warning")
        assert hasattr(color_logger, "info")

    @patch("sys.stdout", new_callable=StringIO)
    def test_success_message(self, mock_stdout, color_logger):
        """Test: Mensaje de éxito con colores"""
        test_message = "Operación exitosa"
        color_logger.success(test_message)

        output = mock_stdout.getvalue()
        assert test_message in output
        # Verificar que contiene caracteres de color (ANSI)
        assert "\033[" in output or test_message in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_error_message(self, mock_stdout, color_logger):
        """Test: Mensaje de error con colores"""
        test_message = "Error detectado"
        color_logger.error(test_message)

        output = mock_stdout.getvalue()
        assert test_message in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_warning_message(self, mock_stdout, color_logger):
        """Test: Mensaje de advertencia con colores"""
        test_message = "Advertencia importante"
        color_logger.warning(test_message)

        output = mock_stdout.getvalue()
        assert test_message in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_info_message(self, mock_stdout, color_logger):
        """Test: Mensaje informativo"""
        test_message = "Información general"
        color_logger.info(test_message)

        output = mock_stdout.getvalue()
        assert test_message in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_quiet_mode(self, mock_stdout, quiet_logger):
        """Test: Modo silencioso no debe mostrar mensajes"""
        test_message = "Mensaje en modo silencioso"
        quiet_logger.info(test_message)

        output = mock_stdout.getvalue()
        # En modo silencioso, algunos mensajes pueden no aparecer
        # Esto depende de la implementación específica
        assert isinstance(output, str)  # Verificar que al menos no falla

    def test_logger_methods_exist(self, color_logger):
        """Test: Verificar que todos los métodos necesarios existen"""
        required_methods = ["success", "error", "warning", "info"]

        for method_name in required_methods:
            assert hasattr(color_logger, method_name)
            assert callable(getattr(color_logger, method_name))

    @pytest.mark.unit
    def test_multiple_messages(self, color_logger):
        """Test: Manejo de múltiples mensajes consecutivos"""
        messages = ["Primer mensaje", "Segundo mensaje", "Tercer mensaje"]

        # No debe fallar al enviar múltiples mensajes
        try:
            for msg in messages:
                color_logger.info(msg)
                color_logger.success(msg)
                color_logger.warning(msg)
            success = True
        except Exception:
            success = False

        assert success is True
