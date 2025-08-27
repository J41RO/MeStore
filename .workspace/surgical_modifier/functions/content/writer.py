import os
from pathlib import Path
from typing import Dict, Optional, Union
from .reader import ContentReader
from ..backup.manager import BackupManager

class ContentWriter:
    def __init__(self, backup_manager: Optional[BackupManager] = None):
        self.backup_manager = backup_manager or BackupManager()
        self.reader = ContentReader()
        self.line_endings = {
            'unix': '\n',
            'windows': '\r\n', 
            'mac': '\r'
        }
    
    def detect_line_ending(self, file_path: str) -> Dict[str, Union[str, int]]:
        """Detectar tipo de line ending en archivo existente"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            crlf_count = content.count(b'\r\n')
            lf_count = content.count(b'\n') - crlf_count  # LF sin CRLF
            cr_count = content.count(b'\r') - crlf_count  # CR sin CRLF
            
            if crlf_count > max(lf_count, cr_count):
                return {'type': 'windows', 'ending': '\r\n', 'count': crlf_count}
            elif lf_count > max(crlf_count, cr_count):
                return {'type': 'unix', 'ending': '\n', 'count': lf_count}
            elif cr_count > 0:
                return {'type': 'mac', 'ending': '\r', 'count': cr_count}
            else:
                return {'type': 'unix', 'ending': '\n', 'count': 0}  # Default para archivos sin line endings
                
        except Exception:
            return {'type': 'unix', 'ending': '\n', 'count': 0}  # Fallback
    
    def write_file(self, file_path: str, content: str, preserve_line_endings: bool = True,
                   backup: bool = True, encoding: Optional[str] = None) -> Dict[str, Union[bool, str, Dict]]:
        """Escribir archivo preservando line endings originales"""
        file_path = str(Path(file_path).resolve())
        
        # Crear backup si el archivo existe y se solicita
        backup_info = {}
        if backup and Path(file_path).exists():
            try:
                backup_path = self.backup_manager.create_snapshot(file_path, 'pre_write')
                backup_info = {'backup_created': True, 'backup_path': backup_path}
            except Exception as e:
                backup_info = {'backup_created': False, 'backup_error': str(e)}
        
        # Detectar line endings si se debe preservar
        line_ending = '\n'  # Default Unix
        if preserve_line_endings and Path(file_path).exists():
            ending_info = self.detect_line_ending(file_path)
            line_ending = ending_info['ending']
        elif not preserve_line_endings:
            # Cuando preserve_line_endings=False, detectar del contenido ya normalizado
            if '\r\n' in content:
                line_ending = '\r\n'
            elif '\r' in content:
                line_ending = '\r'
        
        # Normalizar content a line ending detectado
        normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')  # Normalize to LF
        if line_ending != '\n':
            normalized_content = normalized_content.replace('\n', line_ending)
        
        # Detectar encoding si no especificado
        if not encoding:
            if Path(file_path).exists():
                read_result = self.reader.read_file(file_path)
                encoding = read_result.get('encoding_info', {}).get('encoding', 'utf-8')
            else:
                encoding = 'utf-8'
        
        # Escribir archivo
        try:
            with open(file_path, 'w', encoding=encoding, newline='') as f:
                f.write(normalized_content)
            
            return {
                'success': True, 
                'file_path': file_path,
                'encoding': encoding,
                'line_ending': line_ending,
                'backup_info': backup_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'backup_info': backup_info
            }
            
    def write_with_line_ending(self, file_path: str, content: str, line_ending_type: str = 'unix',
                              backup: bool = True, encoding: str = 'utf-8') -> Dict[str, Union[bool, str, Dict]]:
        """Escribir archivo con line ending especifico"""
        if line_ending_type not in self.line_endings:
            return {'success': False, 'error': f'Invalid line_ending_type: {line_ending_type}'}
        
        # Preparar contenido con line ending específico
        line_ending = self.line_endings[line_ending_type]
        normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')
        if line_ending != '\n':
            normalized_content = normalized_content.replace('\n', line_ending)
        
        # Llamar write_file directamente con el contenido ya formateado
        file_path = str(Path(file_path).resolve())
        
        # Crear backup si el archivo existe y se solicita
        backup_info = {}
        if backup and Path(file_path).exists():
            try:
                backup_path = self.backup_manager.create_snapshot(file_path, 'pre_write')
                backup_info = {'backup_created': True, 'backup_path': backup_path}
            except Exception as e:
                backup_info = {'backup_created': False, 'backup_error': str(e)}
        
        # Escribir archivo directamente
        try:
            with open(file_path, 'w', encoding=encoding, newline='') as f:
                f.write(normalized_content)
            
            return {
                'success': True, 
                'file_path': file_path,
                'encoding': encoding,
                'line_ending': line_ending,
                'backup_info': backup_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'backup_info': backup_info
            }      
    
    
    