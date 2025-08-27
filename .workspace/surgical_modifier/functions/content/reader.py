import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
import charset_normalizer

class ContentReader:
    def __init__(self, fallback_encoding: str = 'utf-8'):
        self.fallback_encoding = fallback_encoding
        self.supported_encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    def detect_encoding(self, file_path: str) -> Dict[str, Union[str, float]]:
        """Detectar encoding de archivo usando charset_normalizer"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            if not raw_data:
                return {'encoding': self.fallback_encoding, 'confidence': 0.0, 'method': 'fallback_empty'}
            
            detection = charset_normalizer.detect(raw_data)
            if detection and detection.get('confidence', 0) > 0.7:
                return {'encoding': detection['encoding'], 'confidence': detection['confidence'], 'method': 'charset_normalizer'}
            
            return {'encoding': self.fallback_encoding, 'confidence': 0.5, 'method': 'fallback_low_confidence'}
        
        except Exception as e:
            return {'encoding': self.fallback_encoding, 'confidence': 0.0, 'method': f'fallback_error_{str(e)[:20]}'}
        
    def read_file(self, file_path: str, encoding: Optional[str] = None) -> Dict[str, Union[str, Dict]]:
        """Leer archivo con deteccion automatica o encoding especificado"""
        file_path = str(Path(file_path).resolve())
        
        if not Path(file_path).exists():
            return {'success': False, 'error': 'File not found', 'content': '', 'encoding_info': {}}
        
        # Usar encoding especificado o detectar
        if encoding:
            encoding_info = {'encoding': encoding, 'confidence': 1.0, 'method': 'user_specified'}
        else:
            encoding_info = self.detect_encoding(file_path)
            encoding = encoding_info['encoding']
        
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                content = f.read()
            
            return {'success': True, 'content': content, 'encoding_info': encoding_info, 'file_path': file_path}
        
        except Exception as e:
            return {'success': False, 'error': str(e), 'content': '', 'encoding_info': encoding_info}
        
    def read_with_fallback(self, file_path: str) -> Dict[str, Union[str, Dict, list]]:
        """Leer archivo con multiples intentos de encoding"""
        attempts = []
        
        # Intento 1: Deteccion automatica
        result = self.read_file(file_path)
        attempts.append({'encoding': result['encoding_info'].get('encoding'), 'success': result['success']})
        if result['success']:
            result['attempts'] = attempts
            return result
        
        # Intento 2-N: Encodings comunes
        for encoding in self.supported_encodings:
            if encoding != result['encoding_info'].get('encoding'):  # Skip ya intentado
                fallback_result = self.read_file(file_path, encoding)
                attempts.append({'encoding': encoding, 'success': fallback_result['success']})
                if fallback_result['success']:
                    fallback_result['attempts'] = attempts
                    return fallback_result
        
        return {'success': False, 'error': 'All encoding attempts failed', 'content': '', 'attempts': attempts}
    


