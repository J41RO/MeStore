import pytest
from unittest.mock import Mock, patch, call
import tempfile
import os
from functions.insertion.indentation_detector import IndentationDetector
from functions.insertion.position_calculator import PositionCalculator
from functions.insertion.content_formatter import ContentFormatter
from functions.insertion.context_analyzer import ContextAnalyzer
from coordinators.append import AppendCoordinator

class TestAppendCoordinatorIntegration:
    """Tests de integración para AppendCoordinator"""
    
    def test_append_calls_insertion_functions_successfully(self):
        """Verificar que append usa correctamente functions/insertion"""
        coordinator = AppendCoordinator()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as temp_file:
            temp_file.write("def example():\n    pass\n")
            temp_path = temp_file.name
        
        try:
            result = coordinator.execute(temp_path, "", "# New comment")
            assert result["success"] == True
            assert "position" in result
            
            with open(temp_path, 'r') as f:
                content = f.read()
                assert "# New comment" in content
                
        finally:
            os.unlink(temp_path)
    
    def test_append_vs_before_after_differentiation(self):
        """Verificar que append inserta al final, diferente de before/after"""
        coordinator = AppendCoordinator()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as temp_file:
            original_content = "line1\nline2\nline3"
            temp_file.write(original_content)
            temp_path = temp_file.name
        
        try:
            result = coordinator.execute(temp_path, "", "appended_line")
            
            with open(temp_path, 'r') as f:
                lines = f.read().strip().split('\n')
                assert lines[-1] == "appended_line", "Append debe insertar al final"
                
        finally:
            os.unlink(temp_path)
    
    def test_append_insertion_functions_reuse(self):
        """Verificar reutilización de functions/insertion sin duplicación"""
        coordinator = AppendCoordinator()
        
        # Verificar que usa los mismos objetos que before/after
        assert hasattr(coordinator, 'indentation_detector')
        assert hasattr(coordinator, 'position_calculator') 
        assert hasattr(coordinator, 'content_formatter')
        assert hasattr(coordinator, 'context_analyzer')
        
        assert isinstance(coordinator.indentation_detector, IndentationDetector)
        assert isinstance(coordinator.position_calculator, PositionCalculator)
        assert isinstance(coordinator.content_formatter, ContentFormatter)
        assert isinstance(coordinator.context_analyzer, ContextAnalyzer)

class TestAppendCoordinatorArchitecture:
    """Tests de arquitectura para AppendCoordinator"""
    
    def test_append_lightweight_orchestrator(self):
        """Verificar que append es orquestador ligero como before/after"""
        coordinator = AppendCoordinator()
        
        # Verificar que tiene los mismos componentes que before/after
        expected_components = [
            'indentation_detector', 'position_calculator', 'content_formatter',
            'context_analyzer', 'backup_manager', 'reader', 'writer'
        ]
        
        for component in expected_components:
            assert hasattr(coordinator, component), f"Falta componente: {component}"
    
    def test_append_same_architecture_as_before_after(self):
        """Verificar que append sigue misma arquitectura que before/after"""
        coordinator = AppendCoordinator()
        
        # Verificar método execute con misma signatura
        import inspect
        execute_signature = inspect.signature(coordinator.execute)
        expected_params = ['file_path', 'target', 'content_to_insert']
        
        actual_params = list(execute_signature.parameters.keys())
        for param in expected_params:
            assert param in actual_params, f"Parámetro {param} faltante en execute()"
    
    def test_append_functions_integration_without_duplication(self):
        """Verificar integración con functions sin duplicar código"""
        coordinator = AppendCoordinator()
        
        with patch.object(coordinator.indentation_detector, 'suggest_indentation') as mock_indent:
            with patch.object(coordinator.content_formatter, 'format_content') as mock_format:
                with patch.object(coordinator.reader, 'read_file') as mock_read:
                    with patch.object(coordinator.writer, 'write_file') as mock_write:
                        with patch.object(coordinator.backup_manager, 'create_snapshot') as mock_backup:
                            
                            mock_read.return_value = {'content': 'test content'}
                            mock_format.return_value = Mock(content='formatted')
                            
                            coordinator.execute('/fake/path', 'target', 'content')
                            
                            mock_backup.assert_called_once()
                            mock_read.assert_called_once()
                            mock_indent.assert_called_once()
                            # append usa contenido directo, no format_content
                            mock_format.assert_not_called()
                            mock_write.assert_called_once()
    
    def test_append_error_handling_consistency(self):
        """Verificar manejo de errores consistente con before/after"""
        coordinator = AppendCoordinator()
        
        # Probar con archivo inexistente
        result = coordinator.execute('/nonexistent/file', 'target', 'content')
        
        assert result["success"] == False
        assert "error" in result
        assert isinstance(result["error"], str)
