"""
Tests unitarios para ContentFormatter.
Cobertura mínima requerida: 90% de métodos principales.
"""

import pytest
from functions.insertion.content_formatter import (
    ContentFormatter, 
    ContentType, 
    FormattedContent
)
from functions.insertion.position_calculator import PositionType


class TestContentFormatter:
    """Tests para la clase ContentFormatter."""
    
    @pytest.fixture
    def formatter(self):
        """Fixture que proporciona una instancia de ContentFormatter."""
        return ContentFormatter()
    
    def test_content_formatter_initialization(self, formatter):
        """Test que ContentFormatter se inicializa correctamente."""
        assert formatter is not None
        assert formatter.indentation_detector is not None
        assert formatter.position_calculator is not None
    
    def test_format_content_basic(self, formatter):
        """Test formateo básico de contenido."""
        content = "def test_method(): pass"
        context = "class TestClass:\n    pass"
        
        result = formatter.format_content(content, context)
        
        assert isinstance(result, FormattedContent)
        assert result.content_type == ContentType.METHOD
        assert result.indentation_level == 4
        assert "def test_method():" in result.content
    
    def test_format_content_with_type(self, formatter):
        """Test formateo con tipo específico."""
        content = "x = 1"
        context = "def function():\n    pass"
        
        result = formatter.format_content(content, context, ContentType.STATEMENT)
        
        assert result.content_type == ContentType.STATEMENT
        assert "x = 1" in result.content
    
    def test_apply_indentation_spaces(self, formatter):
        """Test aplicación de indentación con espacios."""
        content = "line1\nline2"
        
        # Mock indent_info
        class MockIndentInfo:
            dominant_type = type('obj', (object,), {'value': 'spaces'})
            dominant_size = 4
        
        result = formatter.apply_indentation(content, MockIndentInfo())
        
        lines = result.split('\n')
        assert lines[0] == "    line1"
        assert lines[1] == "    line2"
    
    def test_normalize_line_endings(self, formatter):
        """Test normalización de terminaciones de línea."""
        content_with_crlf = "line1\r\nline2\rline3\n"
        
        result = formatter.normalize_line_endings(content_with_crlf)
        
        assert result == "line1\nline2\nline3\n"
        assert '\r' not in result
    
    def test_remove_trailing_whitespace(self, formatter):
        """Test eliminación de espacios trailing."""
        content = "line1   \nline2\t\n   \nline4"
        
        result = formatter.remove_trailing_whitespace(content)
        
        lines = result.split('\n')
        assert lines[0] == "line1"
        assert lines[1] == "line2"
        assert lines[2] == ""
        assert lines[3] == "line4"
    
    def test_format_class_definition(self, formatter):
        """Test formateo de definición de clase."""
        content = "class NewClass:\n    def __init__(self): pass"
        context = "existing_code = True"
        
        result = formatter.format_class_definition(content, context)
        
        assert result.content_type == ContentType.CLASS
        assert "class NewClass:" in result.content
        assert result.has_trailing_newline
    
    def test_format_method_definition(self, formatter):
        """Test formateo de definición de método."""
        content = "def new_method(self):\n    return 'test'"
        context = "class TestClass:\n    pass"
        
        result = formatter.format_method_definition(content, context)
        
        assert result.content_type == ContentType.METHOD
        assert "def new_method(self):" in result.content
        assert result.indentation_level == 4
    
    def test_format_statement(self, formatter):
        """Test formateo de declaración simple."""
        content = "x = 42"
        context = "def function(): pass"
        
        result = formatter.format_statement(content, context)
        
        assert result.content_type == ContentType.STATEMENT
        assert "x = 42" in result.content
    
    def test_format_block(self, formatter):
        """Test formateo de bloque de código."""
        content = "if condition:\n    do_something()\nelse:\n    do_other()"
        context = "def function(): pass"
        
        result = formatter.format_block(content, context)
        
        assert result.content_type == ContentType.BLOCK
        assert "if condition:" in result.content
        assert result.has_trailing_newline
    
    def test_format_for_position_before(self, formatter):
        """Test formateo para posición BEFORE."""
        content = "new_line = True"
        context = "existing_code()"
        
        result = formatter.format_for_position(content, context, PositionType.BEFORE)
        
        assert "new_line = True" in result.content
        assert result.has_trailing_newline
    
    def test_format_for_position_after(self, formatter):
        """Test formateo para posición AFTER."""
        content = "new_line = True"
        context = "existing_code()"
        
        result = formatter.format_for_position(content, context, PositionType.AFTER)
        
        assert "new_line = True" in result.content
        assert result.content.startswith('\n')
    
    def test_format_for_position_inside(self, formatter):
        """Test formateo para posición INSIDE."""
        content = "inner_statement = value"
        context = "def function():\n    existing_code()"
        
        result = formatter.format_for_position(content, context, PositionType.INSIDE)
        
        assert "inner_statement = value" in result.content
        assert result.indentation_level == 8  # Doble indentación
    
    def test_validate_formatted_content_valid(self, formatter):
        """Test validación de contenido válido."""
        content = "    def method(self):\n        return True"
        context = "class Test: pass"
        
        result = formatter.validate_formatted_content(content, context)
        
        assert result is True
    
    def test_validate_formatted_content_invalid_empty(self, formatter):
        """Test validación de contenido vacío."""
        content = ""
        context = "class Test: pass"
        
        result = formatter.validate_formatted_content(content, context)
        
        assert result is False
    
    def test_validate_formatted_content_invalid_indentation(self, formatter):
        """Test validación de indentación inválida."""
        content = "def method():\npass"  # Sin indentación apropiada
        context = "class Test: pass"
        
        result = formatter.validate_formatted_content(content, context)
        
        assert result is False
    
    def test_optimize_whitespace(self, formatter):
        """Test optimización de espacios en blanco."""
        content = "line1\n\n\n\nline2   \n\n\nline3"
        
        result = formatter.optimize_whitespace(content)
        
        lines = result.split('\n')
        # Verificar que espacios excesivos se redujeron
        assert "line1" in result
        assert "line2" in result  
        assert "line3" in result
        # No debe tener más de 2 líneas en blanco consecutivas
        assert "\n\n\n\n" not in result
    
    def test_preserve_code_structure(self, formatter):
        """Test preservación de estructura de código."""
        original = "x = 1  # Important comment"
        formatted = "    x = 1"
        
        result = formatter.preserve_code_structure(formatted, original)
        
        assert "# Important comment" in result
    
    def test_handle_special_characters(self, formatter):
        """Test manejo de caracteres especiales."""
        # Usar comillas curvas reales para el test
        content = 'text = "hello"'  # Estas son comillas curvas
        
        result = formatter.handle_special_characters(content)
        
        # Verificar que se convirtieron a comillas rectas
        assert '"hello"' in result
        assert '"' not in result  # No deben quedar comillas curvas
        assert '"' not in result  # No deben quedar comillas curvas
    
    def test_detect_content_type_class(self, formatter):
        """Test detección de tipo de contenido - clase."""
        content = "class MyClass:\n    pass"
        
        result = formatter._detect_content_type(content)
        
        assert result == ContentType.CLASS
    
    def test_detect_content_type_method(self, formatter):
        """Test detección de tipo de contenido - método."""
        content = "def my_method(self):\n    return True"
        
        result = formatter._detect_content_type(content)
        
        assert result == ContentType.METHOD
    
    def test_detect_content_type_block(self, formatter):
        """Test detección de tipo de contenido - bloque."""
        content = "if condition:\n    do_something()\nelse:\n    do_other()"
        
        result = formatter._detect_content_type(content)
        
        assert result == ContentType.BLOCK
    
    def test_detect_content_type_statement(self, formatter):
        """Test detección de tipo de contenido - declaración."""
        content = "x = 42"
        
        result = formatter._detect_content_type(content)
        
        assert result == ContentType.STATEMENT
    
    def test_integration_with_indentation_detector(self, formatter):
        """Test integración con IndentationDetector."""
        context = "class Test:\n    def method(self): pass"
        content = "new_method_content"
        
        result = formatter.format_content(content, context)
        
        # Debe usar la indentación detectada del contexto (4 espacios)
        assert result.indentation_level == 4
        assert result.content.startswith('    ')
    
    def test_integration_with_position_calculator(self, formatter):
        """Test integración con PositionCalculator."""
        content = "statement = value"
        context = "def function():\n    existing_code()"
        
        # Test todos los tipos de posición
        before = formatter.format_for_position(content, context, PositionType.BEFORE)
        after = formatter.format_for_position(content, context, PositionType.AFTER)
        inside = formatter.format_for_position(content, context, PositionType.INSIDE)
        
        assert before.content != after.content != inside.content
        assert inside.indentation_level > before.indentation_level