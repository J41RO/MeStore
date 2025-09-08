from typing import Dict, List, Any
import re
import logging

class ComponentAnalyzer:
    """Analizador especializado para componentes React"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_component_structure(self, component_code: str) -> Dict[str, Any]:
        """Analiza estructura completa del componente"""
        return {
            'name': self._extract_component_name(component_code),
            'props_interface': self._extract_props_interface(component_code),
            'hooks': self._extract_hooks(component_code),
            'jsx_structure': self._analyze_jsx_structure(component_code),
            'imports': self._extract_imports(component_code)
        }
        
    def _extract_component_name(self, component_code: str) -> str:
        """Extrae nombre del componente"""
        # Buscar patrones como: const ComponentName = () =>
        match = re.search(r'const\s+(\w+)\s*[:=]', component_code)
        if match:
            return match.group(1)
        
        # Buscar patrones como: function ComponentName()
        match = re.search(r'function\s+(\w+)\s*\(', component_code)
        if match:
            return match.group(1)
            
        return 'UnknownComponent'
        
    def _extract_props_interface(self, component_code: str) -> Dict[str, str]:
        """Extrae interface de props"""
        props_interface = {}
        
        # Buscar interface Props
        interface_match = re.search(r'interface\s+\w*Props\w*\s*\{([^}]+)\}', component_code)
        if interface_match:
            props_content = interface_match.group(1)
            prop_matches = re.finditer(r'(\w+):\s*([^;,\n]+)', props_content)
            for match in prop_matches:
                props_interface[match.group(1)] = match.group(2).strip()
                
        return props_interface
        
    def _extract_hooks(self, component_code: str) -> List[str]:
        """Extrae hooks utilizados"""
        hooks = []
        hook_pattern = r'(use\w+)\s*\('
        matches = re.finditer(hook_pattern, component_code)
        
        for match in matches:
            hooks.append(match.group(1))
            
        return list(set(hooks))  # Remove duplicates
        
    def _analyze_jsx_structure(self, component_code: str) -> Dict[str, Any]:
        """Analiza estructura JSX"""
        jsx_analysis = {
            'has_jsx': '<' in component_code and '>' in component_code,
            'element_count': component_code.count('<'),
            'has_fragments': '<>' in component_code or 'Fragment' in component_code,
            'has_conditional_rendering': '?' in component_code and ':' in component_code
        }
        return jsx_analysis
        
    def _extract_imports(self, component_code: str) -> List[str]:
        """Extrae declaraciones de import"""
        imports = []
        import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
        matches = re.finditer(import_pattern, component_code)
        
        for match in matches:
            imports.append(match.group(1))
            
        return imports
