from abc import ABC, abstractmethod
from typing import List, Optional
import os
import re
import time
import shutil
from pathlib import Path

from ...shared_functions.content_processor import detect_pattern_indentation, apply_context_indentation
from ...shared_functions.backup_system import create_automatic_backup, cleanup_old_backups
from ...shared_functions.syntax_validators import validate_python_syntax, validate_javascript_syntax

class InsertionBaseOperation(ABC):
    """Base class for insertion operations (before/after)"""

    def __init__(self):
        pass

    @abstractmethod
    def perform_insertion(self, lines: List[str], match_index: int, content: str, **kwargs) -> List[str]:
        """Abstract method for specific insertion logic"""
        pass
