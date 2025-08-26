#!/usr/bin/env python3
"""
Backup management functions for file versioning
Extracted from replace.py for modular architecture
"""
import os
import shutil
import time



def create_temporary_backup(file_path: str) -> str:
    """Crear backup temporal - se elimina automáticamente al final"""
    backup_path = file_path + '.temp_backup_' + str(int(time.time()))
    shutil.copy2(file_path, backup_path)
    return backup_path

def cleanup_backup(backup_path: str) -> None:
    """Eliminar backup temporal sin dejar rastros"""
    try:
        if os.path.exists(backup_path):
            os.remove(backup_path)
    except:
        pass


def create_automatic_backup(file_path: str) -> str:
    """Crear backup automático con timestamp único"""
    import time
    from pathlib import Path
    import uuid
    timestamp = f"{int(time.time())}.{uuid.uuid4().hex[:8]}"
    backup_dir = Path(file_path).parent / '.backups'
    backup_dir.mkdir(exist_ok=True)
    filename = Path(file_path).name
    backup_path = backup_dir / f'{filename}.backup.{timestamp}'
    shutil.copy2(file_path, backup_path)
    return str(backup_path)

def cleanup_old_backups(file_path: str, keep_last: int = 5):
    """Limpiar backups antiguos, mantener solo los últimos N"""
    from pathlib import Path
    backup_dir = Path(file_path).parent / '.backups'
    if not backup_dir.exists():
        return
    filename = Path(file_path).name
    backup_files = list(backup_dir.glob(f'{filename}.backup.*'))
    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    for old_backup in backup_files[keep_last:]:
        old_backup.unlink()