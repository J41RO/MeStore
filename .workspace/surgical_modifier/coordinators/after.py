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
    
    def execute(self, file_path: str, target: str, content_to_insert: str, **kwargs) -> Dict[str, Any]:
        """Orquestador ligero - coordina functions para inserción after"""
        try:
            self.backup_manager.create_snapshot(file_path)
            read_result = self.reader.read_file(file_path)
            current_content = read_result['content']
            indentation = self.indentation_detector.suggest_indentation(current_content)
            position_obj = self.position_calculator.calculate_after_position(
                current_content, target, content_to_insert)
            formatted_obj = self.content_formatter.format_after_insertion(
                content_to_insert, indentation)
            lines = current_content.split('\n')
            insert_position = position_obj.line_number + 1
            lines.insert(insert_position, formatted_obj.content)
            new_content = '\n'.join(lines)
            self.writer.write_file(file_path, new_content)
            return {"success": True, "position": position_obj.line_number + 1,
                    "context": {"position": position_obj.line_number + 1, "simplified": True},
                    "validation": {"valid": True, "simplified": True}}
        except Exception as e:
            self.logger.error(f"Error in after operation: {e}")
            return {"success": False, "error": f"Error in after operation: {str(e)}"}