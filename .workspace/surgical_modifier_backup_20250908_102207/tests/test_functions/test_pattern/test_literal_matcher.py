import pytest
from functions.pattern.literal_matcher import LiteralMatcher

class TestLiteralMatcher:
    def setup_method(self):
        self.matcher = LiteralMatcher()
    
    def test_basic_literal_matching(self):
        """Test matching literal basico"""
        result = self.matcher.find_literal('hello', 'Hello world hello test')
        assert result['success'] is True
        assert result['found'] is True
        assert result['position'] == 12  # Case sensitive
        
        # Case insensitive
        result = self.matcher.find_literal('hello', 'Hello world hello test', case_sensitive=False)
        assert result['position'] == 0  # Should find 'Hello'
    
    def test_find_all_literals(self):
        """Test encontrar todas las ocurrencias"""
        result = self.matcher.find_all_literals('test', 'test this test that test')
        assert result['success'] is True
        assert result['count'] == 3
        assert len(result['matches']) == 3
        
        positions = [match['position'] for match in result['matches']]
        assert positions == [0, 10, 20]
    
    def test_count_occurrences(self):
        """Test contar ocurrencias eficientemente"""
        result = self.matcher.count_occurrences('the', 'the cat and the dog and the bird')
        assert result['success'] is True
        assert result['count'] == 3
    
    def test_whole_words_matching(self):
        """Test matching solo palabras completas"""
        result = self.matcher.find_whole_words('test', 'testing test tested')
        assert result['success'] is True
        assert result['count'] == 1  # Solo 'test', no 'testing' o 'tested'
    
    def test_literal_replacement(self):
        """Test reemplazo literal"""
        result = self.matcher.replace_literal('old', 'new', 'old value and old item')
        assert result['success'] is True
        assert result['new_text'] == 'new value and new item'
        assert result['replacements_made'] == 2
        
        # Max replacements
        result = self.matcher.replace_literal('old', 'new', 'old value and old item', max_replacements=1)
        assert result['new_text'] == 'new value and old item'
        assert result['replacements_made'] == 1
    
    def test_boundary_matching(self):
        """Test matching en boundaries"""
        text = 'def function():\n  pass\ndef another():'
        result = self.matcher.find_at_boundaries('def', text, 'line')
        assert result['success'] is True
        assert result['count'] == 2  # Dos lineas empiezan con 'def'
    
    def test_multiple_patterns(self):
        """Test busqueda de multiples patrones"""
        result = self.matcher.find_multiple_patterns(['def', 'class'], 'def func():\nclass Test:\n  def method():')
        assert result['success'] is True
        assert result['total_matches'] == 3  # 2 'def' + 1 'class'
    
    def test_context_around_matches(self):
        """Test contexto alrededor de matches"""
        result = self.matcher.get_context_around_match('test', 'This is a test sentence', context_chars=5)
        assert result['success'] is True
        assert len(result['matches_with_context']) == 1
        context = result['matches_with_context'][0]['context']
        assert 'test' in context
        assert len(context) <= 15  # 5 chars before + 'test' + 5 chars after
    
    def test_edge_cases(self):
        """Test casos edge"""
        # Empty pattern
        result = self.matcher.find_literal('', 'text')
        assert result['success'] is False
        
        # Empty text
        result = self.matcher.find_literal('pattern', '')
        assert result['success'] is True
        assert result['found'] is False
        
        # Pattern longer than text
        result = self.matcher.find_literal('very long pattern', 'short')
        assert result['success'] is True
        assert result['found'] is False
        
        # Special characters
        result = self.matcher.find_literal('$%^&', 'test $%^& more')
        assert result['success'] is True
        assert result['found'] is True