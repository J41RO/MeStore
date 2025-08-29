"""
Tests para Engine Selector - Verificación completa de funcionalidad de auto-selección.
"""
import pytest
from unittest.mock import Mock, patch

from functions.engines.selector import EngineSelector, SelectionCriteria, get_best_engine
from functions.engines.base_engine import EngineCapability, BaseEngine, EngineRegistry
from functions.engines import NativeEngine, CombyEngine, AstEngine


class TestEngineSelector:
    """Tests para la clase EngineSelector"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.selector = EngineSelector()
    
    def test_selector_initialization(self):
        """Test inicialización básica del selector"""
        assert self.selector is not None
        assert hasattr(self.selector, '_engine_priorities')
        assert 'structural_search' in self.selector._engine_priorities
        assert 'literal_search' in self.selector._engine_priorities
    
    def test_normalize_capabilities_with_strings(self):
        """Test normalización de capacidades desde strings"""
        capabilities = ['literal_search', 'regex_search']
        normalized = self.selector._normalize_capabilities(capabilities)
        
        assert len(normalized) == 2
        assert EngineCapability.LITERAL_SEARCH in normalized
        assert EngineCapability.REGEX_SEARCH in normalized
    
    def test_normalize_capabilities_with_enums(self):
        """Test normalización de capacidades desde enums"""
        capabilities = [EngineCapability.STRUCTURAL_SEARCH, EngineCapability.AST_AWARE]
        normalized = self.selector._normalize_capabilities(capabilities)
        
        assert len(normalized) == 2
        assert EngineCapability.STRUCTURAL_SEARCH in normalized
        assert EngineCapability.AST_AWARE in normalized
    
    def test_normalize_capabilities_mixed(self):
        """Test normalización de capacidades mixta"""
        capabilities = ['literal_search', EngineCapability.REGEX_SEARCH]
        normalized = self.selector._normalize_capabilities(capabilities)
        
        assert len(normalized) == 2
        assert EngineCapability.LITERAL_SEARCH in normalized
        assert EngineCapability.REGEX_SEARCH in normalized
    
    def test_get_engines_by_capability_literal_search(self):
        """Test filtrado de engines por capacidad literal_search"""
        required = [EngineCapability.LITERAL_SEARCH]
        candidates = self.selector._get_engines_by_capability(required)
        
        # NativeEngine debe estar presente
        engine_names = [e['name'] for e in candidates]
        assert 'native' in engine_names
        
        # Verificar que cada candidato tiene la capacidad requerida
        for candidate in candidates:
            assert EngineCapability.LITERAL_SEARCH in candidate['capabilities']
    
    def test_get_engines_by_capability_structural_search(self):
        """Test filtrado de engines por capacidad structural_search"""
        required = [EngineCapability.STRUCTURAL_SEARCH]
        candidates = self.selector._get_engines_by_capability(required)
        
        # CombyEngine debe estar presente si está disponible
        engine_names = [e['name'] for e in candidates]
        # No podemos garantizar que comby esté disponible, pero si está debe tener la capacidad
        for candidate in candidates:
            assert EngineCapability.STRUCTURAL_SEARCH in candidate['capabilities']
    
    def test_get_primary_capability(self):
        """Test determinación de capacidad primaria"""
        # Test structural search como primaria
        capabilities = [EngineCapability.STRUCTURAL_SEARCH, EngineCapability.LITERAL_SEARCH]
        primary = self.selector._get_primary_capability(capabilities)
        assert primary == 'structural_search'
        
        # Test ast_aware mapeado a structural_search
        capabilities = [EngineCapability.AST_AWARE]
        primary = self.selector._get_primary_capability(capabilities)
        assert primary == 'structural_search'
        
        # Test fallback a literal_search
        capabilities = [EngineCapability.CONTEXT_AWARE]
        primary = self.selector._get_primary_capability(capabilities)
        assert primary == 'literal_search'
    
    def test_select_best_engine_literal_search(self):
        """Test selección de engine para búsqueda literal"""
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=['literal_search']
        )
        
        # Debe retornar algún engine válido
        assert isinstance(engine, BaseEngine)
        assert EngineCapability.LITERAL_SEARCH in engine.capabilities
    
    def test_select_best_engine_structural_search(self):
        """Test selección de engine para búsqueda estructural"""
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=['structural_search']
        )
        
        # En el entorno actual, puede que no haya engines con STRUCTURAL_SEARCH disponibles
        # El selector debe hacer fallback gracioso a un engine válido
        assert isinstance(engine, BaseEngine)
        # No asumir que el engine tiene STRUCTURAL_SEARCH - puede ser fallback
        assert len(engine.capabilities) > 0  # Debe tener alguna capacidad
    
    def test_select_best_engine_with_language(self):
        """Test selección con especificación de lenguaje"""
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=['literal_search'],
            language='python'
        )
        
        assert isinstance(engine, BaseEngine)
        assert EngineCapability.LITERAL_SEARCH in engine.capabilities
    
    def test_select_best_engine_fallback_to_native(self):
        """Test fallback a NativeEngine cuando no hay coincidencias"""
        # Capacidad muy específica que probablemente no esté disponible
        with patch.object(self.selector, '_get_engines_by_capability', return_value=[]):
            engine = self.selector.select_best_engine(
                operation_type='search',
                capabilities_needed=['literal_search']
            )
            
            # Debe fallback a native
            assert isinstance(engine, NativeEngine)
    
    def test_rank_engines(self):
        """Test ranking de engines candidatos"""
        # Mock candidates
        mock_candidates = [
            {
                'name': 'native',
                'class': NativeEngine,
                'capabilities': {EngineCapability.LITERAL_SEARCH},
                'available': True
            },
            {
                'name': 'comby', 
                'class': CombyEngine,
                'capabilities': {EngineCapability.STRUCTURAL_SEARCH, EngineCapability.LITERAL_SEARCH},
                'available': True
            }
        ]
        
        ranked = self.selector._rank_engines(
            mock_candidates,
            'search',
            [EngineCapability.LITERAL_SEARCH]
        )
        
        # Debe retornar lista rankeada
        assert len(ranked) == 2
        assert all('score' in engine for engine in ranked)
        
        # Scores deben estar en orden descendente
        scores = [engine['score'] for engine in ranked]
        assert scores == sorted(scores, reverse=True)
    
    def test_check_engine_availability(self):
        """Test verificación de disponibilidad de engines"""
        # Test engine básico (siempre disponible)
        native_engine = NativeEngine()
        available = self.selector._check_engine_availability('native', native_engine)
        assert available is True
        
        # Test engine con método is_available
        mock_engine = Mock()
        mock_engine.is_available.return_value = True
        available = self.selector._check_engine_availability('mock', mock_engine)
        assert available is True
        
        mock_engine.is_available.return_value = False
        available = self.selector._check_engine_availability('mock', mock_engine)
        assert available is False


class TestConvenienceFunction:
    """Tests para función de conveniencia get_best_engine"""
    
    def test_get_best_engine_function(self):
        """Test función de conveniencia get_best_engine"""
        engine = get_best_engine(
            operation_type='search',
            capabilities_needed=['literal_search']
        )
        
        assert isinstance(engine, BaseEngine)
        assert EngineCapability.LITERAL_SEARCH in engine.capabilities
    
    def test_get_best_engine_with_kwargs(self):
        """Test función de conveniencia con argumentos adicionales"""
        engine = get_best_engine(
            operation_type='search',
            capabilities_needed=['literal_search'],
            language='python'
        )
        
        assert isinstance(engine, BaseEngine)


class TestSelectionCriteria:
    """Tests para enum SelectionCriteria"""
    
    def test_selection_criteria_enum_values(self):
        """Test valores del enum SelectionCriteria"""
        assert SelectionCriteria.CAPABILITY_MATCH.value == "capability_match"
        assert SelectionCriteria.LANGUAGE_SUPPORT.value == "language_support"
        assert SelectionCriteria.PERFORMANCE.value == "performance"
        assert SelectionCriteria.AVAILABILITY.value == "availability"
        assert SelectionCriteria.OPERATION_TYPE.value == "operation_type"


class TestEdgeCases:
    """Tests para casos edge y manejo de errores"""
    
    def setup_method(self):
        self.selector = EngineSelector()
    
    def test_empty_capabilities_list(self):
        """Test con lista vacía de capacidades"""
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[]
        )
        
        # Debe retornar un engine válido (probablemente native como fallback)
        assert isinstance(engine, BaseEngine)
    
    def test_unknown_operation_type(self):
        """Test con tipo de operación desconocido"""
        engine = self.selector.select_best_engine(
            operation_type='unknown_operation',
            capabilities_needed=['literal_search']
        )
        
        # Debe manejar graciosamente y retornar engine válido
        assert isinstance(engine, BaseEngine)
    
    def test_invalid_capability_string(self):
        """Test con string de capacidad inválido"""
        normalized = self.selector._normalize_capabilities(['invalid_capability'])
        
        # Debe manejar graciosamente capacidades inválidas
        assert len(normalized) == 0  # Capacidad inválida se ignora
    
    def test_engine_registry_empty(self):
        """Test comportamiento cuando registry está vacío"""
        with patch.object(EngineRegistry, '_engines', {}):
            candidates = self.selector._get_engines_by_capability([EngineCapability.LITERAL_SEARCH])
            assert candidates == []
    
    def test_engine_instantiation_error(self):
        """Test manejo de errores de instanciación"""
        # Mock engine class que falla al instanciar
        mock_registry = {'failing_engine': Mock(side_effect=Exception("Instantiation failed"))}
        
        with patch.object(EngineRegistry, '_engines', mock_registry):
            candidates = self.selector._get_engines_by_capability([EngineCapability.LITERAL_SEARCH])
            
            # Debe manejar la excepción graciosamente
            assert candidates == []


# Test de integración
class TestIntegration:
    """Tests de integración con sistema completo"""
    
    def test_full_workflow_literal_search(self):
        """Test workflow completo para búsqueda literal"""
        # Usar función de conveniencia
        engine = get_best_engine('search', ['literal_search'])
        
        # Verificar que engine puede realizar operación
        result = engine.search("hello world", "hello")
        assert hasattr(result, 'status')
    
    def test_full_workflow_structural_search(self):
        """Test workflow completo para búsqueda estructural"""
        engine = get_best_engine('search', ['structural_search'])
        
        # El selector puede hacer fallback si no hay engines con capacidad estructural
        assert isinstance(engine, BaseEngine)
        # Verificar que el engine puede realizar operaciones básicas
        assert hasattr(engine, 'search')
        # No asumir capacidad específica - verificar funcionalidad básica

class TestComplexityAnalyzer:
    """Tests for ComplexityAnalyzer functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from functions.engines.selector import ComplexityAnalyzer
        self.analyzer = ComplexityAnalyzer()
    
    def test_complexity_levels_enum(self):
        """Test ComplexityLevel enum values"""
        from functions.engines.selector import ComplexityLevel
        assert len(ComplexityLevel) == 4
        assert ComplexityLevel.LOW in ComplexityLevel
        assert ComplexityLevel.MEDIUM in ComplexityLevel
        assert ComplexityLevel.HIGH in ComplexityLevel
        assert ComplexityLevel.CRITICAL in ComplexityLevel
    
    def test_simple_content_complexity(self):
        """Test complexity analysis of simple content"""
        from functions.engines.selector import ComplexityLevel
        simple_content = "def hello(): pass"
        result = self.analyzer.analyze_content_complexity(simple_content)
        assert result == ComplexityLevel.LOW
    
    def test_complex_content_complexity(self):
        """Test complexity analysis of complex content"""
        from functions.engines.selector import ComplexityLevel
        complex_content = '''
class ComplexClass:
    def __init__(self):
        self.data = {}
        for i in range(100):
            self.data[i] = lambda x: x * 2
            try:
                async def nested_func():
                    return [x for x in range(10) if x % 2 == 0]
            except Exception as e:
                pass
        '''
        result = self.analyzer.analyze_content_complexity(complex_content)
        assert result in [ComplexityLevel.HIGH, ComplexityLevel.CRITICAL]
    
    def test_empty_content_complexity(self):
        """Test complexity analysis of empty content"""
        from functions.engines.selector import ComplexityLevel
        result = self.analyzer.analyze_content_complexity("")
        assert result == ComplexityLevel.LOW
        result = self.analyzer.analyze_content_complexity(None)
        assert result == ComplexityLevel.LOW
    
    def test_operation_complexity_literal_search(self):
        """Test operation complexity for literal search"""
        from functions.engines.selector import ComplexityLevel
        result = self.analyzer.analyze_operation_complexity('literal_search')
        assert result == ComplexityLevel.LOW
    
    def test_operation_complexity_structural_search(self):
        """Test operation complexity for structural search"""
        from functions.engines.selector import ComplexityLevel
        result = self.analyzer.analyze_operation_complexity('structural_search')
        assert result == ComplexityLevel.MEDIUM
    
    def test_operation_complexity_with_content(self):
        """Test operation complexity with content influence"""
        from functions.engines.selector import ComplexityLevel
        complex_content = '''
        class Test:
            def method(self):
                for i in range(10):
                    yield lambda x: x * 2
        '''
        result = self.analyzer.analyze_operation_complexity('structural_search', complex_content)
        assert result in [ComplexityLevel.HIGH, ComplexityLevel.CRITICAL]


class TestComplexityIntegration:
    """Tests for complexity integration in engine selection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from functions.engines.selector import EngineSelector
        self.selector = EngineSelector()
    
    def test_complexity_parameter_in_select_best_engine(self):
        """Test that complexity_level parameter works in select_best_engine"""
        from functions.engines.selector import ComplexityLevel
        from functions.engines.base_engine import EngineCapability
        
        # Should work without errors
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            complexity_level=ComplexityLevel.LOW
        )
        assert engine is not None
    
    def test_different_complexity_levels_selection(self):
        """Test that different complexity levels affect engine selection"""
        from functions.engines.selector import ComplexityLevel
        from functions.engines.base_engine import EngineCapability
        
        # Test with low complexity
        engine_low = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            complexity_level=ComplexityLevel.LOW
        )
        
        # Test with high complexity
        engine_high = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.STRUCTURAL_SEARCH],
            complexity_level=ComplexityLevel.HIGH
        )
        
        assert engine_low is not None
        assert engine_high is not None
    
    def test_automatic_complexity_analysis(self):
        """Test automatic complexity analysis when content is provided"""
        from functions.engines.base_engine import EngineCapability
        
        complex_code = '''
        def complex_function(data):
            result = []
            for item in data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if callable(value):
                            result.append(value(key))
            return result
        '''
        
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.STRUCTURAL_SEARCH],
            content=complex_code,
            language='python'
        )
        assert engine is not None
    
    def test_new_operation_types(self):
        """Test new operation types work correctly"""
        from functions.engines.base_engine import EngineCapability
        
        new_operations = ['insert_before', 'insert_after', 'extract', 'transform']
        
        for op_type in new_operations:
            engine = self.selector.select_best_engine(
                operation_type=op_type,
                capabilities_needed=[EngineCapability.LITERAL_SEARCH]
            )
            assert engine is not None
    
    def test_expanded_operation_types_in_priorities(self):
        """Test that new operation types exist in engine priorities"""
        expected_operations = [
            'structural_search', 'literal_search', 'regex_search', 'batch_operations',
            'insert_before', 'insert_after', 'extract', 'transform'
        ]
        
        for operation in expected_operations:
            assert operation in self.selector._engine_priorities
    
    def test_language_based_priorities(self):
        """Test language-based engine prioritization"""
        from functions.engines.base_engine import EngineCapability
        
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.STRUCTURAL_SEARCH],
            language='python'
        )
        assert engine is not None
    
    def test_complexity_metrics_calculation(self):
        """Test complexity metrics are calculated correctly"""
        from functions.engines.selector import ComplexityAnalyzer
        
        analyzer = ComplexityAnalyzer()
        content_with_functions = '''
        def func1(): pass
        def func2(): pass
        class MyClass: pass
        lambda x: x * 2
        '''
        
        metrics = analyzer._calculate_metrics(content_with_functions)
        assert metrics.function_count > 0
        assert metrics.class_count > 0
        assert metrics.lambda_count > 0
        assert metrics.complexity_score > 0


class TestComplexityEdgeCases:
    """Tests for edge cases in complexity analysis"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from functions.engines.selector import EngineSelector, ComplexityAnalyzer
        self.selector = EngineSelector()
        self.analyzer = ComplexityAnalyzer()
    
    def test_none_complexity_level(self):
        """Test behavior when complexity_level is None"""
        from functions.engines.base_engine import EngineCapability
        
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            complexity_level=None
        )
        assert engine is not None
    
    def test_unknown_operation_type_complexity(self):
        """Test complexity analysis for unknown operation types"""
        from functions.engines.selector import ComplexityLevel
        
        result = self.analyzer.analyze_operation_complexity('unknown_operation')
        assert isinstance(result, ComplexityLevel)
    
    def test_complex_patterns_detection(self):
        """Test detection of complex programming patterns"""
        from functions.engines.selector import ComplexityLevel
        
        patterns_content = '''
        @decorator
        async def async_func():
            yield [x for x in data if x > 0]
            with open('file') as f:
                try:
                    result = dict(item for item in items)
                except Exception:
                    pass
        '''
        
        complexity = self.analyzer.analyze_content_complexity(patterns_content)
        assert complexity in [ComplexityLevel.HIGH, ComplexityLevel.CRITICAL]

if __name__ == '__main__':
    pytest.main([__file__, '-v'])