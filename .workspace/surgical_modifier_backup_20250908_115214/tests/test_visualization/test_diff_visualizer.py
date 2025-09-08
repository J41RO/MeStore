import pytest
import sys
import os
from unittest.mock import Mock, patch


# Agregar path del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from functions.visualization.diff_visualizer import DiffVisualizer


class TestDiffVisualizer:
    """Tests para DiffVisualizer."""
    
    def setup_method(self):
        """Setup para cada test."""
        # Mock console para evitar output real
        self.mock_console = Mock()
        self.visualizer = DiffVisualizer(console=self.mock_console)
    
    def test_diff_visualizer_creation(self):
        """Test que DiffVisualizer se puede crear correctamente."""
        visualizer = DiffVisualizer()
        assert visualizer is not None
        assert hasattr(visualizer, 'console')
    
    def test_generate_diff_basic(self):
        """Test de generación de diff básico."""
        before = 'line 1\nold content\nline 3'
        after = 'line 1\nnew content\nline 3'
        
        diff = self.visualizer.generate_diff(before, after, 'test.txt')
        
        assert isinstance(diff, list)
        assert len(diff) > 0
        
        # Verificar que contiene markers de diff
        diff_str = '\n'.join(diff)
        assert '--- test.txt (before)' in diff_str
        assert '+++ test.txt (after)' in diff_str
    
    def test_generate_diff_no_changes(self):
        """Test cuando no hay cambios."""
        content = 'same content'
        
        diff = self.visualizer.generate_diff(content, content, 'test.txt')
        
        # Sin cambios, diff debería estar vacío
        assert len(diff) == 0
    
    def test_display_preview_with_changes(self):
        """Test de display_preview con cambios."""
        before = 'old content'
        after = 'new content'
        
        # Ejecutar método (no debería fallar)
        self.visualizer.display_preview('test.txt', before, after)
        
        # Verificar que console.print fue llamado
        assert self.mock_console.print.called
    
    def test_display_preview_no_changes(self):
        """Test de display_preview sin cambios."""
        content = 'same content'
        
        self.visualizer.display_preview('test.txt', content, content)
        
        # Verificar que se llamó print (mensaje de no cambios)
        assert self.mock_console.print.called
    
    def test_show_summary(self):
        """Test de show_summary."""
        before = 'line 1\nline 2'
        after = 'line 1\nline 2\nline 3'
        
        self.visualizer.show_summary('test.txt', before, after)
        
        # Verificar que se llamó print
        assert self.mock_console.print.called
    
    def test_show_context(self):
        """Test de show_context."""
        content = 'line 1\nline 2\nline 3\nline 4\nline 5'
        
        self.visualizer.show_context('test.txt', content, content, 2, context_lines=1)
        
        # Verificar que se llamó print
        assert self.mock_console.print.called
