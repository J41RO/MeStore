import os
import shutil
import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
# Config import comentado temporalmente hasta resolver estructura
# from surgical_modifier.config import get_backup_config


class BackupManager:
    def __init__(self, base_path: str = ".surgical_backups"):
        self.backup_root = Path(base_path)
        self.backup_root.mkdir(exist_ok=True)
    
    def create_snapshot(self, file_path: str, operation_type: str = "modify") -> str:
        """Crear snapshot con timestamp único"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        file_path_obj = Path(file_path)
        backup_name = f"{file_path_obj.name}_{operation_type}_{timestamp}.backup"
        backup_path = self.backup_root / backup_name
        shutil.copy2(file_path, backup_path)
        return str(backup_path)

    def list_snapshots(self, file_pattern: Optional[str] = None) -> List[Dict]:
        """Listar snapshots disponibles con metadata"""
        snapshots = []
        pattern = f"*{file_pattern}*" if file_pattern else "*.backup"
        
        for backup_file in self.backup_root.glob(pattern):
            stat = backup_file.stat()
            snapshots.append({
                'path': str(backup_file),
                'name': backup_file.name,
                'size': stat.st_size,
                'created': datetime.datetime.fromtimestamp(stat.st_mtime),
                'file_path': backup_file.name.split('_')[0]
            })
        return sorted(snapshots, key=lambda x: x['created'], reverse=True)

    def cleanup_old_snapshots(self, max_age_days: int = 7, max_count: int = 50) -> int:
        """Limpiar snapshots antiguos o excesivos"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
        snapshots = self.list_snapshots()
        removed_count = 0
        
        for snapshot in snapshots[max_count:]:  # Mantener solo max_count más recientes
            Path(snapshot['path']).unlink()
            removed_count += 1
        
        return removed_count
