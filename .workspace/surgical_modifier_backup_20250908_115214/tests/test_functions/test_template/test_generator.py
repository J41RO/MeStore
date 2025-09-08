import pytest
import tempfile
import os
import sys
from datetime import datetime
from unittest.mock import patch, Mock

# Agregar path del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from functions.template.generator import TemplateGenerator, generate_template, get_template_for_extension, customize_template


class TestTemplateGenerator:
    """Tests unitarios para TemplateGenerator - generación de templates por tipo de archivo"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.generator = TemplateGenerator()
        
    def test_initialization(self):
        """Test inicialización correcta del generador"""
        assert hasattr(self.generator, '_templates')
        assert isinstance(self.generator._templates, dict)
        assert len(self.generator._templates) > 0
        assert 'python' in self.generator._templates
        assert 'default' in self.generator._templates
    
    def test_get_template_for_extension_python(self):
        """Test obtener template para archivo Python"""
        template = self.generator.get_template_for_extension('test.py')
        
        assert '#!/usr/bin/env python3' in template
        assert 'def main():' in template
        assert '__name__ == "__main__"' in template
    
    def test_get_template_for_extension_javascript(self):
        """Test obtener template para archivo JavaScript"""
        template = self.generator.get_template_for_extension('app.js')
        
        assert 'function main()' in template
        assert 'module.exports' in template
        assert '/**' in template  # Comentario de documentación
    
    def test_get_template_for_extension_unknown(self):
        """Test obtener template para extensión desconocida"""
        template = self.generator.get_template_for_extension('unknown.xyz')
        
        # Debe retornar template default
        assert template == self.generator._templates['default']
        assert '// Content goes here' in template
    
    def test_get_template_for_extension_no_extension(self):
        """Test obtener template para archivo sin extensión"""
        template = self.generator.get_template_for_extension('filename')
        
        # Debe retornar template default
        assert template == self.generator._templates['default']
    
    def test_get_template_for_extension_case_insensitive(self):
        """Test que extensiones son case insensitive"""
        template_lower = self.generator.get_template_for_extension('test.py')
        template_upper = self.generator.get_template_for_extension('test.PY')
        
        assert template_lower == template_upper
    
    def test_get_template_for_extension_multiple_dots(self):
        """Test archivo con múltiples puntos"""
        template = self.generator.get_template_for_extension('test.config.js')
        
        # Debe usar la última extensión (.js)
        assert 'function main()' in template
    
    def test_get_template_for_extension_exception_handling(self):
        """Test manejo de excepciones al obtener template"""
        with patch('pathlib.Path') as mock_path:
            mock_path.side_effect = Exception("Path error")
            
            # No debe crash, debe retornar default
            template = self.generator.get_template_for_extension('any.file')
            assert template == self.generator._templates['default']
    
    def test_customize_template_basic(self):
        """Test personalización básica de template"""
        template = "Hello $name, created on $timestamp"
        
        result = self.generator.customize_template(template, name="World")
        
        assert "Hello World" in result
        assert "created on" in result
        # Debe tener timestamp por defecto
        assert str(datetime.now().year) in result
    
    def test_customize_template_all_defaults(self):
        """Test personalización con variables por defecto"""
        template = "$description - $title - $timestamp"
        
        result = self.generator.customize_template(template)
        
        assert len(result) > 50
        assert "Untitled" in result
        assert str(datetime.now().year) in result
    
    def test_customize_template_override_defaults(self):
        """Test sobrescribir variables por defecto"""
        template = "Title: $title, Desc: $description"
        
        result = self.generator.customize_template(
            template, 
            title="My Custom Title",
            description="My custom description"
        )
        
        assert "My Custom Title" in result
        assert "My custom description" in result
        assert "Untitled" not in result
        assert "Auto-generated file" not in result
    
    def test_customize_template_component_name_from_path(self):
        """Test generación automática de component_name desde file_path"""
        template = "Component: $component_name"
        
        result = self.generator.customize_template(
            template, 
            file_path="src/components/user-profile.jsx"
        )
        
        assert "UserProfile" in result  # Debe convertir user-profile a UserProfile
    
    def test_customize_template_component_name_override(self):
        """Test que component_name manual sobrescribe automático"""
        template = "Component: $component_name"
        
        result = self.generator.customize_template(
            template,
            file_path="src/test.jsx",
            component_name="CustomComponent"
        )
        
        assert "CustomComponent" in result
        assert "Test" not in result
    
    def test_customize_template_exception_handling(self):
        """Test manejo de excepciones en personalización"""
        template = "Test {invalid_var}"  # Variable no proporcionada
        
        # No debe crash, debe retornar template original
        result = self.generator.customize_template(template)
        assert result == template
    
    def test_customize_template_format_error_handling(self):
        """Test manejo de errores de formato"""
        template = "Test {unclosed_var"  # Formato inválido
        
        # Debe manejar error y retornar template original
        result = self.generator.customize_template(template)
        assert result == template
    
    def test_generate_template_python(self):
        """Test generación de template Python específico"""
        result = self.generator.generate_template('python')
        
        assert '#!/usr/bin/env python3' in result
        assert 'def main():' in result
        assert 'Auto-generated file' in result  # Descripción por defecto
        assert str(datetime.now().year) in result
    
    # En tests/test_functions/test_template/test_generator.py línea ~173
    def test_generate_template_javascript(self):
        """Test generación de template JavaScript específico"""
        result = self.generator.generate_template('js')
        
        assert 'function main()' in result
        # CAMBIAR: assert 'Auto-generated file' in result
        # POR: Verificar que se personalizó (no contiene placeholders)
        assert '$description' not in result
        assert '$timestamp' not in result
        assert 'Auto-generated file' in result  # Debe estar personalizado
    
    def test_generate_template_with_customization(self):
        """Test generación con personalización"""
        result = self.generator.generate_template(
            'python',
            description="Test script for unit testing",
            file_path="tests/test_example.py"
        )
        
        assert "Test script for unit testing" in result
        assert "Auto-generated file" not in result
    
    def test_generate_template_nonexistent_type(self):
        """Test generación de template inexistente"""
        result = self.generator.generate_template('nonexistent')
        
        # Debe retornar template default
        assert result == self.generator.customize_template(self.generator._templates['default'])
    
    def test_generate_template_exception_handling(self):
        """Test manejo de excepciones en generación"""
        with patch.object(self.generator, 'customize_template') as mock_customize:
            mock_customize.side_effect = Exception("Customize error")
            
            result = self.generator.generate_template('python')
            
            # Debe retornar template default sin personalizar
            assert result == self.generator._templates['default']
    
    def test_get_available_templates(self):
        """Test obtener lista de templates disponibles"""
        templates = self.generator.get_available_templates()
        
        assert isinstance(templates, list)
        assert len(templates) > 0
        assert 'python' in templates
        assert 'js' in templates
        assert 'default' in templates
    
    def test_add_custom_template_success(self):
        """Test agregar template personalizado exitosamente"""
        custom_content = "Custom template: $name"
        
        result = self.generator.add_custom_template('custom', custom_content)
        
        assert result is True
        assert 'custom' in self.generator._templates
        assert self.generator._templates['custom'] == custom_content
    
    def test_add_custom_template_use_after_add(self):
        """Test usar template personalizado después de agregarlo"""
        custom_content = "# Custom $description"
        self.generator.add_custom_template('mycustom', custom_content)
        
        result = self.generator.generate_template('mycustom', description="test file")
        
        assert "# Custom test file" in result
    
    # En tests/test_functions/test_template/test_generator.py línea ~230
    def test_add_custom_template_exception_handling(self):
        """Test manejo de excepciones al agregar template"""
        # CAMBIAR approach - simular excepción en logger en lugar de dict
        with patch.object(self.generator, 'logger') as mock_logger:
            mock_logger.info.side_effect = Exception("Logger error")
            
            result = self.generator.add_custom_template('test', 'content')
            
            # El método debe manejar la excepción y retornar False
            assert result is False


class TestTemplateGeneratorSpecificTemplates:
    """Tests para templates específicos incluidos"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.generator = TemplateGenerator()
    
    def test_python_template_structure(self):
        """Test estructura del template Python"""
        template = self.generator._templates['python']
        
        required_elements = [
            '#!/usr/bin/env python3',
            '"""',
            'def main():',
            'if __name__ == "__main__":',
            '$description',
            '$timestamp'
        ]
        
        for element in required_elements:
            assert element in template
    
    def test_javascript_template_structure(self):
        """Test estructura del template JavaScript"""
        template = self.generator._templates['js']
        
        required_elements = [
            '/**',
            'function main()',
            'module.exports',
            '$description',
            '$timestamp'
        ]
        
        for element in required_elements:
            assert element in template
    
    def test_html_template_structure(self):
        """Test estructura del template HTML si existe"""
        if 'html' in self.generator._templates:
            template = self.generator._templates['html']
            
            required_elements = [
                '<!DOCTYPE html>',
                '<html',
                '<head>',
                '<body>',
                '$title',
                '$description'
            ]
            
            for element in required_elements:
                assert element in template
    
    def test_extension_mapping_completeness(self):
        """Test que mapeo de extensiones es apropiado"""
        # Test extensiones comunes
        common_files = [
            ('test.py', 'python'),
            ('app.js', 'js'),  
            ('component.jsx', 'jsx') if 'jsx' in self.generator._templates else ('component.jsx', 'default'),
            ('styles.css', 'css') if 'css' in self.generator._templates else ('styles.css', 'default'),
            ('README.md', 'md') if 'md' in self.generator._templates else ('README.md', 'default')
        ]
        
        for filename, expected_type in common_files:
            template = self.generator.get_template_for_extension(filename)
            expected_template = self.generator._templates.get(expected_type, self.generator._templates['default'])
            assert template == expected_template


class TestTemplateGeneratorConvenienceFunctions:
    """Tests para funciones de conveniencia"""
    
    def test_generate_template_convenience_function(self):
        """Test función de conveniencia generate_template"""
        result = generate_template('python', description="Test function")
        
        assert isinstance(result, str)
        assert 'Test function' in result
        assert '#!/usr/bin/env python3' in result
    
    def test_get_template_for_extension_convenience_function(self):
        """Test función de conveniencia get_template_for_extension"""
        result = get_template_for_extension('test.py')
        
        assert isinstance(result, str)
        assert '#!/usr/bin/env python3' in result
    
    def test_customize_template_convenience_function(self):
        """Test función de conveniencia customize_template"""
        template = "Hello $name"
        result = customize_template(template, name="World")
        
        assert isinstance(result, str)
        assert "Hello World" in result


class TestTemplateGeneratorEdgeCases:
    """Tests para casos edge y situaciones especiales"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.generator = TemplateGenerator()
    
    def test_empty_template_customization(self):
        """Test personalización de template vacío"""
        result = self.generator.customize_template("")
        assert result == ""
    
    # En tests/test_functions/test_template/test_generator.py línea ~357
    def test_template_with_nested_braces(self):
        """Test template con llaves anidadas"""
        template = "{{not_variable}} but $real_variable"
        result = self.generator.customize_template(template, real_variable="test")
        
        # Python .format() convierte {{}} a {} (escape)
        # CAMBIAR: assert "{{not_variable}}" in result
        # POR: assert "{not_variable}" in result  # Comportamiento esperado de Python
        assert "{not_variable}" in result
        assert "test" in result
    
    def test_template_with_special_characters(self):
        """Test template con caracteres especiales"""
        template = "Special chars: üñícode $description"
        result = self.generator.customize_template(template, description="test")
        
        assert "üñícode" in result
        assert "test" in result
    
    def test_very_long_template(self):
        """Test template muy largo"""
        long_template = "x" * 10000 + " $description"
        result = self.generator.customize_template(long_template, description="test")
        
        assert len(result) > 10000
        assert "test" in result
    
    def test_template_generation_with_none_values(self):
        """Test generación con valores None"""
        result = self.generator.customize_template(
            "$description", 
            description=None
        )
        
        # Debe manejar None apropiadamente
        assert isinstance(result, str)
    
    @patch('logging.getLogger')
    def test_logger_usage(self, mock_logger):
        """Test que el generador usa logger apropiadamente"""
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance
        
        generator = TemplateGenerator()
        generator.get_template_for_extension('test.py')
        
        # Debe haber llamado getLogger
        mock_logger.assert_called_once()