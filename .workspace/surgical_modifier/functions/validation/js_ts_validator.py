"""
Validador de sintaxis JavaScript/TypeScript para Surgical Modifier CLI v6.0
Implementa validación sintáctica post-modificación para prevenir sintaxis malformada.
"""

import re
import json
from typing import Dict, List, Tuple, Optional

from functions.react.jsx_parser import JSXParser


class JsTsValidator:
    """
    Validador de sintaxis JavaScript/TypeScript que verifica código después de modificaciones.
    Diseñado para prevenir sintaxis malformada especialmente con React.memo y estructuras complejas.
    """
    
    def __init__(self):
        # Patrones problemáticos conocidos que el reemplazador puede generar
        self.problematic_patterns = [
            r'React\.memo\(\s*\(\s*\w+\s*\)\s*=>\s*\(\s*\w+\s*\)\s*=>', # React.memo doble arrow
            r'function\s+\w+\(\s*\w+\s*\)\s*\(\s*\w+\s*\)', # function doble paréntesis  
            r'\(\s*\w+\s*\)\s*=>\s*\(\s*\w+\s*\)\s*=>', # double arrow malformado
            r'const\s+\w+\s+=\s+\(\s*$', # const con paréntesis abierto sin cerrar
            r'import\s*{\s*\w+\s*}\s*{\s*\w+\s*}', # imports malformados
        ]
        
        # Patrones válidos de React que deben preservarse
        self.valid_react_patterns = [
            r'React\.memo\(\s*\(\s*\w+\s*\)\s*=>\s*<', # React.memo válido con JSX
            r'React\.memo\(\s*function\s+\w+', # React.memo con function
            r'React\.memo\(\s*\w+\)', # React.memo simple
        ]
    
    def validate_js_syntax(self, content: str) -> Dict[str, any]:
        """
        Valida sintaxis básica de JavaScript usando patrones conocidos.
        
        Args:
            content: Contenido JavaScript a validar
            
        Returns:
            Dict con resultado de validación: {'valid': bool, 'errors': List[str]}
        """
        errors = []
        
        # Verificar balanceado de paréntesis, llaves y corchetes
        if not self._check_balanced_brackets(content):
            errors.append("Paréntesis, llaves o corchetes desbalanceados")
        
        # Verificar patrones problemáticos conocidos
        for pattern in self.problematic_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                errors.append(f"Patrón problemático detectado: {pattern}")
        
        # Verificar que React.memo esté bien formado si está presente
        if 'React.memo' in content:
            react_errors = self._validate_react_memo_syntax(content)
            errors.extend(react_errors)
        
        # Verificar sintaxis básica de funciones
        function_errors = self._validate_function_syntax(content)
        errors.extend(function_errors)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': []
        }
    
    def validate_ts_syntax(self, content: str) -> Dict[str, any]:
        """
        Valida sintaxis específica de TypeScript extendiendo validación JS.
        
        Args:
            content: Contenido TypeScript a validar
            
        Returns:
            Dict con resultado de validación
        """
        # Primero validar como JavaScript
        result = self.validate_js_syntax(content)
        
        # Agregar validaciones específicas de TypeScript
        ts_errors = []
        
        # Verificar interfaces malformadas
        interface_pattern = r'interface\s+\w+\s*{'
        if re.search(interface_pattern, content):
            if not self._validate_interface_syntax(content):
                ts_errors.append("Sintaxis de interface TypeScript malformada")
        
        # Verificar tipos genéricos
        generic_pattern = r'<\s*\w+\s*>'
        if re.search(generic_pattern, content):
            if not self._validate_generic_syntax(content):
                ts_errors.append("Sintaxis de tipos genéricos malformada")
        
        result['errors'].extend(ts_errors)
        result['valid'] = len(result['errors']) == 0
        
        return result
    
    def validate_react_structures(self, content: str) -> Dict[str, any]:
        """
        Validación específica para estructuras React complejas.
        
        Args:
            content: Contenido React a validar
            
        Returns:
            Dict con resultado de validación
        """
        errors = []
        warnings = []
        
        # Validar React.memo específicamente
        if 'React.memo' in content:
            memo_errors = self._validate_react_memo_syntax(content)
            errors.extend(memo_errors)
        
        # Validar hooks si están presentes
        if 'useState' in content or 'useEffect' in content:
            hook_errors = self._validate_hook_syntax(content)
            errors.extend(hook_errors)
        
        # Validar JSX básico
        if '<' in content and '>' in content:
            jsx_errors = self._validate_jsx_syntax_advanced(content)
            errors.extend(jsx_errors)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def get_syntax_errors(self, content: str, file_extension: str) -> List[str]:
        """
        Obtiene lista de errores de sintaxis según el tipo de archivo.
        
        Args:
            content: Contenido del archivo
            file_extension: Extensión del archivo (.js, .jsx, .ts, .tsx)
            
        Returns:
            Lista de errores encontrados
        """
        if file_extension in ['.ts', '.tsx']:
            result = self.validate_ts_syntax(content)
        elif file_extension in ['.js', '.jsx']:
            result = self.validate_js_syntax(content)
        else:
            # Para otros tipos, validación básica
            result = {'valid': True, 'errors': []}
        
        # Si es React (.jsx o .tsx), agregar validaciones específicas
        if file_extension in ['.jsx', '.tsx']:
            react_result = self.validate_react_structures(content)
            result['errors'].extend(react_result['errors'])
        
        return result['errors']
    
    def _check_balanced_brackets(self, content: str) -> bool:
        """Verifica que paréntesis, llaves y corchetes estén balanceados."""
        stack = []
        brackets = {'(': ')', '[': ']', '{': '}'}
        
        for char in content:
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack or brackets.get(stack.pop()) != char:
                    return False
        
        return len(stack) == 0
    
    def _validate_react_memo_syntax(self, content: str) -> List[str]:
        """Valida específicamente sintaxis de React.memo."""
        errors = []
        
        # Buscar React.memo con manejo correcto de paréntesis anidados
        memo_start_pattern = r'React\.memo\s*\('
        matches = re.finditer(memo_start_pattern, content)
        
        for match in matches:
            start_pos = match.end() - 1  # Posición del paréntesis de apertura
            memo_content = self._extract_balanced_parens(content, start_pos)
            
            if memo_content is None:
                errors.append("React.memo con paréntesis desbalanceados")
                continue
            
            # Verificar patrones problemáticos específicos en el contenido completo
            full_memo = content[match.start():start_pos + len(memo_content) + 1]
            if re.search(r'React\.memo\(\s*\(\s*\w+\s*\)\s*=>\s*\(\s*\w+\s*\)\s*=>', full_memo):
                errors.append("React.memo con sintaxis de arrow function malformada")
        
        return errors


    def _validate_jsx_syntax_advanced(self, content: str) -> List[str]:
        """Valida sintaxis JSX usando parser avanzado."""
        try:
            # Usar JSXParser mejorado para validación avanzada
            jsx_parser = JSXParser()
            result = jsx_parser.validate_jsx_advanced(content)
            
            # Si hay errores específicos, usarlos
            if not result['valid']:
                return result['errors']
            
            # Si no hay errores específicos, todo está bien
            return []
            
        except Exception as e:
            # En caso de error, usar validación básica como fallback
            return [f"Error en validación JSX avanzada: {str(e)}"]

    def _extract_balanced_parens(self, content: str, start_pos: int) -> Optional[str]:
        """Extrae contenido con paréntesis balanceados desde posición inicial."""
        if start_pos >= len(content) or content[start_pos] != '(':
            return None
        
        paren_count = 0
        pos = start_pos
        
        while pos < len(content):
            char = content[pos]
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count == 0:
                    return content[start_pos + 1:pos]
            pos += 1
        
        return None  # Paréntesis no balanceados
    
    def _validate_function_syntax(self, content: str) -> List[str]:
        """Valida sintaxis básica de funciones."""
        errors = []
        
        # Verificar funciones con sintaxis problemática
        function_patterns = [
            r'function\s+\w+\(\s*\w+\s*\)\s*\(',  # function con doble paréntesis
            r'const\s+\w+\s+=\s+\([^)]*$',  # const con paréntesis sin cerrar
        ]
        
        for pattern in function_patterns:
            if re.search(pattern, content):
                errors.append("Sintaxis de función problemática detectada")
        
        return errors
    
    def _validate_interface_syntax(self, content: str) -> bool:
        """Valida sintaxis básica de interfaces TypeScript."""
        # Implementación básica - puede expandirse
        interface_pattern = r'interface\s+\w+\s*\{[^}]*\}'
        return bool(re.search(interface_pattern, content, re.DOTALL))
    
    def _validate_generic_syntax(self, content: str) -> bool:
        """Valida sintaxis básica de tipos genéricos."""
        # Verificar que los < > estén balanceados
        open_brackets = content.count('<')
        close_brackets = content.count('>')
        
        # Permitir casos válidos como React.FC<Props>, Array<string>, etc.
        if open_brackets == close_brackets:
            return True
        
        # Si hay desbalance, verificar que no sea dentro de JSX válido
        # JSX también usa < > pero en contexto diferente
        import re
        jsx_pattern = r'<\s*\w+[^>]*>'
        jsx_matches = len(re.findall(jsx_pattern, content))
        
        # Si la diferencia se explica por JSX, considerarlo válido
        return abs(open_brackets - close_brackets) <= jsx_matches
    
    def _validate_hook_syntax(self, content: str) -> List[str]:
        """Valida sintaxis básica de React hooks."""
        errors = []
        
        # Verificar useState básico
        if 'useState' in content:
            if not re.search(r'useState\s*\([^)]*\)', content):
                errors.append("Sintaxis de useState malformada")
        
        return errors
    
    def _validate_jsx_syntax(self, content: str) -> List[str]:
        """Valida sintaxis básica de JSX."""
        errors = []
        
        # Verificar que los tags JSX estén balanceados básicamente
        open_tags = len(re.findall(r'<\w+[^>]*>', content))
        close_tags = len(re.findall(r'</\w+>', content))
        self_closing = len(re.findall(r'<\w+[^>]*/>', content))
        
        # Verificación básica: tags abiertos deben coincidir con cerrados + self-closing
        if open_tags != close_tags + self_closing:
            errors.append("Tags JSX potencialmente desbalanceados")
        
        return errors