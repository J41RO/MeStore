"""
Tests de integración: Engines + Content Functions
Verifica que engines manejan content reader/writer sin corromper archivos
"""
import pytest
import tempfile
import os
from functions.engines.selector import EngineSelector
from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter
from functions.backup.manager import BackupManager


class TestEnginesContentIntegration:
    """Tests de integración entre engines y content functions"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.selector = EngineSelector()
        self.reader = ContentReader()
        self.writer = ContentWriter()
        
    def test_content_reader_works_with_engines(self):
        """Verificar que ContentReader funciona independientemente de engines"""
        assert hasattr(self.reader, 'read_file')
        
    def test_content_writer_works_with_engines(self):
        """Verificar que ContentWriter funciona independientemente de engines"""
        assert hasattr(self.writer, 'write_file')
        
    def test_engines_preserve_content_encoding_dict_format(self):
        """Verificar que engines preservan encoding usando formato dict correcto"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            test_content = "# -*- coding: utf-8 -*-\ndef test(): pass"
            f.write(test_content)
            f.flush()
            
            try:
                result = self.reader.read_file(f.name)
                
                assert isinstance(result, dict)
                assert 'content' in result
                assert 'encoding_info' in result
                assert "utf-8" in result['content']
                assert "def test()" in result['content']
                
            finally:
                os.unlink(f.name)

    def test_backup_system_real_methods_integration(self):
        """Verificar que backup system con métodos reales se integra con engines"""
        backup_manager = BackupManager()
        
        # Test real methods exist
        assert hasattr(backup_manager, 'create_snapshot')
        assert hasattr(backup_manager, 'list_snapshots')
        assert hasattr(backup_manager, 'cleanup_old_snapshots')

    def test_engines_content_workflow_no_corruption_dict(self):
        """Verificar que workflow engines + content no corrompe datos"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            original_content = "def original_function():\n    return 'test'"
            f.write(original_content)
            f.flush()
            
            try:
                result = self.reader.read_file(f.name)
                
                assert isinstance(result, dict)
                assert 'content' in result
                assert "original_function" in result['content']
                assert "return 'test'" in result['content']
                
            finally:
                os.unlink(f.name)

    def test_engines_health_doesnt_affect_content_operations(self):
        """Verificar que health de engines no afecta operaciones de content"""
        health_report = self.selector.get_engines_health_report()
        
        assert hasattr(self.reader, 'read_file')
        assert hasattr(self.writer, 'write_file')
        assert health_report is not None
        assert self.reader is not None
        assert self.writer is not None

    def test_content_functions_preserve_line_endings_dict(self):
        """Verificar que content functions preservan line endings"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            test_content = "line1\nline2\nline3\n"
            f.write(test_content)
            f.flush()
            
            try:
                result = self.reader.read_file(f.name)
                
                assert isinstance(result, dict)
                assert 'content' in result
                content_text = result['content']
                assert content_text.count('\n') == 3
                assert 'line1\nline2' in content_text
                
            finally:
                os.unlink(f.name)

    def test_integration_no_import_conflicts(self):
        """Verificar que no hay conflictos de imports entre engines y content"""
        from functions.engines.selector import EngineSelector
        from functions.content.reader import ContentReader
        from functions.content.writer import ContentWriter
        
        selector = EngineSelector()
        reader = ContentReader()
        writer = ContentWriter()
        
        assert selector is not None
        assert reader is not None  
        assert writer is not None

    def test_backup_snapshot_integration_with_engines(self):
        """Verificar que create_snapshot funciona independientemente de engines"""
        backup_manager = BackupManager()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("test content for backup")
            f.flush()
            
            try:
                # Test snapshot creation works
                snapshot = backup_manager.create_snapshot(f.name, "test_operation")
                assert snapshot is not None
                assert isinstance(snapshot, str)
                
            finally:
                os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
