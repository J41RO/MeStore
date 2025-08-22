#!/usr/bin/env python3
"""
Tests para EscapeProcessor - Procesador especializado de escape.
"""

import pytest
import sys
import os

# Agregar directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.escape_processor import EscapeProcessor


class TestEscapeProcessor:
    """Tests para la clase EscapeProcessor."""
    
    def setup_method(self):
        """Configuración antes de cada test."""
        self.processor = EscapeProcessor()
    
    def test_init(self):
        """Test inicialización del EscapeProcessor."""
        assert self.processor is not None
        assert hasattr(self.processor, 'advanced_patterns')
        assert hasattr(self.processor, 'correction_config')
        assert hasattr(self.processor, 'logger')
    
    def test_fix_escape_issues_double_escape(self):
        """Test corrección de escape doble."""
        content = "test \\\\\\\\n double escape"
        result = self.processor.fix_escape_issues(content, 'double_escape')
        assert result != content  # Verificar que se aplicó algún cambio
    
    def test_fix_escape_issues_broken_json(self):
        """Test corrección de JSON escape roto."""
        content = 'text with \\"quotes\\" problem'
        result = self.processor.fix_escape_issues(content, 'broken_json_escape')
        assert result != content  # Verificar que se aplicó corrección
        assert 'quotes' in result  # Verificar que quotes están presentes
    
    def test_fix_escape_issues_empty_content(self):
        """Test con contenido vacío."""
        result = self.processor.fix_escape_issues("", 'double_escape')
        assert result == ""
        
        result = self.processor.fix_escape_issues(None, 'double_escape')
        assert result is None
    
    def test_analyze_escape_patterns(self):
        """Test análisis de patrones de escape."""
        content = 'mixed \\"quotes\\" and \\\\n sequences'
        analysis = self.processor.analyze_escape_patterns(content)
        
        assert isinstance(analysis, dict)
        assert 'total_escapes' in analysis
        assert 'escape_types' in analysis
        assert 'problematic_sequences' in analysis
        assert analysis['total_escapes'] >= 0
    
    def test_validate_escape_integrity(self):
        """Test validación de integridad."""
        content = 'valid "quoted" content'
        validation = self.processor.validate_escape_integrity(content)
        
        assert isinstance(validation, dict)
        assert 'is_valid' in validation
        assert 'errors' in validation
        assert 'warnings' in validation
        assert isinstance(validation['is_valid'], bool)
    
    def test_suggest_escape_corrections(self):
        """Test sugerencias de corrección."""
        content = 'content with issues'
        suggestions = self.processor.suggest_escape_corrections(content)
        
        assert isinstance(suggestions, list)
        # Si hay sugerencias, deben tener estructura correcta
        for suggestion in suggestions:
            assert 'issue' in suggestion
            assert 'description' in suggestion
            assert 'correction' in suggestion
    
    def test_normalize_escape_sequences(self):
        """Test normalización de secuencias."""
        content = 'mixed \\"quotes\\" and \\\\n\\\\r\\\\t sequences'
        normalized = self.processor.normalize_escape_sequences(content)
        
        assert isinstance(normalized, str)
        assert len(normalized) > 0
    
    def test_integrate_with_content_handler(self):
        """Test integración con ExtremeContentHandler."""
        integration = self.processor.integrate_with_content_handler()
        
        assert isinstance(integration, dict)
        assert 'compatible' in integration
        assert 'handler_available' in integration
        assert 'integration_methods' in integration

    def test_fix_newline_escapes_specific(self):
        """Test específico para regex: re.sub(r"(?<!\\)\\n", "\n", content)"""
        processor = EscapeProcessor()
        
        # Test caso normal: \\n debe convertirse a \n
        test1 = "Normal\\nNewline"
        result1 = processor.fix_newline_escapes(test1)
        assert result1 == "Normal\nNewline"
        
        # Test caso escapado: \\\\n NO debe convertirse
        test2 = "Escaped\\\\nNewline"  
        result2 = processor.fix_newline_escapes(test2)
        assert result2 == "Escaped\\\\nNewline"
        
        # Test caso mixto
        test3 = "Normal\\nAndEscaped\\\\nMixed"
        result3 = processor.fix_newline_escapes(test3)
        assert result3 == "Normal\nAndEscaped\\\\nMixed"

    def test_fix_escape_issues_newline_type(self):
        """Test integración con fix_escape_issues"""
        processor = EscapeProcessor()
        test_content = "Test\\nContent"
        result = processor.fix_escape_issues(test_content, 'newline_escapes')
        assert "\n" in result  # Debe contener newline real
        assert result == "Test\nContent"
        
if __name__ == '__main__':
    pytest.main([__file__, '-v'])