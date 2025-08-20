"""
Tests simples funcionales para BackupManager v5.3
"""

import os
import sys
import tempfile

import pytest

# Importar el módulo principal
try:
    from surgical_modifier_ultimate import BackupManager
except ImportError:
    sys.path.append("..")
    from surgical_modifier_ultimate import BackupManager


class TestBackupManagerSimple:
    """Tests básicos funcionales para BackupManager"""

    @pytest.fixture
    def backup_manager(self):
        """Crear instancia simple de BackupManager"""
        return BackupManager(keep_successful_backups=True, max_backups=3)

    def test_backup_manager_creation(self, backup_manager):
        """Test: Crear instancia de BackupManager"""
        assert backup_manager is not None
        assert backup_manager.keep_successful_backups is True
        assert backup_manager.max_backups == 3

    def test_create_backup_with_valid_file(
        self, backup_manager, sample_text_file, temp_dir
    ):
        """Test: Crear backup de archivo válido"""
        backup_dir = os.path.join(temp_dir, "backups")

        # Crear backup (requiere backup_dir como parámetro)
        backup_path = backup_manager.create_backup(sample_text_file, backup_dir)

        # Verificar que se creó el backup
        assert backup_path is not None
        assert os.path.exists(backup_path)
        assert os.path.isfile(backup_path)

    def test_cleanup_backups(self, backup_manager):
        """Test: Función de limpieza existe"""
        # Solo verificar que el método existe y no falla
        try:
            backup_manager.cleanup_successful_backups()
            success = True
        except Exception:
            success = False

        assert success is True

    def test_has_required_methods(self, backup_manager):
        """Test: Verificar métodos requeridos existen"""
        required_methods = [
            "create_backup",
            "cleanup_successful_backups",
            "restore_from_backup",
        ]

        for method_name in required_methods:
            assert hasattr(backup_manager, method_name)
            assert callable(getattr(backup_manager, method_name))
