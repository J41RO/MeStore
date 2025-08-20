"""
Tests para BackupManager de Surgical Modifier Ultimate v5.3 - API REAL
Reescrito completamente usando métodos que realmente existen
"""

import os
import tempfile

import pytest
from surgical_modifier_ultimate import BackupManager


class TestBackupManager:
    """Tests para la clase BackupManager usando API real"""

    @pytest.fixture
    def backup_manager(self):
        """Crear instancia de BackupManager con parámetros reales"""
        return BackupManager(keep_successful_backups=False, max_backups=5)

    @pytest.fixture
    def temp_test_file(self):
        """Crear archivo temporal para testing"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Test content for backup")
            temp_file = f.name
        yield temp_file
        # Cleanup
        if os.path.exists(temp_file):
            os.unlink(temp_file)

    @pytest.fixture
    def temp_backup_dir(self):
        """Crear directorio temporal para backups"""
        backup_dir = tempfile.mkdtemp(prefix="test_backup_")
        yield backup_dir
        # Cleanup
        import shutil

        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)

    def test_backup_manager_initialization(self, backup_manager):
        """Test: Inicialización correcta del BackupManager con atributos reales"""
        # Verificar atributos que realmente existen
        assert hasattr(backup_manager, "keep_successful_backups")
        assert hasattr(backup_manager, "max_backups")
        assert hasattr(backup_manager, "created_backups")

        # Verificar valores de inicialización
        assert backup_manager.keep_successful_backups is False
        assert backup_manager.max_backups == 5
        assert isinstance(backup_manager.created_backups, list)

    def test_create_backup_with_valid_parameters(
        self, backup_manager, temp_test_file, temp_backup_dir
    ):
        """Test: create_backup con parámetros correctos (file_path, backup_dir)"""
        # Usar API real: create_backup(file_path, backup_dir)
        backup_path = backup_manager.create_backup(temp_test_file, temp_backup_dir)

        # Verificaciones
        assert backup_path is not None
        assert isinstance(backup_path, str)
        assert os.path.exists(backup_path)
        assert backup_path.startswith(temp_backup_dir)

        # Verificar que el contenido es correcto
        with open(backup_path, "r") as f:
            backup_content = f.read()
        with open(temp_test_file, "r") as f:
            original_content = f.read()
        assert backup_content == original_content

    def test_cleanup_successful_backups(self, backup_manager):
        """Test: cleanup_successful_backups método real"""
        # Verificar que el método existe y es callable
        assert hasattr(backup_manager, "cleanup_successful_backups")
        assert callable(backup_manager.cleanup_successful_backups)

        # Ejecutar el método (debería funcionar sin errores)
        backup_manager.cleanup_successful_backups()

    def test_all_required_methods_exist(self, backup_manager):
        """Test: Verificar que todos los métodos reales están disponibles"""
        required_methods = [
            "create_backup",
            "cleanup_successful_backups",
            "restore_from_backup",
            "cleanup_old_backups",
        ]

        for method_name in required_methods:
            assert hasattr(backup_manager, method_name)
            assert callable(getattr(backup_manager, method_name))
