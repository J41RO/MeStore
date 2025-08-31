from pathlib import Path
from typing import Dict, Any
import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from functions.pattern.pattern_factory import PatternMatcherFactory
from functions.backup.manager import BackupManager
from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter
from functions.content.validator import ContentValidator

class ReplaceCoordinator:
    """Coordinador ligero para operación REPLACE. Orquesta functions modulares."""
    
    def __init__(self):
        self.pattern_factory = PatternMatcherFactory()
        self.backup_manager = BackupManager()
        self.reader = ContentReader()
        self.writer = ContentWriter()
        self.validator = ContentValidator()
    
    def execute(self, file_path: str, pattern: str, replacement: str, **kwargs) -> Dict[str, Any]:
        """Orquestador ligero - solo coordina functions modulares"""
        from functions.workflow.replace_workflow import ReplaceWorkflow
        
        workflow = ReplaceWorkflow()
        return workflow.execute_sequence(
            file_path=file_path,
            pattern=pattern,
            replacement=replacement,
            pattern_factory=self.pattern_factory,
            backup_manager=self.backup_manager,
            reader=self.reader,
            writer=self.writer,
            validator=self.validator,
            **kwargs
        )
