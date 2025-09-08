from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
import os
import logging
from datetime import datetime
from enum import Enum
from ..backup.intelligent_manager import IntelligentBackupManager

class TransactionState(Enum):
    """Estados posibles de una transacción"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"

class TransactionManager:
    """Maneja transacciones con rollback automático para operaciones batch"""
    
    def __init__(self):
        self.backup_manager = IntelligentBackupManager()
        self.logger = logging.getLogger(__name__)
        self.state = TransactionState.INACTIVE
        self.transaction_id = None
        self.affected_files = []
        self.transaction_backup_id = None
        
    def begin_transaction(self) -> str:
        """Inicia una nueva transacción"""
        if self.state != TransactionState.INACTIVE:
            raise RuntimeError(f"Cannot begin transaction. Current state: {self.state.value}")
        
        self.transaction_id = f"tx_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        self.state = TransactionState.ACTIVE
        self.affected_files = []
        
        self.logger.info(f"Transaction {self.transaction_id} started")
        return self.transaction_id
    
    def add_file_to_transaction(self, file_path: str) -> None:
        """Añade un archivo a la transacción actual"""
        if self.state != TransactionState.ACTIVE:
            raise RuntimeError(f"No active transaction. Current state: {self.state.value}")
        
        if file_path not in self.affected_files:
            # Crear backup del archivo antes de modificarlo
            if Path(file_path).exists():
                backup_id = self.backup_manager.create_temp_backup(file_path, f"Transaction_{self.transaction_id}")
                self.affected_files.append({
                    'file_path': file_path,
                    'backup_id': backup_id,
                    'existed_before': True
                })
                self.logger.debug(f"File {file_path} added to transaction with backup {backup_id}")
            else:
                self.affected_files.append({
                    'file_path': file_path,
                    'backup_id': None,
                    'existed_before': False
                })
                self.logger.debug(f"New file {file_path} added to transaction")
    
    def commit(self) -> Dict[str, Any]:
        """Confirma la transacción, haciendo permanentes los cambios"""
        if self.state != TransactionState.ACTIVE:
            raise RuntimeError(f"Cannot commit transaction. Current state: {self.state.value}")
        
        try:
            self.state = TransactionState.COMMITTED
            
            result = {
                'success': True,
                'transaction_id': self.transaction_id,
                'files_modified': len(self.affected_files),
                'committed_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"Transaction {self.transaction_id} committed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error committing transaction {self.transaction_id}: {str(e)}")
            return self.rollback()
    
    def rollback(self) -> Dict[str, Any]:
        """Revierte todos los cambios de la transacción"""
        if self.state not in [TransactionState.ACTIVE, TransactionState.COMMITTED]:
            raise RuntimeError(f"Cannot rollback transaction. Current state: {self.state.value}")
        
        try:
            rollback_results = []
            
            for file_info in reversed(self.affected_files):
                try:
                    file_path = file_info['file_path']
                    backup_id = file_info['backup_id']
                    existed_before = file_info['existed_before']
                    
                    if existed_before and backup_id:
                        # Restaurar desde backup
                        self.backup_manager.restore_backup(backup_id)
                        rollback_results.append({
                            'file': file_path,
                            'action': 'restored_from_backup',
                            'success': True
                        })
                    elif not existed_before and Path(file_path).exists():
                        # Eliminar archivo que fue creado durante la transacción
                        Path(file_path).unlink()
                        rollback_results.append({
                            'file': file_path,
                            'action': 'deleted_new_file',
                            'success': True
                        })
                    
                except Exception as e:
                    rollback_results.append({
                        'file': file_info['file_path'],
                        'action': 'rollback_failed',
                        'success': False,
                        'error': str(e)
                    })
            
            self.state = TransactionState.ROLLED_BACK
            
            result = {
                'success': True,
                'transaction_id': self.transaction_id,
                'rollback_results': rollback_results,
                'rolled_back_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"Transaction {self.transaction_id} rolled back successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Critical error during rollback of transaction {self.transaction_id}: {str(e)}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual de la transacción"""
        return {
            'transaction_id': self.transaction_id,
            'state': self.state.value,
            'affected_files_count': len(self.affected_files),
            'affected_files': [f['file_path'] for f in self.affected_files]
        }