"""
Tests unitarios para BaseEngine interface común.
"""
import pytest
from functions.engines.base_engine import (
    BaseEngine, EngineCapability, EngineResult, EngineMatch, 
    OperationType, EngineStatus, EngineRegistry, register_engine
)

class MockEngine(BaseEngine):
    """Engine mock para testing"""
    
    def __init__(self, name="mock", version="1.0.0"):
        super().__init__(name, version)
        self._capabilities = {
            EngineCapability.LITERAL_SEARCH,
            EngineCapability.REGEX_SEARCH
        }
        self._supported_languages = {"python", "javascript"}
    
    def search(self, content: str, pattern: str, **kwargs) -> EngineResult:
        """Mock search implementation"""
        matches = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if pattern in line:
                match = EngineMatch(
                    content=line.strip(),
                    start_line=i,
                    end_line=i,
                    start_column=line.find(pattern),
                    end_column=line.find(pattern) + len(pattern)
                )
                matches.append(match)
        
        return EngineResult(
            status=EngineStatus.SUCCESS if matches else EngineStatus.FAILURE,
            matches=matches
        )
    
    def replace(self, content: str, pattern: str, replacement: str, **kwargs) -> EngineResult:
        """Mock replace implementation"""
        modified = content.replace(pattern, replacement)
        count = content.count(pattern)
        
        return EngineResult(
            status=EngineStatus.SUCCESS if count > 0 else EngineStatus.FAILURE,
            matches=[],  # Simplified for mock
            modified_content=modified,
            operations_count=count
        )

class TestBaseEngine:
    """Tests para BaseEngine interface"""
    
    def test_engine_initialization(self):
        """Test inicialización de engine"""
        engine = MockEngine("test", "2.0.0")
        
        assert engine.name == "test"
        assert engine.version == "2.0.0"
        assert isinstance(engine.capabilities, set)
        assert isinstance(engine.supported_languages, set)
    
    def test_capability_checking(self):
        """Test verificación de capacidades"""
        engine = MockEngine()
        
        assert engine.supports_capability(EngineCapability.LITERAL_SEARCH)
        assert engine.supports_capability(EngineCapability.REGEX_SEARCH)
        assert not engine.supports_capability(EngineCapability.AST_AWARE)
    
    def test_language_support(self):
        """Test soporte de lenguajes"""
        engine = MockEngine()
        
        assert engine.supports_language("python")
        assert engine.supports_language("PYTHON")  # Case insensitive
        assert engine.supports_language("javascript") 
        assert not engine.supports_language("java")
    
    def test_search_operation(self):
        """Test operación de búsqueda"""
        engine = MockEngine()
        content = "def test():\n    return True\n    test_var = 1"
        
        result = engine.search(content, "test")
        
        assert result.success
        assert result.has_matches
        assert len(result.matches) == 2  # "test" aparece 2 veces
        assert result.matches[0].start_line == 1
        assert result.matches[1].start_line == 3
    
    def test_replace_operation(self):
        """Test operación de reemplazo"""
        engine = MockEngine()
        content = "old_value = 1\nold_value = 2"
        
        result = engine.replace(content, "old_value", "new_value")
        
        assert result.success
        assert result.operations_count == 2
        assert "new_value = 1" in result.modified_content
        assert "old_value" not in result.modified_content
    
    def test_insert_before_operation(self):
        """Test inserción antes de patrón"""
        engine = MockEngine()
        content = "line1\ntarget_line\nline3"
        
        result = engine.insert_before(content, "target_line", "inserted_line")
        
        assert result.success
        lines = result.modified_content.split('\n')
        target_index = lines.index("target_line")
        assert lines[target_index - 1] == "inserted_line"
    
    def test_insert_after_operation(self):
        """Test inserción después de patrón"""
        engine = MockEngine()
        content = "line1\ntarget_line\nline3"
        
        result = engine.insert_after(content, "target_line", "inserted_line")
        
        assert result.success
        lines = result.modified_content.split('\n')
        target_index = lines.index("target_line")
        assert lines[target_index + 1] == "inserted_line"

class TestEngineRegistry:
    """Tests para EngineRegistry"""
    
    def setup_method(self):
        """Setup para cada test"""
        EngineRegistry.clear_cache()
        # Limpiar registry para testing aislado
        EngineRegistry._engines.clear()
    
    def test_register_engine(self):
        """Test registro de engine"""
        EngineRegistry.register(MockEngine, "test_engine")
        
        assert "test_engine" in EngineRegistry.list_engines()
        
        engine = EngineRegistry.get_engine("test_engine")
        assert isinstance(engine, MockEngine)
        assert engine.name == "mock"
    
    def test_register_decorator(self):
        """Test decorator de registro"""
        @register_engine("decorated_engine")
        class DecoratedEngine(MockEngine):
            pass
        
        assert "decorated_engine" in EngineRegistry.list_engines()
        engine = EngineRegistry.get_engine("decorated_engine")
        assert isinstance(engine, DecoratedEngine)
    
    def test_engine_not_found(self):
        """Test error cuando engine no existe"""
        with pytest.raises(ValueError, match="Engine 'nonexistent' not found"):
            EngineRegistry.get_engine("nonexistent")
    
    def test_engine_caching(self):
        """Test cache de instancias"""
        EngineRegistry.register(MockEngine, "cached_engine")
        
        engine1 = EngineRegistry.get_engine("cached_engine")
        engine2 = EngineRegistry.get_engine("cached_engine")
        
        # Debe ser la misma instancia (cached)
        assert engine1 is engine2
        
        # Con kwargs debe ser instancia nueva
        engine3 = EngineRegistry.get_engine("cached_engine", version="custom")
        assert engine3 is not engine1