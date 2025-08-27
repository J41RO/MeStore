import pytest
import tempfile
import os
from pathlib import Path
from functions.backup.manager import BackupManager
from functions.backup.cleaner import BackupCleaner


class TestBackupCleaner:
    
    def test_cleanup_by_operation(self):
        """Test limpieza por tipo de operación"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivos temporales para backup
            test_file1 = os.path.join(temp_dir, "test1.py")
            test_file2 = os.path.join(temp_dir, "test2.py")
            
            with open(test_file1, 'w') as f:
                f.write("print('test1')")
            with open(test_file2, 'w') as f:
                f.write("print('test2')")
            
            # Crear backups
            manager = BackupManager()
            manager.create_snapshot(test_file1, "create_operation")
            manager.create_snapshot(test_file2, "replace_operation")
            
            # Test limpieza por operación
            cleaner = BackupCleaner()
            cleaned = cleaner.cleanup_by_operation("create_operation")
            
            assert isinstance(cleaned, dict)
            assert "removed" in cleaned
            assert isinstance(cleaned["removed"], int)
    
    def test_cleanup_by_size(self):
        """Test limpieza por tamaño"""  
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo temporal
            test_file = os.path.join(temp_dir, "test.py")
            
            with open(test_file, 'w') as f:
                f.write("print('test content')")
            
            # Crear backup
            manager = BackupManager()
            manager.create_snapshot(test_file, "size_test")
            
            # Test limpieza por tamaño (sin parámetros según API real)
            cleaner = BackupCleaner()
            cleaned = cleaner.cleanup_by_size()
            
            assert isinstance(cleaned, dict)
            # Ajustar assertion según estructura real del resultado
            assert "total_size_mb" in str(cleaned) or "size" in str(cleaned)
            
    def test_advanced_cleanup(self):
        """Test políticas combinadas"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivos temporales
            test_file1 = os.path.join(temp_dir, "test1.py")
            test_file2 = os.path.join(temp_dir, "test2.py")
            
            with open(test_file1, 'w') as f:
                f.write("print('test1')")
            with open(test_file2, 'w') as f:
                f.write("print('test2')")
            
            # Crear múltiples backups
            manager = BackupManager()
            manager.create_snapshot(test_file1, "operation1")
            manager.create_snapshot(test_file2, "operation2")
            
            # Test cleanup avanzado con políticas múltiples
            cleaner = BackupCleaner()
            policies = {
                'max_age_days': 30,
                'max_size_mb': 10,
                'keep_last_n': 5
            }
            cleaned = cleaner.advanced_cleanup(policies)
            
            assert isinstance(cleaned, dict)
            # Ajustar según estructura real (vemos "total_removed")
            assert "total_removed" in cleaned
            assert isinstance(cleaned["total_removed"], int)
            assert "policies_applied" in cleaned