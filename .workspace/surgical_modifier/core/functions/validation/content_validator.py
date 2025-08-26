#!/usr/bin/env python3
"""
Content validation functions
Extracted from create.py for modular architecture
"""



def validate_file_content(content: str, file_type: str) -> bool:
    """Validate that content is valid for file type"""
    try:
        if file_type == '.py':
            # Basic Python syntax validation
            compile(content, '<string>', 'exec')
            return True
        elif file_type in ['.js', '.ts']:
            # Basic JavaScript validation (check for obvious syntax errors)
            if content.count('(') != content.count(')'):
                return False
            if content.count('{') != content.count('}'):
                return False
            return True
        # For other file types, assume valid
        return True
    except:
        return False