"""
Tests para Functions TypeScript
===============================
Verificación completa de functions TypeScript especializadas
"""

import pytest
import tempfile
import os
from functions.typescript.syntax_validator import TypeScriptSyntaxValidator
from functions.typescript.interface_manager import InterfaceManager
from functions.typescript.import_resolver import ImportResolver

class TestTypeScriptSyntaxValidator:
    """Tests para TypeScriptSyntaxValidator"""
    
    def setup_method(self):
        self.validator = TypeScriptSyntaxValidator()
        
    def test_validate_interface_syntax(self):
        """Test validación de interfaces"""
        valid_interface = '''
        interface User {
            name: string;
            age: number;
            active?: boolean;
        }
        '''
        result = self.validator.validate_typescript_syntax(valid_interface)
        assert result['valid'] == True
        assert 'interfaces' in result['typescript_features']
        
    def test_validate_type_alias_syntax(self):
        """Test validación de type aliases"""
        valid_types = "type Status = 'active' | 'inactive';"
        result = self.validator.validate_typescript_syntax(valid_types)
        assert result['valid'] == True
        assert 'type_aliases' in result['typescript_features']
        
    def test_validate_type_annotations(self):
        """Test validación de anotaciones de tipo"""
        valid_annotations = "const user: User = { name: 'John', age: 30 };"
        result = self.validator.validate_typescript_syntax(valid_annotations)
        assert result['valid'] == True
        assert 'type_annotations' in result['typescript_features']

class TestInterfaceManager:
    """Tests para InterfaceManager"""
    
    def setup_method(self):
        self.manager = InterfaceManager()
        
    def test_create_interface(self):
        """Test creación de interface"""
        properties = {
            'name': 'string',
            'age': 'number',
            'active': 'boolean'
        }
        interface = self.manager.create_interface('User', properties)
        
        assert 'interface User {' in interface
        assert 'name: string;' in interface
        assert 'age: number;' in interface
        assert 'active: boolean;' in interface
        
    def test_create_interface_invalid_name(self):
        """Test creación con nombre inválido"""
        with pytest.raises(ValueError):
            self.manager.create_interface('user', {'name': 'string'})  # lowercase
            
    def test_add_property_to_interface(self):
        """Test agregar propiedad a interface"""
        interface_code = '''interface User {
  name: string;
}'''
        
        updated = self.manager.add_property_to_interface(
            interface_code, 'age', 'number'
        )
        
        assert 'age: number;' in updated
        assert 'name: string;' in updated
        
    def test_add_optional_property(self):
        """Test agregar propiedad opcional"""
        interface_code = '''interface User {
  name: string;
}'''
        
        updated = self.manager.add_property_to_interface(
            interface_code, 'email', 'string', optional=True
        )
        
        assert 'email?: string;' in updated
        
    def test_extract_interfaces(self):
        """Test extraer interfaces del código"""
        code = '''
        interface User {
            name: string;
            age: number;
        }
        
        interface Product {
            id: number;
            title: string;
        }
        '''
        
        interfaces = self.manager.extract_interfaces(code)
        assert len(interfaces) == 2
        assert interfaces[0]['name'] == 'User'
        assert interfaces[1]['name'] == 'Product'

class TestImportResolver:
    """Tests para ImportResolver"""
    
    def setup_method(self):
        self.resolver = ImportResolver()
        
    def test_default_aliases(self):
        """Test alias por defecto"""
        aliases = self.resolver.get_available_aliases()
        assert '@' in aliases
        assert '@components' in aliases
        
    def test_resolve_import_path(self):
        """Test resolución de imports con alias"""
        import_statement = "import Button from '@/components/Button';"
        resolved = self.resolver.resolve_import_path(import_statement)
        
        assert './src/components/Button' in resolved
        
    def test_add_import_if_missing(self):
        """Test agregar import si no existe"""
        content = '''const App = () => {
  return <div>Hello</div>;
};'''
        
        updated = self.resolver.add_import_if_missing(
            content, 
            "import React from 'react';"
        )
        
        assert "import React from 'react';" in updated
        
    def test_import_already_exists(self):
        """Test no duplicar imports existentes"""
        content = '''import React from 'react';
        
const App = () => {
  return <div>Hello</div>;
};'''
        
        updated = self.resolver.add_import_if_missing(
            content,
            "import React from 'react';"
        )
        
        # No debe duplicar el import
        import_count = updated.count("import React from 'react';")
        assert import_count == 1
        
    def test_organize_imports(self):
        """Test organización de imports"""
        content = '''import { Component } from './Component';
import React from 'react';
import Button from '@/components/Button';
import axios from 'axios';

const App = () => {};'''
        
        organized = self.resolver.organize_imports(content)
        lines = organized.split('\n')
        
        # Libraries primero
        react_line = next(i for i, line in enumerate(lines) if 'react' in line)
        axios_line = next(i for i, line in enumerate(lines) if 'axios' in line)
        
        # Alias después
        button_line = next(i for i, line in enumerate(lines) if '@/components' in line)
        
        # Relative al final
        component_line = next(i for i, line in enumerate(lines) if './Component' in line)
        
        assert react_line < button_line < component_line
        
    def test_create_import_statements(self):
        """Test creación de import statements"""
        default_import = self.resolver.create_import_statement('React', 'react', 'default')
        assert default_import == "import React from 'react';"
        
        named_import = self.resolver.create_import_statement('useState', 'react', 'named')
        assert named_import == "import { useState } from 'react';"
        
        namespace_import = self.resolver.create_import_statement('API', './api', 'namespace')
        assert namespace_import == "import * as API from './api';"

# Tests de integración
class TestTypeScriptFunctionsIntegration:
    """Tests de integración entre functions TypeScript"""
    
    def test_validator_with_interface_manager(self):
        """Test validador con gestor de interfaces"""
        manager = InterfaceManager()
        validator = TypeScriptSyntaxValidator()
        
        # Crear interface
        interface = manager.create_interface('User', {
            'name': 'string',
            'age': 'number'
        })
        
        # Validar interface creada
        result = validator.validate_typescript_syntax(interface)
        assert result['valid'] == True
        assert 'interfaces' in result['typescript_features']
        
    def test_import_resolver_with_validator(self):
        """Test resolver de imports con validador"""
        resolver = ImportResolver()
        validator = TypeScriptSyntaxValidator()
        
        content = "const user: User = { name: 'John' };"
        
        # Agregar import
        with_import = resolver.add_import_if_missing(
            content,
            "import { User } from '@/types/User';"
        )
        
        # Validar resultado
        result = validator.validate_typescript_syntax(with_import)
        assert result['valid'] == True
        assert 'imports' in result['typescript_features']
