"""
Tests avanzados para --keep-backups de Surgical Modifier Ultimate
Micro-fase 4: Gestión inteligente de backups
"""

import os
import shutil
import tempfile
from unittest.mock import Mock, patch

import pytest
from surgical_modifier_ultimate import BackupManager, SurgicalModifierUltimate


class TestBackupManagementAdvanced:
    """Tests completos para gestión avanzada de backups"""

    @pytest.fixture
    def temp_backup_dir(self):
        """Crear directorio temporal para backups"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def temp_source_file(self):
        """Crear archivo temporal de origen"""
        fd, path = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(
                    "# Original content\ndef original_function():\n    return True\n"
                )
            yield path
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_backup_manager_keep_backups_false(self, temp_source_file, temp_backup_dir):
        """Test BackupManager con keep_successful_backups=False"""
        manager = BackupManager(keep_successful_backups=False, max_backups=5)

        # Crear backup
        backup_path = manager.create_backup(temp_source_file, temp_backup_dir)
        assert os.path.exists(backup_path)
        assert len(manager.created_backups) == 1

        # Ejecutar cleanup de backups exitosos
        manager.cleanup_successful_backups()

        # Verificar que el backup fue eliminado
        assert not os.path.exists(backup_path)
        assert len(manager.created_backups) == 0

    def test_backup_manager_keep_backups_true(self, temp_source_file, temp_backup_dir):
        """Test BackupManager con keep_successful_backups=True"""
        manager = BackupManager(keep_successful_backups=True, max_backups=5)

        # Crear backup
        backup_path = manager.create_backup(temp_source_file, temp_backup_dir)
        assert os.path.exists(backup_path)
        assert len(manager.created_backups) == 1

        # Ejecutar cleanup de backups exitosos
        manager.cleanup_successful_backups()

        # Verificar que el backup fue conservado
        assert os.path.exists(backup_path)
        assert len(manager.created_backups) == 1

    def test_backup_manager_max_backups_policy(self, temp_source_file, temp_backup_dir):
        """Test política de retención max_backups"""
        manager = BackupManager(keep_successful_backups=True, max_backups=3)

        # Crear múltiples backups simulando timestamps diferentes
        backup_paths = []
        for i in range(5):
            # Simular diferentes archivos de backup con timestamps
            backup_filename = f"test.py.backup.{1000000 + i}"
            backup_path = os.path.join(temp_backup_dir, backup_filename)
            shutil.copy2(temp_source_file, backup_path)
            backup_paths.append(backup_path)

        # Ejecutar limpieza de backups antiguos
        manager.cleanup_old_backups(temp_backup_dir)

        # Verificar que solo se conservaron los últimos 3 backups
        remaining_backups = [p for p in backup_paths if os.path.exists(p)]
        assert len(remaining_backups) == 3

    def test_backup_manager_restore_from_backup(
        self, temp_source_file, temp_backup_dir
    ):
        """Test restauración desde backup"""
        manager = BackupManager(keep_successful_backups=True)

        # Crear backup
        backup_path = manager.create_backup(temp_source_file, temp_backup_dir)

        # Modificar archivo original
        with open(temp_source_file, "w") as f:
            f.write("# Modified content\ndef modified_function():\n    return False\n")

        # Restaurar desde backup
        manager.restore_from_backup(backup_path, temp_source_file)

        # Verificar que el contenido original fue restaurado
        with open(temp_source_file, "r") as f:
            content = f.read()
        assert "original_function" in content
        assert "modified_function" not in content

    def test_backup_manager_tracking_multiple_backups(self, temp_backup_dir):
        """Test tracking de múltiples backups"""
        manager = BackupManager(keep_successful_backups=False)

        # Crear múltiples archivos temporales y sus backups
        temp_files = []
        for i in range(3):
            fd, path = tempfile.mkstemp(suffix=f"_file_{i}.py")
            with os.fdopen(fd, "w") as f:
                f.write(f"# Test file {i}\ndef function_{i}():\n    return {i}\n")
            temp_files.append(path)

            # Crear backup para cada archivo
            manager.create_backup(path, temp_backup_dir)

        # Verificar tracking
        assert len(manager.created_backups) == 3

        # Cleanup
        manager.cleanup_successful_backups()
        assert len(manager.created_backups) == 0

        # Limpiar archivos temporales
        for path in temp_files:
            if os.path.exists(path):
                os.unlink(path)

    def test_surgical_modifier_with_keep_backups_flag(self, temp_source_file):
        """Test SurgicalModifierUltimate con flag keep_backups"""
        # Test con keep_backups=True
        modifier_keep = SurgicalModifierUltimate(keep_backups=True)
        assert modifier_keep.backup_manager.keep_successful_backups is True

        # Test con keep_backups=False
        modifier_no_keep = SurgicalModifierUltimate(keep_backups=False)
        assert modifier_no_keep.backup_manager.keep_successful_backups is False

    def test_backup_creation_with_timestamps(self, temp_source_file, temp_backup_dir):
        """Test creación de backups con timestamps únicos"""
        manager = BackupManager(keep_successful_backups=True)

        # Crear un backup y verificar su estructura
        backup_path = manager.create_backup(temp_source_file, temp_backup_dir)

        # Verificar que el backup existe
        assert os.path.exists(backup_path)

        # Verificar que el nombre contiene timestamp
        backup_filename = os.path.basename(backup_path)
        assert ".backup." in backup_filename

        # Verificar que el timestamp es numérico
        timestamp_part = backup_filename.split(".backup.")[-1]
        assert timestamp_part.isdigit()

        # Verificar tracking
        assert len(manager.created_backups) == 1
        assert manager.created_backups[0]["path"] == backup_path

    def test_backup_cleanup_error_handling(self, temp_backup_dir):
        """Test manejo de errores durante cleanup"""
        manager = BackupManager(keep_successful_backups=False)

        # Simular backup info con path inexistente
        manager.created_backups.append(
            {
                "path": "/nonexistent/backup.file",
                "original_file": "/some/file.py",
                "timestamp": 1234567890,
                "filename": "backup.file",
            }
        )

        # El cleanup no debe fallar por archivo inexistente
        with patch("builtins.print"):  # Suprimir logs para test limpio
            manager.cleanup_successful_backups()

        # La lista debe limpiarse incluso si hubo errores
        assert len(manager.created_backups) == 0

    def test_backup_directory_creation(self, temp_source_file):
        """Test creación automática de directorio de backup"""
        manager = BackupManager(keep_successful_backups=True)

        # Usar directorio que no existe
        nonexistent_backup_dir = os.path.join(
            tempfile.gettempdir(), "test_backup_new_dir"
        )

        # Asegurar que no existe
        if os.path.exists(nonexistent_backup_dir):
            shutil.rmtree(nonexistent_backup_dir)

        # Crear backup debe crear el directorio
        backup_path = manager.create_backup(temp_source_file, nonexistent_backup_dir)

        # Verificar que directorio y backup existen
        assert os.path.exists(nonexistent_backup_dir)
        assert os.path.exists(backup_path)

        # Cleanup
        shutil.rmtree(nonexistent_backup_dir, ignore_errors=True)

    def test_backup_content_integrity(self, temp_source_file, temp_backup_dir):
        """Test integridad del contenido del backup"""
        manager = BackupManager(keep_successful_backups=True)

        # Leer contenido original
        with open(temp_source_file, "r") as f:
            original_content = f.read()

        # Crear backup
        backup_path = manager.create_backup(temp_source_file, temp_backup_dir)

        # Verificar que el contenido del backup es idéntico
        with open(backup_path, "r") as f:
            backup_content = f.read()

        assert original_content == backup_content
