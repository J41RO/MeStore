#!/usr/bin/env python3
"""
Universal Code Modifier

Una herramienta para modificar código de forma universal y segura.
Permite aplicar transformaciones y modificaciones a diferentes tipos de archivos de código.

Author: Laboratorio de Desarrollo
Version: 0.1.0
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional, Union
from abc import ABC, abstractmethod

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UniversalCodeModifier:
    """
    Clase principal para modificaciones universales de código.
    
    Esta clase proporciona la funcionalidad base para modificar
    archivos de código de diferentes lenguajes de forma segura y controlada.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Inicializar el modificador universal.
        
        Args:
            base_path (str, optional): Ruta base para operaciones de archivos
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.supported_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs']
        self.backup_enabled = True
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        self.logger.info(f"UniversalModifier inicializado en: {self.base_path}")

    def validate_file(self, file_path: Union[str, Path]) -> bool:
        """
        Validar que el archivo existe y es modificable.
        
        Args:
            file_path: Ruta al archivo a validar
            
        Returns:
            bool: True si el archivo es válido, False en caso contrario
        """
        path = Path(file_path)
        
        if not path.exists():
            self.logger.error(f"Archivo no encontrado: {path}")
            return False
            
        if not path.is_file():
            self.logger.error(f"La ruta no es un archivo: {path}")
            return False
            
        if path.suffix not in self.supported_extensions:
            self.logger.warning(f"Extensión no soportada: {path.suffix}")
            return False
            
        return True
    
    def create_backup(self, file_path: Union[str, Path]) -> Optional[Path]:
        """
        Crear respaldo de un archivo antes de modificarlo.
        
        Args:
            file_path: Ruta al archivo original
            
        Returns:
            Path: Ruta al archivo de respaldo creado, None si falla
        """
        if not self.backup_enabled:
            return None
            
        original_path = Path(file_path)
        backup_path = original_path.with_suffix(f"{original_path.suffix}.backup")
        
        try:
            backup_path.write_text(original_path.read_text(encoding='utf-8'))
            self.logger.info(f"Backup creado: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Error creando backup: {e}")
            return None
    
    def list_files(self, directory: Optional[Union[str, Path]] = None, 
                   recursive: bool = True) -> List[Path]:
        """
        Listar archivos de código en un directorio.
        
        Args:
            directory: Directorio a escanear (por defecto: base_path)
            recursive: Si buscar recursivamente en subdirectorios
            
        Returns:
            List[Path]: Lista de archivos encontrados
        """
        search_path = Path(directory) if directory else self.base_path
        found_files = []
        
        try:
            if recursive:
                for ext in self.supported_extensions:
                    found_files.extend(search_path.rglob(f"*{ext}"))
            else:
                for ext in self.supported_extensions:
                    found_files.extend(search_path.glob(f"*{ext}"))
                    
            self.logger.info(f"Encontrados {len(found_files)} archivos en {search_path}")
            return sorted(found_files)
            
        except Exception as e:
            self.logger.error(f"Error listando archivos: {e}")
            return []


    def detect_language(self, file_path: Union[str, Path]) -> Optional[str]:
        """
        Detectar el lenguaje de programación basado en la extensión del archivo.
        """
        path = Path(file_path)
        extension_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.java': 'Java'
        }
        return extension_map.get(path.suffix.lower())

    def analyze_file_metrics(self, file_path: Union[str, Path]) -> Dict[str, int]:
        """
        Analizar métricas básicas de un archivo de código.
        """
        content = self.read_file_safe(file_path) if hasattr(self, 'read_file_safe') else None
        if not content:
            try:
                content = Path(file_path).read_text()
            except:
                return {}
        lines = content.split('\n')
        return {
            'total_lines': len(lines),
            'non_empty_lines': len([line for line in lines if line.strip()]),
            'total_characters': len(content)
        }

def main():
    """Función principal para pruebas y uso directo."""
    print("Universal Code Modifier v0.1.0")
    print("Herramienta de modificación universal de código")
    
    modifier = UniversalCodeModifier()
    print(f"Inicializado en: {modifier.base_path}")
    print(f"Extensiones soportadas: {modifier.supported_extensions}")


if __name__ == "__main__":
    main()
