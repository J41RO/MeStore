"""
TypeScript Syntax Validator for Surgical Modifier v6.0
Prevents insertion of malformed code and validates structure
"""

import re
from typing import Dict, List, Optional, Tuple


class TypeScriptValidator:
    """Validates TypeScript syntax and structure before insertions"""

    def __init__(self):
        self.interface_pattern = re.compile(r"interface\s+(\w+)\s*{")
        self.function_pattern = re.compile(r"(const|function)\s+(\w+)")
        self.variable_pattern = re.compile(r"const\s+(\w+)\s*=")
        self.import_pattern = re.compile(r"import\s+.*from\s+[\x27\x22].*[\x27\x22]")

    def validate_insertion(
        self, content: str, target_content: str, position: str
    ) -> Dict:
        """Validate if insertion will maintain valid TypeScript"""
        errors = []
        warnings = []

        # Check for incomplete assignments
        if re.search(r"const\s+\w+\s*=\s*;", content):
            errors.append("Incomplete variable assignment detected")

        # Check for bash-style comments in TS code
        if re.search(r"#\s+[^/]", content):
            errors.append("Bash-style comment detected in TypeScript code")

        # Check for special characters that need escaping
        special_chars = re.findall(r"[!@#$%^&*()]\w+", content)
        if special_chars:
            warnings.append(f"Special characters detected: {special_chars}")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def validate_syntax_integrity(self, filepath: str) -> Dict:
        """Quick syntax validation for existing files"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            issues = []

            # Check for incomplete statements
            if re.search(r"const\s+\w+\s*=\s*;", content):
                issues.append("Incomplete variable assignments found")

            return {"valid": len(issues) == 0, "issues": issues}

        except Exception as e:
            return {"valid": False, "issues": [f"File read error: {str(e)}"]}
