import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Agregar path del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from functions.interaction.interactive_confirm import InteractiveConfirm


class TestInteractiveConfirm:
    """Tests para InteractiveConfirm."""
    
    def setup_method(self):
        """Setup para cada test."""
        # Mock console para evitar output real
        self.mock_console = Mock()
        self.confirm = InteractiveConfirm(console=self.mock_console)
    
    def test_interactive_confirm_creation(self):
        """Test que InteractiveConfirm se puede crear correctamente."""
        confirm = InteractiveConfirm()
        assert confirm is not None
        assert hasattr(confirm, 'console')
        assert confirm.user_choice is None
    
    def test_show_summary(self):
        """Test de show_summary."""
        old_content = 'old content here'
        new_content = 'new content here'
        
        self.confirm.show_summary('test.txt', old_content, new_content, 1)
        
        # Verificar que console.print fue llamado
        assert self.mock_console.print.called
    
    def test_confirm_batch_operation(self):
        """Test de confirm_batch_operation."""
        with patch('rich.prompt.Confirm.ask', return_value=True):
            result = self.confirm.confirm_batch_operation(5, 10)
            assert result is True
        
        with patch('rich.prompt.Confirm.ask', return_value=False):
            result = self.confirm.confirm_batch_operation(5, 10)
            assert result is False
    
    def test_show_operation_result_success(self):
        """Test de show_operation_result con éxito."""
        self.confirm.show_operation_result(True, 3, 5, None)
        
        # Verificar que console.print fue llamado
        assert self.mock_console.print.called
    
    def test_show_operation_result_with_errors(self):
        """Test de show_operation_result con errores."""
        errors = {'file1.txt': 'Error de sintaxis', 'file2.txt': 'Archivo no encontrado'}
        
        self.confirm.show_operation_result(False, 1, 2, errors)
        
        # Verificar que console.print fue llamado
        assert self.mock_console.print.called
    
    def test_reset_user_choice(self):
        """Test de reset_user_choice."""
        self.confirm.user_choice = 'all'
        self.confirm.reset_user_choice()
        assert self.confirm.user_choice is None
    
    @patch('rich.prompt.Prompt.ask')
    def test_prompt_user_yes(self, mock_prompt):
        """Test de prompt_user con respuesta 'yes'."""
        mock_prompt.return_value = 'y'
        
        result = self.confirm.prompt_user('test.txt', 'Test change')
        
        assert result == 'yes'
        assert self.mock_console.print.called
    
    @patch('rich.prompt.Prompt.ask')
    def test_prompt_user_all_mode(self, mock_prompt):
        """Test de prompt_user cuando user_choice ya es 'all'."""
        self.confirm.user_choice = 'all'
        
        result = self.confirm.prompt_user('test.txt', 'Test change')
        
        assert result == 'yes'
        # No debería llamar Prompt.ask porque está en modo 'all'
        mock_prompt.assert_not_called()
    
    @patch('rich.prompt.Prompt.ask')
    def test_prompt_user_quit(self, mock_prompt):
        """Test de prompt_user con respuesta 'quit'."""
        mock_prompt.return_value = 'q'
        
        result = self.confirm.prompt_user('test.txt', 'Test change')
        
        assert result == 'quit'
        assert self.mock_console.print.called
