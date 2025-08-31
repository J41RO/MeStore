import os
from pathlib import Path
from typing import Dict, Optional, Any, Union
from datetime import datetime
import logging

class TemplateGenerator:
    """
    Generador de templates por tipo de archivo.
    Sigue arquitectura modular functions/ del proyecto.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._templates = self._initialize_templates()
        
    def _initialize_templates(self) -> Dict[str, str]:
        """Inicializar templates básicos por extensión"""
        return {
            'python': '''#!/usr/bin/env python3
"""
{description}

Created: {timestamp}
"""

def main():
    """Main function"""
    pass

if __name__ == "__main__":
    main()
''',
            'js': '''/**
 * {description}
 * 
 * Created: {timestamp}
 */

function main() {
    // Implementation here
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {{ main }};
}
''',
            'jsx': '''import React from 'react';

/**
 * {description}
 * 
 * Created: {timestamp}
 */
const {component_name} = () => {
    return (
        <div>
            <h1>{component_name} Component</h1>
        </div>
    );
};

export default {component_name};
''',
            'ts': '''/**
 * {description}
 * 
 * Created: {timestamp}
 */

interface MainInterface {
    // Define interface here
}

function main(): void {
    // Implementation here
}

export {{ main, MainInterface }};
''',
            'tsx': '''import React from 'react';

/**
 * {description}
 * 
 * Created: {timestamp}
 */

interface {component_name}Props {
    // Define props here
}

const {component_name}: React.FC<{component_name}Props> = () => {
    return (
        <div>
            <h1>{component_name} Component</h1>
        </div>
    );
};

export default {component_name};
''',
            'html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    <p>{description}</p>
    
    <!-- Created: {timestamp} -->
</body>
</html>
''',
            'css': '''/**
 * {description}
 * 
 * Created: {timestamp}
 */

/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: system-ui, -apple-system, sans-serif;
    line-height: 1.6;
    color: #333;
}
''',
            'md': '''# {title}

{description}

## Overview

Add your content here.

## Usage

```bash
# Example usage
```

## License

<!-- Created: {timestamp} -->
''',
            'json': '''{
    "name": "{name}",
    "description": "{description}",
    "version": "1.0.0",
    "created": "{timestamp}"
}
''',
            'yaml': '''# {description}
# Created: {timestamp}

name: {name}
description: {description}
version: "1.0.0"
''',
            'sql': '''-- {description}
-- Created: {timestamp}

-- Example table creation
CREATE TABLE example (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''',
            'default': '''/**
 * {description}
 * 
 * Created: {timestamp}
 */

// Content goes here
'''
        }
    
    def get_template_for_extension(self, file_path: str) -> str:
        """
        Obtener template apropiado según extensión de archivo.
        
        Args:
            file_path: Ruta del archivo para determinar extensión
            
        Returns:
            Template string apropiado
        """
        try:
            path_obj = Path(file_path)
            extension = path_obj.suffix.lower().lstrip('.')
            
            # Mapeo de extensiones a tipos de template
            extension_mapping = {
                'py': 'python',
                'js': 'js',
                'jsx': 'jsx', 
                'ts': 'ts',
                'tsx': 'tsx',
                'html': 'html',
                'htm': 'html',
                'css': 'css',
                'md': 'md',
                'markdown': 'md',
                'json': 'json',
                'yml': 'yaml',
                'yaml': 'yaml',
                'sql': 'sql',
            }
            
            template_type = extension_mapping.get(extension, 'default')
            template = self._templates.get(template_type, self._templates['default'])
            
            self.logger.debug(f"Selected template '{template_type}' for extension '{extension}'")
            return template
            
        except Exception as e:
            self.logger.error(f"Error getting template for {file_path}: {e}")
            return self._templates['default']
    
    def customize_template(self, template: str, **kwargs) -> str:
        """
        Personalizar template con variables específicas.
        
        Args:
            template: Template string base
            **kwargs: Variables para reemplazar en template
            
        Returns:
            Template personalizado
        """
        try:
            # Variables por defecto
            default_vars = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'description': 'Auto-generated file',
                'title': 'Untitled',
                'name': 'untitled',
                'component_name': 'Component'
            }
            
            # Combinar variables por defecto con las proporcionadas
            template_vars = {**default_vars, **kwargs}
            
            # Generar component_name inteligentemente si no se proporciona
            if 'component_name' not in kwargs and 'file_path' in kwargs:
                path_obj = Path(kwargs['file_path'])
                component_name = path_obj.stem
                # Capitalizar primera letra para componentes React
                component_name = component_name.replace('_', ' ').replace('-', ' ').title().replace(' ', '')
                template_vars['component_name'] = component_name
            
            # Reemplazar variables en template
            customized = template.format(**template_vars)
            
            self.logger.debug(f"Template customized with variables: {list(template_vars.keys())}")
            return customized
            
        except Exception as e:
            self.logger.error(f"Error customizing template: {e}")
            # Retornar template original si falla personalización
            return template
    
    def generate_template(self, template_type: str, **kwargs) -> str:
        """
        Generar template específico con personalización.
        
        Args:
            template_type: Tipo de template ('python', 'js', etc.)
            **kwargs: Variables para personalizar
            
        Returns:
            Template generado y personalizado
        """
        try:
            # Obtener template base
            if template_type in self._templates:
                base_template = self._templates[template_type]
            else:
                self.logger.warning(f"Template type '{template_type}' not found, using default")
                base_template = self._templates['default']
            
            # Personalizar template
            generated = self.customize_template(base_template, **kwargs)
            
            self.logger.info(f"Generated template of type '{template_type}'")
            return generated
            
        except Exception as e:
            self.logger.error(f"Error generating template '{template_type}': {e}")
            return self._templates['default']
    
    def get_available_templates(self) -> list:
        """Obtener lista de templates disponibles"""
        return list(self._templates.keys())
    
    def add_custom_template(self, template_type: str, template_content: str) -> bool:
        """
        Agregar template personalizado.
        
        Args:
            template_type: Nombre del tipo de template
            template_content: Contenido del template
            
        Returns:
            True si se agregó exitosamente
        """
        try:
            self._templates[template_type] = template_content
            self.logger.info(f"Added custom template: {template_type}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding custom template: {e}")
            return False


# Funciones de conveniencia para compatibilidad
def generate_template(template_type: str, **kwargs) -> str:
    """Función de conveniencia para generar template"""
    generator = TemplateGenerator()
    return generator.generate_template(template_type, **kwargs)

def get_template_for_extension(file_path: str) -> str:
    """Función de conveniencia para obtener template por extensión"""
    generator = TemplateGenerator()
    return generator.get_template_for_extension(file_path)

def customize_template(template: str, **kwargs) -> str:
    """Función de conveniencia para personalizar template"""
    generator = TemplateGenerator()
    return generator.customize_template(template, **kwargs)