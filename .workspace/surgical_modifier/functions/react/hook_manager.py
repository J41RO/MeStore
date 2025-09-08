from typing import Dict, List, Any, Optional
import re
import logging

class HookManager:
    """Gestor especializado para hooks React"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.common_hooks = ['useState', 'useEffect', 'useContext', 'useReducer', 'useCallback', 'useMemo']
        
    def detect_existing_hooks(self, component_code: str) -> List[str]:
        """Detecta hooks existentes en componente"""
        detected_hooks = []
        for hook in self.common_hooks:
            if hook in component_code:
                detected_hooks.append(hook)
        return detected_hooks
        
    def add_use_state(self, component_code: str, state_name: str, state_type: str = 'any', initial_value: str = 'null') -> str:
        """Agrega useState en posición correcta del componente"""
        hook_line = f'  const [{state_name}, set{state_name.capitalize()}] = useState<{state_type}>({initial_value});'
        
        lines = component_code.split('\n')
        insert_position = self._find_hook_insertion_point(lines)
        
        lines.insert(insert_position, hook_line)
        return '\n'.join(lines)
        
    def add_use_effect(self, component_code: str, effect_code: str, dependencies: Optional[List[str]] = None) -> str:
        """Agrega useEffect con dependencias correctas"""
        deps = '[]' if dependencies is None else f'[{", ".join(dependencies)}]'
        effect_block = f'  useEffect(() => {{\n    {effect_code}\n  }}, {deps});'
        
        lines = component_code.split('\n')
        insert_position = self._find_hook_insertion_point(lines)
        
        lines.insert(insert_position, effect_block)
        return '\n'.join(lines)
        
    def _find_hook_insertion_point(self, lines: List[str]) -> int:
        """Encuentra mejor punto para insertar hooks"""
        for i, line in enumerate(lines):
            if 'return' in line and ('<' in line or '(' in line):
                return i
        return len(lines) - 1
