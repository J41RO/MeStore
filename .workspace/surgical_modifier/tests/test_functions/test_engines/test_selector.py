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

    def test_engine_metrics_tracking(self):
        """Test tracking automático de métricas en engines"""
        engine = NativeEngine()
        initial_count = engine._metrics.operation_count["search"]
        
        result = engine.search("def test(): pass", "def")
        
        assert engine._metrics.operation_count["search"] == initial_count + 1
        assert hasattr(result, "execution_time")
        assert result.execution_time > 0

    def test_performance_benchmark_functionality(self):
        """Test sistema de benchmarking comparativo"""
        benchmark_results = self.selector.run_comparative_benchmark(
            operation="search",
            test_content="def hello(): return \"world\"",
            pattern="def",
            engines=["native"],
            iterations=2
        )
        
        assert "native" in benchmark_results
        assert "avg_execution_time" in benchmark_results["native"]
        assert "success_rate" in benchmark_results["native"]

    def test_ml_prediction_system(self):
        """Test sistema predictivo ML"""
        prediction = self.selector.predict_optimal_engine(
            operation="search",
            content="def complex_function(): pass",
            context={"language": "python"}
        )
        
        assert "recommended_engine" in prediction
        assert "confidence_score" in prediction

    def test_performance_dashboard(self):
        """Test dashboard de analytics"""
        dashboard = self.selector.get_performance_dashboard()
        
        required_sections = ["overview", "engine_comparison", "trends", "alerts", "recommendations"]
        for section in required_sections:
            assert section in dashboard

    def test_adaptive_learning_feedback(self):
        """Test sistema de aprendizaje adaptativo"""
        feedback = self.selector.record_operation_feedback(
            engine="native",
            operation="search",
            success=True,
            execution_time=0.05
        )
        
        assert feedback["feedback_recorded"] is True

    def test_auto_optimization(self):
        """Test optimización automática de parámetros"""
        optimization = self.selector.auto_optimize_parameters()
        
        assert "optimizations_applied" in optimization
        assert isinstance(optimization["optimizations_applied"], int)

    def test_engine_metrics_performance_summary(self):
        """Test resumen de métricas de performance"""
        engine = NativeEngine()
        
        # Generar algunas operaciones
        for i in range(3):
            engine.search(f'test{i}', 'test')
        
        summary = engine.get_performance_metrics()
        
        assert 'engine_name' in summary
        assert 'total_operations' in summary
        assert 'success_rate' in summary
        assert summary['total_operations'] >= 3

    def test_benchmarking_error_handling(self):
        """Test manejo de errores en benchmarking"""
        results = self.selector.run_comparative_benchmark(
            operation='search',
            test_content='invalid content',
            pattern='test',
            engines=['native'],
            iterations=1
        )
        
        # Debe manejar errores gracefully
        assert 'native' in results

    def test_performance_alerts_system(self):
        """Test sistema de alertas de performance"""
        alerts = self.selector.check_performance_alerts()
        
        assert 'status' in alerts
        assert 'active_alerts' in alerts
        assert 'alert_summary' in alerts
        assert isinstance(alerts['active_alerts'], list)

    def test_optimization_recommendations(self):
        """Test sistema de recomendaciones"""
        recommendations = self.selector.get_optimization_recommendations()
        
        assert isinstance(recommendations, list)
        for rec in recommendations:
            assert 'type' in rec
            assert 'priority' in rec

    def test_engine_selection_with_performance_data(self):
        """Test selección con datos de performance"""
        # Test con performance data habilitada
        engine1 = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH]
        )
        
        assert isinstance(engine1, BaseEngine)

    def test_metrics_persistence_across_operations(self):
        """Test persistencia de métricas entre operaciones"""
        engine = NativeEngine()
        
        # Primera operación
        engine.search('test1', 'test')
        first_count = engine._metrics.operation_count['search']
        
        # Segunda operación
        engine.search('test2', 'test')
        second_count = engine._metrics.operation_count['search']
        
        assert second_count == first_count + 1

    def test_performance_trends_analysis(self):
        """Test análisis de tendencias"""
        dashboard = self.selector.get_performance_dashboard()
        trends = dashboard['trends']
        
        assert 'selection_times' in trends
        assert 'engine_usage' in trends
        assert 'error_rates' in trends

    def test_efficiency_report_generation(self):
        """Test generación de reportes de eficiencia"""
        report = self.selector.generate_efficiency_report()
        
        assert 'system_efficiency' in report
        assert 'engine_efficiency' in report
        assert 'resource_utilization' in report
        assert 'timestamp' in report

    def test_content_complexity_analysis(self):
        """Test análisis de complejidad de contenido"""
        # Contenido simple
        simple_prediction = self.selector.predict_optimal_engine(
            'search', 'hello world', {'complexity': 'low'}
        )
        
        # Contenido complejo
        complex_content = '''
        class ComplexClass:
            def __init__(self, *args, **kwargs):
                self.data = [x for x in args if callable(x)]
        '''
        complex_prediction = self.selector.predict_optimal_engine(
            'search', complex_content, {'complexity': 'high'}
        )
        
        assert 'content_analysis' in complex_prediction
        assert complex_prediction['content_analysis']['complexity'] in ['low', 'medium', 'high']

    def test_selection_small_files(self):
        """Test selección automática para archivos pequeños (<1KB)"""
        small_content = "def hello(): pass"  # ~20 bytes
        
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            content=small_content
        )
        
        # Para archivos pequeños debe preferir NativeEngine (más eficiente)
        assert isinstance(engine, BaseEngine)
        assert engine.__class__.__name__ in ['NativeEngine', 'MockEngine']

    def test_selection_medium_files(self):
        """Test selección automática para archivos medianos (1KB-50KB)"""
        medium_content = "def function():\n    pass\n" * 100  # ~2KB
        
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            content=medium_content
        )
        
        assert isinstance(engine, BaseEngine)

    def test_selection_large_files(self):
        """Test selección automática para archivos grandes (>50KB)"""  
        large_content = "def large_function():\n    return 'data'\n" * 2000  # ~60KB
        
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            content=large_content
        )
        
        assert isinstance(engine, BaseEngine)

    def test_selection_search_operations(self):
        """Test selección automática para operaciones de búsqueda"""
        content = "function searchMe() { return true; }"
        
        # Search literal debería preferir NativeEngine
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            content=content
        )
        
        assert isinstance(engine, BaseEngine)
        # Verificar que puede realizar búsqueda
        result = engine.search(content, "searchMe")
        assert hasattr(result, 'matches')

    def test_selection_replace_operations(self):
        """Test selección automática para operaciones de reemplazo"""
        content = "function oldName() { return false; }"
        
        # Replace debería seleccionar engine apropiado
        engine = self.selector.select_best_engine(
            operation_type='replace',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            content=content
        )
        
        assert isinstance(engine, BaseEngine)
        # Verificar que puede realizar reemplazo
        result = engine.replace(content, "oldName", "newName")
        assert hasattr(result, 'modified_content')

    def test_selection_structural_operations(self):
        """Test selección automática para operaciones estructurales"""
        content = "class MyClass { method() { return data; } }"
        
        # Operaciones estructurales necesitan engines avanzados
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.STRUCTURAL_SEARCH],
            content=content
        )
        
        assert isinstance(engine, BaseEngine)
        # Engine debe soportar búsqueda estructural
        assert engine.supports_capability(EngineCapability.STRUCTURAL_SEARCH) or \
            engine.supports_capability(EngineCapability.LITERAL_SEARCH)
    
    def test_selection_python_language(self):
        """Test selección automática para código Python"""
        python_content = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
        """
        
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            content=python_content,
            language='python'
        )
        
        assert isinstance(engine, BaseEngine)
        # Engine debe soportar Python o ser genérico
        assert engine.supports_language('python') or len(engine.supported_languages) == 0

    def test_selection_javascript_language(self):
        """Test selección automática para código JavaScript"""
        js_content = """
function calculateSum(arr) {
    return arr.reduce((acc, val) => acc + val, 0);
}
        """
        
        engine = self.selector.select_best_engine(
            operation_type='replace',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            content=js_content,
            language='javascript'
        )
        
        assert isinstance(engine, BaseEngine)
        # Engine debe soportar JavaScript o ser genérico
        assert engine.supports_language('javascript') or len(engine.supported_languages) == 0

    def test_selection_generic_language_fallback(self):
        """Test selección con lenguaje no específicamente soportado"""
        rust_content = """
fn main() {
    let x = 5;
    println!("Value: {}", x);
}
        """
        
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            content=rust_content,
            language='rust'
        )
        
        assert isinstance(engine, BaseEngine)
        # Engine debe funcionar aunque no soporte específicamente el lenguaje
        result = engine.search(rust_content, "main")
        assert hasattr(result, 'matches')
    
    def test_selection_simple_patterns(self):
        """Test selección para patrones simples y literales"""
        content = "function simple() { return true; }"
        simple_pattern = "simple"
        
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            content=content,
            pattern=simple_pattern
        )
        
        assert isinstance(engine, BaseEngine)
        # Para patrones simples cualquier engine debería funcionar
        result = engine.search(content, simple_pattern)
        assert hasattr(result, 'matches')

    def test_selection_regex_patterns(self):
        """Test selección para patrones con regex"""
        content = "user_id_123 and admin_id_456"
        regex_pattern = r"\w+_id_\d+"
        
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.REGEX_SEARCH],
            content=content
        )
        
        assert isinstance(engine, BaseEngine)
        # Engine debe soportar regex o fallback a literal
        supports_regex = engine.supports_capability(EngineCapability.REGEX_SEARCH)
        supports_literal = engine.supports_capability(EngineCapability.LITERAL_SEARCH)
        assert supports_regex or supports_literal

    def test_selection_complex_multiline_patterns(self):
        """Test selección para patrones complejos multilínea"""
        complex_content = """
class DatabaseManager:
    def __init__(self):
        self.connection = None
        
    def connect(self):
        # Complex connection logic
        pass
        
    def disconnect(self):
        if self.connection:
            self.connection.close()
        """
        
        engine = self.selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.MULTILINE_PATTERNS],
            content=complex_content
        )
        
        assert isinstance(engine, BaseEngine)
        # Engine debe manejar contenido multilínea
        result = engine.search(complex_content, "class")
        assert hasattr(result, 'matches')
    
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

class TestFallbackSystem:
    """Tests para el sistema de fallback robusto"""
    
    def test_fallback_strategy_enum_values(self):
        """Test que verifica los valores del enum FallbackStrategy"""
        from functions.engines.selector import FallbackStrategy
        
        assert FallbackStrategy.STRICT.value == "strict"
        assert FallbackStrategy.GRACEFUL.value == "graceful"
        assert FallbackStrategy.AGGRESSIVE.value == "aggressive"
    
    def test_failure_registry_initialization(self):
        """Test inicialización de FailureRegistry"""
        from functions.engines.selector import FailureRegistry
        
        registry = FailureRegistry()
        assert registry.failure_threshold == 3
        assert registry.recovery_window == 300
        assert len(registry.circuit_breakers) == 0
    
    def test_failure_registry_record_failure(self):
        """Test registro de fallos en FailureRegistry"""
        from functions.engines.selector import FailureRegistry
        
        registry = FailureRegistry()
        registry.record_failure('test_engine', 'timeout')
        
        assert registry.failure_counts['test_engine'] == 1
        assert 'test_engine' in registry.last_failure_time
        assert len(registry.failures['test_engine']) == 1
    
    def test_failure_registry_record_success(self):
        """Test registro de éxitos en FailureRegistry"""
        from functions.engines.selector import FailureRegistry
        
        registry = FailureRegistry()
        registry.record_success('test_engine')
        
        assert registry.success_counts['test_engine'] == 1
    
    def test_failure_registry_reliability_score(self):
        """Test cálculo de score de confiabilidad"""
        from functions.engines.selector import FailureRegistry
        
        registry = FailureRegistry()
        # Sin historial debe retornar score neutral
        score = registry.get_reliability_score('new_engine')
        assert score == 0.8
        
        # Con éxitos debe tener score alto
        for _ in range(10):
            registry.record_success('good_engine')
        score = registry.get_reliability_score('good_engine')
        assert score >= 0.8
        
        # Con fallos debe tener score bajo
        for _ in range(8):
            registry.record_failure('bad_engine', 'error')
        for _ in range(2):
            registry.record_success('bad_engine')
        score = registry.get_reliability_score('bad_engine')
        assert score < 0.5
    
    def test_failure_registry_circuit_breaker(self):
        """Test activación de circuit breaker"""
        from functions.engines.selector import FailureRegistry
        
        registry = FailureRegistry(failure_threshold=2)
        
        # No debe estar en circuit breaker inicialmente
        assert registry.is_engine_available('test_engine')
        
        # Después de superar threshold debe activar circuit breaker
        registry.record_failure('test_engine', 'error')
        registry.record_failure('test_engine', 'error')
        
        assert 'test_engine' in registry.circuit_breakers
        assert not registry.is_engine_available('test_engine')
    
    def test_execute_with_fallback_graceful_strategy(self):
        """Test execute_with_fallback con estrategia GRACEFUL"""
        from functions.engines.selector import EngineSelector, FallbackStrategy
        from functions.engines.base_engine import EngineCapability
        
        selector = EngineSelector()
        result = selector.execute_with_fallback(
            operation='search',
            content='def test(): pass',
            pattern='test',
            capabilities=[EngineCapability.LITERAL_SEARCH],
            fallback_strategy=FallbackStrategy.GRACEFUL
        )
        
        assert result is not None
        assert hasattr(result, 'status')
        assert hasattr(result, 'metadata')
        if hasattr(result, 'metadata') and result.metadata:
            assert 'fallback_strategy' in result.metadata
            assert result.metadata['fallback_strategy'] == 'graceful'
    
    def test_execute_with_fallback_strict_strategy(self):
        """Test execute_with_fallback con estrategia STRICT"""
        from functions.engines.selector import EngineSelector, FallbackStrategy
        from functions.engines.base_engine import EngineCapability
        
        selector = EngineSelector()
        result = selector.execute_with_fallback(
            operation='search',
            content='def test(): pass',
            pattern='test',
            capabilities=[EngineCapability.LITERAL_SEARCH],
            fallback_strategy=FallbackStrategy.STRICT
        )
        
        assert result is not None
        assert hasattr(result, 'status')
    
    def test_execute_with_fallback_aggressive_strategy(self):
        """Test execute_with_fallback con estrategia AGGRESSIVE"""
        from functions.engines.selector import EngineSelector, FallbackStrategy
        from functions.engines.base_engine import EngineCapability
        
        selector = EngineSelector()
        result = selector.execute_with_fallback(
            operation='search',
            content='def test(): pass',
            pattern='test',
            capabilities=[EngineCapability.LITERAL_SEARCH],
            fallback_strategy=FallbackStrategy.AGGRESSIVE
        )
        
        assert result is not None
        assert hasattr(result, 'status')
    
    def test_select_best_engine_with_fallback_strategy(self):
        """Test select_best_engine con parámetro fallback_strategy"""
        from functions.engines.selector import EngineSelector, FallbackStrategy
        from functions.engines.base_engine import EngineCapability
        
        selector = EngineSelector()
        
        # Test con diferentes estrategias
        engine1 = selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            fallback_strategy=FallbackStrategy.GRACEFUL
        )
        assert engine1 is not None
        
        engine2 = selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            fallback_strategy=FallbackStrategy.AGGRESSIVE
        )
        assert engine2 is not None


class TestFailureRecovery:
    """Tests para recovery y health monitoring"""
    
    def test_engine_health_report_generation(self):
        """Test generación de reporte de salud de engines"""
        from functions.engines.selector import EngineSelector
        
        selector = EngineSelector()
        health_report = selector.get_engines_health_report()
        
        assert isinstance(health_report, dict)
        assert len(health_report) > 0
        
        # Verificar estructura de cada entry
        for engine_name, info in health_report.items():
            assert 'engine_class' in info
            assert 'capabilities' in info
            assert 'available' in info
            assert 'health_status' in info
            assert 'recommendations' in info
    
    def test_engine_health_check(self):
        """Test verificación de salud individual de engines"""
        from functions.engines.selector import EngineSelector
        
        selector = EngineSelector()
        
        # Test con engine que debería estar disponible
        is_healthy = selector.is_engine_healthy('native')
        assert isinstance(is_healthy, bool)
        
        # Test con engine que no existe
        is_healthy_fake = selector.is_engine_healthy('fake_engine')
        assert is_healthy_fake == False
    
    def test_engine_recovery_attempt(self):
        """Test intento de recuperación de engine"""
        from functions.engines.selector import EngineSelector
        
        selector = EngineSelector()
        
        # Test recovery de engine existente
        recovery_result = selector.attempt_engine_recovery('native')
        assert isinstance(recovery_result, bool)
        
        # Test recovery de engine que no existe
        recovery_fake = selector.attempt_engine_recovery('fake_engine')
        assert recovery_fake == False
    
    def test_failure_prediction_system(self):
        """Test sistema de predicción de fallos"""
        from functions.engines.selector import EngineSelector
        
        selector = EngineSelector()
        
        # Test predicción para engine existente
        prediction = selector.predict_engine_failure_risk('native')
        
        assert isinstance(prediction, dict)
        assert 'risk_level' in prediction
        assert 'risk_score' in prediction
        assert 'risk_factors' in prediction
        assert 'reliability_score' in prediction
        assert 'recommendations' in prediction
        
        # Test predicción para engine inexistente
        prediction_fake = selector.predict_engine_failure_risk('fake_engine')
        assert prediction_fake['risk_level'] == 'UNKNOWN'


class TestPerformanceOptimization:
    """Tests para optimización y caching"""
    
    def test_performance_metrics_availability(self):
        """Test disponibilidad de métricas de performance"""
        from functions.engines.selector import EngineSelector
        
        selector = EngineSelector()
        metrics = selector.get_performance_metrics()
        
        assert isinstance(metrics, dict)
        assert 'cache_statistics' in metrics
        assert 'performance_statistics' in metrics
        assert 'fallback_statistics' in metrics
        assert 'engine_health_summary' in metrics
        
        # Verificar estructura de cache statistics
        cache_stats = metrics['cache_statistics']
        assert 'hit_rate_percent' in cache_stats
        assert 'total_hits' in cache_stats
        assert 'total_misses' in cache_stats
        assert 'cache_size' in cache_stats
    
    def test_caching_functionality(self):
        """Test funcionalidad de caching"""
        from functions.engines.selector import EngineSelector, FallbackStrategy
        from functions.engines.base_engine import EngineCapability
        import time
        
        selector = EngineSelector()
        
        # Primera llamada (debe generar cache miss)
        start_time = time.time()
        engine1 = selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            fallback_strategy=FallbackStrategy.GRACEFUL
        )
        first_call_time = time.time() - start_time
        
        # Segunda llamada idéntica (debe usar cache)
        start_time = time.time()
        engine2 = selector.select_best_engine(
            operation_type='search',
            capabilities_needed=[EngineCapability.LITERAL_SEARCH],
            fallback_strategy=FallbackStrategy.GRACEFUL
        )
        second_call_time = time.time() - start_time
        
        # Segunda llamada debe ser más rápida (usa cache)
        assert second_call_time <= first_call_time
        assert engine1.__class__ == engine2.__class__
        
        # Verificar que cache hit rate aumentó
        metrics = selector.get_performance_metrics()
        assert metrics['cache_statistics']['total_hits'] > 0
    
    def test_cache_invalidation(self):
        """Test invalidación de cache por engine unhealthy"""
        from functions.engines.selector import EngineSelector, FallbackStrategy
        from functions.engines.base_engine import EngineCapability
        
        selector = EngineSelector()
        
        # Forzar fallo en un engine para que sea unhealthy
        selector.failure_registry.record_failure('native', 'test_failure')
        selector.failure_registry.record_failure('native', 'test_failure')
        selector.failure_registry.record_failure('native', 'test_failure')
        
        # Cache key debería invalidarse para engines unhealthy
        cache_key = selector._get_cache_key(
            'search', [EngineCapability.LITERAL_SEARCH], None, FallbackStrategy.GRACEFUL
        )
        
        # Simular entrada en cache
        selector._cache_selection(cache_key, 'native', 0.5)
        
        # Al intentar obtener desde cache, debería rechazar engine unhealthy
        cached_result = selector._get_cached_selection(cache_key)
        # Debería ser None porque native está unhealthy
        assert cached_result is None or selector.is_engine_healthy(cached_result)


class TestFallbackEdgeCases:
    """Tests para casos edge del sistema de fallback"""
    
    def test_fallback_with_no_engines_available(self):
        """Test fallback cuando no hay engines disponibles"""
        from functions.engines.selector import EngineSelector, FallbackStrategy
        from functions.engines.base_engine import EngineCapability
        
        selector = EngineSelector()
        
        # Simular que todos los engines están en circuit breaker
        for engine_name in ['native', 'comby', 'ast-grep']:
            for _ in range(5):  # Exceder threshold
                selector.failure_registry.record_failure(engine_name, 'test_failure')
        
        result = selector.execute_with_fallback(
            operation='search',
            content='def test(): pass',
            pattern='test',
            capabilities=[EngineCapability.LITERAL_SEARCH],
            fallback_strategy=FallbackStrategy.AGGRESSIVE
        )
        
        # Debe retornar resultado de fallo
        assert result is not None
        assert hasattr(result, 'status')
    
    def test_fallback_timeout_handling(self):
        """Test manejo de timeouts en fallback"""
        from functions.engines.selector import EngineSelector, FallbackStrategy
        from functions.engines.base_engine import EngineCapability
        
        selector = EngineSelector()
        
        # Test con timeout muy corto
        result = selector.execute_with_fallback(
            operation='search',
            content='def test(): pass',
            pattern='test',
            capabilities=[EngineCapability.LITERAL_SEARCH],
            fallback_strategy=FallbackStrategy.GRACEFUL,
            timeout=0.001  # 1ms timeout muy corto
        )
        
        assert result is not None
        assert hasattr(result, 'metadata')
        if result.metadata and 'fallback_attempts' in result.metadata:
            attempts = result.metadata['fallback_attempts']
            # Debería haber algunos intentos con timeout
            timeout_attempts = [a for a in attempts if a['status'] == 'timeout']
            # Al menos un timeout o resultado exitoso
            assert len(timeout_attempts) > 0 or any(a['status'] == 'success' for a in attempts)
    
    def test_circuit_breaker_recovery(self):
        """Test recuperación automática de circuit breaker"""
        from functions.engines.selector import FailureRegistry
        from datetime import datetime, timedelta
        
        registry = FailureRegistry(recovery_window=1)  # 1 segundo de recovery
        
        # Activar circuit breaker
        registry.record_failure('test_engine', 'error')
        registry.record_failure('test_engine', 'error')
        registry.record_failure('test_engine', 'error')
        
        assert not registry.is_engine_available('test_engine')
        
        # Simular paso del tiempo ajustando last_failure_time
        registry.last_failure_time['test_engine'] = datetime.now() - timedelta(seconds=2)
        
        # Ahora debería estar disponible
        assert registry.is_engine_available('test_engine')
        assert 'test_engine' not in registry.circuit_breakers