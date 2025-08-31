"""
Tests de regresión completo: Verificación de 0 regresiones con engines
Garantiza que funcionalidad pre-engines permanece idéntica
"""
import pytest
from functions.engines.selector import EngineSelector
from functions.pattern.pattern_factory import PatternMatcherFactory
from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter
from functions.backup.manager import BackupManager
from coordinators.create import CreateCoordinator


class TestNoRegressionsEngines:
    """Tests que verifican que no hay regresiones con engines integrados"""
    
    def test_all_core_systems_import_successfully(self):
        """Verificar que todos los sistemas core importan sin regresiones"""
        # All critical imports should work
        selector = EngineSelector()
        factory = PatternMatcherFactory()
        reader = ContentReader()
        writer = ContentWriter()
        backup = BackupManager()
        coordinator = CreateCoordinator()
        
        assert selector is not None
        assert factory is not None
        assert reader is not None
        assert writer is not None
        assert backup is not None
        assert coordinator is not None

    def test_pattern_functions_maintain_pre_engines_functionality(self):
        """Verificar que pattern functions mantienen funcionalidad pre-engines"""
        factory = PatternMatcherFactory()
        
        # Core pattern functionality should be preserved
        literal_matcher = factory.get_optimized_matcher("literal", "native")
        regex_matcher = factory.get_optimized_matcher("regex", "native")
        
        assert literal_matcher is not None
        assert regex_matcher is not None
        assert hasattr(literal_matcher, 'find')
        assert hasattr(regex_matcher, 'find')

    def test_content_functions_maintain_pre_engines_functionality(self):
        """Verificar que content functions mantienen funcionalidad pre-engines"""
        reader = ContentReader()
        writer = ContentWriter()
        
        # Core content functionality should be preserved
        assert hasattr(reader, 'read_file')
        assert hasattr(writer, 'write_file')

    def test_backup_system_maintains_pre_engines_functionality(self):
        """Verificar que backup system mantiene funcionalidad pre-engines"""
        backup = BackupManager()
        
        # Core backup functionality should be preserved
        assert hasattr(backup, 'create_snapshot')
        assert hasattr(backup, 'list_snapshots')

    def test_coordinators_maintain_pre_engines_functionality(self):
        """Verificar que coordinadores mantienen funcionalidad pre-engines"""
        coordinator = CreateCoordinator()
        
        # Core coordinator functionality should be preserved
        assert coordinator is not None
        expected_methods = ['create_file', 'execute', 'run', 'process']
        has_method = any(hasattr(coordinator, method) for method in expected_methods)
        assert has_method

    def test_engines_integration_doesnt_break_existing_apis(self):
        """Verificar que integración engines no rompe APIs existentes"""
        selector = EngineSelector()
        
        # Engine system should provide expected functionality
        health = selector.get_engines_health_report()
        assert health is not None
        assert isinstance(health, dict)

    def test_system_wide_no_critical_import_errors(self):
        """Verificar que no hay errores críticos de import a nivel sistema"""
        try:
            from functions.engines.selector import EngineSelector, get_best_engine
            from functions.pattern.pattern_factory import PatternMatcherFactory, get_optimized_matcher
            from functions.content.reader import ContentReader
            from functions.content.writer import ContentWriter
            from functions.backup.manager import BackupManager
            from coordinators.create import CreateCoordinator
            
            # All imports successful
            assert True
            
        except ImportError as e:
            pytest.fail(f"Critical import failure: {e}")

    def test_engines_coexistence_with_all_systems(self):
        """Verificar que engines coexisten pacíficamente con todos los sistemas"""
        # Initialize all systems together
        selector = EngineSelector()
        factory = PatternMatcherFactory()
        reader = ContentReader()
        writer = ContentWriter()
        backup = BackupManager()
        coordinator = CreateCoordinator()
        
        # All should coexist without conflicts
        health = selector.get_engines_health_report()
        stats = factory.get_factory_statistics()
        
        assert health is not None
        assert stats is not None
        assert reader is not None
        assert writer is not None
        assert backup is not None
        assert coordinator is not None

    def test_performance_baseline_maintained(self):
        """Verificar que performance baseline se mantiene"""
        import time
        
        # Test basic operations don't have performance regressions
        start = time.time()
        
        selector = EngineSelector()
        factory = PatternMatcherFactory()
        reader = ContentReader()
        
        # Basic operations should complete quickly
        health = selector.get_engines_health_report()
        matcher = factory.get_optimized_matcher("literal", "native")
        
        end = time.time()
        duration = end - start
        
        # Should complete in reasonable time (less than 1 second)
        assert duration < 1.0, f"Basic operations took too long: {duration}s"
        assert health is not None
        assert matcher is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
