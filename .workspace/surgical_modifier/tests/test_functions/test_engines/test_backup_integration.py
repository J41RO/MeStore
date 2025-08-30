"""
Tests de integración entre engines y sistema backup.
Verifica que todas las operaciones destructivas crean snapshots automáticamente.
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, Mock
from functions.engines.base_engine import BaseEngine
from functions.engines.native_engine import NativeEngine
from functions.engines.comby_engine import CombyEngine
from functions.engines.ast_engine import AstEngine
from functions.engines.selector import EngineSelector
from functions.backup.manager import BackupManager


class TestBackupIntegration:
    """Test suite para integración backup-engines"""

    def setup_method(self):
        """Setup para cada test"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        self.temp_file.write("def hello():\n    print('Hello World')\n")
        self.temp_file.close()
        self.file_path = self.temp_file.name

    def teardown_method(self):
        """Cleanup después de cada test"""
        if os.path.exists(self.file_path):
            os.unlink(self.file_path)

    def test_base_engine_has_backup_manager(self):
        """Test que BaseEngine tiene BackupManager integrado"""
        engine = NativeEngine()
        assert hasattr(engine, 'backup_manager')
        assert isinstance(engine.backup_manager, BackupManager)

    def test_native_engine_creates_backup_before_replace(self):
        """Test que NativeEngine crea backup antes de replace"""
        engine = NativeEngine()
        content = "def hello():\n    print('Hello World')"
        
        with patch.object(engine, '_create_backup_before_operation') as mock_backup:
            mock_backup.return_value = True
            
            # Mock the matchers to avoid actual pattern matching
            with patch.object(engine, '_literal_matcher') as mock_literal:
                mock_literal.replace_literal.return_value = {
                    'new_text': content.replace("Hello World", "Hello Universe"),
                    'replacements_made': 1
                }
                
                result = engine._replace_impl(
                    content, 
                    "print('Hello World')", 
                    "print('Hello Universe')",
                    file_path=self.file_path
                )
                
                mock_backup.assert_called_once_with(self.file_path, 'replace')

    def test_comby_engine_creates_backup_before_replace(self):
        """Test que CombyEngine crea backup antes de replace"""
        engine = CombyEngine()
        content = "def hello():\n    print('Hello World')"
        
        # Mock subprocess to simulate comby execution
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = '{"uri": "test", "rewritten_source": "def hello():\\n    print(\'Hello Universe\')", "diff": "test"}'
        
        with patch.object(engine, '_create_backup_before_operation') as mock_backup:
            with patch('subprocess.run', return_value=mock_process):
                mock_backup.return_value = True
                
                result = engine._replace_impl(
                    "print('Hello World')",
                    "print('Hello Universe')", 
                    content,
                    file_path=self.file_path
                )
                
                mock_backup.assert_called_once_with(self.file_path, 'replace')

    def test_ast_engine_creates_backup_before_replace(self):
        """Test que AstEngine crea backup antes de replace"""
        engine = AstEngine()
        content = "def hello():\n    print('Hello World')"
        
        # Mock subprocess to simulate ast-grep execution
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = '{"matches": [{"text": "test", "range": {"start": {"line": 1}}}]}'
        
        with patch.object(engine, '_create_backup_before_operation') as mock_backup:
            with patch('subprocess.run', return_value=mock_process):
                mock_backup.return_value = True
                
                result = engine._replace_impl(
                    content,
                    "print('Hello World')",
                    "print('Hello Universe')",
                    file_path=self.file_path
                )
                
                mock_backup.assert_called_once_with(self.file_path, 'replace')

    def test_engine_selector_configures_backup(self):
        """Test que EngineSelector configura backup en engines"""
        selector = EngineSelector()
        engine = NativeEngine()
        
        # Guardar backup_manager original del engine
        original_backup_manager = engine.backup_manager
        
        # Verificar que selector tiene backup_manager
        assert hasattr(selector, 'backup_manager')
        assert isinstance(selector.backup_manager, BackupManager)
        
        # Configurar backup en engine
        selector.configure_backup_for_engine(engine)
        
        # Verificar que engine ahora usa el backup_manager del selector
        assert engine.backup_manager is selector.backup_manager
        assert engine.backup_manager is not original_backup_manager

    def test_search_operations_do_not_create_backup(self):
        """Test que operaciones de búsqueda no crean backup"""
        engine = NativeEngine()
        content = "def hello():\n    print('Hello World')"
        
        with patch.object(engine, '_create_backup_before_operation') as mock_backup:
            # Mock the matcher to avoid actual pattern matching
            with patch.object(engine, '_literal_matcher') as mock_literal:
                mock_literal.find_matches.return_value = []
                
                result = engine._search_impl(content, "hello")
                
                # Search no debe llamar backup
                mock_backup.assert_not_called()

    def test_backup_creation_with_metadata(self):
        """Test que backup incluye metadata del engine"""
        engine = NativeEngine()
        
        with patch.object(engine.backup_manager, 'create_snapshot') as mock_create:
            mock_create.return_value = 'test_snapshot_id'
            
            result = engine._create_backup_before_operation(self.file_path, 'replace')
            
            assert result is True
            mock_create.assert_called_once()
            call_args = mock_create.call_args
            
            # Verificar que se llama con file_path y metadata
            assert call_args[0][0] == self.file_path
            assert 'metadata' in call_args[1]
            metadata = call_args[1]['metadata']
            assert metadata['engine'] == 'native'
            assert metadata['operation'] == 'replace'
            assert 'timestamp' in metadata

    def test_backup_failure_does_not_interrupt_operation(self):
        """Test que fallo en backup no interrumpe la operación"""
        engine = NativeEngine()
        
        with patch.object(engine.backup_manager, 'create_snapshot') as mock_create:
            mock_create.side_effect = Exception("Backup failed")
            
            # Backup debe fallar pero retornar False, no raise exception
            result = engine._create_backup_before_operation(self.file_path, 'replace')
            
            assert result is False

    def test_no_backup_for_unknown_file(self):
        """Test que no se crea backup si file_path es unknown_file"""
        engine = NativeEngine()
        
        with patch.object(engine, '_create_backup_before_operation') as mock_backup:
            mock_backup.return_value = True
            content = "def hello():\n    print('Hello World')"
            
            # Mock matchers to avoid actual execution
            with patch.object(engine, '_literal_matcher') as mock_literal:
                mock_literal.replace_literal.return_value = {
                    'new_text': content.replace("Hello World", "Hello Universe"),
                    'replacements_made': 1
                }
                
                result = engine._replace_impl(
                    content,
                    "print('Hello World')",
                    "print('Hello Universe')"
                    # No file_path proporcionado, debería usar 'unknown_file'
                )
                
                # Debe llamarse pero con 'unknown_file'
                mock_backup.assert_called_once_with('unknown_file', 'replace')

    def test_backup_integration_end_to_end(self):
        """Test de integración completa backup-engine"""
        engine = NativeEngine()
        content = "def hello():\n    print('Hello World')"
        
        # Crear archivo real para test
        with open(self.file_path, 'w') as f:
            f.write(content)
        
        # Contar snapshots antes
        initial_snapshots = len(os.listdir('.surgical_backups/'))
        
        # Mock solo las operaciones de matching para evitar dependencias externas
        with patch.object(engine, '_literal_matcher') as mock_literal:
            mock_literal.find_matches.return_value = [Mock()]  # Simular match encontrado
            mock_literal.replace_literal.return_value = {
                'new_text': content.replace("Hello World", "Hello Universe"),
                'replacements_made': 1
            }
            
            # Ejecutar operación que debería crear backup
            result = engine._replace_impl(
                content,
                "print('Hello World')",
                "print('Hello Universe')",
                file_path=self.file_path
            )
        
        # Verificar que se creó un nuevo snapshot
        final_snapshots = len(os.listdir('.surgical_backups/'))
        assert final_snapshots > initial_snapshots, "No se creó backup automáticamente"
        
        # Verificar que la operación fue exitosa
        assert result.success, "Operación de reemplazo falló"
        assert result.modified_content is not None, "No se generó contenido modificado"