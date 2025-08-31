import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from coordinators.replace import ReplaceCoordinator
from functions.pattern.pattern_factory import PatternMatcherFactory
from functions.backup.manager import BackupManager
from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter
from functions.content.validator import ContentValidator

class TestReplaceCoordinatorPatternFactory:
    """Tests integration para verificar llamadas a PatternMatcherFactory en ReplaceCoordinator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = ReplaceCoordinator()
        self.test_file_path = "test_replace_file.py"
        self.test_pattern = "old_code"
        self.test_replacement = "new_code"
    
    def test_replace_calls_pattern_factory_successfully(self):
        """Test que REPLACE llama PatternMatcherFactory.get_optimized_matcher() correctamente"""
        with patch.object(self.coordinator, 'pattern_factory') as mock_factory:
            mock_matcher = Mock()
            mock_matcher.find_matches.return_value = {'matches': [{'match': 'old_code'}]}
            mock_matcher.replace_pattern.return_value = {'new_text': 'new_code content', 'success': True}
            mock_factory.get_optimized_matcher.return_value = mock_matcher
            
            # Mock other dependencies
            with patch('pathlib.Path.exists', return_value=True), \
                 patch.object(self.coordinator, 'backup_manager') as mock_backup, \
                 patch.object(self.coordinator, 'reader') as mock_reader, \
                 patch.object(self.coordinator, 'writer') as mock_writer, \
                 patch.object(self.coordinator, 'validator') as mock_validator:
                
                mock_backup.create_snapshot.return_value = 'backup_path'
                mock_reader.read_file.return_value = {'success': True, 'content': 'old_code content'}
                mock_writer.write_file.return_value = {'success': True}
                mock_validator.validate_file.return_value = {'valid': True}
                
                result = self.coordinator.execute(self.test_file_path, self.test_pattern, self.test_replacement)
                
                # Verificar llamadas
                mock_factory.get_optimized_matcher.assert_called_once_with('regex')
                mock_matcher.find_matches.assert_called_once_with(self.test_pattern, 'old_code content')
                mock_matcher.replace_pattern.assert_called_once_with(self.test_pattern, self.test_replacement, 'old_code content')
                assert result['success'] is True

class TestReplaceCoordinatorBackupManager:
    """Tests integration para verificar llamadas a BackupManager en ReplaceCoordinator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = ReplaceCoordinator()
        self.test_file_path = "test_backup_file.py"
    
    def test_replace_calls_backup_manager_create_snapshot(self):
        """Test que REPLACE llama BackupManager.create_snapshot() antes del cambio"""
        with patch.object(self.coordinator, 'backup_manager') as mock_backup:
            mock_backup.create_snapshot.return_value = 'backup_path'
            
            # Mock other dependencies
            with patch('pathlib.Path.exists', return_value=True), \
                 patch.object(self.coordinator, 'pattern_factory') as mock_factory, \
                 patch.object(self.coordinator, 'reader') as mock_reader, \
                 patch.object(self.coordinator, 'writer') as mock_writer, \
                 patch.object(self.coordinator, 'validator') as mock_validator:
                
                mock_matcher = Mock()
                mock_matcher.find_matches.return_value = {'matches': [{'match': 'pattern'}]}
                mock_matcher.replace_pattern.return_value = {'new_text': 'new content', 'success': True}
                mock_factory.get_optimized_matcher.return_value = mock_matcher
                mock_reader.read_file.return_value = {'success': True, 'content': 'content'}
                mock_writer.write_file.return_value = {'success': True}
                mock_validator.validate_file.return_value = {'valid': True}
                
                result = self.coordinator.execute(self.test_file_path, 'pattern', 'replacement')
                
                # Verificar backup fue llamado con parámetros correctos
                mock_backup.create_snapshot.assert_called_once_with(self.test_file_path, 'replace')
                assert result['backup_created'] == 'backup_path'

class TestReplaceCoordinatorContentOperations:
    """Tests integration para verificar llamadas a Reader/Writer en ReplaceCoordinator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = ReplaceCoordinator()
        self.test_file_path = "test_content_file.py"
    
    def test_replace_calls_reader_and_writer_sequence(self):
        """Test que REPLACE ejecuta secuencia Reader -> Pattern -> Writer correctamente"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch.object(self.coordinator, 'reader') as mock_reader, \
             patch.object(self.coordinator, 'writer') as mock_writer, \
             patch.object(self.coordinator, 'pattern_factory') as mock_factory, \
             patch.object(self.coordinator, 'backup_manager') as mock_backup, \
             patch.object(self.coordinator, 'validator') as mock_validator:
            
            # Setup mocks
            mock_reader.read_file.return_value = {'success': True, 'content': 'original content'}
            mock_writer.write_file.return_value = {'success': True}
            mock_backup.create_snapshot.return_value = 'backup_path'
            mock_validator.validate_file.return_value = {'valid': True}
            
            mock_matcher = Mock()
            mock_matcher.find_matches.return_value = {'matches': [{'match': 'original'}]}
            mock_matcher.replace_pattern.return_value = {'new_text': 'modified content', 'success': True}
            mock_factory.get_optimized_matcher.return_value = mock_matcher
            
            result = self.coordinator.execute(self.test_file_path, 'original', 'modified')
            
            # Verificar secuencia de llamadas
            mock_reader.read_file.assert_called_once_with(self.test_file_path)
            mock_writer.write_file.assert_called_once_with(self.test_file_path, 'modified content')
            assert result['success'] is True

class TestReplaceCoordinatorArchitecture:
    """Tests para verificar arquitectura orquestador ligero del ReplaceCoordinator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = ReplaceCoordinator()
    
    def test_coordinator_is_lightweight_orchestrator(self):
        """Test que ReplaceCoordinator es verdaderamente un orquestador ligero"""
        import inspect
        
        # Verificar método execute es ligero
        execute_source = inspect.getsource(self.coordinator.execute)
        execute_lines = len(execute_source.split('\n'))
        
        assert execute_lines <= 25, f"execute() debe ser ≤25 líneas, actual: {execute_lines}"
        
        # Verificar que delega a workflow
        assert 'ReplaceWorkflow' in execute_source, "Debe delegar a ReplaceWorkflow"
        assert 'execute_sequence' in execute_source, "Debe llamar execute_sequence del workflow"
    
    def test_coordinator_functions_integration(self):
        """Test que coordinador integra todas las functions modulares requeridas"""
        # Verificar dependencies inyectadas
        assert hasattr(self.coordinator, 'pattern_factory'), "Debe tener PatternMatcherFactory"
        assert hasattr(self.coordinator, 'backup_manager'), "Debe tener BackupManager"
        assert hasattr(self.coordinator, 'reader'), "Debe tener ContentReader"
        assert hasattr(self.coordinator, 'writer'), "Debe tener ContentWriter"
        assert hasattr(self.coordinator, 'validator'), "Debe tener ContentValidator"
        
        # Verificar tipos correctos
        assert isinstance(self.coordinator.pattern_factory, PatternMatcherFactory)
        assert isinstance(self.coordinator.backup_manager, BackupManager)
        assert isinstance(self.coordinator.reader, ContentReader)
        assert isinstance(self.coordinator.writer, ContentWriter)
        assert isinstance(self.coordinator.validator, ContentValidator)

class TestReplaceCoordinatorIntegrationComplete:
    """Tests integration completa end-to-end del ReplaceCoordinator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = ReplaceCoordinator()
    
    def test_replace_workflow_complete_integration(self):
        """Test integración completa del workflow REPLACE con todas las functions"""
        import tempfile
        import os
        
        # Crear archivo temporal real
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('old_value = "test"')
            temp_file = f.name
        
        try:
            # Ejecutar replace completo
            result = self.coordinator.execute(temp_file, 'old_value', 'new_value')
            
            # Verificar resultado
            assert result['success'] is True, f"Replace failed: {result.get('error')}"
            assert result['matches_found'] == 1, "Debe encontrar 1 match"
            assert len(result['phases_completed']) == 7, "Debe completar 7 fases"
            assert 'backup_created' in result, "Debe crear backup"
            
            # Verificar contenido modificado
            with open(temp_file, 'r') as f:
                final_content = f.read()
            assert 'new_value = "test"' in final_content, "Contenido debe estar modificado"
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_replace_pattern_not_found_handling(self):
        """Test manejo cuando pattern no se encuentra"""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('some_content = "test"')
            temp_file = f.name
        
        try:
            result = self.coordinator.execute(temp_file, 'nonexistent_pattern', 'replacement')
            
            # Debe fallar gracefully
            assert result['success'] is False, "Debe fallar cuando pattern no existe"
            assert 'Pattern not found' in result['error'], "Debe reportar pattern no encontrado"
            assert 'phases_completed' in result, "Debe reportar fases completadas"
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
