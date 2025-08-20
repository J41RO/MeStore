import logging
import os
import tempfile
import unittest

from universal_modifier import LoggerManager


class TestLoggingSystem(unittest.TestCase):

    def setUp(self):
        """Setup para cada test"""
        self.lm = LoggerManager(name="test_logger")

    def test_logger_manager_creation(self):
        """Test creación de LoggerManager"""
        self.assertIsNotNone(self.lm)
        self.assertIsInstance(self.lm.logger, logging.Logger)

    def test_console_handler_setup(self):
        """Test configuración de handler de consola"""
        handler = self.lm.setup_console_handler()
        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertIn("console", self.lm.handlers)

    def test_file_handler_setup(self):
        """Test configuración de handler de archivo"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            handler = self.lm.setup_file_handler(tmp.name)
            self.assertIsInstance(handler, logging.FileHandler)
            self.assertIn(f"file_{tmp.name}", self.lm.handlers)
            os.unlink(tmp.name)

    def test_formatter_creation(self):
        """Test creación de formatters"""
        formatter = self.lm.create_formatter()
        self.assertIsInstance(formatter, logging.Formatter)

    def test_contextual_logging_methods(self):
        """Test métodos de logging contextual"""
        # Estos métodos no deben fallar
        self.lm.log_operation_start("test_op", {"key": "value"})
        self.lm.log_operation_end("test_op", True, {"key": "value"})
        self.lm.log_performance("test_op", 0.123, {"key": "value"})

        try:
            raise ValueError("Test error")
        except ValueError as e:
            self.lm.log_error_with_context("test_op", e, {"key": "value"})


if __name__ == "__main__":
    unittest.main()
