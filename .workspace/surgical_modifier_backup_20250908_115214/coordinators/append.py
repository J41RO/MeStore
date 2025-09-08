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

class AppendCoordinator:
    """Coordinador para agregar contenido AL FINAL del archivo"""

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
        """Orquestador ligero - coordina functions para inserción append"""
        try:
            self.backup_manager.create_snapshot(file_path)
            read_result = self.reader.read_file(file_path)
            current_content = read_result['content']

            indentation = self.indentation_detector.suggest_indentation(current_content)
            # Para append, no necesitamos indentación automática
            formatted_obj = type("obj", (), {"content": content_to_insert})()

            lines = current_content.split('\n')
            lines.append(formatted_obj.content)
            new_content = '\n'.join(lines)

            self.writer.write_file(file_path, new_content)

            return {"success": True, "position": len(lines) - 1,
                    "context": {"position": len(lines) - 1, "simplified": True},
                    "validation": {"valid": True, "simplified": True}}

        except Exception as e:
            self.logger.error(f"Error in append operation: {e}")
            return {"success": False, "error": str(e)}
