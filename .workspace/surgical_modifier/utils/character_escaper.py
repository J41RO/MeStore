"""
Character Escaper for Surgical Modifier v6.0
Handles special characters that cause bash/shell issues
Prevents corruption like the !product problem
"""

import re
from typing import Dict, List


class CharacterEscaper:
    """Handles escaping of special characters for safe operations"""

    BASH_SPECIAL = [
        "!",
        "@",
        "#",
        "$",
        "%",
        "^",
        "&",
        "*",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
    ]

    @staticmethod
    def escape_for_bash(content: str) -> str:
        """Escape content for safe bash execution"""
        # Escape exclamation marks and other bash specials
        content = content.replace("!", "\\!")
        content = content.replace("$", "\\$")
        content = content.replace("`", "\\`")
        content = content.replace("&", "\\&")
        return content

    @staticmethod
    def escape_for_typescript(content: str) -> str:
        """Escape content for TypeScript insertion"""
        # Handle template literals and quotes
        content = content.replace("`", "\\`")
        content = content.replace("${", "\\${")
        return content

    @staticmethod
    def auto_escape(content: str, target_file: str) -> str:
        """Auto-escape based on file type"""
        escaped_content = content

        if target_file.endswith((".ts", ".tsx", ".js", ".jsx")):
            escaped_content = CharacterEscaper.escape_for_typescript(escaped_content)

        # Always escape for bash safety in CLI operations
        escaped_content = CharacterEscaper.escape_for_bash(escaped_content)
        return escaped_content

    @staticmethod
    def is_safe_content(content: str) -> bool:
        """Check if content is safe without escaping"""
        # Check for problematic patterns
        if re.search(r"[!$`&]\w+", content):
            return False
        if "${" in content and "}" not in content:
            return False
        return True

    @staticmethod
    def get_escape_report(original: str, escaped: str) -> dict:
        """Generate report of what was escaped"""
        changes = []
        if "!" in original:
            changes.append("Escaped exclamation marks")
        if "$" in original:
            changes.append("Escaped dollar signs")
        if "`" in original:
            changes.append("Escaped backticks")

        return {
            "original_length": len(original),
            "escaped_length": len(escaped),
            "changes_made": changes,
            "safe": True,
        }
