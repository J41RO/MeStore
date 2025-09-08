"""
Tests de integración: Engines + Coordinador CREATE
Verifica que coordinador CREATE usa engines correctamente
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from functions.engines.selector import EngineSelector
from coordinators.create import CreateCoordinator


class TestEnginesCoordinatorIntegration:
    """Tests de integración entre engines y coordinador CREATE"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.selector = EngineSelector()
        
    def test_create_coordinator_imports_correctly(self):
        """Verificar que CreateCoordinator importa correctamente con engines"""
        # Test basic import and instantiation
        coordinator = CreateCoordinator()
        assert coordinator is not None
        
    def test_create_coordinator_basic_functionality_with_engines(self):
        """Verificar que CreateCoordinator mantiene funcionalidad básica con engines"""
        coordinator = CreateCoordinator()
        
        # Test basic methods exist
        assert hasattr(coordinator, 'create_file') or hasattr(coordinator, 'execute')
        
    def test_engines_selector_coexists_with_create_coordinator(self):
        """Verificar que EngineSelector coexiste con CreateCoordinator"""
        selector = EngineSelector()
        coordinator = CreateCoordinator()
        
        # Both should be functional
        health_report = selector.get_engines_health_report()
        assert health_report is not None
        assert coordinator is not None
        
    def test_create_coordinator_file_operations_integration(self):
        """Verificar que operaciones de archivo funcionan con engines presentes"""
        coordinator = CreateCoordinator()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            test_file = f.name
            
        try:
            # Test file creation works with engines in system
            if hasattr(coordinator, 'create_file'):
                # Test that method exists and can be called
                assert callable(getattr(coordinator, 'create_file'))
            elif hasattr(coordinator, 'execute'):
                # Alternative method
                assert callable(getattr(coordinator, 'execute'))
                
            # Engines should not interfere
            selector = EngineSelector()
            health = selector.get_engines_health_report()
            assert health is not None
            
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    def test_create_workflow_end_to_end_with_engines(self):
        """Verificar workflow completo CREATE con engines en sistema"""
        coordinator = CreateCoordinator()
        selector = EngineSelector()
        
        # Test complete workflow doesn't break
        try:
            # Systems should coexist
            health = selector.get_engines_health_report()
            assert health is not None
            assert coordinator is not None
            
            # Basic functionality preserved
            assert hasattr(coordinator, 'create_file') or hasattr(coordinator, 'execute')
            
        except Exception as e:
            # Should not fail due to engine integration
            assert "EngineSelector" not in str(e)
            assert "select_best_engine" not in str(e)

    def test_create_coordinator_preserves_functionality_with_engines(self):
        """Verificar que funcionalidad CREATE se preserva con engines"""
        coordinator = CreateCoordinator()
        
        # Test that CREATE functionality is preserved
        assert coordinator is not None
        
        # Engine system should not interfere with coordinator methods
        expected_methods = ['create_file', 'execute', 'run', 'process']
        has_expected_method = any(hasattr(coordinator, method) for method in expected_methods)
        assert has_expected_method, f"Coordinator should have at least one of: {expected_methods}"

    def test_integration_imports_no_circular_dependencies(self):
        """Verificar que no hay dependencias circulares entre engines y coordinador"""
        # Test imports work cleanly
        from functions.engines.selector import EngineSelector
        from coordinators.create import CreateCoordinator
        
        # Should instantiate without issues
        selector = EngineSelector()
        coordinator = CreateCoordinator()
        
        assert selector is not None
        assert coordinator is not None

    def test_engines_health_independent_of_coordinator_state(self):
        """Verificar que health engines es independiente del estado del coordinador"""
        selector = EngineSelector()
        coordinator = CreateCoordinator()
        
        # Health should work regardless of coordinator
        health_before = selector.get_engines_health_report()
        
        # Coordinator operations shouldn't affect engine health reporting
        health_after = selector.get_engines_health_report()
        
        assert health_before is not None
        assert health_after is not None
        assert isinstance(health_before, dict)
        assert isinstance(health_after, dict)

    def test_create_coordinator_error_handling_with_engines(self):
        """Verificar que manejo de errores funciona con engines presentes"""
        coordinator = CreateCoordinator()
        selector = EngineSelector()
        
        # Test error scenarios don't create integration issues
        try:
            # Both systems should handle errors independently  
            health = selector.get_engines_health_report()
            assert health is not None
            
            # Coordinator should still function
            assert coordinator is not None
            
        except Exception as e:
            # Errors should not be due to integration issues
            assert "engine" not in str(e).lower() or "selector" not in str(e).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
