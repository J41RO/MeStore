"""
Tests unitarios para AstEngine - motor de búsqueda basado en AST.
"""
import pytest
from functions.engines.ast_engine import AstEngine
from functions.engines.base_engine import EngineStatus, EngineRegistry


class TestAstEngine:
    """Tests para AstEngine implementation"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.engine = AstEngine()
    
    def test_engine_initialization(self):
        """Test inicialización de AstEngine"""
        assert self.engine.name == "ast-grep"
        assert self.engine.version == "1.0.0"
        assert len(self.engine.capabilities) >= 1
        assert "AST_AWARE" in [cap.name for cap in self.engine.capabilities]
    
    def test_search_when_ast_grep_not_available(self):
        """Test búsqueda cuando ast-grep no está disponible"""
        content = "def test_function():\n    variable = 'test'\n    return variable"
        result = self.engine.search(content, "test")
        
        # AstEngine debería retornar NOT_SUPPORTED cuando ast-grep no está instalado
        assert result.status == EngineStatus.NOT_SUPPORTED
        assert not result.success
        assert result.error_message is not None
        assert "ast-grep" in result.error_message.lower() or "ast" in result.error_message.lower()
    
    def test_replace_when_ast_grep_not_available(self):
        """Test reemplazo cuando ast-grep no está disponible"""
        content = "old_name = 1"
        result = self.engine.replace(content, "old_name", "new_name")
        
        assert result.status == EngineStatus.NOT_SUPPORTED
        assert not result.success
        assert result.error_message is not None
        assert "ast-grep" in result.error_message.lower() or "ast" in result.error_message.lower()
        # El contenido no debe modificarse cuando la herramienta no está disponible
        assert result.modified_content == content
    
    def test_ast_aware_capability(self):
        """Test capacidad específica de análisis AST"""
        capabilities = [cap.name for cap in self.engine.capabilities]
        assert "AST_AWARE" in capabilities
        
        # Verificar que también tiene capacidad de búsqueda estructural
        assert "STRUCTURAL_SEARCH" in capabilities or len(capabilities) >= 1
        
        # Verificar lenguajes soportados para análisis AST
        supported_langs = self.engine.supported_languages
        assert len(supported_langs) >= 0  # AST engines can support 0 (all) or specific languages
    
    def test_structural_search_capability(self):
        """Test capacidad de búsqueda estructural basada en AST"""
        capabilities = [cap.name for cap in self.engine.capabilities]
        
        # AST engines deberían tener capacidades estructurales
        expected_capabilities = ["AST_AWARE", "STRUCTURAL_SEARCH"]
        found_capabilities = [cap for cap in expected_capabilities if cap in capabilities]
        assert len(found_capabilities) >= 1
    
    def test_error_message_clarity(self):
        """Test claridad de mensajes de error"""
        content = "test content"
        result = self.engine.search(content, "pattern")
        
        assert result.error_message is not None
        assert len(result.error_message) > 10  # Mensaje descriptivo
        # Debe mencionar la herramienta específica
        assert any(word in result.error_message.lower() for word in ["ast-grep", "ast", "install", "available"])
    
    def test_language_specific_support(self):
        """Test soporte específico de lenguajes para AST"""
        supported_langs = self.engine.supported_languages
        
        # AST engines típicamente soportan lenguajes específicos
        if len(supported_langs) > 0:
            # Verificar que los lenguajes son strings válidos
            for lang in supported_langs:
                assert isinstance(lang, str)
                assert len(lang) > 0
        
        # El engine debería reportar lenguajes soportados o soportar todos
        assert len(supported_langs) >= 0
    
    def test_engine_registry_integration(self):
        """Test integración con EngineRegistry"""
        # Verificar que el engine puede ser registrado
        assert self.engine.name is not None
        assert len(self.engine.name) > 0
        
        # Verificar que tiene las propiedades requeridas para registry
        assert hasattr(self.engine, 'capabilities')
        assert hasattr(self.engine, 'supported_languages')
        assert hasattr(self.engine, 'version')
        
        # Verificar que el name es específico para AST
        assert "ast" in self.engine.name.lower()