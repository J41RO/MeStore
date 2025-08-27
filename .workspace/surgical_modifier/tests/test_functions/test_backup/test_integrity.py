import pytest
import tempfile
import os
from pathlib import Path
from functions.backup.manager import BackupManager
from functions.backup.integrity import IntegrityChecker


class TestIntegrityChecker:
    
    def test_calculate_checksum(self):
        """Test cálculo checksums MD5"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content for checksum")
            temp_path = temp_file.name
        
        try:
            ic = IntegrityChecker()
            checksum = ic.calculate_checksum(temp_path)
            
            # Verificar que el checksum MD5 tiene 32 caracteres hexadecimales
            assert isinstance(checksum, str)
            assert len(checksum) == 32
            assert all(c in '0123456789abcdef' for c in checksum)
            
            # Verificar consistencia - mismo archivo debe dar mismo checksum
            checksum2 = ic.calculate_checksum(temp_path)
            assert checksum == checksum2
            
        finally:
            os.unlink(temp_path)
    
    def test_verify_snapshot_integrity(self):
        """Test verificación integridad"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo original
            original_file = os.path.join(temp_dir, "original.py")
            with open(original_file, 'w') as f:
                f.write("print('original content')")
            
            # Crear snapshot con BackupManager
            manager = BackupManager()
            snapshot_path = manager.create_snapshot(original_file, "integrity_test")
            
            # Verificar integridad
            ic = IntegrityChecker(manager)
            result = ic.verify_snapshot_integrity(snapshot_path, original_file)
            
            assert isinstance(result, dict)
            assert "valid" in result
            assert result["valid"] is True
            assert "snapshot_hash" in result
            assert "original_hash" in result
            assert result["snapshot_hash"] == result["original_hash"]
    
    def test_verify_snapshot_integrity_missing_files(self):
        """Test verificación con archivos faltantes"""
        ic = IntegrityChecker()
        
        # Test con snapshot inexistente
        result = ic.verify_snapshot_integrity("/path/to/nonexistent/snapshot", "/tmp/original")
        assert result["valid"] is False
        assert "error" in result
        assert "no existe" in result["error"].lower()
        
        # Test con archivo original inexistente
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(b"test")
            temp_path = temp.name
        
        try:
            result = ic.verify_snapshot_integrity(temp_path, "/path/to/nonexistent/original")
            assert result["valid"] is False
            assert "error" in result
            assert "no existe" in result["error"].lower()
        finally:
            os.unlink(temp_path)
    
    def test_scan_all_snapshots(self):
        """Test auditoría completa"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear algunos archivos y snapshots
            test_file1 = os.path.join(temp_dir, "test1.py")
            test_file2 = os.path.join(temp_dir, "test2.py")
            
            with open(test_file1, 'w') as f:
                f.write("print('test1')")
            with open(test_file2, 'w') as f:
                f.write("print('test2')")
            
            # Crear snapshots
            manager = BackupManager()
            manager.create_snapshot(test_file1, "scan_test1")
            manager.create_snapshot(test_file2, "scan_test2")
            
            # Ejecutar scan
            ic = IntegrityChecker(manager)
            result = ic.scan_all_snapshots()
            
            assert isinstance(result, dict)
            assert "total" in result
            assert "valid" in result
            assert "corrupted" in result
            assert "missing_original" in result
            assert "errors" in result
            
            assert isinstance(result["total"], int)
            assert isinstance(result["valid"], int)
            assert isinstance(result["corrupted"], int)
            assert isinstance(result["errors"], list)
            
            # Debe haber encontrado al menos los snapshots que creamos
            assert result["total"] >= 2
    
    def test_repair_corrupted(self):
        """Test reparación"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo y snapshot
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, 'w') as f:
                f.write("print('test')")
            
            manager = BackupManager()
            manager.create_snapshot(test_file, "repair_test")
            
            # Ejecutar repair
            ic = IntegrityChecker(manager)
            result = ic.repair_corrupted()
            
            assert isinstance(result, dict)
            assert "detected_issues" in result
            assert "repaired" in result
            assert isinstance(result["detected_issues"], int)
            assert isinstance(result["repaired"], int)
            
            # Test con remove_corrupted=True
            result_with_removal = ic.repair_corrupted(remove_corrupted=True)
            assert isinstance(result_with_removal, dict)
            assert "detected_issues" in result_with_removal
            assert "repaired" in result_with_removal