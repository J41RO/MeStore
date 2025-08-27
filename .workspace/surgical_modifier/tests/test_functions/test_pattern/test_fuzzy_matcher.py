# Crear tests/test_functions/test_pattern/test_fuzzy_matcher.py con:
import pytest
from functions.pattern.fuzzy_matcher import FuzzyMatcher

class TestFuzzyMatcher:
    def setup_method(self):
        self.matcher = FuzzyMatcher(default_threshold=0.6)
    
    def test_basic_similarity_calculation(self):
        """Test calculo de similaridad basico"""
        # Identical strings
        similarity = self.matcher.calculate_similarity('test', 'test')
        assert similarity == 1.0
        
        # Similar strings
        similarity = self.matcher.calculate_similarity('test', 'tset')
        assert 0.7 <= similarity <= 0.8  # Transposed characters
        
        # Different strings
        similarity = self.matcher.calculate_similarity('test', 'completely different')
        assert similarity < 0.3
    
    def test_fuzzy_match_found(self):
        """Test encontrar match aproximado"""
        result = self.matcher.find_fuzzy_match('test', 'This is a tset example')
        assert result['success'] is True
        assert result['found'] is True
        assert result['match'] == 'tset'
        assert result['similarity'] >= 0.6
    
    def test_fuzzy_match_not_found(self):
        """Test no encontrar match aproximado"""
        result = self.matcher.find_fuzzy_match('xyz', 'This is a test example', threshold=0.8)
        assert result['success'] is True
        assert result['found'] is False
    
    def test_find_all_fuzzy_matches(self):
        """Test encontrar todos los matches aproximados"""
        result = self.matcher.find_all_fuzzy_matches('test', 'test tset taste testing')
        assert result['success'] is True
        assert result['count'] >= 2  # Should find 'test' and 'tset' at minimum
    
    def test_close_matches(self):
        """Test obtener matches cercanos"""
        candidates = ['hello world', 'helo wrold', 'hello earth', 'hi there']
        result = self.matcher.get_close_matches('hello world', candidates, n=3)
        assert result['success'] is True
        assert result['count'] >= 1
        assert result['matches'][0]['match'] == 'hello world'  # Exact match should be first
    
    def test_levenshtein_distance(self):
        """Test distancia Levenshtein"""
        # Identical strings
        distance = self.matcher.levenshtein_distance('test', 'test')
        assert distance == 0
        
        # One character difference
        distance = self.matcher.levenshtein_distance('test', 'tset')
        assert distance == 2  # Two transpositions
        
        # Completely different
        distance = self.matcher.levenshtein_distance('abc', 'xyz')
        assert distance == 3
    
    def test_detailed_similarity(self):
        """Test analisis detallado de similaridad"""
        result = self.matcher.similarity_detailed('hello world', 'helo wrold')
        assert result['success'] is True
        assert 'sequence_ratio' in result
        assert 'edit_distance' in result
        assert 'edit_similarity' in result
        assert 'word_similarity' in result
        assert 'overall_score' in result
        assert 0.0 <= result['overall_score'] <= 1.0
    
    def test_fuzzy_search_in_lines(self):
        """Test busqueda fuzzy en lineas"""
        lines = ['def function():', 'class TestCase:', 'def method():']
        result = self.matcher.fuzzy_search_in_lines('def', lines)
        assert result['success'] is True
        assert result['lines_with_matches'] >= 2  # Should find 'def' in at least 2 lines
    
    def test_suggest_corrections(self):
        """Test sugerencias de correcion"""
        text = 'This is a test example with sample text'
        result = self.matcher.suggest_corrections('tset', text)
        assert result['success'] is True
        if result['count'] > 0:
            assert 'test' in [s['suggestion'].lower() for s in result['suggestions']]
    
    def test_edge_cases(self):
        """Test casos edge"""
        # Empty pattern
        result = self.matcher.find_fuzzy_match('', 'text')
        assert result['success'] is False
        
        # Empty text
        result = self.matcher.find_fuzzy_match('pattern', '')
        assert result['success'] is True
        assert result['found'] is False
        
        # Very short strings
        result = self.matcher.calculate_similarity('a', 'b')
        assert 0.0 <= result <= 1.0
    
    def test_integration_with_other_matchers(self):
        """Test integracion conceptual con otros matchers"""
        # This test verifies that FuzzyMatcher complements other pattern matchers
        from functions.pattern.regex_matcher import RegexMatcher
        from functions.pattern.literal_matcher import LiteralMatcher
        
        regex_matcher = RegexMatcher()
        literal_matcher = LiteralMatcher()
        
        text = 'This is a tset example'
        pattern = 'test'
        
        # Literal matcher should not find approximate match
        literal_result = literal_matcher.find_literal(pattern, text)
        assert literal_result['found'] is False
        
        # Regex matcher should not find approximate match (without fuzzy regex)
        regex_result = regex_matcher.find_matches(pattern, text)
        assert regex_result['count'] == 0
        
        # Fuzzy matcher should find approximate match
        fuzzy_result = self.matcher.find_fuzzy_match(pattern, text)
        assert fuzzy_result['found'] is True
        
        # This demonstrates the complementary nature of the three matchers