# Syntax Validators - Sistema de validación sintáctica
def validate_python_syntax():
    pass

def validate_javascript_syntax():
    pass

def validate_python_syntax(content: str) -> bool:
    """Validar sintaxis Python"""
    try:
        compile(content, chr(60) + chr(115) + chr(116) + chr(114) + chr(105) + chr(110) + chr(103) + chr(62), chr(101) + chr(120) + chr(101) + chr(99))
        return True
    except SyntaxError as e:
        from ..operations.base_operation import ContentError
        raise ContentError(f"Invalid Python syntax after insertion: {e}")

def validate_javascript_syntax(content: str) -> bool:
    """Validación básica JavaScript"""
    stack = []
    pairs = {chr(40): chr(41), chr(91): chr(93), chr(123): chr(125)}
    for char in content:
        if char in pairs:
            stack.append(pairs[char])
        elif char in pairs.values():
            if not stack or stack.pop() != char:
                from ..operations.base_operation import ContentError
                raise ContentError(chr(85) + chr(110) + chr(98) + chr(97) + chr(108) + chr(97) + chr(110) + chr(99) + chr(101) + chr(100) + chr(32) + chr(98) + chr(114) + chr(97) + chr(99) + chr(107) + chr(101) + chr(116) + chr(115))
    return True
