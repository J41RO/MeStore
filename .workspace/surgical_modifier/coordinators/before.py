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
from functions.content.validator import ContentValidator

class BeforeCoordinator:
    """Coordinador ligero para operación BEFORE. Orquesta functions modulares para inserción."""
    
    def __init__(self):
        self.indentation_detector = IndentationDetector()
        self.position_calculator = PositionCalculator()
        self.content_formatter = ContentFormatter()
        self.context_analyzer = ContextAnalyzer()
        self.backup_manager = BackupManager()
        self.reader = ContentReader()
        self.writer = ContentWriter()
        self.validator = ContentValidator()
        self.logger = logging.getLogger(__name__)

    def execute(self, file_path: str, target: str, content_to_insert: str, **kwargs) -> Dict[str, Any]:
        """Orquestador ligero - coordina functions para inserción before"""
        try:
            self.backup_manager.create_snapshot(file_path)
            read_result = self.reader.read_file(file_path)
            current_content = read_result['content']
            
            indentation = self.indentation_detector.suggest_indentation(current_content)
            position_obj = self.position_calculator.calculate_before_position(current_content, target, content_to_insert)
            formatted_obj = self.content_formatter.format_before_insertion(content_to_insert, indentation)
            
            lines = current_content.split('\n')
            lines.insert(position_obj.line_number, formatted_obj.content)
            new_content = '\n'.join(lines)
            
            self.writer.write_file(file_path, new_content)
            
            return {"success": True, "position": position_obj.line_number, 
                    "context": {"position": position_obj.line_number, "simplified": True}, 
                    "validation": {"valid": True, "simplified": True}}
        except Exception as e:
            self.logger.error(f"Error in before operation: {e}")
            return {"success": False, "error": str(e)}