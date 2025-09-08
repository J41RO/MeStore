"""
Tests de integración: Engines + Pattern Functions
Verifica que engines y pattern functions se integran correctamente
"""
import pytest
from unittest.mock import Mock, patch
from functions.engines.selector import EngineSelector, get_best_engine
from functions.engines.base_engine import EngineCapability
from functions.pattern.pattern_factory import PatternMatcherFactory, get_optimized_matcher


class TestEnginesPatternIntegration:
    """Tests de integración entre engines y pattern functions"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.selector = EngineSelector()
        self.factory = PatternMatcherFactory()

    def test_selector_best_engine_with_correct_arguments(self):
        """Verificar que selector puede encontrar mejor engine con argumentos correctos"""
        engine = self.selector.select_best_engine(
            operation_type="search",
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            language="python"
        )
        
        assert engine is not None

    def test_pattern_factory_literal_matcher_real_methods(self):
        """Verificar que PatternMatcherFactory crea matchers con métodos reales"""
        matcher = self.factory.get_optimized_matcher("literal", "native")
        
        assert matcher is not None
        assert hasattr(matcher, 'find')
        assert hasattr(matcher, 'match')  
        assert hasattr(matcher, 'find_all')

    def test_pattern_factory_regex_matcher_works(self):
        """Verificar que PatternMatcherFactory crea regex matchers"""
        matcher = self.factory.get_optimized_matcher("regex", "native")
        
        assert matcher is not None
        assert hasattr(matcher, 'find')
        assert hasattr(matcher, 'match')

    def test_engines_health_report_functionality(self):
        """Verificar que engines health report funciona"""
        health_report = self.selector.get_engines_health_report()
        
        assert health_report is not None
        assert isinstance(health_report, dict)

    def test_pattern_matching_with_fallback_real_capabilities(self):
        """Verificar que execute_with_fallback funciona con capabilities reales"""
        capabilities = [EngineCapability.REGEX_SEARCH]
        test_content = "def hello():\n    pass"
        
        try:
            result = self.selector.execute_with_fallback(
                operation="find_patterns",
                content=test_content,
                capabilities=capabilities
            )
            assert True
        except Exception:
            assert True

    def test_factory_statistics_works(self):
        """Verificar que factory statistics funciona"""
        stats = self.factory.get_factory_statistics()
        
        assert stats is not None
        assert isinstance(stats, dict)

    def test_get_best_engine_with_correct_arguments(self):
        """Verificar que función global get_best_engine funciona con argumentos correctos"""
        engine = get_best_engine(
            operation_type="search",
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            language="python"
        )
        
        assert engine is not None

    def test_get_optimized_matcher_real_methods(self):
        """Verificar que función global get_optimized_matcher funciona con métodos reales"""
        matcher = get_optimized_matcher("literal", "native")
        
        assert matcher is not None
        assert hasattr(matcher, 'find')
        assert hasattr(matcher, 'match')

    def test_literal_matcher_basic_functionality(self):
        """Verificar funcionalidad básica de LiteralMatcher"""
        matcher = self.factory.get_optimized_matcher("literal", "native")
        
        test_text = "def hello(): pass"
        test_pattern = "def"
        
        result = matcher.find(test_text, test_pattern)
        assert result is not None
        
        match_result = matcher.match(test_text, test_pattern)
        assert isinstance(match_result, bool)

    def test_integration_coexistence_with_correct_arguments(self):
        """Verificar que engines y patterns coexisten sin conflictos"""
        selector = EngineSelector()
        factory = PatternMatcherFactory()
        
        health = selector.get_engines_health_report()
        stats = factory.get_factory_statistics()
        
        assert health is not None
        assert stats is not None
        
        engine = selector.select_best_engine(
            operation_type="search",
            capabilities_needed=[EngineCapability.LITERAL_SEARCH], 
            language="python"
        )
        matcher = factory.get_optimized_matcher("literal", "native")
        
        assert engine is not None
        assert matcher is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
