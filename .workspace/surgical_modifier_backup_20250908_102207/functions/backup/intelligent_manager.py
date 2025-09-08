"""
Gestor de Backups Inteligente para Surgical Modifier
- Solo mantiene backups de estados VÁLIDOS conocidos
- Limpia backups automáticamente después de operaciones exitosas
- Evita pérdida de progreso en rollbacks
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class IntelligentBackupManager:
    """Gestor de backups que preserva solo estados válidos y limpia automáticamente"""
    
    def __init__(self, backup_dir: str = ".surgical_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def create_valid_state_backup(self, file_path: str, operation: str) -> str:
        """
        Crea backup solo DESPUÉS de confirmar que el estado es válido.
        Reemplaza backup anterior del mismo archivo.
        """
        file_path_obj = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Nombre del backup: archivo_VALID_timestamp.backup
        backup_name = f"{file_path_obj.name}_VALID_{timestamp}.backup"
        backup_path = self.backup_dir / backup_name
        
        # PRIMERO: Borrar backup válido anterior de este archivo
        self._cleanup_old_valid_backups(file_path_obj.name)
        
        # SEGUNDO: Crear nuevo backup del estado válido
        try:
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Valid state backup created: {backup_path}")
            return str(backup_path)
        except Exception as e:
            self.logger.error(f"Failed to create valid backup: {e}")
            raise
    
    def create_temp_backup(self, file_path: str, operation: str) -> str:
        """
        Crea backup temporal ANTES de operación (para rollback de emergencia).
        Este se borra automáticamente si la operación es exitosa.
        """
        file_path_obj = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Nombre temporal: archivo_TEMP_timestamp.backup  
        backup_name = f"{file_path_obj.name}_TEMP_{timestamp}.backup"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Temporary backup created: {backup_path}")
            return str(backup_path)
        except Exception as e:
            self.logger.error(f"Failed to create temp backup: {e}")
            raise
    
    def confirm_operation_success(self, file_path: str, temp_backup_path: str):
        """
        Confirma que operación fue exitosa:
        1. Crea backup del nuevo estado válido
        2. Borra backup temporal
        3. Limpia backups viejos
        """
        try:
            # 1. Crear backup del estado válido actual
            self.create_valid_state_backup(file_path, "confirmed_success")
            
            # 2. Borrar backup temporal
            if os.path.exists(temp_backup_path):
                os.remove(temp_backup_path)
                self.logger.info(f"Temporary backup cleaned: {temp_backup_path}")
            
            # 3. Limpieza general de backups obsoletos
            self._cleanup_obsolete_backups()
            
        except Exception as e:
            self.logger.error(f"Error confirming operation success: {e}")
    
    def rollback_to_valid_state(self, file_path: str) -> bool:
        """
        Rollback inteligente: restaura al último estado VÁLIDO conocido,
        no al backup temporal que puede ser de una micro-fase intermedia.
        """
        file_name = Path(file_path).name
        
        # Buscar último backup VÁLIDO de este archivo
        valid_backup = self._find_latest_valid_backup(file_name)
        
        if not valid_backup:
            self.logger.error(f"No valid backup found for {file_path}")
            return False
        
        try:
            shutil.copy2(valid_backup, file_path)
            self.logger.info(f"Rolled back to valid state: {valid_backup}")
            return True
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False
    
    def emergency_rollback(self, file_path: str, temp_backup_path: str) -> bool:
        """
        Rollback de emergencia: usa backup temporal si no hay válido disponible
        """
        if os.path.exists(temp_backup_path):
            try:
                shutil.copy2(temp_backup_path, file_path)
                self.logger.info(f"Emergency rollback from temp backup: {temp_backup_path}")
                return True
            except Exception as e:
                self.logger.error(f"Emergency rollback failed: {e}")
                return False
        
        # Fallback: intentar rollback a estado válido
        return self.rollback_to_valid_state(file_path)
    
    def _find_latest_valid_backup(self, file_name: str) -> Optional[str]:
        """Encuentra el backup VÁLIDO más reciente de un archivo"""
        valid_backups = []
        
        for backup_file in self.backup_dir.glob(f"{file_name}_VALID_*.backup"):
            valid_backups.append(backup_file)
        
        if not valid_backups:
            return None
        
        # Retornar el más reciente por timestamp
        latest = max(valid_backups, key=lambda x: x.stat().st_mtime)
        return str(latest)
    
    def _cleanup_old_valid_backups(self, file_name: str):
        """Borra backups válidos viejos del mismo archivo (mantiene solo el más reciente)"""
        valid_backups = list(self.backup_dir.glob(f"{file_name}_VALID_*.backup"))
        
        if len(valid_backups) > 0:
            # Borrar todos los backups válidos viejos
            for backup in valid_backups:
                try:
                    os.remove(backup)
                    self.logger.info(f"Cleaned old valid backup: {backup}")
                except Exception as e:
                    self.logger.warning(f"Failed to clean old backup {backup}: {e}")
    
    def _cleanup_obsolete_backups(self):
        """Limpia backups temporales huérfanos y muy viejos"""
        cutoff_time = datetime.now().timestamp() - (24 * 3600)  # 24 horas
        
        for backup_file in self.backup_dir.glob("*_TEMP_*.backup"):
            if backup_file.stat().st_mtime < cutoff_time:
                try:
                    os.remove(backup_file)
                    self.logger.info(f"Cleaned obsolete temp backup: {backup_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to clean obsolete backup {backup_file}: {e}")
    
    def get_backup_status(self, file_path: str) -> Dict[str, any]:
        """Retorna estado de backups para un archivo"""
        file_name = Path(file_path).name
        
        valid_backup = self._find_latest_valid_backup(file_name)
        temp_backups = list(self.backup_dir.glob(f"{file_name}_TEMP_*.backup"))
        
        return {
            'has_valid_backup': valid_backup is not None,
            'valid_backup_path': valid_backup,
            'temp_backups_count': len(temp_backups),
            'backup_dir_size': self._get_dir_size()
        }
    
    def _get_dir_size(self) -> int:
        """Calcula tamaño total del directorio de backups"""
        total_size = 0
        for backup_file in self.backup_dir.glob("*.backup"):
            total_size += backup_file.stat().st_size
        return total_size

    def create_snapshot(self, file_path: str, operation: str) -> str:
        """Método de compatibilidad con sistema existente"""
        return self.create_temp_backup(file_path, operation)


# Clase de compatibilidad con sistema existente
class BackupManager:
    """Wrapper de compatibilidad para mantener API existente"""
    
    def __init__(self):
        self.intelligent_manager = IntelligentBackupManager()
    
    def create_snapshot(self, file_path: str, operation: str) -> str:
        """Crea backup temporal para compatibilidad"""
        return self.intelligent_manager.create_temp_backup(file_path, operation)
    
    def restore_backup(self, file_path: str, backup_path: str):
        """Restaura desde backup específico"""
        try:
            shutil.copy2(backup_path, file_path)
            return True
        except Exception:
            return False