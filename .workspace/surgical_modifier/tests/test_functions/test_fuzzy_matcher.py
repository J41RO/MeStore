import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from functions.matching.fuzzy_matcher import FuzzyMatcher


class TestFuzzyMatcher:
    """Tests para la clase FuzzyMatcher"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.fuzzy_matcher = FuzzyMatcher()
    
    def test_normalize_whitespace_basic(self):
        """Test normalización básica de espacios"""
        text = '  hello    world  '
        expected = 'hello world'
        result = self.fuzzy_matcher.normalize_whitespace(text)
        assert result == expected
    
    def test_normalize_whitespace_multiline(self):
        """Test normalización de múltiples saltos de línea"""
        text = 'line1\n\n\nline2\n   line3   \n'
        expected = 'line1\nline2\nline3'
        result = self.fuzzy_matcher.normalize_whitespace(text)
        assert result == expected
    
    def test_fuzzy_match_exact_mode_false(self):
        """Test matching exacto (flexible=False)"""
        target = 'class User:'
        line = 'class User:'
        assert self.fuzzy_matcher.fuzzy_match(target, line, flexible=False) == True
        
        # No debe hacer match si hay diferencias de espaciado en modo exacto
        line_spaces = 'class  User:'  # espacios extra
        assert self.fuzzy_matcher.fuzzy_match(target, line_spaces, flexible=False) == False
    
    def test_fuzzy_match_flexible_mode_true(self):
        """Test matching flexible (flexible=True)"""
        target = 'class User:'
        
        # Debe hacer match con espacios extra
        line_spaces = 'class  User:'
        assert self.fuzzy_matcher.fuzzy_match(target, line_spaces, flexible=True) == True
        
        # Debe hacer match con espacios al inicio/final
        line_padded = '  class User:  '
        assert self.fuzzy_matcher.fuzzy_match(target, line_padded, flexible=True) == True
        
        # Debe hacer match con tabs vs espacios
        line_tabs = 'class\tUser:'
        assert self.fuzzy_matcher.fuzzy_match(target, line_tabs, flexible=True) == True
    
    def test_fuzzy_match_default_behavior_backward_compatibility(self):
        """Test backward compatibility - comportamiento por defecto"""
        target = 'def hello():'
        line = 'def hello():'
        
        # Sin especificar flexible, debe usar matching exacto (backward compatibility)
        assert self.fuzzy_matcher.fuzzy_match(target, line) == True
        
        line_spaces = 'def  hello():'
        assert self.fuzzy_matcher.fuzzy_match(target, line_spaces) == False
    
    def test_find_target_line_exact_mode(self):
        """Test encontrar línea en modo exacto"""
        lines = [
            'def func1():',
            'class User:',
            'def func2():'
        ]
        
        # Debe encontrar línea exacta
        result = self.fuzzy_matcher.find_target_line(lines, 'class User:', flexible=False)
        assert result == 1
        
        # No debe encontrar con espacios extra en modo exacto
        result = self.fuzzy_matcher.find_target_line(lines, 'class  User:', flexible=False)
        assert result is None
    
    def test_find_target_line_flexible_mode(self):
        """Test encontrar línea en modo flexible"""
        lines = [
            'def func1():',
            '  class   User:  ',  # espacios extra
            'def func2():'
        ]
        
        # Debe encontrar línea con espacios normalizados
        result = self.fuzzy_matcher.find_target_line(lines, 'class User:', flexible=True)
        assert result == 1
        
        # Debe encontrar línea exacta también
        lines_exact = ['def func1():', 'class User:', 'def func2():']
        result = self.fuzzy_matcher.find_target_line(lines_exact, 'class User:', flexible=True)
        assert result == 1
    
    def test_edge_case_empty_strings(self):
        """Test casos edge con strings vacíos"""
        # String vacío en normalize_whitespace
        assert self.fuzzy_matcher.normalize_whitespace('') == ''
        assert self.fuzzy_matcher.normalize_whitespace('   ') == ''
        
        # Match con strings vacíos
        assert self.fuzzy_matcher.fuzzy_match('', '', flexible=True) == True
        assert self.fuzzy_matcher.fuzzy_match('text', '', flexible=True) == False
    
    def test_edge_case_complex_spacing(self):
        """Test casos edge con espaciado complejo"""
        target = 'if condition:'
        
        # Línea con múltiples tipos de espacios
        complex_line = '\t  if   condition:   \n'
        
        # En modo exacto no debe hacer match
        assert self.fuzzy_matcher.fuzzy_match(target, complex_line, flexible=False) == False
        
        # En modo flexible sí debe hacer match
        assert self.fuzzy_matcher.fuzzy_match(target, complex_line, flexible=True) == True


# Tests adicionales para integración con coordinadores
class TestFuzzyMatcherIntegration:
    """Tests de integración para verificar que fuzzy matching funciona con coordinadores"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.fuzzy_matcher = FuzzyMatcher()
    
    def test_python_class_definition_matching(self):
        """Test matching de definiciones de clase Python"""
        target = 'class User(models.Model):'
        
        # Variaciones que deben hacer match en modo flexible
        variations = [
            'class User(models.Model):',  # exacto
            'class  User(models.Model):',  # espacios extra
            '  class User(models.Model):  ',  # padding
            'class\tUser(models.Model):',  # tabs
        ]
        
        for variation in variations:
            assert self.fuzzy_matcher.fuzzy_match(target, variation, flexible=True) == True
            # En modo exacto, verificar el comportamiento real del operador 'in'
            expected_exact = target in variation
            assert self.fuzzy_matcher.fuzzy_match(target, variation, flexible=False) == expected_exact

    
    def test_function_definition_matching(self):
        """Test matching de definiciones de función"""
        target = 'def process_data(self):'
        
        lines = [
            'def __init__(self):',
            '  def  process_data(self):  ',  # espacios problemáticos
            'def cleanup(self):'
        ]
        
        # Debe encontrar la función con espacios problemáticos en modo flexible
        result = self.fuzzy_matcher.find_target_line(lines, target, flexible=True)
        assert result == 1
        
        # No debe encontrarla en modo exacto
        result = self.fuzzy_matcher.find_target_line(lines, target, flexible=False)
        assert result is None
