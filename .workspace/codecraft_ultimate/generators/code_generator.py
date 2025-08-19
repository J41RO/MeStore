"""
🚀 CodeCraft Ultimate v6.0 - Generador de Código
"""

import os
from typing import Dict, List, Any
from ..core.exceptions import GenerationError


class CodeGenerator:
    """Generador de código fuente"""
    
    def __init__(self):
        self.templates = {
            'python': {
                'class': self._generate_python_class,
                'function': self._generate_python_function,
                'module': self._generate_python_module,
                'fastapi_route': self._generate_fastapi_route,
                'pydantic_model': self._generate_pydantic_model
            },
            'javascript': {
                'class': self._generate_js_class,
                'function': self._generate_js_function,
                'react_component': self._generate_react_component,
                'express_route': self._generate_express_route,
                'vue_component': self._generate_vue_component
            },
            'typescript': {
                'interface': self._generate_ts_interface,
                'type': self._generate_ts_type,
                'class': self._generate_ts_class,
                'react_component': self._generate_react_ts_component
            }
        }
    
    def generate_code(self, language: str, code_type: str, name: str, **options) -> Dict[str, Any]:
        """Generar código específico"""
        
        if language not in self.templates:
            raise GenerationError(f"Unsupported language: {language}")
        
        if code_type not in self.templates[language]:
            raise GenerationError(f"Unsupported code type '{code_type}' for {language}")
        
        try:
            generator = self.templates[language][code_type]
            code = generator(name, **options)
            
            file_extension = self._get_file_extension(language, code_type)
            suggested_filename = f"{name}{file_extension}"
            
            return {
                'success': True,
                'language': language,
                'code_type': code_type,
                'name': name,
                'code': code,
                'suggested_filename': suggested_filename,
                'options_used': options
            }
            
        except Exception as e:
            raise GenerationError(f"Code generation failed: {e}")
    
    def _generate_python_class(self, name: str, **options) -> str:
        """Generar clase Python"""
        
        base_class = options.get('base_class', '')
        methods = options.get('methods', ['__init__'])
        docstring = options.get('docstring', f'Class {name}')
        
        base_part = f"({base_class})" if base_class else ""
        
        code = f'''class {name}{base_part}:
    """{docstring}"""
    
    def __init__(self):
        """Initialize {name}"""
        pass
'''
        
        for method in methods:
            if method != '__init__':
                code += f'''
    def {method}(self):
        """Method {method}"""
        pass
'''
        
        return code
    
    def _generate_python_function(self, name: str, **options) -> str:
        """Generar función Python"""
        
        parameters = options.get('parameters', [])
        return_type = options.get('return_type', 'None')
        docstring = options.get('docstring', f'Function {name}')
        
        param_str = ', '.join(parameters) if parameters else ''
        
        code = f'''def {name}({param_str}) -> {return_type}:
    """{docstring}"""
    pass
'''
        
        return code
    
    def _generate_python_module(self, name: str, **options) -> str:
        """Generar módulo Python"""
        
        imports = options.get('imports', [])
        classes = options.get('classes', [])
        functions = options.get('functions', [])
        
        code = f'''"""
{name} module
"""

'''
        
        # Agregar imports
        for imp in imports:
            code += f"import {imp}\n"
        
        if imports:
            code += "\n"
        
        # Agregar classes
        for cls in classes:
            code += self._generate_python_class(cls) + "\n\n"
        
        # Agregar functions
        for func in functions:
            code += self._generate_python_function(func) + "\n\n"
        
        return code
    
    def _generate_fastapi_route(self, name: str, **options) -> str:
        """Generar ruta FastAPI"""
        
        method = options.get('method', 'GET').lower()
        path = options.get('path', f'/{name}')
        response_model = options.get('response_model', 'dict')
        
        code = f'''from fastapi import APIRouter

router = APIRouter()

@router.{method}("{path}")
async def {name}():
    """Route {name}"""
    return {{"message": "Hello from {name}"}}
'''
        
        return code
    
    def _generate_pydantic_model(self, name: str, **options) -> str:
        """Generar modelo Pydantic"""
        
        fields = options.get('fields', [{'name': 'id', 'type': 'int'}])
        
        code = f'''from pydantic import BaseModel

class {name}(BaseModel):
    """Pydantic model {name}"""
'''
        
        for field in fields:
            field_name = field.get('name', 'field')
            field_type = field.get('type', 'str')
            code += f"    {field_name}: {field_type}\n"
        
        return code
    
    def _generate_js_class(self, name: str, **options) -> str:
        """Generar clase JavaScript"""
        
        methods = options.get('methods', ['constructor'])
        
        code = f'''class {name} {{
    constructor() {{
        // Initialize {name}
    }}
'''
        
        for method in methods:
            if method != 'constructor':
                code += f'''
    {method}() {{
        // Method {method}
    }}
'''
        
        code += "}\n"
        
        return code
    
    def _generate_js_function(self, name: str, **options) -> str:
        """Generar función JavaScript"""
        
        parameters = options.get('parameters', [])
        arrow_function = options.get('arrow_function', True)
        
        param_str = ', '.join(parameters) if parameters else ''
        
        if arrow_function:
            code = f'''const {name} = ({param_str}) => {{
    // Function {name}
}};
'''
        else:
            code = f'''function {name}({param_str}) {{
    // Function {name}
}}
'''
        
        return code
    
    def _generate_react_component(self, name: str, **options) -> str:
        """Generar componente React"""
        
        functional = options.get('functional', True)
        props = options.get('props', [])
        
        if functional:
            props_str = '{' + ', '.join(props) + '}' if props else ''
            
            code = f'''import React from 'react';

const {name} = ({props_str}) => {{
    return (
        <div className="{name.lower()}">
            <h2>{name}</h2>
            {{/* Component content */}}
        </div>
    );
}};

export default {name};
'''
        else:
            code = f'''import React, {{ Component }} from 'react';

class {name} extends Component {{
    render() {{
        return (
            <div className="{name.lower()}">
                <h2>{name}</h2>
                {{/* Component content */}}
            </div>
        );
    }}
}}

export default {name};
'''
        
        return code
    
    def _generate_vue_component(self, name: str, **options) -> str:
        """Generar componente Vue"""
        
        props = options.get('props', [])
        
        props_section = ''
        if props:
            props_list = ', '.join(f"'{prop}'" for prop in props)
            props_section = f"  props: [{props_list}],"
        
        code = f'''<template>
  <div class="{name.lower()}">
    <h2>{name}</h2>
    <!-- Component content -->
  </div>
</template>

<script>
export default {{
  name: '{name}',{props_section}
  data() {{
    return {{
      // Component data
    }};
  }},
  methods: {{
    // Component methods
  }}
}};
</script>

<style scoped>
.{name.lower()} {{
  /* Component styles */
}}
</style>
'''
        
        return code
    
    def _generate_ts_interface(self, name: str, **options) -> str:
        """Generar interfaz TypeScript"""
        
        properties = options.get('properties', [])
        
        code = f'''interface {name} {{
'''
        
        for prop in properties:
            prop_name = prop.get('name', 'property')
            prop_type = prop.get('type', 'string')
            optional = '?' if prop.get('optional', False) else ''
            code += f"  {prop_name}{optional}: {prop_type};\n"
        
        code += "}\n"
        
        return code
    
    def _generate_ts_type(self, name: str, **options) -> str:
        """Generar tipo TypeScript"""
        
        union_types = options.get('union_types', ['string'])
        
        union_str = ' | '.join(union_types)
        
        code = f'''type {name} = {union_str};
'''
        
        return code
    
    def _generate_ts_class(self, name: str, **options) -> str:
        """Generar clase TypeScript"""
        
        properties = options.get('properties', [])
        methods = options.get('methods', [])
        
        code = f'''class {name} {{
'''
        
        # Propiedades
        for prop in properties:
            prop_name = prop.get('name', 'property')
            prop_type = prop.get('type', 'string')
            visibility = prop.get('visibility', 'public')
            code += f"  {visibility} {prop_name}: {prop_type};\n"
        
        # Constructor
        code += f'''
  constructor() {{
    // Initialize {name}
  }}
'''
        
        # Métodos
        for method in methods:
            method_name = method.get('name', 'method')
            return_type = method.get('return_type', 'void')
            visibility = method.get('visibility', 'public')
            
            code += f'''
  {visibility} {method_name}(): {return_type} {{
    // Method {method_name}
  }}
'''
        
        code += "}\n"
        
        return code
    
    def _generate_react_ts_component(self, name: str, **options) -> str:
        """Generar componente React TypeScript"""
        
        props = options.get('props', [])
        
        # Generar interface para props
        props_interface = ''
        if props:
            props_interface = f'''interface {name}Props {{
'''
            for prop in props:
                prop_name = prop.get('name', 'prop')
                prop_type = prop.get('type', 'string')
                optional = '?' if prop.get('optional', False) else ''
                props_interface += f"  {prop_name}{optional}: {prop_type};\n"
            
            props_interface += "}\n\n"
        
        props_param = f"props: {name}Props" if props else ""
        
        code = f'''import React from 'react';

{props_interface}const {name}: React.FC<{name + 'Props' if props else ''}> = ({props_param}) => {{
  return (
    <div className="{name.lower()}">
      <h2>{name}</h2>
      {{/* Component content */}}
    </div>
  );
}};

export default {name};
'''
        
        return code
    
    def _get_file_extension(self, language: str, code_type: str) -> str:
        """Obtener extensión de archivo apropiada"""
        
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts'
        }
        
        # Casos especiales
        if language == 'javascript' and 'react' in code_type:
            return '.jsx'
        elif language == 'typescript' and 'react' in code_type:
            return '.tsx'
        elif language == 'javascript' and 'vue' in code_type:
            return '.vue'
        
        return extensions.get(language, '.txt')