from pathlib import Path
from typing import Dict, Any
import sys
import os
import logging

from functions.pattern.pattern_factory import PatternMatcherFactory
from functions.backup.intelligent_manager import IntelligentBackupManager
from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter
from functions.content.validator import ContentValidator
from functions.debugging.context_extractor import ContextExtractor
from functions.debugging.pattern_suggester import PatternSuggester

class ReplaceCoordinator:
    """Coordinador para operaciones REPLACE - orquesta workflow con backup inteligente"""
    
    def __init__(self):
        self.pattern_factory = PatternMatcherFactory()
        self.backup_manager = IntelligentBackupManager()
        self.reader = ContentReader()
        self.writer = ContentWriter()
        self.context_extractor = ContextExtractor()
        self.pattern_suggester = PatternSuggester()
        self.validator = ContentValidator()
        self.logger = logging.getLogger(__name__)
    
    def execute(self, file_path: str, pattern: str, replacement: str, **kwargs) -> Dict[str, Any]:
        """Orquestador con backup inteligente integrado"""
        from functions.workflow.replace_workflow import ReplaceWorkflow

        workflow = ReplaceWorkflow()
        return workflow.execute_sequence(
            file_path=file_path,
            pattern=pattern,
            replacement=replacement,
            pattern_factory=self.pattern_factory,
            backup_manager=self.backup_manager,
            dry_run=kwargs.get('dry_run', False),
            reader=self.reader,
            writer=self.writer,
            validator=self.validator,
            context_extractor=self.context_extractor,
            pattern_suggester=self.pattern_suggester,
            **kwargs
        )