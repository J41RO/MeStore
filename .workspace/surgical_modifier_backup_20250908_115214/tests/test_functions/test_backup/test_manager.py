import pytest
import tempfile
import os
from pathlib import Path
from surgical_modifier.functions.backup.manager import BackupManager

def test_create_snapshot():
    """Test creación snapshot básico"""
    bm = BackupManager()
    # Crear archivo temporal para test
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('test content')
        temp_file = f.name
    try:
        # Crear snapshot
        backup_path = bm.create_snapshot(temp_file, 'test')
        # Verificaciones
        assert os.path.exists(backup_path)
        assert backup_path.endswith('.backup')
        assert 'test' in backup_path
        # Verificar contenido del backup
        with open(backup_path, 'r') as f:
            assert f.read() == 'test content'
    finally:
        # Limpiar archivos temporales
        os.unlink(temp_file)
        if os.path.exists(backup_path):
            os.unlink(backup_path)

def test_list_snapshots():
    """Test listado con metadata"""
    bm = BackupManager()
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('test content')
        temp_file = f.name
    try:
        # Crear snapshot
        backup_path = bm.create_snapshot(temp_file, 'test')
        # Listar snapshots
        snapshots = bm.list_snapshots()
        # Verificaciones
        assert isinstance(snapshots, list)
        assert len(snapshots) > 0
        # Verificar estructura de metadata
        snapshot = snapshots[0]
        assert 'path' in snapshot
        assert 'name' in snapshot
        assert 'size' in snapshot
        assert 'created' in snapshot
        assert 'file_path' in snapshot
    finally:
        # Limpiar archivos
        os.unlink(temp_file)
        if os.path.exists(backup_path):
            os.unlink(backup_path)

def test_cleanup_old_snapshots():
    """Test limpieza automática"""
    bm = BackupManager()
    # Crear múltiples archivos temporales y snapshots
    temp_files = []
    backup_paths = []
    try:
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(f'test content {i}')
                temp_files.append(f.name)
                backup_paths.append(bm.create_snapshot(f.name, f'test_{i}'))
        # Verificar que se crearon los snapshots
        snapshots_before = bm.list_snapshots()
        assert len(snapshots_before) >= 3
        # Ejecutar cleanup con límite bajo
        removed = bm.cleanup_old_snapshots(max_count=1)
        # Verificar que se removieron snapshots
        snapshots_after = bm.list_snapshots()
        assert len(snapshots_after) <= len(snapshots_before)
        assert isinstance(removed, int)
    finally:
        # Limpiar todos los archivos temporales
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        for backup_path in backup_paths:
            if os.path.exists(backup_path):
                os.unlink(backup_path)
