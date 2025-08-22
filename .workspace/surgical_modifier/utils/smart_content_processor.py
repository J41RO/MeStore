"""
Smart Content Processor for Surgical Modifier v6.0
Handles intelligent escape processing and validation
"""

import re

# Typing imports cleaned for pre-commit


class SmartContentProcessor:
    """Processes content intelligently to avoid literal escapes and syntax errors"""

    @staticmethod
    def smart_content_processing(content: str, operation_type: str) -> str:
        """Process content avoiding literal escape of special characters"""
        if not content:
            return content

        processed = content

        if operation_type in ["create", "after", "before", "append"]:
            # Fix double escapes that become problematic
            processed = processed.replace("\\\\n", "\n")
            processed = processed.replace("\\\\t", "\t")

            # Handle proper unicode escapes
            if "\\n" in processed:
                processed = re.sub(r"(?<!\\)\\n", "\n", processed)
            if "\\t" in processed:
                processed = re.sub(r"(?<!\\)\\t", "\t", processed)

        return processed
