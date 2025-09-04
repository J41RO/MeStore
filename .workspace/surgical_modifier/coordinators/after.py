from pathlib import Path
from typing import Dict, Any
import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from functions.insertion.indentation_detector import IndentationDetector
from functions.insertion.position_calculator import PositionCalculator
from functions.insertion.content_formatter import ContentFormatter
from functions.insertion.context_analyzer import ContextAnalyzer
from functions.backup.manager import BackupManager
from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter
from functions.content.writer import ContentWriter
from functions.matching.fuzzy_matcher import FuzzyMatcher


class AfterCoordinator:
    """Coordinador para insertar contenido DESPUÉS de líneas/patrones específicos"""
    
    def __init__(self):
        self.indentation_detector = IndentationDetector()
        self.position_calculator = PositionCalculator()
        self.content_formatter = ContentFormatter()
        self.context_analyzer = ContextAnalyzer()
        self.backup_manager = BackupManager()
        self.reader = ContentReader()
        self.writer = ContentWriter()
        self.logger = logging.getLogger(__name__)
        self.logger = logging.getLogger(__name__)
        self.fuzzy_matcher = FuzzyMatcher()
    
    def execute(self, file_path: str, target: str, content: str, flexible: bool = False, **kwargs) -> Dict[str, Any]:
        """Coordinador simplificado con lógica directa"""
        try:
            # 1. Crear backup
            self.backup_manager.create_snapshot(file_path)
            
            # 2. Leer archivo
            read_result = self.reader.read_file(file_path)
            if not read_result.get('success', False):
                return {"success": False, "error": f"Failed to read file: {read_result.get('error', 'Unknown error')}"}
            
            current_content = read_result['content']
            lines = current_content.splitlines()
            
            # 3. LÓGICA DIRECTA - encontrar línea target
            line_index = -1
            for i, line in enumerate(lines):
                if self.fuzzy_matcher.fuzzy_match(target, line, flexible):
                    line_index = i
                    break
                    
            if line_index == -1:
                return {"success": False, "error": f"Target '{target}' not found"}
                
            # 4. LÓGICA DIRECTA - insertar contenido DESPUÉS
            insert_position = line_index + 1
            if '\n' in content:
                new_lines = content.split('\n')
                # Insertar líneas en orden correcto
                for i, new_line in enumerate(new_lines):
                    lines.insert(insert_position + i, new_line)
            else:
                lines.insert(insert_position, content)
                
            # 5. ESCRIBIR DIRECTAMENTE
            new_content = '\n'.join(lines)
            write_result = self.writer.write_file(file_path, new_content)
            
            if not write_result.get('success', False):
                return {"success": False, "error": f"Failed to write file: {write_result.get('error', 'Unknown error')}"}
            
            return {"success": True, "message": "Content inserted after target"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}