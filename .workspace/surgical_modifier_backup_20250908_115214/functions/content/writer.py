import os
from pathlib import Path
from typing import Dict, Optional, Union, Any
from .reader import ContentReader

class ContentWriter:
    def __init__(self, backup_manager: Optional[Any] = None):
        self.backup_manager = backup_manager
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
            lf_count = content.count(b'\n') - crlf_count
            cr_count = content.count(b'\r') - crlf_count
            
            if crlf_count > max(lf_count, cr_count):
                return {'type': 'windows', 'ending': '\r\n', 'count': crlf_count}
            elif lf_count > max(crlf_count, cr_count):
                return {'type': 'unix', 'ending': '\n', 'count': lf_count}
            elif cr_count > 0:
                return {'type': 'mac', 'ending': '\r', 'count': cr_count}
            else:
                return {'type': 'unix', 'ending': '\n', 'count': 0}
                
        except Exception:
            return {'type': 'unix', 'ending': '\n', 'count': 0}
    
    def write_file(self, file_path: str, content: str, preserve_line_endings: bool = True,
                   backup: bool = False, encoding: Optional[str] = None) -> Dict[str, Union[bool, str, Dict]]:
        """Escribir archivo preservando line endings originales"""
        file_path = str(Path(file_path).resolve())
        
        backup_info = {'backup_created': False}
        
        line_ending = '\n'
        if preserve_line_endings and Path(file_path).exists():
            ending_info = self.detect_line_ending(file_path)
            line_ending = ending_info['ending']
        elif not preserve_line_endings:
            if '\r\n' in content:
                line_ending = '\r\n'
            elif '\r' in content:
                line_ending = '\r'
        
        normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')
        if line_ending != '\n':
            normalized_content = normalized_content.replace('\n', line_ending)
        
        if not encoding:
            if Path(file_path).exists():
                read_result = self.reader.read_file(file_path)
                encoding = read_result.get('encoding_info', {}).get('encoding', 'utf-8')
            else:
                encoding = 'utf-8'
        
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
                              backup: bool = False, encoding: str = 'utf-8') -> Dict[str, Union[bool, str, Dict]]:
        """Escribir archivo con line ending especifico"""
        if line_ending_type not in self.line_endings:
            return {'success': False, 'error': f'Invalid line_ending_type: {line_ending_type}'}
        
        line_ending = self.line_endings[line_ending_type]
        normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')
        if line_ending != '\n':
            normalized_content = normalized_content.replace('\n', line_ending)
        
        file_path = str(Path(file_path).resolve())
        backup_info = {'backup_created': False}
        
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