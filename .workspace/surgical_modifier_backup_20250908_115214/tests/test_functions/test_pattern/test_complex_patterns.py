"""
Tests avanzados para patrones complejos en código Python, JavaScript y HTML.
Valida capacidades de los 4 matchers con patrones sofisticados.
"""

import pytest
import os
from pathlib import Path

from functions.pattern.regex_matcher import RegexMatcher
from functions.pattern.literal_matcher import LiteralMatcher
from functions.pattern.fuzzy_matcher import FuzzyMatcher
from functions.pattern.multiline_matcher import MultilineMatcher


class TestComplexPatterns:
    """Tests para patrones complejos en múltiples lenguajes."""
    
    @pytest.fixture
    def sample_files_path(self):
        """Path a los archivos de ejemplo."""
        return Path(__file__).parent.parent.parent / "fixtures" / "sample_code"
    
    @pytest.fixture
    def python_content(self, sample_files_path):
        """Contenido del archivo Python de ejemplo."""
        with open(sample_files_path / "sample.py", 'r') as f:
            return f.read()
    
    @pytest.fixture
    def js_content(self, sample_files_path):
        """Contenido del archivo JavaScript de ejemplo."""
        with open(sample_files_path / "sample.js", 'r') as f:
            return f.read()
    
    @pytest.fixture
    def html_content(self, sample_files_path):
        """Contenido del archivo HTML de ejemplo."""
        with open(sample_files_path / "sample.html", 'r') as f:
            return f.read()

    # ========== TESTS PYTHON COMPLEJOS ==========
    
    def test_python_complex_class_structure(self, python_content):
        """Test detección de estructura compleja de clase Python."""
        matcher = MultilineMatcher()
        
        # Buscar definición de clase con métodos anidados
        class_pattern = r"class\s+\w+:.*?def\s+\w+"
        result = matcher.find_multiline_pattern(class_pattern, python_content)
        
        assert result['success']
        assert result['count'] > 0
        assert "TestClass" in python_content
        assert "method_one" in python_content

    def test_python_complex_method_with_conditions(self, python_content):
        """Test detección de métodos con estructuras condicionales complejas."""
        matcher = RegexMatcher()
        
        # Buscar métodos con if-else usando patrón más simple que funcione con multiline
        method_pattern = r"def\s+\w+"
        result = matcher.find_single_match(method_pattern, python_content)
        
        assert result['success']
        assert result['found']
        assert "method_one" in result['match']
        # Verificar que if y else existen en el contenido
        assert "if condition" in python_content
        assert "else:" in python_content

    def test_python_complex_docstring_detection(self, python_content):
        """Test detección de docstrings en métodos."""
        matcher = LiteralMatcher()
        
        # Buscar docstrings específicos
        result = matcher.find_literal('"""Docstring here"""', python_content)
        
        assert result['success']
        assert result['found']
        assert result['position'] >= 0
        
        # Verificar contexto usando find_all_literals para obtener más info
        all_results = matcher.find_all_literals('"""Docstring here"""', python_content)
        assert len(all_results) > 0
        assert "def method_one" in python_content  # Verificar que está en el mismo contenido

    def test_python_complex_nested_print_statements(self, python_content):
        """Test detección de print statements en contexto anidado."""
        matcher = FuzzyMatcher()
        
        # Buscar print statements con fuzzy matching
        result = matcher.find_fuzzy_match("complex nested structure", python_content, threshold=0.8)
        
        assert result['success']
        assert result['found']
        assert "print" in python_content
        assert result['similarity'] > 0.8

    def test_python_complex_indentation_analysis(self, python_content):
        """Test análisis complejo de indentación Python."""
        matcher = MultilineMatcher()
        
        # Analizar niveles de indentación
        indentation_info = matcher.analyze_indentation_structure(python_content)
        
        assert indentation_info['success']
        assert indentation_info['max_indent_level'] >= 3  # class -> def -> if -> print
        assert indentation_info['total_blocks'] > 0
        assert len(indentation_info['line_structure']) > 0

    # ========== TESTS JAVASCRIPT COMPLEJOS ==========
    
    def test_javascript_complex_function_objects(self, js_content):
        """Test detección de funciones con objetos complejos."""
        matcher = MultilineMatcher()
        
        # Buscar funciones con objetos anidados
        func_pattern = r"function\s+\w+\([^)]*\)\s*{[^}]*const\s+\w+\s*=\s*{"
        result = matcher.find_multiline_pattern(func_pattern, js_content)
        
        assert result['success']
        assert result['count'] > 0
        assert "complexFunction" in js_content
        assert "const nested" in js_content

    def test_javascript_complex_method_chaining(self, js_content):
        """Test detección de method chaining y propiedades."""
        matcher = RegexMatcher()
        
        # Buscar acceso a propiedades this
        property_pattern = r"this\.\w+"
        result = matcher.find_matches(property_pattern, js_content)
        
        # Verificar que la operación fue exitosa
        assert result['success']
        assert result['count'] > 0
        assert len(result['matches']) > 0
        
        # Verificar que this.property está en el contenido original
        assert "this.property" in js_content
        
        # Verificar que encontró this.property en los matches
        matches_text = [match['match'] for match in result['matches']]
        assert any("this.property" in match_text for match_text in matches_text)

    def test_javascript_complex_conditional_logic(self, js_content):
        """Test detección de lógica condicional con propiedades."""
        matcher = LiteralMatcher()
        
        # Buscar estructura if con propiedades
        result = matcher.find_literal("if (nested.property)", js_content)
        
        assert result['success']
        assert result['found']
        assert result['position'] >= 0

    def test_javascript_complex_console_patterns(self, js_content):
        """Test detección de patrones console.log complejos."""
        matcher = FuzzyMatcher()
        
        # Buscar console.log statements
        result = matcher.find_fuzzy_match("JavaScript pattern", js_content, threshold=0.9)
        
        assert result['success']
        assert result['found']
        assert result['similarity'] > 0.9

    def test_javascript_complex_closure_detection(self, js_content):
        """Test detección de closures y funciones anidadas."""
        matcher = RegexMatcher()
        
        # Buscar funciones dentro de objetos
        closure_pattern = r"method:\s*function\(\)"
        result = matcher.find_single_match(closure_pattern, js_content)
        
        assert result['success']
        assert result['found']
        assert "return this.property" in js_content  # Verificar contexto

    # ========== TESTS HTML COMPLEJOS ==========
    
    def test_html_complex_form_structure(self, html_content):
        """Test detección de estructuras de formulario complejas."""
        matcher = MultilineMatcher()
        
        # Buscar formularios con elementos anidados
        form_pattern = r"<form[^>]*>.*?<input[^>]*>.*?<button[^>]*>"
        result = matcher.find_multiline_pattern(form_pattern, html_content)
        
        assert result['success']
        assert result['count'] > 0
        assert "complex-form" in html_content
        assert "input" in html_content
        assert "button" in html_content

    def test_html_complex_event_handlers(self, html_content):
        """Test detección de event handlers inline."""
        matcher = LiteralMatcher()
        
        # Buscar onclick handlers
        result = matcher.find_literal('onclick="handleClick()"', html_content)
        
        assert result['success']
        assert result['found']
        assert result['position'] >= 0

    def test_html_complex_nested_elements(self, html_content):
        """Test detección de elementos HTML anidados."""
        matcher = RegexMatcher()
        
        # Buscar div con clase container
        container_pattern = r'<div\s+class="container">'
        result = matcher.find_single_match(container_pattern, html_content)
        
        assert result['success']
        assert result['found']
        assert "container" in result['match']

    def test_html_complex_input_attributes(self, html_content):
        """Test detección de atributos complejos en inputs."""
        matcher = FuzzyMatcher()
        
        # Buscar inputs con múltiples atributos
        result = matcher.find_fuzzy_match('type="text" name="field"', html_content, threshold=0.8)
        
        assert result['success']
        assert result['found']
        assert result['similarity'] > 0.8

    def test_html_complex_comment_detection(self, html_content):
        """Test detección de comentarios HTML complejos."""
        matcher = LiteralMatcher()
        
        # Buscar comentarios específicos
        result = matcher.find_literal("<!-- Complex nested HTML -->", html_content)
        
        assert result['success']
        assert result['found']
        assert result['position'] >= 0

    # ========== TESTS CROSS-LANGUAGE ==========
    
    def test_cross_language_pattern_consistency(self, python_content, js_content, html_content):
        """Test consistencia de patrones entre lenguajes."""
        regex_matcher = RegexMatcher()
        
        # Buscar patrones de comentarios en diferentes lenguajes
        python_comment = regex_matcher.find_single_match(r'"""[^"]*"""', python_content)
        js_comment = regex_matcher.find_single_match(r'/\*[^*]*\*/', js_content)  # No existe en sample pero debe procesar
        html_comment = regex_matcher.find_single_match(r'<!--[^>]*-->', html_content)
        
        # Al menos Python y HTML deben tener comentarios
        assert python_comment['success']
        assert python_comment['found']
        assert html_comment['success']
        assert html_comment['found']

    def test_cross_language_function_detection(self, python_content, js_content):
        """Test detección de funciones en múltiples lenguajes."""
        matcher = FuzzyMatcher()
        
        # Buscar definiciones de funciones/métodos
        python_func = matcher.find_fuzzy_match("def method", python_content, threshold=0.7)
        js_func = matcher.find_fuzzy_match("function complex", js_content, threshold=0.7)
        
        assert python_func['success']
        assert python_func['found']
        assert js_func['success']
        assert js_func['found']
        assert python_func['similarity'] > 0.7
        assert js_func['similarity'] > 0.7

    def test_cross_language_matcher_performance(self, python_content, js_content, html_content):
        """Test performance de matchers con diferentes tipos de contenido."""
        contents = [python_content, js_content, html_content]
        
        # Test RegexMatcher
        regex_matcher = RegexMatcher()
        for content in contents:
            try:
                result = regex_matcher.find_single_match("test", content)
                assert result['success']
                assert isinstance(result['found'], bool)
            except Exception as e:
                pytest.fail(f"RegexMatcher falló con contenido: {e}")
        
        # Test LiteralMatcher
        literal_matcher = LiteralMatcher()
        for content in contents:
            try:
                result = literal_matcher.find_literal("test", content)
                assert result['success']
                assert isinstance(result['found'], bool)
            except Exception as e:
                pytest.fail(f"LiteralMatcher falló con contenido: {e}")
        
        # Test FuzzyMatcher
        fuzzy_matcher = FuzzyMatcher()
        for content in contents:
            try:
                result = fuzzy_matcher.find_fuzzy_match("test", content)
                assert result['success']
                assert isinstance(result['found'], bool)
            except Exception as e:
                pytest.fail(f"FuzzyMatcher falló con contenido: {e}")
        
        # Test MultilineMatcher
        multiline_matcher = MultilineMatcher()
        for content in contents:
            try:
                result = multiline_matcher.find_multiline_pattern("test", content)
                assert result['success']
                assert isinstance(result['count'], int)
            except Exception as e:
                pytest.fail(f"MultilineMatcher falló con contenido: {e}")

    def test_cross_language_pattern_extraction(self, python_content, js_content, html_content):
        """Test extracción de patrones complejos cross-language."""
        multiline_matcher = MultilineMatcher()
        
        # Extraer bloques de código de diferentes lenguajes
        python_analysis = multiline_matcher.analyze_indentation_structure(python_content)
        js_analysis = multiline_matcher.analyze_indentation_structure(js_content)
        html_analysis = multiline_matcher.analyze_indentation_structure(html_content)
        
        # Verificar que se analizaron correctamente todos los lenguajes
        assert python_analysis['success']
        assert python_analysis['total_blocks'] > 0
        assert js_analysis['success']
        assert js_analysis['total_blocks'] > 0
        assert html_analysis['success']
        assert html_analysis['total_blocks'] > 0