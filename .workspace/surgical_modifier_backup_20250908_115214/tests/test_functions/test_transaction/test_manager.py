import pytest
import tempfile
import os
from pathlib import Path
from functions.transaction.manager import TransactionManager, TransactionState

class TestTransactionManager:
    """Tests comprehensivos para TransactionManager"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.tx_manager = TransactionManager()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup después de cada test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initial_state(self):
        """Test estado inicial del TransactionManager"""
        assert self.tx_manager.state == TransactionState.INACTIVE
        assert self.tx_manager.transaction_id is None
        assert len(self.tx_manager.affected_files) == 0
    
    def test_begin_transaction(self):
        """Test inicio de transacción"""
        tx_id = self.tx_manager.begin_transaction()
        
        assert tx_id is not None
        assert tx_id.startswith('tx_')
        assert self.tx_manager.state == TransactionState.ACTIVE
        assert self.tx_manager.transaction_id == tx_id
    
    def test_begin_transaction_when_active_fails(self):
        """Test error al intentar comenzar transacción cuando ya hay una activa"""
        self.tx_manager.begin_transaction()
        
        with pytest.raises(RuntimeError, match='Cannot begin transaction'):
            self.tx_manager.begin_transaction()
    
    def test_add_existing_file_to_transaction(self):
        """Test agregar archivo existente a la transacción"""
        # Crear archivo temporal
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('original content')
        
        self.tx_manager.begin_transaction()
        self.tx_manager.add_file_to_transaction(test_file)
        
        assert len(self.tx_manager.affected_files) == 1
        file_info = self.tx_manager.affected_files[0]
        assert file_info['file_path'] == test_file
        assert file_info['existed_before'] is True
        assert file_info['backup_id'] is not None
    
    def test_add_new_file_to_transaction(self):
        """Test agregar archivo nuevo (inexistente) a la transacción"""
        new_file = os.path.join(self.temp_dir, 'new_file.txt')
        
        self.tx_manager.begin_transaction()
        self.tx_manager.add_file_to_transaction(new_file)
        
        assert len(self.tx_manager.affected_files) == 1
        file_info = self.tx_manager.affected_files[0]
        assert file_info['file_path'] == new_file
        assert file_info['existed_before'] is False
        assert file_info['backup_id'] is None
    
    def test_add_file_without_active_transaction_fails(self):
        """Test error al agregar archivo sin transacción activa"""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        
        with pytest.raises(RuntimeError, match='No active transaction'):
            self.tx_manager.add_file_to_transaction(test_file)
    
    def test_commit_transaction(self):
        """Test commit de transacción exitoso"""
        self.tx_manager.begin_transaction()
        
        result = self.tx_manager.commit()
        
        assert result['success'] is True
        assert 'transaction_id' in result
        assert 'committed_at' in result
        assert self.tx_manager.state == TransactionState.COMMITTED
    
    def test_commit_without_active_transaction_fails(self):
        """Test error al hacer commit sin transacción activa"""
        with pytest.raises(RuntimeError, match='Cannot commit transaction'):
            self.tx_manager.commit()
    
    def test_rollback_transaction(self):
        """Test rollback de transacción"""
        # Crear archivo temporal
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('original content')
        
        self.tx_manager.begin_transaction()
        self.tx_manager.add_file_to_transaction(test_file)
        
        result = self.tx_manager.rollback()
        
        assert result['success'] is True
        assert 'transaction_id' in result
        assert 'rolled_back_at' in result
        assert self.tx_manager.state == TransactionState.ROLLED_BACK
    
    def test_rollback_new_file_deletion(self):
        """Test rollback elimina archivos nuevos creados durante transacción"""
        new_file = os.path.join(self.temp_dir, 'new_file.txt')
        
        self.tx_manager.begin_transaction()
        self.tx_manager.add_file_to_transaction(new_file)
        
        # Simular creación del archivo durante la transacción
        with open(new_file, 'w') as f:
            f.write('new content')
        
        result = self.tx_manager.rollback()
        
        assert result['success'] is True
        assert not Path(new_file).exists()
    
    def test_get_status(self):
        """Test obtención de estado de transacción"""
        status = self.tx_manager.get_status()
        
        assert 'transaction_id' in status
        assert 'state' in status
        assert 'affected_files_count' in status
        assert 'affected_files' in status
        
        # Test después de comenzar transacción
        self.tx_manager.begin_transaction()
        status = self.tx_manager.get_status()
        
        assert status['state'] == 'active'
        assert status['affected_files_count'] == 0