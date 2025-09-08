import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Union, Any
import stat
import logging

class PathChecker:
    """
    Validador de rutas, permisos y directorios padres.
    Sigue arquitectura modular functions/ del proyecto.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def validate_path(self, file_path: str) -> Dict[str, Any]:
        """
        Validación completa de ruta de archivo.
        
        Args:
            file_path: Ruta del archivo a validar
            
        Returns:
            Dict con resultado de validación y detalles
        """
        try:
            # Normalizar ruta
            normalized_path = os.path.normpath(os.path.expanduser(file_path))
            path_obj = Path(normalized_path)
            
            result = {
                'success': True,
                'path': normalized_path,
                'absolute_path': str(path_obj.absolute()),
                'exists': path_obj.exists(),
                'is_file': False,
                'is_directory': False,
                'parent_exists': False,
                'parent_writable': False,
                'errors': []
            }
            
            # Verificar si existe
            if path_obj.exists():
                result['is_file'] = path_obj.is_file()
                result['is_directory'] = path_obj.is_dir()
                
                if result['is_directory']:
                    result['errors'].append(f"Path is directory, not file: {normalized_path}")
                    result['success'] = False
            
            # Verificar directorio padre
            parent_dir = path_obj.parent
            result['parent_exists'] = parent_dir.exists()
            
            if result['parent_exists']:
                result['parent_writable'] = os.access(str(parent_dir), os.W_OK)
            else:
                result['errors'].append(f"Parent directory does not exist: {parent_dir}")
                result['success'] = False
                
            # Verificar nombre de archivo válido
            if not path_obj.name:
                result['errors'].append("Empty filename not allowed")
                result['success'] = False
                
            # Verificar caracteres problemáticos
            invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
            if any(char in path_obj.name for char in invalid_chars):
                result['errors'].append(f"Invalid characters in filename: {path_obj.name}")
                result['success'] = False
                
            return result
            
        except Exception as e:
            self.logger.error(f"Path validation error: {e}")
            return {
                'success': False,
                'path': file_path,
                'errors': [f"Validation exception: {str(e)}"]
            }
    
    def check_permissions(self, file_path: str) -> Dict[str, Any]:
        """
        Verificar permisos de archivo y directorio padre.
        
        Args:
            file_path: Ruta del archivo a verificar
            
        Returns:
            Dict con información de permisos
        """
        try:
            path_obj = Path(file_path)
            parent_dir = path_obj.parent
            
            result = {
                'success': True,
                'file_exists': path_obj.exists(),
                'parent_exists': parent_dir.exists(),
                'parent_readable': False,
                'parent_writable': False,
                'parent_executable': False,
                'file_readable': False,
                'file_writable': False,
                'can_create': False,
                'errors': []
            }
            
            # Permisos del directorio padre
            if result['parent_exists']:
                parent_path = str(parent_dir)
                result['parent_readable'] = os.access(parent_path, os.R_OK)
                result['parent_writable'] = os.access(parent_path, os.W_OK)
                result['parent_executable'] = os.access(parent_path, os.X_OK)
                
                # Capacidad de crear archivo
                result['can_create'] = (result['parent_writable'] and 
                                      result['parent_executable'])
            else:
                result['errors'].append(f"Parent directory not accessible: {parent_dir}")
                result['success'] = False
                
            # Permisos del archivo si existe
            if result['file_exists']:
                file_path_str = str(path_obj)
                result['file_readable'] = os.access(file_path_str, os.R_OK)
                result['file_writable'] = os.access(file_path_str, os.W_OK)
                
                # Si es directory, marcar error
                if path_obj.is_dir():
                    result['errors'].append("Path is directory, expected file")
                    result['success'] = False
            
            return result
            
        except Exception as e:
            self.logger.error(f"Permission check error: {e}")
            return {
                'success': False,
                'errors': [f"Permission check exception: {str(e)}"]
            }
    
    def ensure_parent_dirs(self, file_path: str, mode: int = 0o755) -> Dict[str, Any]:
        """
        Crear directorios padres si no existen.
        
        Args:
            file_path: Ruta del archivo
            mode: Permisos para directorios creados
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            path_obj = Path(file_path)
            parent_dir = path_obj.parent
            
            result = {
                'success': True,
                'parent_path': str(parent_dir),
                'existed_before': parent_dir.exists(),
                'created_dirs': [],
                'errors': []
            }
            
            if not result['existed_before']:
                # Crear directorios padres recursivamente
                parent_dir.mkdir(parents=True, exist_ok=True, mode=mode)
                
                # Identificar qué directorios se crearon
                current = parent_dir
                created_paths = []
                
                while current and not current.exists():
                    created_paths.append(str(current))
                    current = current.parent
                    
                result['created_dirs'] = created_paths
                self.logger.info(f"Created parent directories for: {file_path}")
            
            # Verificar resultado final
            if not parent_dir.exists():
                result['success'] = False
                result['errors'].append(f"Failed to create parent directory: {parent_dir}")
            elif not os.access(str(parent_dir), os.W_OK):
                result['success'] = False
                result['errors'].append(f"Parent directory not writable: {parent_dir}")
                
            return result
            
        except PermissionError as e:
            self.logger.error(f"Permission denied creating directories: {e}")
            return {
                'success': False,
                'errors': [f"Permission denied: {str(e)}"]
            }
        except Exception as e:
            self.logger.error(f"Directory creation error: {e}")
            return {
                'success': False,
                'errors': [f"Directory creation exception: {str(e)}"]
            }


# Funciones de conveniencia para compatibilidad
def validate_path(file_path: str) -> Dict[str, Any]:
    """Función de conveniencia para validar ruta"""
    checker = PathChecker()
    return checker.validate_path(file_path)

def check_permissions(file_path: str) -> Dict[str, Any]:
    """Función de conveniencia para verificar permisos"""
    checker = PathChecker()
    return checker.check_permissions(file_path)

def ensure_parent_dirs(file_path: str, mode: int = 0o755) -> Dict[str, Any]:
    """Función de conveniencia para crear directorios padres"""
    checker = PathChecker()
    return checker.ensure_parent_dirs(file_path, mode)