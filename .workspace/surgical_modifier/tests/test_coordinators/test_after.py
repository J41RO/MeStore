import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from coordinators.after import AfterCoordinator
from functions.insertion.indentation_detector import IndentationDetector
from functions.insertion.position_calculator import PositionCalculator
from functions.insertion.content_formatter import ContentFormatter
from functions.insertion.context_analyzer import ContextAnalyzer
from functions.backup.manager import BackupManager
from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter


class TestAfterCoordinatorIntegration:
    """Tests integration para verificar inserción AFTER en AfterCoordinator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = AfterCoordinator()
        self.test_file_path = "test_after_file.py"
        self.test_content = """def function():
    existing_line = 1
    return value"""

    def test_after_calls_insertion_functions_successfully(self):
        """Test que AFTER integra insertion functions correctamente"""
        with patch.object(self.coordinator.backup_manager, 'create_snapshot') as mock_backup, \
             patch.object(self.coordinator.reader, 'read_file') as mock_reader, \
             patch.object(self.coordinator.indentation_detector, 'suggest_indentation') as mock_indent, \
             patch.object(self.coordinator.position_calculator, 'calculate_after_position') as mock_position, \
             patch.object(self.coordinator.content_formatter, 'format_after_insertion') as mock_formatter, \
             patch.object(self.coordinator.writer, 'write_file') as mock_writer:
            
            # Setup mocks
            mock_reader.return_value = {'content': self.test_content}
            mock_indent.return_value = '    '
            mock_position_obj = Mock()
            mock_position_obj.line_number = 1
            mock_position.return_value = mock_position_obj
            mock_formatted_obj = Mock()
            mock_formatted_obj.content = 'inserted_after_line = True'
            mock_formatter.return_value = mock_formatted_obj
            
            # Ejecutar
            result = self.coordinator.execute(self.test_file_path, 'existing_line', 'inserted_after_line = True')
            
            # Verificar llamadas a functions
            mock_backup.assert_called_once_with(self.test_file_path)
            mock_reader.assert_called_once_with(self.test_file_path)
            mock_indent.assert_called_once_with(self.test_content)
            mock_position.assert_called_once_with(self.test_content, 'existing_line', 'inserted_after_line = True')
            mock_formatter.assert_called_once_with('inserted_after_line = True', '    ')
            mock_writer.assert_called_once()
            
            # Verificar resultado
            assert result['success'] is True
            assert result['position'] == 2  # line_number + 1 para AFTER

    def test_after_vs_before_differentiation(self):
        """Test diferenciación AFTER vs BEFORE - inserción después del target"""
        with patch.object(self.coordinator.backup_manager, 'create_snapshot'), \
             patch.object(self.coordinator.reader, 'read_file') as mock_reader, \
             patch.object(self.coordinator.indentation_detector, 'suggest_indentation') as mock_indent, \
             patch.object(self.coordinator.position_calculator, 'calculate_after_position') as mock_position, \
             patch.object(self.coordinator.content_formatter, 'format_after_insertion') as mock_formatter, \
             patch.object(self.coordinator.writer, 'write_file') as mock_writer:
            
            mock_reader.return_value = {'content': self.test_content}
            mock_indent.return_value = '    '
            mock_position_obj = Mock()
            mock_position_obj.line_number = 1  # Target en línea 1
            mock_position.return_value = mock_position_obj
            mock_formatted_obj = Mock()
            mock_formatted_obj.content = 'after_insert = 1'
            mock_formatter.return_value = mock_formatted_obj
            
            result = self.coordinator.execute(self.test_file_path, 'existing_line', 'after_insert = 1')
            
            # AFTER debe usar calculate_after_position y format_after_insertion
            mock_position.assert_called_once_with(self.test_content, 'existing_line', 'after_insert = 1')
            mock_formatter.assert_called_once_with('after_insert = 1', '    ')
            
            # Posición de inserción debe ser line_number + 1 (DESPUÉS)
            assert result['position'] == 2

    def test_after_insertion_functions_reuse(self):
        """Test reutilización de functions sin duplicación"""
        # Verificar que AFTER usa las mismas functions que BEFORE
        assert hasattr(self.coordinator, 'indentation_detector')
        assert hasattr(self.coordinator, 'position_calculator')
        assert hasattr(self.coordinator, 'content_formatter')
        assert hasattr(self.coordinator, 'context_analyzer')
        assert isinstance(self.coordinator.indentation_detector, IndentationDetector)
        assert isinstance(self.coordinator.position_calculator, PositionCalculator)
        assert isinstance(self.coordinator.content_formatter, ContentFormatter)
        assert isinstance(self.coordinator.context_analyzer, ContextAnalyzer)


class TestAfterCoordinatorArchitecture:
    """Tests arquitectura para verificar orquestador ligero AFTER"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = AfterCoordinator()

    def test_after_lightweight_orchestrator(self):
        """Test que AFTER mantiene arquitectura orquestador ligero (≤24 líneas)"""
        import inspect
        source = inspect.getsource(self.coordinator.execute)
        lines = len(source.split('\n'))
        assert lines <= 25, f"execute() debe ser ≤24 líneas, actual: {lines}"

    def test_after_same_architecture_as_before(self):
        """Test que AFTER sigue misma arquitectura que BEFORE"""
        from coordinators.before import BeforeCoordinator
        import inspect
        
        before_coordinator = BeforeCoordinator()
        before_source = inspect.getsource(before_coordinator.execute)
        after_source = inspect.getsource(self.coordinator.execute)
        
        before_lines = len(before_source.split('\n'))
        after_lines = len(after_source.split('\n'))
        
        # Ambos deben tener arquitectura similar (≤24 líneas)
        assert before_lines <= 25
        assert after_lines <= 25
        assert abs(before_lines - after_lines) <= 2, "Arquitectura debe ser consistente"

    def test_after_functions_integration_without_duplication(self):
        """Test que AFTER integra functions sin duplicar código"""
        # Verificar que las functions son instancias reales, no duplicadas
        assert id(self.coordinator.indentation_detector) != id(self.coordinator.position_calculator)
        assert id(self.coordinator.content_formatter) != id(self.coordinator.context_analyzer)
        
        # Verificar que cada function es una instancia válida
        functions = [
            self.coordinator.indentation_detector,
            self.coordinator.position_calculator,
            self.coordinator.content_formatter,
            self.coordinator.context_analyzer
        ]
        for func in functions:
            assert hasattr(func, '__class__')
            assert func.__class__.__name__ in [
                'IndentationDetector', 'PositionCalculator', 
                'ContentFormatter', 'ContextAnalyzer'
            ]

    def test_after_error_handling_consistency(self):
        """Test manejo de errores consistente con patrón BEFORE"""
        with patch.object(self.coordinator.backup_manager, 'create_snapshot', side_effect=Exception("Test error")):
            result = self.coordinator.execute("test_file.py", "target", "content")
            
            assert result['success'] is False
            assert 'error' in result
            assert 'Error in after operation' in result['error']