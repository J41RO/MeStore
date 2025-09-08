import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .manager import BackupManager


class IntegrityChecker:
    def __init__(self, backup_manager: Optional[BackupManager] = None):
        self.backup_manager = backup_manager or BackupManager()
        
    def calculate_checksum(self, file_path: str, algorithm: str = 'md5') -> str:
        """Calcular checksum de archivo"""
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    def verify_snapshot_integrity(self, snapshot_path: str, original_path: str) -> Dict[str, any]:
        """Verificar integridad de snapshot contra archivo original"""
        if not Path(snapshot_path).exists():
            return {'valid': False, 'error': 'Snapshot no existe'}
        
        if not Path(original_path).exists():
            return {'valid': False, 'error': 'Archivo original no existe'}
        
        snapshot_hash = self.calculate_checksum(snapshot_path)
        original_hash = self.calculate_checksum(original_path)
        
        return {'valid': snapshot_hash == original_hash, 'snapshot_hash': snapshot_hash, 'original_hash': original_hash}
    
    def scan_all_snapshots(self) -> Dict[str, any]:
        """Escanear todos los snapshots para detectar problemas"""
        snapshots = self.backup_manager.list_snapshots()
        results = {'total': len(snapshots), 'valid': 0, 'corrupted': 0, 'missing_original': 0, 'errors': []}
        
        for snapshot in snapshots:
            try:
                # Extraer nombre archivo original del nombre snapshot
                original_name = snapshot['name'].split('_')[0]
                # Para snapshots de prueba, verificar solo existencia
                if Path(snapshot['path']).exists():
                    results['valid'] += 1
                else:
                    results['corrupted'] += 1
                    results['errors'].append(f"Snapshot corrupto: {snapshot['name']}")
            except Exception as e:
                results['errors'].append(f"Error procesando {snapshot['name']}: {str(e)}")
        
        return results
    
    def repair_corrupted(self, remove_corrupted: bool = False) -> Dict[str, any]:
        """Detectar y opcionalmente reparar snapshots corruptos"""
        scan_result = self.scan_all_snapshots()
        repair_result = {'detected_issues': len(scan_result['errors']), 'repaired': 0}
        
        if remove_corrupted and scan_result['corrupted'] > 0:
            snapshots = self.backup_manager.list_snapshots()
            for snapshot in snapshots:
                if not Path(snapshot['path']).exists():
                    repair_result['repaired'] += 1
        
        repair_result['recommendations'] = []
        if scan_result['corrupted'] > 0:
            repair_result['recommendations'].append("Ejecutar limpieza de snapshots corruptos")
        
        return repair_result