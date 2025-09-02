import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from coordinators.before import BeforeCoordinator
from functions.insertion.indentation_detector import IndentationDetector
from functions.insertion.position_calculator import PositionCalculator
from functions.insertion.content_formatter import ContentFormatter
from functions.insertion.context_analyzer import ContextAnalyzer
from functions.backup.manager import BackupManager
from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter


class TestBeforeCoordinatorIntegration:
    """Tests integration para verificar inserción BEFORE en BeforeCoordinator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = BeforeCoordinator()
        self.test_file_path = "test_before_file.py"
        self.test_content = """def function():
    existing_line = 1
    return value"""

    def test_before_calls_insertion_functions_successfully(self):
        """Test que BEFORE integra insertion functions correctamente"""
        with patch.object(self.coordinator.backup_manager, 'create_snapshot') as mock_backup, \
             patch.object(self.coordinator.reader, 'read_file') as mock_reader, \
             patch.object(self.coordinator.indentation_detector, 'suggest_indentation') as mock_indent, \
             patch.object(self.coordinator.position_calculator, 'calculate_before_position') as mock_position, \
             patch.object(self.coordinator.content_formatter, 'format_before_insertion') as mock_formatter, \
             patch.object(self.coordinator.writer, 'write_file') as mock_writer:
            
            # Setup mocks
            mock_reader.return_value = {'content': self.test_content}
            mock_indent.return_value = '    '
            mock_position.return_value = Mock(line_number=1)
            mock_formatter.return_value = Mock(content='    new_line = 0')
            
            result = self.coordinator.execute(self.test_file_path, 'existing_line', 'new_line = 0')
            
            # Verificar integration functions llamadas
            mock_backup.assert_called_once_with(self.test_file_path)
            mock_reader.assert_called_once_with(self.test_file_path)
            mock_indent.assert_called_once()
            mock_position.assert_called_once()
            mock_formatter.assert_called_once()
            mock_writer.assert_called_once()
            
            assert result['success'] is True

    def test_before_strategy_insertion_workflow(self):
        """Test workflow específico de estrategia BEFORE"""
        with patch.object(self.coordinator.backup_manager, 'create_snapshot'), \
             patch.object(self.coordinator.reader, 'read_file') as mock_reader, \
             patch.object(self.coordinator.position_calculator, 'calculate_before_position') as mock_position, \
             patch.object(self.coordinator.content_formatter, 'format_before_insertion') as mock_formatter, \
             patch.object(self.coordinator.writer, 'write_file') as mock_writer:
            
            mock_reader.return_value = {'content': self.test_content}
            mock_position.return_value = Mock(line_number=1)
            mock_formatter.return_value = Mock(content='    inserted_before = True')
            
            result = self.coordinator.execute(self.test_file_path, 'existing_line', 'inserted_before = True')
            
            # Verificar estrategia BEFORE específica
            assert mock_position.call_args[0][1] == 'existing_line'  # target pattern
            assert mock_position.call_args[0][2] == 'inserted_before = True'  # new content
            assert result['success'] is True
            assert 'position' in result

    def test_before_preserves_indentation(self):
        """Test que BEFORE preserva indentación original"""
        with patch.object(self.coordinator.backup_manager, 'create_snapshot'), \
             patch.object(self.coordinator.reader, 'read_file') as mock_reader, \
             patch.object(self.coordinator.indentation_detector, 'suggest_indentation') as mock_indent, \
             patch.object(self.coordinator.content_formatter, 'format_before_insertion') as mock_formatter, \
             patch.object(self.coordinator.writer, 'write_file'):
            
            mock_reader.return_value = {'content': self.test_content}
            mock_indent.return_value = '    '
            mock_formatter.return_value = Mock(content='    properly_indented = True')
            
            self.coordinator.execute(self.test_file_path, 'existing_line', 'properly_indented = True')
            
            # Verificar indentación pasada al formatter
            mock_formatter.assert_called_with('properly_indented = True', '    ')

    def test_before_error_handling(self):
        """Test manejo de errores en workflow BEFORE"""
        with patch.object(self.coordinator.backup_manager, 'create_snapshot'), \
            patch.object(self.coordinator.reader, 'read_file') as mock_reader:
            mock_reader.side_effect = Exception("File read error")
            
            result = self.coordinator.execute(self.test_file_path, 'target', 'content')
            
            assert result['success'] is False
            assert 'error' in result
            assert 'File read error' in result['error']


class TestBeforeCoordinatorArchitecture:
    """Tests para verificar arquitectura orquestador ligero"""
    
    def test_orchestrator_lightweight_architecture(self):
        """Test que BeforeCoordinator es orquestador ligero"""
        import inspect
        coordinator = BeforeCoordinator()
        source = inspect.getsource(coordinator.execute)
        lines = len([line for line in source.split('\n') if line.strip()])
        
        # Verificar arquitectura ligera
        assert lines <= 25, f"execute() debe ser ≤25 líneas, actual: {lines}"
        
        # Verificar que integra insertion functions
        attrs = ['indentation_detector', 'position_calculator', 'content_formatter', 'context_analyzer']
        for attr in attrs:
            assert hasattr(coordinator, attr), f"Missing {attr} integration"

    def test_insertion_functions_integration(self):
        """Test integración completa de insertion functions"""
        coordinator = BeforeCoordinator()
        
        # Verificar 4 insertion functions integradas
        assert hasattr(coordinator, 'indentation_detector')
        assert hasattr(coordinator, 'position_calculator')
        assert hasattr(coordinator, 'content_formatter')
        assert hasattr(coordinator, 'context_analyzer')
        
        # Verificar backup_manager también integrado
        assert hasattr(coordinator, 'backup_manager')
        
        # Verificar content functions
        assert hasattr(coordinator, 'reader')
        assert hasattr(coordinator, 'writer')

    def test_before_coordinator_follows_pattern(self):
        """Test que BeforeCoordinator sigue patrón establecido"""
        coordinator = BeforeCoordinator()
        
        # Verificar método execute existe
        assert hasattr(coordinator, 'execute')
        assert callable(coordinator.execute)
        
        # Verificar signature correcta
        import inspect
        sig = inspect.signature(coordinator.execute)
        params = list(sig.parameters.keys())
        assert 'file_path' in params
        assert 'target' in params
        assert 'content_to_insert' in params