"""
Basic extraction utilities for Surgical Modifier v6.0

This module contains utility functions for extracting and processing
code patterns that are commonly used across different operations.

Functions:
    extract_line_indentation: Extract indentation from a line
    apply_indentation_to_content: Apply indentation to multi-line content
    extract_v53_arguments: Extract common arguments from v5.3 format
"""

from pathlib import Path
from typing import List, Dict, Any, Optional


# Module version and metadata
__version__ = "1.0.0"
__author__ = "Surgical Modifier Team"


def extract_line_indentation(line: str) -> str:
    """
    Extract indentation from a line.
    
    Args:
        line (str): The line from which to extract indentation
        
    Returns:
        str: The indentation string (spaces/tabs at the beginning)
        
    Examples:
        >>> extract_line_indentation("    hello world")
        "    "
        >>> extract_line_indentation("\t\tdef function():")
        "\t\t"
        >>> extract_line_indentation("no_indent")
        ""
    """
    if not isinstance(line, str):
        raise ValueError("Input must be a string")
    return line[:len(line) - len(line.lstrip())]    \n\n\ndef apply_indentation_to_content(content: str, indentation: str) -> str:\n    \"\"\"\n    Apply indentation to content, handling multi-line content.\n    \n    Args:\n        content (str): The content to indent\n        indentation (str): The indentation string to apply\n        \n    Returns:\n        str: The indented content\n        \n    Examples:\n        >>> apply_indentation_to_content(\'line1\\nline2\', \'  \')\n        \'  line1\\n  line2\'\n        >>> apply_indentation_to_content(\'single\', \'    \')\n        \'    single\'\n        >>> apply_indentation_to_content(\'line1\\n\\nline3\', \'\\t\')\n        \'\\tline1\\n\\n\\tline3\'\n    \"\"\"\n    if not indentation:\n        return content\n    lines = content.splitlines()\n    indented_lines = []\n    for i, line in enumerate(lines):\n        if i == 0:\n            # First line gets the base indentation\n            indented_lines.append(indentation + line)\n        else:\n            # Subsequent lines get additional indentation if not empty\n            if line.strip():\n                indented_lines.append(indentation + line)\n            else:\n                indented_lines.append(line)\n    return \'\\n\'.join(indented_lines)