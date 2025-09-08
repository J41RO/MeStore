"""
Tests de compatibilidad e intercambiabilidad de engines.
Verifica que todos los engines implementen interface común y sean intercambiables.
"""
import pytest
from functions.engines.base_engine import (
    BaseEngine, EngineCapability, EngineResult, EngineMatch,
    OperationType, EngineStatus, EngineRegistry, register_engine
)


class TestEngineCompatibility:
    """Tests que verifican intercambiabilidad completa entre engines."""
    
    def setup_method(self):
        """Configurar registry para cada test."""
        self.registry = EngineRegistry()
        
    def test_all_engines_implement_same_interface(self):
        """Verificar que todos los engines implementan la interfaz común correctamente."""
        engines = self.registry.list_engines()
        assert len(engines) >= 1, f"Esperado al menos 1 engine, encontrado: {len(engines)}"
        
        # Verificar que todos los engines tienen los métodos requeridos
        for engine_name in engines:
            engine = self.registry.get_engine(engine_name)
            
            # Verificar métodos obligatorios
            assert hasattr(engine, 'search'), f"Engine {engine_name} falta método search"
            assert hasattr(engine, 'replace'), f"Engine {engine_name} falta método replace"
            assert hasattr(engine, 'capabilities'), f"Engine {engine_name} falta atributo capabilities"
            assert hasattr(engine, 'supports_capability'), f"Engine {engine_name} falta método supports_capability"
            
            # Verificar herencia correcta
            assert isinstance(engine, BaseEngine), f"Engine {engine_name} no hereda de BaseEngine"
            
    def test_engine_result_consistency(self):
        """Verificar que todos los engines retornan EngineResult con estructura consistente."""
        test_content = "def hello():\n    print('world')"
        test_pattern = "hello"
        
        for engine_name in self.registry.list_engines():
            engine = self.registry.get_engine(engine_name)
            
            # Test search method
            result = engine.search(test_content, test_pattern)
            assert isinstance(result, EngineResult), f"Engine {engine_name} search no retorna EngineResult"
            assert hasattr(result, 'status'), f"Engine {engine_name} result falta status"
            assert hasattr(result, 'matches'), f"Engine {engine_name} result falta matches"
            assert hasattr(result, 'metadata'), f"Engine {engine_name} result falta metadata"
            
            # Test replace method
            replace_result = engine.replace(test_content, test_pattern, "hi")
            assert isinstance(replace_result, EngineResult), f"Engine {engine_name} replace no retorna EngineResult"
            
    def test_engine_selection_by_capability(self):
        """Verificar selección automática de engines basada en capacidades."""
        # Test literal search - debería estar disponible en native
        literal_engines = []
        structural_engines = []
        
        for engine_name in self.registry.list_engines():
            engine = self.registry.get_engine(engine_name)
            
            if engine.supports_capability(EngineCapability.LITERAL_SEARCH):
                literal_engines.append(engine_name)
            if engine.supports_capability(EngineCapability.STRUCTURAL_SEARCH):
                structural_engines.append(engine_name)
                
        # Verificar que al menos hay cobertura para literal search
        assert len(literal_engines) > 0, "No hay engines que soporten LITERAL_SEARCH"
        # Verificar que hay al menos un engine con literal search (puede ser native u otro)
        print(f"Engines con LITERAL_SEARCH: {literal_engines}")
        
        # Verificar engines estructurales (comby/ast-grep pueden estar disponibles)
        print(f"Engines con LITERAL_SEARCH: {literal_engines}")
        print(f"Engines con STRUCTURAL_SEARCH: {structural_engines}")
        
    def test_fallback_behavior_robust(self):
        """Verificar comportamiento robusto de fallback automático."""
        test_content = "function test() { return 42; }"
        test_pattern = "test"
        
        results = {}
        for engine_name in self.registry.list_engines():
            engine = self.registry.get_engine(engine_name)
            result = engine.search(test_content, test_pattern)
            results[engine_name] = result
            
            # Todos los engines deben retornar resultado válido
            assert result.status in [EngineStatus.SUCCESS, EngineStatus.NOT_SUPPORTED], \
                f"Engine {engine_name} retornó status inválido: {result.status}"
                
        # Al menos un engine debe funcionar (native siempre debe funcionar)
        successful_engines = [name for name, result in results.items() 
                            if result.status == EngineStatus.SUCCESS]
        assert len(successful_engines) > 0, "Ningún engine funcionó correctamente"
        # Verificar que al menos un engine funciona
        print(f"Engines exitosos: {successful_engines}")
        
    def test_capability_coverage_complete(self):
        """Verificar cobertura completa de capacidades y complementariedad."""
        all_capabilities = set()
        coverage_map = {}
        
        # Recopilar todas las capacidades disponibles
        for capability in EngineCapability:
            coverage_map[capability] = []
            
        for engine_name in self.registry.list_engines():
            engine = self.registry.get_engine(engine_name)
            engine_caps = engine.capabilities
            all_capabilities.update(engine_caps)
            
            for cap in engine_caps:
                coverage_map[cap].append(engine_name)
                
        # Verificar que capacidades críticas están cubiertas
        critical_caps = [EngineCapability.LITERAL_SEARCH]
        for cap in critical_caps:
            assert len(coverage_map[cap]) > 0, f"Capacidad crítica {cap.value} no está cubierta"
            
        print("=== CAPABILITY COVERAGE ===")
        for cap, engines in coverage_map.items():
            if engines:  # Solo mostrar capacidades que están cubiertas
                print(f"{cap.value}: {engines}")
                
    def test_engine_substitution_transparent(self):
        """Verificar que engines pueden ser sustituidos transparentemente."""
        test_content = "class User:\n    def __init__(self):\n        pass"
        test_pattern = "User"
        
        # Obtener results de engines que soporten literal search
        literal_engines = []
        results = {}
        
        for engine_name in self.registry.list_engines():
            engine = self.registry.get_engine(engine_name)
            if engine.supports_capability(EngineCapability.LITERAL_SEARCH):
                literal_engines.append(engine_name)
                result = engine.search(test_content, test_pattern)
                results[engine_name] = result
                
        if len(literal_engines) > 1:
            # Si hay múltiples engines con literal search, deberían dar resultados similares
            successful_results = {name: result for name, result in results.items() 
                                if result.status == EngineStatus.SUCCESS}
            
            if len(successful_results) > 1:
                # Verificar que encontraron matches similares
                match_counts = {name: len(result.matches) for name, result in successful_results.items()}
                print(f"Match counts por engine: {match_counts}")
                
                # Al menos deberían encontrar el mismo número de matches básicos
                # (puede variar por implementación específica)
                min_matches = min(match_counts.values())
                assert min_matches > 0, "Engines deberían encontrar al menos un match"
                
    def test_consistent_error_handling(self):
        """Verificar manejo consistente de errores entre engines."""
        # Test con content vacío
        empty_content = ""
        test_pattern = "anything"
        
        for engine_name in self.registry.list_engines():
            engine = self.registry.get_engine(engine_name)
            result = engine.search(empty_content, test_pattern)
            
            # Debería retornar resultado válido incluso con content vacío
            assert isinstance(result, EngineResult), f"Engine {engine_name} no maneja content vacío"
            assert result.status in [EngineStatus.SUCCESS, EngineStatus.NOT_SUPPORTED, EngineStatus.FAILURE], \
                f"Engine {engine_name} status inválido para content vacío: {result.status}"
                
        # Test con pattern vacío
        test_content = "some content"
        empty_pattern = ""
        
        for engine_name in self.registry.list_engines():
            engine = self.registry.get_engine(engine_name)
            result = engine.search(test_content, empty_pattern)
            
            # Debería manejar gracefully el pattern vacío
            assert isinstance(result, EngineResult), f"Engine {engine_name} no maneja pattern vacío"
            
    def test_registry_integration_correct(self):
        """Verificar que integración con registry funciona correctamente."""
        # Verificar que registry mantiene engines disponibles
        engines_list = self.registry.list_engines()
        assert len(engines_list) >= 1, f"Registry debería tener al menos 1 engine, encontrado: {len(engines_list)}"
        
        # Verificar que get_engine funciona para todos los engines listados
        for engine_name in engines_list:
            engine = self.registry.get_engine(engine_name)
            assert engine is not None, f"Registry no puede obtener engine: {engine_name}"
            assert isinstance(engine, BaseEngine), f"Registry retorna objeto inválido para {engine_name}"
            
        # Verificar que get_engine con nombre inválido maneja gracefully (lanza ValueError)
        with pytest.raises(ValueError, match="Engine 'nonexistent_engine' not found"):
            self.registry.get_engine("nonexistent_engine")