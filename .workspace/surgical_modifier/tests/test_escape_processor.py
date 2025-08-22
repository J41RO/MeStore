#!/usr/bin/env python3
"""
Tests para EscapeProcessor - Procesador especializado de escape.
"""

import os
import sys

import pytest

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
        assert hasattr(self.processor, "advanced_patterns")
        assert hasattr(self.processor, "correction_config")
        assert hasattr(self.processor, "logger")

    def test_fix_escape_issues_double_escape(self):
        """Test corrección de escape doble."""
        content = "test \\\\\\\\n double escape"
        result = self.processor.fix_escape_issues(content, "double_escape")
        assert result != content  # Verificar que se aplicó algún cambio

    def test_fix_escape_issues_broken_json(self):
        """Test corrección de JSON escape roto."""
        content = 'text with \\"quotes\\" problem'
        result = self.processor.fix_escape_issues(content, "broken_json_escape")
        assert result != content  # Verificar que se aplicó corrección
        assert "quotes" in result  # Verificar que quotes están presentes

    def test_fix_escape_issues_empty_content(self):
        """Test con contenido vacío."""
        result = self.processor.fix_escape_issues("", "double_escape")
        assert result == ""

        result = self.processor.fix_escape_issues(None, "double_escape")
        assert result is None

    def test_analyze_escape_patterns(self):
        """Test análisis de patrones de escape."""
        content = 'mixed \\"quotes\\" and \\\\n sequences'
        analysis = self.processor.analyze_escape_patterns(content)

        assert isinstance(analysis, dict)
        assert "total_escapes" in analysis
        assert "escape_types" in analysis
        assert "problematic_sequences" in analysis
        assert analysis["total_escapes"] >= 0

    def test_validate_escape_integrity(self):
        """Test validación de integridad."""
        content = 'valid "quoted" content'
        validation = self.processor.validate_escape_integrity(content)

        assert isinstance(validation, dict)
        assert "is_valid" in validation
        assert "errors" in validation
        assert "warnings" in validation
        assert isinstance(validation["is_valid"], bool)

    def test_suggest_escape_corrections(self):
        """Test sugerencias de corrección."""
        content = "content with issues"
        suggestions = self.processor.suggest_escape_corrections(content)

        assert isinstance(suggestions, list)
        # Si hay sugerencias, deben tener estructura correcta
        for suggestion in suggestions:
            assert "issue" in suggestion
            assert "description" in suggestion
            assert "correction" in suggestion

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
        assert "compatible" in integration
        assert "handler_available" in integration
        assert "integration_methods" in integration

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
        result = processor.fix_escape_issues(test_content, "newline_escapes")
        assert "\n" in result  # Debe contener newline real
        assert result == "Test\nContent"

    # ========================================
    # TESTS ESPECÍFICOS PARA \t, ", ' LITERALES
    # ========================================

    def test_fix_tab_escapes_specific(self):
        """Test específico para procesamiento de tabs literales"""
        processor = EscapeProcessor()

        # Test tab normal: \\t debe convertirse a \t
        test1 = "Content\\twith\\ttabs"
        result1 = processor.fix_tab_escapes(test1)
        assert result1 == "Content\twith\ttabs"

        # Test tab escapado: \\\\t NO debe convertirse
        test2 = "Escaped\\\\ttab"
        result2 = processor.fix_tab_escapes(test2)
        assert result2 == "Escaped\\\\ttab"

        # Test contenido vacío
        assert processor.fix_tab_escapes("") == ""
        assert processor.fix_tab_escapes(None) == None

    def test_fix_quote_escapes_specific(self):
        """Test específico para procesamiento de comillas literales"""
        processor = EscapeProcessor()

        # Test comillas dobles
        test1 = 'Content\\"with\\"quotes'
        result1 = processor.fix_quote_escapes(test1)
        assert result1 == 'Content"with"quotes'

        # Test comillas simples
        test2 = "Content\\'with\\'quotes"
        result2 = processor.fix_quote_escapes(test2)
        assert result2 == "Content'with'quotes"

        # Test ambas comillas separadas
        test3 = 'Mixed\\"double'
        result3 = processor.fix_quote_escapes(test3)
        assert result3 == 'Mixed"double'

        test4 = "Also\\'single"
        result4 = processor.fix_quote_escapes(test4)
        assert result4 == "Also'single"

        # Test contenido vacío
        assert processor.fix_quote_escapes("") == ""
        assert processor.fix_quote_escapes(None) == None

    def test_literal_escapes_integration(self):
        """Test integración completa de escapes literales"""
        processor = EscapeProcessor()

        # Test tipo 'tab_escapes'
        test_content = "Mixed\\tcontent\\twith\\ttabs"
        result = processor.fix_escape_issues(test_content, "tab_escapes")
        expected = "Mixed\tcontent\twith\ttabs"
        assert result == expected

        # Test tipo 'quote_escapes'
        test_content2 = 'Content\\"with\\"quotes'
        result2 = processor.fix_escape_issues(test_content2, "quote_escapes")
        expected2 = 'Content"with"quotes'
        assert result2 == expected2

        # Test tipo 'literal_escapes' (combinado)
        test_content3 = 'Mixed\\tcontent\\"with\\ttypes'
        result3 = processor.fix_escape_issues(test_content3, "literal_escapes")
        expected3 = 'Mixed\tcontent"with\ttypes'
        assert result3 == expected3

    def test_advanced_patterns_integration(self):
        """Test que los nuevos patrones están en advanced_patterns"""
        processor = EscapeProcessor()

        # Verificar que los nuevos patrones existen
        required_patterns = ["tab_literals", "quote_literals", "single_quote_literals"]
        for pattern in required_patterns:
            assert pattern in processor.advanced_patterns
            assert hasattr(
                processor.advanced_patterns[pattern], "findall"
            )  # Es un objeto compilado

        # Test que los patrones funcionan
        test_content = 'Test\\twith\\"quotes'
        analysis = processor.analyze_escape_patterns(test_content)

        assert analysis["total_escapes"] > 0
        assert "tab_literals" in analysis["escape_types"]
        assert "quote_literals" in analysis["escape_types"]

    def test_suggest_escape_corrections_extended(self):
        """Test que las sugerencias incluyen nuevos tipos"""
        processor = EscapeProcessor()

        # Test contenido con tabs literales
        content_tabs = "Content\\twith\\ttabs"
        suggestions = processor.suggest_escape_corrections(content_tabs)
        tab_suggestions = [s for s in suggestions if s["issue"] == "tab_escapes"]
        assert len(tab_suggestions) > 0

        # Test contenido con comillas literales
        content_quotes = 'Content\\"with\\"quotes'
        suggestions2 = processor.suggest_escape_corrections(content_quotes)
        quote_suggestions = [s for s in suggestions2 if s["issue"] == "quote_escapes"]
        assert len(quote_suggestions) > 0

    def test_edge_cases_literal_escapes(self):
        """Test casos edge para escapes literales"""
        processor = EscapeProcessor()

        # Test múltiples tabs consecutivos
        test1 = "Content\\t\\t\\tmultiple"
        result1 = processor.fix_tab_escapes(test1)
        assert result1 == "Content\t\t\tmultiple"

        # Test comillas dobles múltiples
        test2 = 'Outer\\"inner\\"nested\\"quotes'
        result2 = processor.fix_quote_escapes(test2)
        assert result2 == 'Outer"inner"nested"quotes'

        # Test contenido con solo escapes
        test3 = "\\t\\t\\t"
        result3 = processor.fix_tab_escapes(test3)
        assert result3 == "\t\t\t"

        # Test contenido sin escapes
        test4 = "Normal content without escapes"
        result4 = processor.fix_tab_escapes(test4)
        assert result4 == "Normal content without escapes"

        result5 = processor.fix_quote_escapes(test4)
        assert result5 == "Normal content without escapes"

    def test_compatibility_with_existing_methods(self):
        """Test que los nuevos métodos no rompen funcionalidad existente"""
        processor = EscapeProcessor()

        # Test que fix_newline_escapes sigue funcionando
        test_newlines = "Content\\nwith\\nnewlines"
        result_newlines = processor.fix_newline_escapes(test_newlines)
        assert "\n" in result_newlines

        # Test que analyze_escape_patterns sigue funcionando
        test_content = "Mixed\\ncontent\\twith\\ttypes"
        analysis = processor.analyze_escape_patterns(test_content)
        assert isinstance(analysis, dict)
        assert "total_escapes" in analysis
        assert "escape_types" in analysis

        # Test que validate_escape_integrity sigue funcionando
        validation = processor.validate_escape_integrity(test_content)
        assert isinstance(validation, dict)
        assert "is_valid" in validation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
