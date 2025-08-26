import os
import shutil
import tempfile
import logging
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime


class RollbackManager:
    """
    Gestor de rollback automático para operaciones de modificación de código.
    
    Proporciona funcionalidad para crear checkpoints y restaurar estado
    en caso de corrupción o fallas durante modificaciones.
    """
    
    def __init__(self, logger_name: str = 'rollback_manager'):
        """
        Inicializa el gestor de rollback.
        
        Args:
            logger_name: Nombre del logger para reportes
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        
        # Configurar handler si no existe
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Directorio temporal para checkpoints
        self.checkpoint_dir = tempfile.mkdtemp(prefix='rollback_checkpoints_')
        self.logger.info(f'Directorio de checkpoints inicializado: {self.checkpoint_dir}')
    
    def create_checkpoint(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Crea un checkpoint del estado actual de un archivo.
        
        Args:
            file_path: Ruta al archivo para crear checkpoint
            
        Returns:
            Dict con información del checkpoint o None si falla
        """
        if not os.path.exists(file_path):
            self.logger.error(f'Archivo no encontrado para checkpoint: {file_path}')
            return None
        
        try:
            # Generar ID único para el checkpoint
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            file_hash = self._calculate_file_hash(file_path)
            checkpoint_id = f'{os.path.basename(file_path)}_{timestamp}_{file_hash[:8]}'
            
            # Crear copia de seguridad
            checkpoint_path = os.path.join(self.checkpoint_dir, checkpoint_id)
            shutil.copy2(file_path, checkpoint_path)
            
            checkpoint_info = {
                'id': checkpoint_id,
                'original_path': file_path,
                'checkpoint_path': checkpoint_path,
                'timestamp': timestamp,
                'file_hash': file_hash,
                'file_size': os.path.getsize(file_path)
            }
            
            self.logger.info(f'Checkpoint creado: {checkpoint_id} para {file_path}')
            return checkpoint_info
            
        except Exception as e:
            self.logger.error(f'Error creando checkpoint para {file_path}: {str(e)}')
            return None
    
    def rollback_to_checkpoint(self, file_path: str, checkpoint_info: Dict[str, Any]) -> bool:
        """
        Restaura un archivo desde un checkpoint.
        
        Args:
            file_path: Ruta al archivo a restaurar
            checkpoint_info: Información del checkpoint (de create_checkpoint)
            
        Returns:
            bool: True si el rollback fue exitoso, False en caso contrario
        """
        if not checkpoint_info:
            self.logger.error('Información de checkpoint no válida')
            return False
        
        checkpoint_path = checkpoint_info.get('checkpoint_path')
        if not checkpoint_path or not os.path.exists(checkpoint_path):
            self.logger.error(f'Checkpoint no encontrado: {checkpoint_path}')
            return False
        
        try:
            # Verificar integridad del checkpoint
            current_hash = self._calculate_file_hash(checkpoint_path)
            expected_hash = checkpoint_info.get('file_hash')
            
            if current_hash != expected_hash:
                self.logger.warning('Checkpoint podría estar corrupto (hash no coincide)')
            
            # Crear backup del estado actual antes del rollback
            if os.path.exists(file_path):
                backup_path = f'{file_path}.rollback_backup'
                shutil.copy2(file_path, backup_path)
                self.logger.info(f'Backup pre-rollback creado: {backup_path}')
            
            # Restaurar desde checkpoint
            shutil.copy2(checkpoint_path, file_path)
            
            self.logger.info(f'Rollback exitoso: {file_path} restaurado desde checkpoint {checkpoint_info["id"]}')
            return True
            
        except Exception as e:
            self.logger.error(f'Error durante rollback de {file_path}: {str(e)}')
            return False
    
    def validate_file_integrity(self, file_path: str, expected_hash: str = None) -> bool:
        """
        Valida la integridad de un archivo comparando hashes.
        
        Args:
            file_path: Ruta al archivo a validar
            expected_hash: Hash esperado (opcional)
            
        Returns:
            bool: True si la integridad es válida
        """
        if not os.path.exists(file_path):
            self.logger.error(f'Archivo no encontrado para validación: {file_path}')
            return False
        
        try:
            current_hash = self._calculate_file_hash(file_path)
            
            if expected_hash:
                is_valid = current_hash == expected_hash
                if is_valid:
                    self.logger.info(f'Integridad válida: {file_path}')
                else:
                    self.logger.warning(f'Integridad comprometida: {file_path}')
                return is_valid
            else:
                self.logger.info(f'Hash calculado para {file_path}: {current_hash}')
                return True
                
        except Exception as e:
            self.logger.error(f'Error validando integridad de {file_path}: {str(e)}')
            return False
    
    def cleanup_checkpoints(self, max_age_hours: int = 24):
        """
        Limpia checkpoints antiguos para liberar espacio.
        
        Args:
            max_age_hours: Edad máxima en horas para conservar checkpoints
        """
        try:
            current_time = datetime.now()
            cleaned_count = 0
            
            for filename in os.listdir(self.checkpoint_dir):
                file_path = os.path.join(self.checkpoint_dir, filename)
                
                # Obtener tiempo de modificación
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                age_hours = (current_time - mod_time).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    os.remove(file_path)
                    cleaned_count += 1
            
            if cleaned_count > 0:
                self.logger.info(f'Limpieza completada: {cleaned_count} checkpoints antiguos eliminados')
            
        except Exception as e:
            self.logger.error(f'Error durante limpieza de checkpoints: {str(e)}')
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calcula el hash SHA256 de un archivo.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            str: Hash SHA256 del archivo
        """
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def __del__(self):
        """
        Limpia el directorio temporal al destruir la instancia.
        """
        try:
            if hasattr(self, 'checkpoint_dir') and os.path.exists(self.checkpoint_dir):
                shutil.rmtree(self.checkpoint_dir)
        except Exception:
            pass  # Silenciar errores durante destrucción