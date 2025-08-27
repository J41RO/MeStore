"""
Tests arquitecturales para verificar independencia y combinabilidad de matchers.
Valida que todos los matchers implementen la interface común BaseMatcher correctamente.
"""

import pytest
import sys
import os

# Agregar path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../functions/pattern'))

from functions.pattern import BaseMatcher, MatcherCombiner
from functions.pattern import RegexMatcher
from functions.pattern import LiteralMatcher
from functions.pattern import FuzzyMatcher
from functions.pattern import MultilineMatcher


class TestMatcherIndependence:
    """Tests que verifican independencia completa de cada matcher"""
    
    def test_literal_matcher_independence(self):
        """Verifica que LiteralMatcher no depende de otros matchers"""
        # Debe instanciarse sin dependencias externas
        matcher = LiteralMatcher()
        assert isinstance(matcher, LiteralMatcher)
        assert isinstance(matcher, BaseMatcher)
        
        # Verificar que no importa regex_matcher internamente
        import inspect
        source = inspect.getsource(LiteralMatcher)
        assert 'regex_matcher' not in source.lower()
        assert 'RegexMatcher' not in source
    
    def test_regex_matcher_independence(self):
        """Verifica que RegexMatcher no depende de otros matchers"""
        matcher = RegexMatcher()
        assert isinstance(matcher, RegexMatcher)
        assert isinstance(matcher, BaseMatcher)
    
    def test_fuzzy_matcher_independence(self):
        """Verifica que FuzzyMatcher no depende de otros matchers"""
        matcher = FuzzyMatcher()
        assert isinstance(matcher, FuzzyMatcher)
        assert isinstance(matcher, BaseMatcher)
    
    def test_multiline_matcher_independence(self):
        """Verifica que MultilineMatcher no depende de otros matchers"""
        matcher = MultilineMatcher()
        assert isinstance(matcher, MultilineMatcher)
        assert isinstance(matcher, BaseMatcher)


class TestCommonInterface:
    """Tests que verifican interface común BaseMatcher en todos los matchers"""
    
    @pytest.fixture
    def all_matchers(self):
        """Fixture que retorna instancias de todos los matchers"""
        return [
            RegexMatcher(),
            LiteralMatcher(),
            FuzzyMatcher(),
            MultilineMatcher()
        ]
    
    def test_standard_methods_exist(self, all_matchers):
        """Verifica que todos los matchers tienen métodos estándar"""
        for matcher in all_matchers:
            assert hasattr(matcher, 'find'), f"{matcher.__class__.__name__} missing find() method"
            assert hasattr(matcher, 'match'), f"{matcher.__class__.__name__} missing match() method"  
            assert hasattr(matcher, 'find_all'), f"{matcher.__class__.__name__} missing find_all() method"
    
    def test_find_method_signature(self, all_matchers):
        """Verifica que método find() tiene signature consistente"""
        test_text = "hello world test"
        test_pattern = "world"
        
        for matcher in all_matchers:
            # find() debe aceptar text, pattern y kwargs
            result = matcher.find(test_text, test_pattern)
            # Resultado debe ser None o dict
            assert result is None or isinstance(result, dict)
            
            if result:
                # Formato estándar verificado
                assert 'match' in result
                assert 'start' in result  
                assert 'end' in result
                assert 'groups' in result
    
    def test_match_method_returns_bool(self, all_matchers):
        """Verifica que método match() retorna bool"""
        test_text = "hello world test"
        test_pattern = "world"
        
        for matcher in all_matchers:
            result = matcher.match(test_text, test_pattern)
            assert isinstance(result, bool), f"{matcher.__class__.__name__}.match() must return bool"
    
    def test_find_all_method_returns_list(self, all_matchers):
        """Verifica que método find_all() retorna lista"""
        test_text = "hello world test world"
        test_pattern = "world"
        
        for matcher in all_matchers:
            result = matcher.find_all(test_text, test_pattern)
            assert isinstance(result, list), f"{matcher.__class__.__name__}.find_all() must return list"
            
            # Cada elemento debe ser dict con formato estándar
            for match in result:
                assert isinstance(match, dict)
                assert 'match' in match
                assert 'start' in match
                assert 'end' in match
                assert 'groups' in match


class TestMatcherCombinability:
    """Tests que verifican combinabilidad de matchers usando MatcherCombiner"""
    
    def test_matcher_combiner_creation(self):
        """Verifica que MatcherCombiner funciona con múltiples matchers"""
        matchers = [RegexMatcher(), LiteralMatcher(), FuzzyMatcher()]
        combiner = MatcherCombiner(matchers)
        assert len(combiner.matchers) == 3
    
    def test_find_any_functionality(self):
        """Verifica funcionalidad find_any() del combinador"""
        matchers = [RegexMatcher(), LiteralMatcher()]
        combiner = MatcherCombiner(matchers)
        
        text = "hello world test"
        patterns = ["world", "test"]
        
        result = combiner.find_any(text, patterns)
        assert result is not None
        assert isinstance(result, dict)
        assert 'match' in result
        assert 'matcher_index' in result
        assert 'pattern_index' in result
    
    def test_find_all_combined_functionality(self):
        """Verifica funcionalidad find_all_combined() del combinador"""
        matchers = [RegexMatcher(), LiteralMatcher()]
        combiner = MatcherCombiner(matchers)
        
        text = "hello world test world"
        patterns = ["world"]
        
        results = combiner.find_all_combined(text, patterns)
        assert isinstance(results, list)
        
        for result in results:
            assert isinstance(result, dict)
            assert 'match' in result
            assert 'matcher_index' in result
            assert 'pattern_index' in result
    
    def test_match_any_functionality(self):
        """Verifica funcionalidad match_any() del combinador"""
        matchers = [RegexMatcher(), LiteralMatcher()]
        combiner = MatcherCombiner(matchers)
        
        text = "hello world test"
        patterns = ["world", "nonexistent"]
        
        result = combiner.match_any(text, patterns)
        assert isinstance(result, bool)
        assert result is True  # Debe encontrar "world"


class TestArchitecturalConstraints:
    """Tests que verifican restricciones arquitecturales críticas"""
    
    def test_no_cross_dependencies(self):
        """Verifica que no hay dependencias cruzadas entre matchers"""
        import inspect
        
        # Lista de matchers a verificar
        matcher_classes = [RegexMatcher, LiteralMatcher, FuzzyMatcher, MultilineMatcher]
        matcher_names = ["RegexMatcher", "LiteralMatcher", "FuzzyMatcher", "MultilineMatcher"]
        
        for i, matcher_class in enumerate(matcher_classes):
            source = inspect.getsource(matcher_class)
            
            # Verificar que no importa otros matchers (excepto BaseMatcher)
            for j, other_name in enumerate(matcher_names):
                if i != j:  # No verificar contra sí mismo
                    assert other_name not in source, f"{matcher_class.__name__} depends on {other_name}"
    
    def test_base_matcher_inheritance(self):
        """Verifica que todos los matchers heredan de BaseMatcher"""
        matcher_classes = [RegexMatcher, LiteralMatcher, FuzzyMatcher, MultilineMatcher]
        
        for matcher_class in matcher_classes:
            assert issubclass(matcher_class, BaseMatcher), f"{matcher_class.__name__} must inherit BaseMatcher"
    
    def test_package_imports_work(self):
        """Verifica que imports desde package funcionan correctamente"""
        # Simular import desde __init__.py
        import __init__ as pattern_module
        
        # Verificar que todas las clases están disponibles
        assert hasattr(pattern_module, 'RegexMatcher')
        assert hasattr(pattern_module, 'LiteralMatcher')
        assert hasattr(pattern_module, 'FuzzyMatcher')
        assert hasattr(pattern_module, 'MultilineMatcher')
        assert hasattr(pattern_module, 'BaseMatcher')
        assert hasattr(pattern_module, 'MatcherCombiner')


class TestFunctionalIntegration:
    """Tests de integración funcional entre matchers"""
    
    def test_matchers_find_same_pattern_consistently(self):
        """Verifica que matchers encuentran patrones básicos consistentemente"""
        text = "The quick brown fox jumps over the lazy dog"
        pattern = "quick"
        
        # Estos matchers deberían encontrar literal "quick"
        literal = LiteralMatcher()
        regex = RegexMatcher()
        
        literal_result = literal.match(text, pattern)
        regex_result = regex.match(text, pattern)
        
        # Ambos deberían encontrar el patrón
        assert literal_result is True
        assert regex_result is True
    
    def test_matchers_work_with_different_patterns(self):
        """Verifica que cada matcher funciona con su tipo de patrón específico"""
        text = "Email: user@example.com, Phone: 123-456-7890"
        
        # RegexMatcher con patrón regex
        regex = RegexMatcher()
        email_found = regex.match(text, r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        assert email_found is True
        
        # LiteralMatcher con texto literal
        literal = LiteralMatcher()
        literal_found = literal.match(text, "Email:")
        assert literal_found is True
        
        # FuzzyMatcher con coincidencia aproximada
        fuzzy = FuzzyMatcher(default_threshold=0.7)
        fuzzy_found = fuzzy.match(text, "emial")  # Typo intencional
        assert fuzzy_found is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])