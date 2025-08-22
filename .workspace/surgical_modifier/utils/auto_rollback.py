"""
Auto Rollback System for Surgical Modifier v6.0
Automatically detects errors and reverts changes to prevent corruption
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class AutoRollback:
    """Automatic rollback system for failed operations"""

    def __init__(self, backup_dir: str = "./.rollback_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self, filepath: str) -> str:
        """Create backup before operation"""
        source_path = Path(filepath)
        if not source_path.exists():
            raise FileNotFoundError("Cannot backup non-existent file: " + filepath)

        backup_filename = source_path.name + "." + str(os.getpid()) + ".backup"
        backup_path = self.backup_dir / backup_filename

        shutil.copy2(source_path, backup_path)
        return str(backup_path)

    def verify_syntax(self, filepath: str) -> Dict:
        """Verify file syntax after operation"""
        file_path = Path(filepath)

        if file_path.suffix == ".py":
            return self._verify_python_syntax(filepath)
        elif file_path.suffix in [".ts", ".tsx", ".js", ".jsx"]:
            return self._verify_basic_syntax(filepath)
        else:
            return {"valid": True, "errors": []}

    def _verify_python_syntax(self, filepath: str) -> Dict:
        """Verify Python syntax using compile"""
        try:
            result = subprocess.run(
                ["python3", "-m", "py_compile", filepath],
                capture_output=True,
                text=True,
            )
            return {
                "valid": result.returncode == 0,
                "errors": [result.stderr] if result.stderr else [],
            }
        except Exception as e:
            return {"valid": False, "errors": [str(e)]}

    def _verify_basic_syntax(self, filepath: str) -> Dict:
        """Basic syntax verification for non-Python files"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            errors = []

            # Check for unmatched braces
            if content.count("{") != content.count("}"):
                errors.append("Unmatched braces")

            # Check for unmatched parentheses
            if content.count("(") != content.count(")"):
                errors.append("Unmatched parentheses")

            return {"valid": len(errors) == 0, "errors": errors}

        except Exception as e:
            return {"valid": False, "errors": [str(e)]}

    def rollback_file(self, filepath: str, backup_path: str) -> bool:
        """Rollback file from backup"""
        try:
            shutil.copy2(backup_path, filepath)
            os.remove(backup_path)
            return True
        except Exception:
            return False

    def execute_with_rollback(self, filepath: str, operation_func, *args, **kwargs):
        """Execute operation with automatic rollback on failure"""
        backup_path = self.create_backup(filepath)

        try:
            result = operation_func(*args, **kwargs)

            syntax_check = self.verify_syntax(filepath)

            if not syntax_check["valid"]:
                self.rollback_file(filepath, backup_path)
                error_msg = "Syntax validation failed: " + str(syntax_check["errors"])
                raise Exception(error_msg)

            os.remove(backup_path)
            return result

        except Exception as e:
            self.rollback_file(filepath, backup_path)
            raise e
