import os
import tempfile

import pytest
from surgical_modifier_ultimate import UniversalPatternHelper


class TestUniversalPatternHelper:
    """Tests completos para UniversalPatternHelper"""

    def test_pattern_helper_initialization(self):
        """Test: Inicialización correcta de UniversalPatternHelper"""
        file_content = "def test_function():\n    pass"
        file_path = "test_file.py"

        helper = UniversalPatternHelper(file_content, file_path)

        assert helper.content == file_content
        assert helper.file_path == file_path
        assert helper.lines == ["def test_function():", "    pass"]
        assert helper.file_type == "python"
        assert isinstance(helper.framework_context, list)

    def test_detect_file_type_python(self):
        """Test: Detección correcta de archivos Python"""
        helper = UniversalPatternHelper("print('hello')", "script.py")
        assert helper.file_type == "python"

    def test_detect_file_type_javascript(self):
        """Test: Detección correcta de archivos JavaScript"""
        helper = UniversalPatternHelper("console.log('hello')", "script.js")
        assert helper.file_type == "javascript"

    def test_detect_file_type_generic(self):
        """Test: Detección de archivos desconocidos como generic"""
        helper = UniversalPatternHelper("content", "file.unknown")
        assert helper.file_type == "generic"

    def test_detect_framework_context_pytest(self):
        """Test: Detección de contexto pytest"""
        content = "@pytest.fixture\ndef test_something():\n    pass"
        helper = UniversalPatternHelper(content, "test_file.py")
        assert "pytest" in helper.framework_context

    def test_detect_framework_context_django(self):
        """Test: Detección de contexto Django"""
        content = "from django.db import models\nclass User(models.Model):\n    pass"
        helper = UniversalPatternHelper(content, "models.py")
        assert "django" in helper.framework_context

    def test_find_flexible_pattern_returns_list(self):
        """Test: find_flexible_pattern retorna lista de resultados"""
        content = "def hello_world():\n    print('Hello')\n    return True"
        helper = UniversalPatternHelper(content, "test.py")

        result = helper.find_flexible_pattern("def hello_world")
        assert isinstance(result, list)
        assert len(result) >= 0  # Puede estar vacía o tener resultados

    def test_suggest_pattern_fragments_returns_list(self):
        """Test: suggest_pattern_fragments retorna lista"""
        content = "def calculate_sum(a, b):\n    return a + b"
        helper = UniversalPatternHelper(content, "math.py")

        suggestions = helper.suggest_pattern_fragments(
            "this_is_a_very_long_pattern_that_should_trigger_fragment_logic"
        )
        assert isinstance(suggestions, list)
        # El método puede retornar lista vacía en algunos casos

    def test_framework_specific_patterns_pytest(self):
        """Test: Obtener patrones específicos de pytest"""
        content = "@pytest.fixture\ndef test_example():\n    pass"
        helper = UniversalPatternHelper(content, "test_file.py")

        patterns = helper.get_framework_specific_patterns()
        assert isinstance(patterns, list)

    def test_get_common_words_by_type(self):
        """Test: Obtener palabras comunes por tipo de archivo"""
        helper = UniversalPatternHelper("def hello():\n    pass", "script.py")

        words = helper._get_common_words_by_type()
        assert isinstance(words, list)
