from typing import Dict, List, Any, Optional
import re
import logging

class PropsManager:
    """Gestor especializado para props y interfaces React"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def add_prop_to_interface(self, component_code: str, prop_name: str, prop_type: str, optional: bool = False) -> str:
        """Agrega prop a interface Props y al destructuring"""
        prop_declaration = f"  {prop_name}{'?' if optional else ''}: {prop_type};"
        
        # Buscar interface Props existente
        interface_match = re.search(r'(interface\s+\w*Props\w*\s*\{)([^}]+)(\})', component_code)
        if interface_match:
            # Agregar a interface existente
            updated_interface = interface_match.group(1) + interface_match.group(2) + '\n' + prop_declaration + '\n' + interface_match.group(3)
            component_code = component_code.replace(interface_match.group(0), updated_interface)
        else:
            # Crear nueva interface
            component_name = self._extract_component_name(component_code)
            new_interface = f"interface {component_name}Props {{\n{prop_declaration}\n}}\n\n"
            component_code = new_interface + component_code
            
        return self._update_destructuring(component_code, prop_name)
        
    def _update_destructuring(self, component_code: str, prop_name: str) -> str:
        """Actualiza destructuring de props para incluir nueva prop"""
        # Buscar patrón de destructuring como: ({existingProp, ...}) =>
        destructure_match = re.search(r'(\{\s*)([^}]+)(\s*\})', component_code)
        if destructure_match:
            existing_props = destructure_match.group(2).strip()
            if existing_props and not existing_props.endswith(','):
                existing_props += ', '
            updated_destructuring = destructure_match.group(1) + existing_props + prop_name + destructure_match.group(3)
            component_code = component_code.replace(destructure_match.group(0), updated_destructuring)
            
        return component_code
        
    def _extract_component_name(self, component_code: str) -> str:
        """Extrae nombre del componente para generar interface Props"""
        match = re.search(r'const\s+(\w+)\s*[:=]', component_code)
        if match:
            return match.group(1)
        
        match = re.search(r'function\s+(\w+)\s*\(', component_code)
        if match:
            return match.group(1)
            
        return 'Component'
        
    def update_prop_type(self, component_code: str, prop_name: str, new_type: str) -> str:
        """Actualiza tipo de prop existente"""
        prop_pattern = rf'(\s+{prop_name}\??\s*:\s*)([^;,\n]+)'
        replacement = rf'\g<1>{new_type}'
        return re.sub(prop_pattern, replacement, component_code)
        
    def add_prop_to_component_usage(self, jsx_code: str, component_name: str, prop_name: str, prop_value: str) -> str:
        """Agrega prop al uso del componente en JSX"""
        component_pattern = rf'(<{component_name}[^>]*?)(/?>)'
        
        def add_prop(match):
            existing_props = match.group(1)
            closing = match.group(2)
            if not existing_props.strip().endswith(' '):
                existing_props += ' '
            return f"{existing_props}{prop_name}={prop_value}{closing}"
            
        return re.sub(component_pattern, add_prop, jsx_code)
