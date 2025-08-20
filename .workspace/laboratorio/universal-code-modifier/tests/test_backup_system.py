import os
import tempfile
import time
import unittest
from pathlib import Path

from universal_modifier import BackupManager, UniversalCodeModifier


class TestBackupSystem(unittest.TestCase):

    def setUp(self):
        """Setup para cada test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.bm = BackupManager(backup_dir=self.temp_dir, max_backups_per_file=3)

    def tearDown(self):
        """Cleanup después de cada test"""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_backup_manager_creation(self):
        """Test creación de BackupManager"""
        self.assertIsNotNone(self.bm)
        self.assertEqual(self.bm.max_backups_per_file, 3)

    def test_timestamped_backup_creation(self):
        """Test creación de backup con timestamp"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write('print("test")')
            test_file = f.name

        backup_path = self.bm.create_timestamped_backup(test_file)
        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.exists())
        self.assertIn("backup_", backup_path.name)

        os.unlink(test_file)

    def test_backup_rotation(self):
        """Test rotación automática de backups"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write('print("test")')
            test_file = f.name

        # Crear 5 backups
        for i in range(5):
            self.bm.create_timestamped_backup(test_file)
            time.sleep(0.01)

        # Verificar que solo quedan 3 (max_backups_per_file)
        backups = self.bm.list_backups_for_file(test_file)
        self.assertLessEqual(len(backups), 3)

        os.unlink(test_file)

    def test_backup_size_calculation(self):
        """Test cálculo de tamaño total"""
        initial_size = self.bm.calculate_total_backup_size()
        self.assertIsInstance(initial_size, int)
        self.assertGreaterEqual(initial_size, 0)

    def test_integration_with_universal_modifier(self):
        """Test integración con UniversalCodeModifier"""
        ucm = UniversalCodeModifier(backup_enabled=True)
        self.assertIsNotNone(ucm.backup_manager)
        self.assertIsInstance(ucm.backup_manager, BackupManager)

    def test_backup_listing(self):
        """Test listado de backups"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write('print("test")')
            test_file = f.name

        # Crear algunos backups
        self.bm.create_timestamped_backup(test_file)
        time.sleep(0.01)
        self.bm.create_timestamped_backup(test_file)

        backups = self.bm.list_backups_for_file(test_file)
        self.assertGreaterEqual(len(backups), 1)  # Al menos 1 backup debe existir

        os.unlink(test_file)


if __name__ == "__main__":
    unittest.main()
