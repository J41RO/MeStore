import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from manager import BackupManager


class RollbackManager:
    def __init__(self, backup_manager: Optional[BackupManager] = None):
        self.backup_manager = backup_manager or BackupManager()
    
    def restore_snapshot(self, snapshot_path: str, target_path: str) -> bool:
        """Restaurar archivo desde snapshot específico"""
        snapshot_file = Path(snapshot_path)
        target_file = Path(target_path)
        
        if not snapshot_file.exists():
            raise FileNotFoundError(f"Snapshot no encontrado: {snapshot_path}")
        
        shutil.copy2(snapshot_file, target_file)
        return target_file.exists()

    def find_latest_snapshot(self, file_path: str, operation_type: Optional[str] = None) -> Optional[str]:
        """Encontrar snapshot más reciente para archivo específico"""
        file_name = Path(file_path).name
        snapshots = self.backup_manager.list_snapshots(file_name)
        
        if operation_type:
            snapshots = [s for s in snapshots if operation_type in s['name']]
        
        return snapshots[0]['path'] if snapshots else None

    def restore_latest(self, file_path: str, operation_type: Optional[str] = None, 
                    create_backup: bool = True) -> Tuple[bool, str]:
        """Restaurar desde snapshot más reciente con backup opcional del estado actual"""
        if create_backup and Path(file_path).exists():
            current_backup = self.backup_manager.create_snapshot(file_path, 'pre_restore')
        
        latest_snapshot = self.find_latest_snapshot(file_path, operation_type)
        if not latest_snapshot:
            return False, "No se encontró snapshot para restaurar"
        
        success = self.restore_snapshot(latest_snapshot, file_path)
        message = f"Restaurado desde {latest_snapshot}" if success else "Error en restauración"
        return success, message