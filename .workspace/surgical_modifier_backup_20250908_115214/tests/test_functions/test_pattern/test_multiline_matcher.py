import pytest
from functions.pattern.multiline_matcher import MultilineMatcher

class TestMultilineMatcher:
    def setup_method(self):
        self.matcher = MultilineMatcher()
    
    def test_basic_multiline_pattern(self):
        """Test patrón multiline básico"""
        text = '''def function():
    return True'''
        result = self.matcher.find_multiline_pattern(r'def \w+\(\):\s*\n\s+return', text)
        assert result['success'] is True
        assert result['count'] == 1
        assert result['matches'][0]['lines_spanned'] == 2
    
    def test_find_function_blocks(self):
        """Test encontrar bloques de función"""
        text = '''def function1():
    return 1

def function2():
    return 2'''
        result = self.matcher.find_block_patterns(text, 'function')
        assert result['success'] is True
        assert result['count'] == 2
    
    def test_find_class_blocks(self):
        """Test encontrar bloques de clase"""
        text = '''class TestClass:
    def __init__(self):
        self.value = 1
    
    def method(self):
        return self.value'''
        result = self.matcher.find_block_patterns(text, 'class')
        assert result['success'] is True
        assert result['count'] == 1
    
    def test_line_context(self):
        """Test contexto alrededor de línea"""
        text = '''line 1
line 2
target line
line 4
line 5'''
        result = self.matcher.get_line_context(text, 3, context_lines=1)
        assert result['success'] is True
        assert result['target_line'] == 3
        assert result['target_content'] == 'target line'
        assert len(result['context_lines']) == 3  # line 2, target, line 4
    
    def test_indentation_analysis(self):
        """Test análisis de indentación"""
        text = '''def function():
    if condition:
        return True
    else:
        return False'''
        result = self.matcher.analyze_indentation_structure(text)
        assert result['success'] is True
        assert result['total_blocks'] > 0
        assert result['max_indent_level'] >= 4
    
    def test_find_blocks_by_indent(self):
        """Test encontrar bloques por indentación"""
        text = '''top level
    indented block
        deeper block
    back to level 1'''
        result = self.matcher.find_code_blocks_by_indent(text, target_indent=0)
        assert result['success'] is True
        assert result['count'] >= 1
    
    def test_nested_structures(self):
        """Test estructuras anidadas"""
        text = '''class MyClass:
    def method1(self):
        return 1
    
    def method2(self):
        return 2'''
        result = self.matcher.extract_nested_structures(text)
        assert result['success'] is True
        assert len(result['classes']) == 1
        assert len(result['methods']) == 2
        assert len(result['nesting_relationships']) == 1
    
    def test_contextual_pattern_search(self):
        """Test búsqueda de patrones con contexto"""
        text = '''def function1():
    return 1

class Test:
    pass

def function2():
    return 2'''
        patterns = [r'def \w+', r'class \w+']
        result = self.matcher.find_patterns_with_context(patterns, text)
        assert result['success'] is True
        assert result['total_matches'] == 3  # 2 functions + 1 class
        assert all('context' in match for match in result['all_matches_sorted'])
    
    def test_between_markers(self):
        """Test encontrar contenido entre marcadores"""
        text = '''before
START
multiline content
here
END
after'''
        result = self.matcher.find_multiline_between_markers('START', 'END', text, include_markers=False)
        assert result['success'] is True
        assert result['count'] == 1
        assert 'multiline content' in result['matches'][0]['content']
    
    def test_multiline_replacement(self):
        """Test reemplazo multiline"""
        text = '''def old_function():
    return "old"'''
        pattern = r'def old_function\(\):\s*\n\s*return "old"'
        replacement = 'def new_function():\n    return "new"'
        result = self.matcher.replace_multiline_blocks(text, pattern, replacement)
        assert result['success'] is True
        assert result['replacements_made'] == 1
        assert 'new_function' in result['new_text']
    
    def test_integration_with_other_matchers(self):
        """Test integración conceptual con otros pattern matchers"""
        # Test que MultilineMatcher maneja casos que otros matchers no pueden
        from functions.pattern.regex_matcher import RegexMatcher
        from functions.pattern.literal_matcher import LiteralMatcher
        
        multiline_text = '''def function():
    if condition:
        return True'''
        
        # Single line matchers might miss this pattern
        regex_matcher = RegexMatcher()
        literal_matcher = LiteralMatcher()
        
        # Try to find the complete function block
        multiline_pattern = r'def \w+\(\):\s*\n(?:\s{4,}.*\n?)*'
        
        # MultilineMatcher should handle this better
        multiline_result = self.matcher.find_multiline_pattern(multiline_pattern, multiline_text)
        assert multiline_result['success'] is True
        
        # This demonstrates MultilineMatcher's unique capability
        if multiline_result['count'] > 0:
            assert multiline_result['matches'][0]['lines_spanned'] > 1
    
    def test_edge_cases(self):
        """Test casos edge"""
        # Empty pattern
        result = self.matcher.find_multiline_pattern('', 'text')
        assert result['success'] is False
        
        # Empty text
        result = self.matcher.find_multiline_pattern('pattern', '')
        assert result['success'] is True
        assert result['count'] == 0
        
        # Invalid line number
        result = self.matcher.get_line_context('text', 0)
        assert result['success'] is False
        
        # Single line text
        result = self.matcher.analyze_indentation_structure('single line')
        assert result['success'] is True
        assert result['total_lines'] == 1
