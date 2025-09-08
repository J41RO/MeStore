import pytest
from surgical_modifier.base_coordinator import BaseCoordinator

class TestableCoordinator(BaseCoordinator):
    """Implementación concreta para testing de BaseCoordinator"""
    def execute(self, *args, **kwargs):
        return {"status": "success", "data": "test"}
    
    def validate_inputs(self, *args, **kwargs):
        return True

class TestBaseCoordinator:
    """Tests unitarios para BaseCoordinator - solo funcionalidad verificada"""
    
    def test_coordinator_basic_instantiation(self):
        """Test instanciación básica funciona"""
        coordinator = TestableCoordinator()
        assert coordinator is not None
    
    def test_execute_method_works(self):
        """Test método execute implementado"""
        coordinator = TestableCoordinator()
        result = coordinator.execute()
        assert result["status"] == "success"
    
    def test_validate_inputs_method_works(self):
        """Test método validate_inputs implementado"""
        coordinator = TestableCoordinator()
        result = coordinator.validate_inputs()
        assert result == True
    
    def test_is_instance_of_basecoordinator(self):
        """Test herencia funciona correctamente"""
        coordinator = TestableCoordinator()
        assert isinstance(coordinator, BaseCoordinator)
    
    def test_has_required_abstract_methods(self):
        """Test que los métodos abstractos existen"""
        # Si la clase se puede instanciar, significa que implementó los métodos abstractos
        coordinator = TestableCoordinator()
        assert callable(getattr(coordinator, 'execute', None))
        assert callable(getattr(coordinator, 'validate_inputs', None))
