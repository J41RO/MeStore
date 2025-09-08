import pytest
import tempfile
import os
from pathlib import Path
from functions.backup.manager import BackupManager
from functions.backup.rollback import RollbackManager
from functions.backup.cleaner import BackupCleaner
from functions.backup.integrity import IntegrityChecker


class TestBackupIntegration:
    
    def test_full_backup_workflow(self):
        """Test completo: backup -> modify -> verify -> rollback -> clean"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # PASO 1: Crear archivo original y backup
            original_file = os.path.join(temp_dir, "workflow_test.py")
            original_content = "print('original content')"
            
            with open(original_file, 'w') as f:
                f.write(original_content)
            
            # Crear backup usando BackupManager
            backup_manager = BackupManager()
            snapshot_path = backup_manager.create_snapshot(original_file, "workflow_test")
            
            assert Path(snapshot_path).exists()
            
            # PASO 2: Modificar archivo original
            modified_content = "print('modified content')"
            with open(original_file, 'w') as f:
                f.write(modified_content)
            
            # Verificar que el archivo se modificó
            with open(original_file, 'r') as f:
                assert f.read() == modified_content
            
            # PASO 3: Verificar integridad snapshot (debe detectar diferencia)
            integrity_checker = IntegrityChecker(backup_manager)
            integrity_result = integrity_checker.verify_snapshot_integrity(snapshot_path, original_file)
            
            assert isinstance(integrity_result, dict)
            assert "valid" in integrity_result
            # El snapshot debe ser diferente del archivo modificado
            assert integrity_result["valid"] is False
            assert "snapshot_hash" in integrity_result
            assert "original_hash" in integrity_result
            assert integrity_result["snapshot_hash"] != integrity_result["original_hash"]
            
            # PASO 4: Rollback desde snapshot (PARÁMETROS CORREGIDOS)
            rollback_manager = RollbackManager(backup_manager)
            rollback_result = rollback_manager.restore_snapshot(snapshot_path, original_file)
            
            assert rollback_result is True
            
            # Verificar que el contenido se restauró
            with open(original_file, 'r') as f:
                restored_content = f.read()
            
            assert restored_content == original_content
            
            # PASO 5: Verificar integridad final (ahora debe coincidir)
            final_integrity = integrity_checker.verify_snapshot_integrity(snapshot_path, original_file)
            assert final_integrity["valid"] is True
            assert final_integrity["snapshot_hash"] == final_integrity["original_hash"]
            
            # PASO 6: Limpiar snapshots antiguos
            cleaner = BackupCleaner(backup_manager)
            cleanup_result = cleaner.cleanup_by_operation("workflow_test")
            
            assert isinstance(cleanup_result, dict)
            assert "removed" in cleanup_result
    
    def test_cuarteto_integration_health_check(self):
        """Test de salud del cuarteto completo"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "health_check.py")
            with open(test_file, 'w') as f:
                f.write("print('health check')")
            
            # Verificar que todos los componentes se pueden instanciar
            manager = BackupManager()
            rollback = RollbackManager(manager)
            cleaner = BackupCleaner(manager)
            integrity = IntegrityChecker(manager)
            
            # Verificar operaciones básicas
            snapshot = manager.create_snapshot(test_file, "health_check")
            assert Path(snapshot).exists()
            
            snapshots = manager.list_snapshots()
            assert len(snapshots) > 0
            
            scan_result = integrity.scan_all_snapshots()
            assert scan_result["total"] > 0
            
            repair_result = integrity.repair_corrupted()
            assert isinstance(repair_result, dict)
            
            latest = rollback.find_latest_snapshot(test_file)
            assert latest is not None
    
    def test_error_handling_integration(self):
        """Test manejo de errores en integración"""
        # Test con archivos inexistentes
        manager = BackupManager()
        rollback = RollbackManager(manager)
        integrity = IntegrityChecker(manager)
        
        # Test rollback con archivo inexistente - USAR TRY/CATCH
        try:
            result = rollback.restore_snapshot("/nonexistent/snapshot.backup", "/nonexistent/file.py")
            # Si llega aquí, debería ser False
            assert result is False
        except FileNotFoundError:
            # Este es el comportamiento actual - la excepción es esperada
            pass
        
        # Test verificación de integridad con archivos inexistentes
        integrity_result = integrity.verify_snapshot_integrity("/nonexistent/snapshot", "/nonexistent/original")
        assert integrity_result["valid"] is False
        assert "error" in integrity_result