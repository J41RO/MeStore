import pytest
import json
import tempfile
import os
from pathlib import Path
from coordinators.batch import BatchCoordinator

class TestBatchCoordinator:
    """Tests comprehensivos para BatchCoordinator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = BatchCoordinator()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_parse_valid_json_batch_file(self):
        """Test parsing de archivo JSON válido"""
        batch_data = {
            'operations': [
                {'command': 'replace', 'args': ['test.txt', 'old', 'new']},
                {'command': 'after', 'args': ['test.txt', 'pattern', 'content']}
            ]
        }
        
        batch_file = os.path.join(self.temp_dir, 'batch.json')
        with open(batch_file, 'w') as f:
            json.dump(batch_data, f)
        
        operations = self.coordinator._parse_batch_file(batch_file)
        
        assert len(operations) == 2
        assert operations[0]['command'] == 'replace'
        assert operations[1]['command'] == 'after'
    
    def test_parse_invalid_batch_file_missing_operations(self):
        """Test error con archivo que no tiene 'operations'"""
        batch_data = {'invalid': 'data'}
        
        batch_file = os.path.join(self.temp_dir, 'invalid.json')
        with open(batch_file, 'w') as f:
            json.dump(batch_data, f)
        
        with pytest.raises(ValueError, match='Batch file must contain'):
            self.coordinator._parse_batch_file(batch_file)
    
    def test_parse_nonexistent_batch_file(self):
        """Test error con archivo inexistente"""
        nonexistent_file = os.path.join(self.temp_dir, 'nonexistent.json')
        
        with pytest.raises(FileNotFoundError):
            self.coordinator._parse_batch_file(nonexistent_file)
    
    def test_execute_batch_dry_run(self):
        """Test ejecución en modo dry-run"""
        batch_data = {
            'operations': [
                {'command': 'replace', 'args': ['test.txt', 'old', 'new']}
            ]
        }
        
        batch_file = os.path.join(self.temp_dir, 'batch.json')
        with open(batch_file, 'w') as f:
            json.dump(batch_data, f)
        
        result = self.coordinator.execute(batch_file, dry_run=True)
        
        assert result['success'] is True
        assert result['operations_executed'] == 1
        assert result['operations_failed'] == 0
        assert len(result['details']) == 1
    
    def test_execute_batch_with_invalid_file(self):
        """Test ejecución con archivo inválido"""
        result = self.coordinator.execute('nonexistent.json', dry_run=True)
        
        assert result['success'] is False
        assert 'error' in result
        assert result['operations_executed'] == 0
        assert result['operations_failed'] == 0
    
    def test_unsupported_file_format(self):
        """Test error con formato de archivo no soportado"""
        batch_file = os.path.join(self.temp_dir, 'batch.txt')
        with open(batch_file, 'w') as f:
            f.write('invalid content')
        
        with pytest.raises(ValueError, match='Unsupported batch file format'):
            self.coordinator._parse_batch_file(batch_file)