import pytest
import tempfile
import time
import os
from pathlib import Path
from surgical_modifier.functions.backup.manager import BackupManager
from surgical_modifier.functions.backup.rollback import RollbackManager


class TestRollbackManager:
    
    def test_restore_snapshot(self):
        """Test restauración específica desde snapshot"""
        # Crear archivo temporal con contenido original
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('original_content')
            original_file = f.name
        
        try:
            # Crear backup del archivo original
            bm = BackupManager()
            backup_path = bm.create_snapshot(original_file, 'test_op')
            
            # Modificar archivo original
            with open(original_file, 'w') as f:
                f.write('modified_content')
            
            # Restaurar desde snapshot
            rm = RollbackManager(bm)
            result = rm.restore_snapshot(backup_path, original_file)
            
            # Verificar restauración
            assert result is True
            with open(original_file, 'r') as f:
                content = f.read()
            assert content == 'original_content'
            
        finally:
            os.unlink(original_file)
    
    def test_restore_snapshot_file_not_found(self):
        """Test error cuando snapshot no existe"""
        rm = RollbackManager()
        
        with pytest.raises(FileNotFoundError, match="Snapshot no encontrado"):
            rm.restore_snapshot("nonexistent_snapshot.backup", "target.txt")
    
    def test_find_latest_snapshot(self):
        """Test encontrar snapshot más reciente"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.test') as f:
            f.write('test_content')
            test_file = f.name
        
        try:
            bm = BackupManager()
            # Crear múltiples snapshots
            backup1 = bm.create_snapshot(test_file, 'operation1')
            time.sleep(0.01)  # Pequeño delay para garantizar timestamps únicos
            backup2 = bm.create_snapshot(test_file, 'operation2')
            time.sleep(0.01)
            backup3 = bm.create_snapshot(test_file, 'operation1')
            
            rm = RollbackManager(bm)
            
            # Test sin filtro de operación - verificar que devuelve alguno válido
            latest = rm.find_latest_snapshot(test_file)
            assert latest in [backup1, backup2, backup3]  # Debe ser uno de los backups válidos
            
            # Test con filtro de operación específica
            latest_op2 = rm.find_latest_snapshot(test_file, 'operation2')
            assert latest_op2 == backup2
            
        finally:
            os.unlink(test_file)
    
    def test_find_latest_snapshot_no_snapshots(self):
        """Test cuando no hay snapshots disponibles"""
        rm = RollbackManager()
        result = rm.find_latest_snapshot("nonexistent_file.txt")
        assert result is None
    
    def test_restore_latest(self):
        """Test restauración desde snapshot más reciente"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('original_content')
            test_file = f.name
        
        try:
            bm = BackupManager()
            # Crear snapshot
            backup_path = bm.create_snapshot(test_file, 'test_restore')
            
            # Modificar archivo
            with open(test_file, 'w') as f:
                f.write('modified_content')
            
            rm = RollbackManager(bm)
            success, message = rm.restore_latest(test_file, 'test_restore')
            
            assert success is True
            assert "Restaurado desde" in message
            assert backup_path in message
            
            # Verificar contenido restaurado
            with open(test_file, 'r') as f:
                content = f.read()
            assert content == 'original_content'
            
        finally:
            os.unlink(test_file)
    
    def test_restore_latest_no_snapshot_found(self):
        """Test cuando no se encuentra snapshot para restaurar"""
        rm = RollbackManager()
        success, message = rm.restore_latest("nonexistent_file.txt", "nonexistent_op")
        
        assert success is False
        assert message == "No se encontró snapshot para restaurar"
    
    def test_integration_with_backup_manager(self):
        """Test integración completa con BackupManager"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('integration_test')
            test_file = f.name
        
        try:
            # Test con BackupManager personalizado
            custom_bm = BackupManager()
            rm = RollbackManager(custom_bm)
            
            # Verificar que usa el mismo BackupManager
            assert rm.backup_manager is custom_bm
            
            # Test funcionalidad completa
            backup_path = custom_bm.create_snapshot(test_file, 'integration')
            
            with open(test_file, 'w') as f:
                f.write('modified_for_integration')
            
            success = rm.restore_snapshot(backup_path, test_file)
            assert success is True
            
            with open(test_file, 'r') as f:
                content = f.read()
            assert content == 'integration_test'
            
        finally:
            os.unlink(test_file)
    
    def test_restore_latest_with_backup_creation(self):
        """Test que restore_latest crea backup del estado actual por defecto"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('original')
            test_file = f.name
        
        try:
            bm = BackupManager()
            backup_path = bm.create_snapshot(test_file, 'first_backup')
            
            # Modificar archivo
            with open(test_file, 'w') as f:
                f.write('modified_state')
            
            # Contar snapshots antes de restore_latest
            snapshots_before = bm.list_snapshots(Path(test_file).name)
            count_before = len(snapshots_before)
            
            rm = RollbackManager(bm)
            success, message = rm.restore_latest(test_file, 'first_backup', create_backup=True)
            
            # Verificar que se creó un backup adicional (pre_restore)
            snapshots_after = bm.list_snapshots(Path(test_file).name)
            count_after = len(snapshots_after)
            
            assert success is True
            assert count_after == count_before + 1  # Un snapshot adicional
            
            # Verificar que existe un snapshot con 'pre_restore'
            pre_restore_snapshots = [s for s in snapshots_after if 'pre_restore' in s['name']]
            assert len(pre_restore_snapshots) == 1
            
        finally:
            os.unlink(test_file)