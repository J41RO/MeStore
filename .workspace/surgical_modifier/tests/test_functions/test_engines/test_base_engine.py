"""
Tests unitarios para BaseEngine interface común.
"""
import pytest
from typing import List
from functions.engines.base_engine import (
    BaseEngine, EngineCapability, EngineResult, EngineMatch,
    OperationType, EngineStatus, EngineRegistry, register_engine
)

class MockEngine(BaseEngine):
    """Mock engine for testing"""
    
    def __init__(self, name="mock", version="1.0.0"):
        super().__init__(name, version)
        self._capabilities = {EngineCapability.LITERAL_SEARCH, EngineCapability.REGEX_SEARCH}
        self._supported_languages = {"python", "javascript", "java"}
    
    def _search_impl(self, content: str, pattern: str, **kwargs) -> EngineResult:
        """Mock search implementation"""
        matches = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if pattern in line:
                start_col = line.find(pattern)
                end_col = start_col + len(pattern)
                match = EngineMatch(
                    content=pattern,
                    start_line=line_num,
                    end_line=line_num,
                    start_column=start_col,
                    end_column=end_col,
                    context_before=line[:start_col],
                    context_after=line[end_col:]
                )
                matches.append(match)
        
        return EngineResult(
            status=EngineStatus.SUCCESS if matches else EngineStatus.FAILURE,
            matches=matches,
            operations_count=len(matches)
        )
    
    def _replace_impl(self, content: str, pattern: str, replacement: str, **kwargs) -> EngineResult:
        """Mock replace implementation"""
        search_result = self._search_impl(content, pattern, **kwargs)
        
        if not search_result.matches:
            return EngineResult(
                status=EngineStatus.FAILURE,
                matches=[],
                error_message=f"Pattern '{pattern}' not found"
            )
        
        modified_content = content.replace(pattern, replacement)
        
        return EngineResult(
            status=EngineStatus.SUCCESS,
            matches=search_result.matches,
            modified_content=modified_content,
            operations_count=len(search_result.matches)
        )


class TestBaseEngine:
    """Tests for BaseEngine abstract class"""
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = MockEngine("test", "2.0.0")
        assert engine.name == "test"
        assert engine.version == "2.0.0"
        # Removed is_available() - method doesn't exist in BaseEngine
    
    def test_capability_checking(self):
        """Test engine capability checking"""
        engine = MockEngine()
        assert engine.supports_capability(EngineCapability.LITERAL_SEARCH)
        assert engine.supports_capability(EngineCapability.REGEX_SEARCH)
        assert not engine.supports_capability(EngineCapability.STRUCTURAL_SEARCH)
    
    def test_language_support(self):
        """Test language support checking"""
        engine = MockEngine()
        assert engine.supports_language("python")
        assert engine.supports_language("javascript")
        assert not engine.supports_language("cobol")
    
    def test_search_operation(self):
        """Test search operation"""
        engine = MockEngine()
        content = "def hello():\n    print('world')\n    return 'hello'"
        
        result = engine.search(content, "hello")
        assert result.success
        assert len(result.matches) >= 1
        assert result.matches[0].content == "hello"
    
    def test_replace_operation(self):
        """Test replace operation"""
        engine = MockEngine()
        content = "def old_function():\n    return 'old'"
        
        result = engine.replace(content, "old", "new")
        assert result.success
        assert "new_function" in result.modified_content
        assert "new" in result.modified_content
        assert "old" not in result.modified_content
    
    def test_insert_before_operation(self):
        """Test insert before operation"""
        engine = MockEngine()
        content = "def function():\n    return True"
        
        result = engine.insert_before(content, "return True", "# Comment")
        assert result.success
        assert "# Comment" in result.modified_content
        assert result.modified_content.index("# Comment") < result.modified_content.index("return True")
    
    def test_insert_after_operation(self):
        """Test insert after operation"""
        engine = MockEngine()
        content = "def function():\n    pass"
        
        result = engine.insert_after(content, "def function():", "    # New line")
        assert result.success
        assert "# New line" in result.modified_content

class TestEngineRegistry:
    """Tests for EngineRegistry"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Clear registry before each test
        EngineRegistry._engines.clear()
        EngineRegistry._instances.clear()
    
    def test_register_engine(self):
        """Test engine registration"""
        # Fixed parameter order: (engine_class, name)
        EngineRegistry.register(MockEngine, "test_engine")
        assert "test_engine" in EngineRegistry._engines
        
        engine = EngineRegistry.get_engine("test_engine")
        assert isinstance(engine, MockEngine)
    
    def test_register_decorator(self):
        """Test register decorator"""
        @register_engine("decorated_engine")
        class DecoratedEngine(MockEngine):
            pass
        
        engine = EngineRegistry.get_engine("decorated_engine")
        assert isinstance(engine, DecoratedEngine)
    
    def test_engine_not_found(self):
        """Test engine not found exception"""
        with pytest.raises(ValueError, match="Engine 'nonexistent' not found"):
            EngineRegistry.get_engine("nonexistent")
    
    def test_engine_caching(self):
        """Test engine instance caching"""
        # Fixed parameter order: (engine_class, name)
        EngineRegistry.register(MockEngine, "cached_engine")
        
        engine1 = EngineRegistry.get_engine("cached_engine")
        engine2 = EngineRegistry.get_engine("cached_engine")
        
        assert engine1 is engine2  # Should be the same instance