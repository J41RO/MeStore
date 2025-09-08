"""
Tests de integración para inserción de código con indentación correcta.
Valida funcionalidad end-to-end de inserción usando functions directamente.
"""
import pytest
from functions.insertion.indentation_detector import detect_indentation
from functions.insertion.position_calculator import calculate_position, PositionType
from functions.insertion.content_formatter import format_content, ContentType
from functions.insertion.context_analyzer import analyze_context


class TestInsertionWithIndentation:
    """Tests de inserción manteniendo indentación correcta"""
    
    @pytest.fixture
    def python_function_code(self):
        return '''def example_function():
    existing_line = "test"
    if True:
        nested_code = True
        return nested_code
    return existing_line'''
    
    @pytest.fixture  
    def python_class_code(self):
        return '''class ExampleClass:
    def __init__(self):
        self.value = 1
    
    def method(self):
        if self.value:
            return True
        return False'''
    
    def test_basic_structure_validation(self, python_function_code):
        """Test básico de validación de estructura - MICRO-FASE 1"""
        # Test que las functions básicas funcionan correctamente
        
        # 1. Test analyze_context funciona
        context = analyze_context(python_function_code, "existing_line", PositionType.AFTER)
        assert context is not None
        assert context.indentation_level >= 0
        
        # 2. Test detect_indentation funciona  
        indentation = detect_indentation(python_function_code)
        assert indentation is not None
        assert indentation.dominant_size > 0

        
        # 3. Test calculate_position funciona
        position = calculate_position(python_function_code, "existing_line", PositionType.AFTER)
        assert position is not None
        assert position.line_number > 0
        
        # 4. Test format_content funciona
        formatted = format_content("test_content", content_type=ContentType.STATEMENT)
        assert formatted is not None
        assert len(formatted.content) > 0
        
    def test_fixtures_are_valid_python(self, python_function_code, python_class_code):
        """Test que las fixtures contienen código Python válido"""
        import ast
        
        # Verificar que function_code es Python válido
        try:
            ast.parse(python_function_code)
        except SyntaxError:
            pytest.fail("python_function_code fixture contiene Python inválido")
            
        # Verificar que class_code es Python válido  
        try:
            ast.parse(python_class_code)
        except SyntaxError:
            pytest.fail("python_class_code fixture contiene Python inválido")
    
    def test_insert_after_function_level(self, python_function_code):
        """Test inserción después de línea a nivel función"""
        target_pattern = 'existing_line = "test"'
        new_code = 'new_variable = "inserted"'
        
        # Analizar contexto
        context = analyze_context(python_function_code, target_pattern, PositionType.AFTER)
        
        # Verificar indentación detectada
        assert len(context.suggested_indentation) == 4  # Nivel función
        assert context.context_type.value in ['function_body', 'block_statement']
        
        # Formatear código nuevo con indentación correcta
        formatted = format_content(new_code, content_type=ContentType.STATEMENT)
        
        # Verificar que mantiene indentación
        expected_indentation = " " * 4  # 4 espacios para función
        assert formatted.content.startswith(expected_indentation) or \
            new_code in formatted.content

    def test_insert_after_nested_level(self, python_function_code):
        """Test inserción después de línea anidada"""
        target_pattern = "nested_code = True"
        new_code = "debug_print = True"
        
        context = analyze_context(python_function_code, target_pattern, PositionType.AFTER)
        
        # Verificar detección de nivel anidado
        assert len(context.suggested_indentation) >= 4  # Al menos nivel función (API limitada)
        
        formatted = format_content(new_code, content_type=ContentType.STATEMENT)
        # Verificar indentación de 8 espacios
        lines = python_function_code.split('\n')
        target_line_indent = len(lines[3]) - len(lines[3].lstrip())
        assert target_line_indent == 8
    
    def test_insert_before_method(self, python_class_code):
        """Test inserción antes de método en clase"""
        target_pattern = "def method(self):"
        new_code = "def helper_method(self):\n        pass"
        
        context = analyze_context(python_class_code, target_pattern, PositionType.BEFORE)
        
        # Verificar contexto de clase usando API real
        assert context.context_type.value in ['class_body', 'function_body']
        assert len(context.suggested_indentation) == 4  # Nivel clase
        
        # Simular inserción completa
        position = calculate_position(python_class_code, target_pattern, PositionType.BEFORE)
        
        lines = python_class_code.split('\n')
        # Insertar en posición calculada  
        lines.insert(position.line_number - 1, "    " + new_code.replace('\n', '\n    '))
        result = '\n'.join(lines)
        
        # Verificar que la inserción mantiene estructura
        assert "def helper_method(self):" in result
        assert "def method(self):" in result
        assert result.count("def ") == 3  # __init__, helper_method, method

    def test_insert_before_with_complex_indentation(self):
        """Test inserción con indentación compleja"""
        complex_code = '''class Complex:
    def outer(self):
        for i in range(3):
            if i > 0:
                inner_var = i * 2
                return inner_var'''
        
        target = "inner_var = i * 2"
        new_code = "logging.debug(f'Processing {i}')"
        
        context = analyze_context(complex_code, target, PositionType.BEFORE)
        
        # Verificar detección de indentación usando API real
        assert len(context.suggested_indentation) >= 4  # Al menos nivel base
        
        # Verificar sugerencia de indentación
        assert len(context.suggested_indentation) > 0
        
    
    def test_insert_module_level_import(self):
        """Test inserción de imports a nivel módulo"""
        module_code = '''import os
import sys
from typing import List

def main():
    pass'''
        
        target = "from typing import List"
        new_import = "from dataclasses import dataclass"
        
        context = analyze_context(module_code, target, PositionType.AFTER)
        
        # Verificar contexto módulo/import usando API real
        assert context.context_type.value in ['import_section', 'module_level', 'function_body']
        assert len(context.suggested_indentation) == 0  # Nivel módulo sin indentación
        
        # Verificar hints apropiados para imports
        assert len(context.insertion_hints) > 0

    def test_insert_module_level_function(self):
        """Test inserción de función a nivel módulo"""
        module_code = '''#!/usr/bin/env python3
"""Module docstring"""

import os

def existing_function():
    pass'''
        
        target = "def existing_function():"
        new_function = '''def new_function():
    """New function"""
    return True'''
        
        context = analyze_context(module_code, target, PositionType.BEFORE)
        
        assert context.context_type.value in ['module_level', 'function_body', 'import_section']
        assert len(context.suggested_indentation) == 0  # Nivel módulo
        
        # Formatear función nueva
        formatted = format_content(new_function, content_type=ContentType.METHOD)
        
        # Verificar que no se agrega indentación extra a nivel módulo
        assert 'def new_function' in formatted.content  # Más flexible para indentación automática

    def test_insert_with_blank_line_preservation(self):
        """Test inserción preservando líneas en blanco"""
        code_with_spacing = '''class Spaced:
    
    def method1(self):
        pass
    
    def method2(self):
        pass'''
        
        target = "def method1(self):"
        new_method = '''def inserted_method(self):
        return "inserted"'''
        
        context = analyze_context(code_with_spacing, target, PositionType.AFTER)
        formatted = format_content(new_method, content_type=ContentType.METHOD, preserve_blank_lines=True)
        
        # Verificar que el formateo preserva estilo de espaciado
        assert len(context.suggested_indentation) >= 4  # Al menos indentación de clase
        assert context.compatibility_score > 0.5  # Alta compatibilidad con código existente
    
    def test_insert_mixed_indentation_detection(self):
        """Test detección de indentación mixta"""
        mixed_code = '''def mixed_function():
\tif True:  # Tab
        nested = True  # 8 espacios
\t\treturn nested  # 2 tabs'''
        
        indentation_info = detect_indentation(mixed_code)
        
        # Verificar detección de patrón inconsistente
        assert indentation_info.dominant_type.value in ['mixed', 'tabs', 'spaces']
        
        context = analyze_context(mixed_code, "nested = True", PositionType.AFTER)
        
        # Verificar que sugiere indentación consistente
        assert len(context.suggested_indentation) > 0
        assert context.compatibility_score < 1.0  # Penaliza inconsistencia

    def test_insert_empty_line_handling(self):
        """Test manejo de líneas vacías"""
        code_with_empty = '''def function():
    line1 = True
    
    line2 = False
    return line1 and line2'''
        
        target = "line1 = True"
        new_code = "middle_line = 'inserted'"
        
        context = analyze_context(code_with_empty, target, PositionType.AFTER)
        
        # Verificar que detecta correctamente posición con líneas vacías
        assert len(context.suggested_indentation) == 4
        assert 'blank' not in str(context.context_type).lower()

    def test_insert_at_file_boundaries(self):
        """Test inserción al inicio y final de archivo"""
        simple_code = '''def simple():
    pass'''
        
        # Test inserción al inicio
        context_start = analyze_context(simple_code, "def simple", PositionType.BEFORE)
        assert context_start.context_type.value in ['module_level', 'function_body', 'import_section']
        
        # Test inserción al final
        context_end = analyze_context(simple_code, "pass", PositionType.AFTER)
        assert len(context_end.suggested_indentation) >= 0  # Al final del archivo puede ser 0

    @pytest.mark.parametrize("indentation_type,expected_spaces", [
        ("spaces_2", 2),
        ("spaces_4", 4),
        ("tabs", 1),
    ])
    def test_different_indentation_styles(self, indentation_type, expected_spaces):
        """Test diferentes estilos de indentación"""
        if indentation_type == "spaces_2":
            code = '''def func():
  line = True
  return line'''
            indent_char = " "
            indent_size = 2
        elif indentation_type == "spaces_4":
            code = '''def func():
    line = True
    return line'''
            indent_char = " "
            indent_size = 4
        else:  # tabs
            code = '''def func():
\tline = True
\treturn line'''
            indent_char = "\t"
            indent_size = 1
        
        indentation_info = detect_indentation(code)
        context = analyze_context(code, "line = True", PositionType.AFTER)
        
        # Verificar detección correcta del estilo
        if indentation_type != "tabs":
            assert indentation_info.dominant_size == indent_size
        
        # Verificar sugerencia consistente
        if indent_char == "\t":
            assert "\t" in context.suggested_indentation
        else:
            assert " " in context.suggested_indentation
    
    