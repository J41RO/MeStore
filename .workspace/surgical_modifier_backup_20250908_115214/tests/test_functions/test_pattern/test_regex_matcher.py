import pytest
from functions.pattern.regex_matcher import RegexMatcher, CodePatterns

class TestRegexMatcher:
    def setup_method(self):
        self.matcher = RegexMatcher()
    
    def test_basic_matching(self):
        """Test matching basico"""
        result = self.matcher.find_matches(r'\d+', 'test 123 and 456 end')
        assert result['success'] is True
        assert result['count'] == 2
        assert result['matches'][0]['match'] == '123'
        assert result['matches'][1]['match'] == '456'
    
    def test_groups_extraction(self):
        """Test extraccion de grupos"""
        result = self.matcher.extract_groups(r'(\w+)@(\w+)\.(\w+)', 'user@domain.com')
        assert result['success'] is True
        assert len(result['numbered_groups']) == 3
        assert result['numbered_groups'] == ('user', 'domain', 'com')
    
    def test_pattern_replacement(self):
        """Test reemplazo de patrones"""
        result = self.matcher.replace_pattern(r'\d+', 'NUM', 'value 123 and 456')
        assert result['success'] is True
        assert result['new_text'] == 'value NUM and NUM'
        assert result['replacements_made'] == 2
    
    def test_python_code_patterns(self):
        """Test patrones de codigo Python"""
        code = '''
def hello(name, age=25):
    return f"Hello {name}"
    
class Person:
    def __init__(self):
        pass
'''
        result = self.matcher.find_code_patterns(code, 'python')
        assert result['success'] is True
        assert len(result['patterns']['function_def']) == 2  # hello + __init__
        assert len(result['patterns']['class_def']) == 1
    
    def test_invalid_regex_handling(self):
        """Test manejo de regex invalidos"""
        result = self.matcher.find_matches(r'[invalid(', 'test text')
        assert result['success'] is False
        assert 'error' in result
    
    def test_edge_cases(self):
        """Test casos edge"""
        # Texto vacio
        result = self.matcher.find_matches(r'\d+', '')
        assert result['success'] is True
        assert result['count'] == 0
        
        # Patron vacio (deberia fallar)
        result = self.matcher.find_matches('', 'test')
        assert result['success'] is True  # Patron vacio es valido
        
        # Texto muy largo (stress test basico)
        long_text = 'word ' * 1000 + '123'
        result = self.matcher.find_matches(r'\d+', long_text)
        assert result['success'] is True
        assert result['count'] == 1