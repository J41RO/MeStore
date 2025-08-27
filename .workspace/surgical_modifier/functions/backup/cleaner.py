import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from manager import BackupManager

class BackupCleaner:
    def __init__(self, backup_manager: Optional[BackupManager] = None):
        self.backup_manager = backup_manager or BackupManager()
    
    def cleanup_by_operation(self, operation_type: str, max_count: int = 10) -> Dict[str, int]:
        """Limpiar snapshots por tipo específico de operación"""
        snapshots = self.backup_manager.list_snapshots()
        op_snapshots = [s for s in snapshots if operation_type in s['name']]
        
        removed_count = 0
        for snapshot in op_snapshots[max_count:]:  # Mantener solo max_count más recientes
            Path(snapshot['path']).unlink()
            removed_count += 1
        
        return {'operation': operation_type, 'removed': removed_count, 'kept': min(len(op_snapshots), max_count)}

    def cleanup_by_size(self, max_total_mb: float = 100.0) -> Dict[str, any]:
        """Limpiar snapshots manteniendo tamaño total bajo límite"""
        snapshots = self.backup_manager.list_snapshots()
        total_size = sum(s['size'] for s in snapshots)
        max_bytes = max_total_mb * 1024 * 1024
        
        if total_size <= max_bytes:
            return {'action': 'none', 'total_size_mb': total_size / 1024 / 1024}
        
        removed_count = 0
        current_size = total_size
        for snapshot in reversed(snapshots):  # Remover más antiguos primero
            if current_size <= max_bytes:
                break
            Path(snapshot['path']).unlink()
            current_size -= snapshot['size']
            removed_count += 1
        
        return {'removed': removed_count, 'size_before_mb': total_size / 1024 / 1024, 'size_after_mb': current_size / 1024 / 1024}
    
    def advanced_cleanup(self, policies: Dict[str, any]) -> Dict[str, any]:
        """Aplicar múltiples políticas de limpieza en secuencia"""
        results = {'policies_applied': [], 'total_removed': 0}
        
        if 'max_age_days' in policies:
            basic_result = self.backup_manager.cleanup_old_snapshots(
                max_age_days=policies['max_age_days'], 
                max_count=policies.get('max_count', 50)
            )
            results['basic_cleanup'] = basic_result
            results['total_removed'] += basic_result
            results['policies_applied'].append('age_and_count')
        
        if 'max_size_mb' in policies:
            size_result = self.cleanup_by_size(policies['max_size_mb'])
            results['size_cleanup'] = size_result
            results['total_removed'] += size_result.get('removed', 0)
            results['policies_applied'].append('size_limit')
        
        return results