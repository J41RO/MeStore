#!/usr/bin/env python3
"""
Syntax validation functions for different file types
Extracted from replace.py for modular architecture
"""
# ContentError will be imported from operations module when needed


def validate_python_syntax(content: str) -> bool:
    """Validar sintaxis Python"""
    try:
        compile(content, '<string>', 'exec')
        return True
    except SyntaxError as e:
        # Import ContentError locally to avoid circular imports
        from ...operations.base_operation import ContentError
        raise ContentError(f"Invalid Python syntax after replace: {e}")


def validate_javascript_syntax(content: str) -> bool:
    """Validación básica JavaScript - balanceado de llaves"""
    stack = []
    pairs = {'(': ')', '[': ']', '{': '}'}
    for char in content:
        if char in pairs:
            stack.append(pairs[char])
        elif char in pairs.values():
            if not stack or stack.pop() != char:
                # Import ContentError locally to avoid circular imports
                from ...operations.base_operation import ContentError
                raise ContentError(f"Unbalanced brackets in JavaScript after replace")
    return True