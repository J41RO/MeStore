"""
Post-Operation Validator for CLI v6.0
Validates files after operations and triggers rollback if needed
"""

import ast
import subprocess
from pathlib import Path


class PostOperationValidator:
    """Validates files after operations"""

    @staticmethod
    def validate_python_file(filepath):
        """Validate Python file syntax"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            ast.parse(content)
            return True, "Valid Python syntax"
        except SyntaxError as e:
            return False, f"Python syntax error: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"

    @staticmethod
    def validate_typescript_file(filepath):
        """Basic TypeScript validation"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for common issues
            if "\\\\n" in content:
                return False, "Literal escape sequences found"
            if "\\'" in content and content.count("\\'") > content.count("'"):
                return False, "Excessive literal quote escapes"

            return True, "Basic TypeScript validation passed"
        except Exception as e:
            return False, f"TypeScript validation error: {e}"

    @staticmethod
    def auto_validate_file(filepath):
        """Auto-validate based on file extension"""
        path = Path(filepath)

        if path.suffix == ".py":
            return PostOperationValidator.validate_python_file(filepath)
        elif path.suffix in [".ts", ".tsx"]:
            return PostOperationValidator.validate_typescript_file(filepath)
        else:
            return True, "No validation needed for this file type"
