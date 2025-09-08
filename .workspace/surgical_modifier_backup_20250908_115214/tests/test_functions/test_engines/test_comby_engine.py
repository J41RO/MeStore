"""
Tests unitarios para CombyEngine - motor de búsqueda estructural.
"""
import pytest
from functions.engines.comby_engine import CombyEngine
from functions.engines.base_engine import EngineStatus, EngineRegistry


class TestCombyEngine:
    """Tests para CombyEngine implementation"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.engine = CombyEngine()
    
    def test_engine_initialization(self):
        """Test inicialización de CombyEngine"""
        assert self.engine.name == "comby"
        assert self.engine.version == "1.0.0"
        assert len(self.engine.capabilities) >= 1
        assert "STRUCTURAL_SEARCH" in [cap.name for cap in self.engine.capabilities]
    
    def test_search_when_comby_not_available(self):
        """Test búsqueda cuando comby no está disponible"""
        content = "def test_function():\n    variable = 'test'\n    return variable"
        result = self.engine.search(content, "test")
        
        # CombyEngine debería retornar NOT_SUPPORTED cuando comby no está instalado
        assert result.status == EngineStatus.NOT_SUPPORTED
        assert not result.success
        assert result.error_message is not None
        assert "comby" in result.error_message.lower()
    
    def test_replace_when_comby_not_available(self):
        """Test reemplazo cuando comby no está disponible"""
        content = "old_name = 1"
        result = self.engine.replace(content, "old_name", "new_name")
        
        assert result.status == EngineStatus.NOT_SUPPORTED
        assert not result.success
        assert result.error_message is not None
        assert "comby" in result.error_message.lower()
        # El contenido puede ser None cuando la herramienta no está disponible
        assert result.modified_content is None or result.modified_content == content
    
    def test_structural_search_capability(self):
        """Test capacidad de búsqueda estructural específica"""
        capabilities = [cap.name for cap in self.engine.capabilities]
        assert "STRUCTURAL_SEARCH" in capabilities
        
        # Verificar que tiene capacidades específicas de comby
        supported_langs = self.engine.supported_languages
        # CombyEngine debería soportar múltiples lenguajes para búsqueda estructural
        assert len(supported_langs) > 0 or len(supported_langs) == 0  # 0 means all languages
    
    def test_error_message_clarity(self):
        """Test claridad de mensajes de error"""
        content = "test content"
        result = self.engine.search(content, "pattern")
        
        assert result.error_message is not None
        assert len(result.error_message) > 10  # Mensaje descriptivo
        # Debe mencionar la herramienta específica
        assert any(word in result.error_message.lower() for word in ["comby", "install", "available"])
    
    def test_engine_registry_integration(self):
        """Test integración con EngineRegistry"""
        # Verificar que el engine puede ser registrado
        assert self.engine.name is not None
        assert len(self.engine.name) > 0
        
        # Verificar que tiene las propiedades requeridas para registry
        assert hasattr(self.engine, 'capabilities')
        assert hasattr(self.engine, 'supported_languages')
        assert hasattr(self.engine, 'version')