import os
from pathlib import Path
from typing import Dict, Optional, Any, Union
from datetime import datetime
import logging
from string import Template

class TemplateGenerator:
    """
    Generador de templates por tipo de archivo.
    Usa string.Template para evitar conflictos con llaves JavaScript.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._templates = self._initialize_templates()
        
    def _initialize_templates(self) -> Dict[str, str]:
        """Inicializar templates básicos usando $variable syntax"""
        return {
            'python': '''#!/usr/bin/env python3
"""
$description

Created: $timestamp
"""

def main():
    """Main function"""
    pass

if __name__ == "__main__":
    main()
''',
            'js': '''/**
 * $description
 * 
 * Created: $timestamp
 */

function main() {
    // Implementation here
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { main };
}
''',
            'jsx': '''import React from 'react';

/**
 * $description
 * 
 * Created: $timestamp
 */
const $component_name = () => {
    return (
        <div>
            <h1>$component_name Component</h1>
        </div>
    );
};

export default $component_name;
''',
            'react-form': '''// ~/MeStore/frontend/src/components/$component_name.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - $component_name Component
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: $component_name.tsx
// Ruta: ~/MeStore/frontend/src/components/$component_name.tsx
// Autor: Jairo
// Fecha de Creación: $timestamp
// Última Actualización: $timestamp
// Versión: 1.0.0
// Propósito: $description
//
// ---------------------------------------------------------------------------------------------
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

interface ${component_name}Props {
  mode: 'create' | 'edit';
  initialData?: any;
  onSubmit?: (data: any) => void;
  onCancel?: () => void;
  onSuccess?: () => void;
}

interface MessageState {
  text: string;
  type: 'success' | 'error' | 'info';
}

interface FormData {
  name: string;
  description: string;
  // Add more fields as needed
}

const validationSchema = yup.object({
  name: yup.string().required('Name is required'),
  description: yup.string().required('Description is required'),
});

const $component_name: React.FC<${component_name}Props> = ({
  mode,
  initialData,
  onSubmit,
  onCancel,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<MessageState | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset,
  } = useForm<FormData>({
    resolver: yupResolver(validationSchema),
    defaultValues: initialData || {
      name: '',
      description: '',
    },
  });

  const handleFormSubmit = async (data: FormData) => {
    setLoading(true);
    setMessage(null);

    try {
      // Handle form submission
      if (onSubmit) {
        await onSubmit(data);
      }

      setMessage({
        text: mode === 'create' ? 'Created successfully!' : 'Updated successfully!',
        type: 'success',
      });

      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      setMessage({
        text: 'An error occurred. Please try again.',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        {mode === 'create' ? 'Create' : 'Edit'} $component_name
      </h2>

      {message && (
        <div className={`mb-4 p-3 rounded-md ${
          message.type === 'success'
            ? 'bg-green-100 text-green-700 border border-green-300'
            : message.type === 'error'
            ? 'bg-red-100 text-red-700 border border-red-300'
            : 'bg-blue-100 text-blue-700 border border-blue-300'
        }`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Name
          </label>
          <input
            type="text"
            id="name"
            {...register('name')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.name.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Description
          </label>
          <textarea
            id="description"
            {...register('description')}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.description.message}</p>
          )}
        </div>

        <div className="flex space-x-3 pt-4">
          <button
            type="submit"
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Saving...' : mode === 'create' ? 'Create' : 'Update'}
          </button>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default $component_name;
''',
            'react-layout': '''// ~/MeStore/frontend/src/components/$component_name.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - $component_name Component
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: $component_name.tsx
// Ruta: ~/MeStore/frontend/src/components/$component_name.tsx
// Autor: Jairo
// Fecha de Creación: $timestamp
// Última Actualización: $timestamp
// Versión: 1.0.0
// Propósito: $description
//
// ---------------------------------------------------------------------------------------------
import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface ${component_name}Props {
  children: React.ReactNode;
}

const $component_name: React.FC<${component_name}Props> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const navigationItems = [
    { name: 'Dashboard', href: '/dashboard' },
    { name: 'Settings', href: '/settings' },
    { name: 'Profile', href: '/profile' },
    { name: 'Reports', href: '/reports' },
  ];

  const NavigationItems = ({ onItemClick }: { onItemClick?: () => void }) => (
    <nav className="space-y-1">
      {navigationItems.map(item => {
        const isActive = location.pathname === item.href;
        return (
          <button
            key={item.name}
            onClick={() => {
              navigate(item.href);
              onItemClick?.();
            }}
            className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
              isActive
                ? 'bg-blue-600 text-white'
                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
            }`}
          >
            {item.name}
          </button>
        );
      })}
    </nav>
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 transform transition-transform duration-300 ease-in-out ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } md:translate-x-0`}>
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">$component_name</h1>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <NavigationItems onItemClick={() => setSidebarOpen(false)} />
          </div>
        </div>
      </div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="md:ml-64">
        <div className="sticky top-0 z-10 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between p-4">
            <button
              className="md:hidden text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h2 className="text-lg font-medium text-gray-900 dark:text-white">Content Area</h2>
          </div>
        </div>
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default $component_name;
''',
            'ts': '''/**
 * $description
 * 
 * Created: $timestamp
 */

interface MainInterface {
    // Define interface here
}

function main(): void {
    // Implementation here
}

export { main, MainInterface };
''',
            'react-modal': '''// ~/MeStore/frontend/src/components/$component_name.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - $component_name Component
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: $component_name.tsx
// Ruta: ~/MeStore/frontend/src/components/$component_name.tsx
// Autor: Jairo
// Fecha de Creación: $timestamp
// Última Actualización: $timestamp
// Versión: 1.0.0
// Propósito: $description
//
// ---------------------------------------------------------------------------------------------
import React from 'react';
import { X, Package } from 'lucide-react';

interface ${component_name}Props {
  isOpen: boolean;
  onClose: () => void;
  onActionCompleted?: () => void;
}

const $component_name: React.FC<${component_name}Props> = ({
  isOpen,
  onClose,
  onActionCompleted,
}) => {
  const handleSubmit = (data: any) => {
    console.log('Action completed:', data);
    // Handle form submission or action
  };

  const handleSuccess = () => {
    if (onActionCompleted) {
      onActionCompleted();
    }
    onClose();
  };


  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <Package className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              $component_name
            </h2>
          </div>
          <button
            onClick={onClose}
            aria-label="Cerrar modal"
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        <div className="p-6">
          {/* Add your modal content here */}
          <p className="text-gray-600 dark:text-gray-300">
            Modal content goes here
          </p>
        </div>
      </div>
    </div>
  );
};

export default $component_name;
''',
            'tsx': '''import React from 'react';

/**
 * $description
 * 
 * Created: $timestamp
 */

interface ${component_name}Props {
    // Define props here
}

const $component_name: React.FC<${component_name}Props> = () => {
    return (
        <div>
            <h1>$component_name Component</h1>
        </div>
    );
};

export default $component_name;
''',
            'html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title</title>
</head>
<body>
    <h1>$title</h1>
    <p>$description</p>
    
    <!-- Created: $timestamp -->
</body>
</html>
''',
            'css': '''/**
 * $description
 * 
 * Created: $timestamp
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
            'md': '''# $title

$description

## Overview

Add your content here.

## Usage

```bash
# Example usage
```

## License

<!-- Created: $timestamp -->
''',
            'json': '''{
    "name": "$name",
    "description": "$description",
    "version": "1.0.0",
    "created": "$timestamp"
}
''',
            'yaml': '''# $description
# Created: $timestamp

name: $name
description: $description
version: "1.0.0"
''',
            'sql': '''-- $description
-- Created: $timestamp

-- Example table creation
CREATE TABLE example (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''',
            'default': '''/**
 * $description
 * 
 * Created: $timestamp
 */

// Content goes here
'''
        }
    
    def get_template_for_extension(self, file_path: str) -> str:
        """
        Obtener template apropiado según extensión de archivo.
        """
        try:
            path_obj = Path(file_path)
            extension = path_obj.suffix.lower().lstrip('.')
            
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
        Personalizar template usando string.Template.
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
            
            # Usar string.Template para reemplazar variables
            template_obj = Template(template)
            customized = template_obj.safe_substitute(template_vars)
            
            self.logger.debug(f"Template customized with variables: {list(template_vars.keys())}")
            return customized
            
        except Exception as e:
            self.logger.error(f"Error customizing template: {e}")
            return template
    
    def generate_template(self, template_type: str, **kwargs) -> str:
        """
        Generar template específico con personalización.
        """
        try:
            if template_type in self._templates:
                base_template = self._templates[template_type]
            else:
                self.logger.warning(f"Template type '{template_type}' not found, using default")
                base_template = self._templates['default']
            
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