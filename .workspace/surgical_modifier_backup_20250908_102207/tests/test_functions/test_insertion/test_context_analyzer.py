"""
Tests unitarios para context_analyzer.py
"""
import pytest
from functions.insertion.context_analyzer import (
    analyze_context, 
    ContextAnalyzer, 
    ContextType, 
    ContextAnalysis
)

class TestContextAnalyzer:
    
    def test_analyze_function_context(self):
        """Test análisis de contexto dentro de función"""
        content = """def example_function():
    existing_code = True
    # insertion point here
    return existing_code"""
        
        result = analyze_context(content, "existing_code = True", "after")
        
        assert isinstance(result, ContextAnalysis)
        assert result.context_type == ContextType.FUNCTION_BODY
        assert result.indentation_level >= 0
        
    def test_analyze_class_context(self):
        """Test análisis de contexto dentro de clase"""
        content = """class ExampleClass:
    def method(self):
        pass
    # insertion point here"""
        
        result = analyze_context(content, "def method", "after")
        
        assert result.context_type in [ContextType.CLASS_BODY, ContextType.FUNCTION_BODY]
        assert isinstance(result.surrounding_code, dict)
        
    def test_analyze_module_context(self):
        """Test análisis de contexto a nivel módulo"""
        content = """import os
import sys
# insertion point here

def main():
    pass"""
        
        result = analyze_context(content, "import sys", "after")
        
        assert result.compatibility_score >= 0.0
        assert isinstance(result.insertion_hints, list)
        
    def test_context_analyzer_direct(self):
        """Test uso directo de ContextAnalyzer"""
        analyzer = ContextAnalyzer()
        
        content = "def test():\n    pass"
        result = analyzer.analyze_context(content, "def test", "after")
        
        assert isinstance(result, ContextAnalysis)
        assert result.suggested_indentation is not None

    def test_context_analysis_attributes(self):
        """Test que ContextAnalysis tiene todos los atributos requeridos"""
        content = "def example():\n    pass"
        result = analyze_context(content, "def example", "after")
        
        # Verificar todos los atributos requeridos
        assert hasattr(result, 'context_type')
        assert hasattr(result, 'indentation_level')
        assert hasattr(result, 'surrounding_code')
        assert hasattr(result, 'suggested_indentation')
        assert hasattr(result, 'insertion_hints')
        assert hasattr(result, 'compatibility_score')
        
    def test_position_type_string_conversion(self):
        """Test conversión de position_type como string"""
        content = "def test():\n    pass"
        
        # Test con string en lugar de enum
        result = analyze_context(content, "def test", "before")
        assert isinstance(result, ContextAnalysis)
        
    def test_different_context_types(self):
        """Test detección de diferentes tipos de contexto"""
        
        # Test función
        func_content = "def my_function():\n    return True"
        func_result = analyze_context(func_content, "def my_function", "after")
        assert func_result.context_type == ContextType.FUNCTION_BODY
        
        # Test clase
        class_content = "class MyClass:\n    pass"
        class_result = analyze_context(class_content, "class MyClass", "after")
        assert class_result.context_type in [ContextType.CLASS_BODY, ContextType.MODULE_LEVEL]
        
    def test_compatibility_score_range(self):
        """Test que compatibility_score está en rango válido"""
        content = "def test():\n    pass"
        result = analyze_context(content, "def test", "after")
        
        assert 0.0 <= result.compatibility_score <= 1.0
        
    def test_surrounding_code_structure(self):
        """Test estructura del surrounding_code"""
        content = """line1
line2
target_line
line4
line5"""
        
        result = analyze_context(content, "target_line", "after")
        
        assert isinstance(result.surrounding_code, dict)
        assert 'before' in result.surrounding_code
        assert 'current' in result.surrounding_code
        assert 'after' in result.surrounding_code