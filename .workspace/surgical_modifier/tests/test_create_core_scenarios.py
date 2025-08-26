#!/usr/bin/env python3
"""
Suite de tests core para CREATE Operation v6.0 - Sin dependencias externas
Cobertura completa: casos básicos, formato Google, performance básica
"""
import os
import sys
import pytest
import tempfile
import shutil
import time
import threading
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.operations.basic.create import (
   create_operation,
   create_with_template,
   create_with_backup
)

from core.functions.formatting.content_formatter import (
   apply_google_format, 
   format_python_google_style, 
   format_javascript_google_style,
   get_file_extension
)

from core.functions.validation.content_validator import validate_file_content

class TestCreateBasicFunctionality:
   """Tests básicos - 10 tests"""
   
   def test_create_simple_file(self):
       """Test crear archivo simple"""
       with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf:
           temp_path = tf.name
       
       os.unlink(temp_path)
       
       result = create_operation(temp_path, '', 'print("hello")')
       
       assert result['success'] is True
       assert os.path.exists(temp_path)
       assert result['format_applied'] == '.py'
       
       os.unlink(temp_path)
   
   def test_create_empty_file(self):
       """Test crear archivo vacío"""
       with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tf:
           temp_path = tf.name
       
       os.unlink(temp_path)
       
       result = create_operation(temp_path, '', '')
       
       assert result['success'] is True
       assert os.path.exists(temp_path)
       assert result['content_length'] == 0
       
       os.unlink(temp_path)
   
   def test_create_utf8_special_chars(self):
       """Test caracteres especiales UTF-8"""
       special_content = '# Código UTF-8\nprint("Hola 世界 🌍")\nvar = "ñáéíóú"'
       
       with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf:
           temp_path = tf.name
       
       os.unlink(temp_path)
       
       result = create_operation(temp_path, '', special_content)
       
       assert result['success'] is True
       
       with open(temp_path, 'r', encoding='utf-8') as f:
           content = f.read()
       
       assert '🌍' in content
       assert 'ñáéíóú' in content
       
       os.unlink(temp_path)
   
   def test_create_file_with_spaces_in_name(self):
       """Test archivo con espacios en nombre"""
       temp_dir = tempfile.mkdtemp()
       file_path = os.path.join(temp_dir, 'file with spaces.py')
       
       result = create_operation(file_path, '', 'print("spaces")')
       
       assert result['success'] is True
       assert os.path.exists(file_path)
       
       shutil.rmtree(temp_dir)
   
   def test_overwrite_existing_file(self):
       """Test sobrescribir archivo existente"""
       with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
           tf.write('original content')
           temp_path = tf.name
       
       result = create_operation(temp_path, '', 'new content')
       
       assert result['success'] is True
       
       with open(temp_path, 'r') as f:
           content = f.read()
       
       assert content == 'new content'
       
       os.unlink(temp_path)

class TestAutoDirectoryCreation:
   """Tests auto-creación directorios - 6 tests"""
   
   def test_create_simple_missing_directory(self):
       """Test crear directorio simple faltante"""
       temp_base = tempfile.mkdtemp()
       file_path = os.path.join(temp_base, 'new_dir', 'file.py')
       
       result = create_operation(file_path, '', 'print("auto_dir")')
       
       assert result['success'] is True
       assert os.path.exists(file_path)
       assert os.path.exists(os.path.dirname(file_path))
       
       shutil.rmtree(temp_base)
   
   def test_create_nested_deep_structure(self):
       """Test estructura anidada 5+ niveles"""
       temp_base = tempfile.mkdtemp()
       file_path = os.path.join(temp_base, 'a', 'b', 'c', 'd', 'e', 'deep.py')
       
       result = create_operation(file_path, '', 'print("deep")')
       
       assert result['success'] is True
       assert os.path.exists(file_path)
       
       shutil.rmtree(temp_base)
   
   def test_create_multiple_files_same_new_directory(self):
       """Test múltiples archivos en mismo directorio nuevo"""
       temp_base = tempfile.mkdtemp()
       new_dir = os.path.join(temp_base, 'shared_new_dir')
       
       files = ['file1.py', 'file2.js', 'file3.html']
       
       for filename in files:
           file_path = os.path.join(new_dir, filename)
           result = create_operation(file_path, '', f'content for {filename}')
           assert result['success'] is True
           assert os.path.exists(file_path)
       
       assert len(os.listdir(new_dir)) == 3
       
       shutil.rmtree(temp_base)

class TestGoogleFormatting:
   """Tests formato Google - 8 tests"""
   
   def test_python_tabs_to_4_spaces(self):
       """Test Python: tabs → 4 espacios"""
       content = 'def test():\n\treturn True\n\t\tif condition:\n\t\t\tpass'
       
       with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf:
           temp_path = tf.name
       
       os.unlink(temp_path)
       
       result = create_operation(temp_path, '', content)
       
       with open(temp_path, 'r') as f:
           formatted = f.read()
       
       assert '\t' not in formatted
       assert '    ' in formatted
       assert '        ' in formatted
       assert '            ' in formatted
       
       os.unlink(temp_path)
   
   def test_javascript_tabs_to_2_spaces(self):
       """Test JavaScript: tabs → 2 espacios"""
       content = 'function test() {\n\treturn true;\n\t\tif (condition) {\n\t\t\tconsole.log("test");\n\t\t}\n}'
       
       with tempfile.NamedTemporaryFile(delete=False, suffix='.js') as tf:
           temp_path = tf.name
       
       os.unlink(temp_path)
       
       result = create_operation(temp_path, '', content)
       
       with open(temp_path, 'r') as f:
           formatted = f.read()
       
       assert '\t' not in formatted
       assert '  ' in formatted
       
       os.unlink(temp_path)
   
   def test_trailing_whitespace_removal(self):
       """Test eliminación espacios al final"""
       content = 'def test():   \n    return True  \n'
       
       with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf:
           temp_path = tf.name
       
       os.unlink(temp_path)
       
       result = create_operation(temp_path, '', content)
       
       with open(temp_path, 'r') as f:
           formatted = f.read()
       
       lines = formatted.split('\n')
       for line in lines[:-1]:
           assert not line.endswith(' ')
           assert not line.endswith('\t')
       
       os.unlink(temp_path)
   
   def test_format_multiple_languages(self):
       """Test formato para múltiples lenguajes"""
       test_cases = [
           ('.py', 'def test():\n\treturn True', '    '),  # 4 espacios
           ('.js', 'function test() {\n\treturn true;\n}', '  '),  # 2 espacios
           ('.html', '<div>\n\t<p>Hello</p>\n</div>', '  '),  # 2 espacios
           ('.css', '.class {\n\tcolor: red;\n}', '  '),  # 2 espacios
       ]
       
       for ext, content, expected_indent in test_cases:
           with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tf:
               temp_path = tf.name
           
           os.unlink(temp_path)
           
           result = create_operation(temp_path, '', content)
           
           with open(temp_path, 'r') as f:
               formatted = f.read()
           
           assert '\t' not in formatted
           assert expected_indent in formatted
           
           os.unlink(temp_path)

class TestFormatFunctions:
   """Tests funciones de formato - 6 tests"""
   
   def test_get_file_extension(self):
       """Test detección extensión archivo"""
       assert get_file_extension('file.py') == '.py'
       assert get_file_extension('file.JS') == '.js'
       assert get_file_extension('file.HTML') == '.html'
       assert get_file_extension('file') == ''
       assert get_file_extension('file.test.py') == '.py'
   
   def test_apply_google_format_routing(self):
       """Test enrutamiento formato por tipo"""
       content = 'function test() {\n\treturn true;\n}'
       
       py_formatted = apply_google_format(content, '.py')
       js_formatted = apply_google_format(content, '.js')
       unknown_formatted = apply_google_format(content, '.unknown')
       
       # Python: 4 espacios
       assert '    ' in py_formatted
       
       # JavaScript: 2 espacios  
       assert '  ' in js_formatted
       
       # Unknown: sin cambios
       assert unknown_formatted == content
   
   def test_format_python_google_style_direct(self):
       """Test función formato Python directa"""
       content = 'def test():\n\treturn True\n\t\tif condition:\n\t\t\tpass'
       formatted = format_python_google_style(content)
       
       assert '\t' not in formatted
       assert '    return True' in formatted
       assert '        if condition:' in formatted
       assert '            pass' in formatted
   
   def test_format_javascript_google_style_direct(self):
       """Test función formato JavaScript directa"""
       content = 'function test() {\n\treturn true;\n\t\tif (condition) {\n\t\t\tconsole.log("test");\n\t\t}\n}'
       formatted = format_javascript_google_style(content)
       
       assert '\t' not in formatted
       assert '  return true;' in formatted
       assert '    if (condition) {' in formatted
       assert '      console.log("test");' in formatted

class TestAdvancedFunctions:
   """Tests funciones avanzadas - 4 tests"""
   
   def test_create_with_template_function(self):
       """Test función template"""
       temp_dir = tempfile.mkdtemp()
       file_path = os.path.join(temp_dir, 'template_test.py')
       
       variables = {'name': 'TestClass'}
       result = create_with_template(file_path, 'python_class', variables)
       
       assert result['success'] is True
       
       with open(file_path, 'r') as f:
           content = f.read()
       
       assert 'class TestClass:' in content
       
       shutil.rmtree(temp_dir)
   
   def test_create_with_backup_function(self):
       """Test función backup automático"""
       temp_dir = tempfile.mkdtemp()
       file_path = os.path.join(temp_dir, 'backup_test.py')
       
       # Crear archivo original
       with open(file_path, 'w') as f:
           f.write('original content')
       
       # Usar create_with_backup
       result = create_with_backup(file_path, 'new content')
       
       assert result['success'] is True
       assert result['backup_created'] is True
       
       # Verificar archivo actual
       with open(file_path, 'r') as f:
           content = f.read()
       assert 'new content' in content
       
       # Verificar backup
       backup_path = file_path + '.backup'
       assert os.path.exists(backup_path)
       
       shutil.rmtree(temp_dir)

class TestPerformanceBasic:
   """Tests performance básicos - 3 tests"""
   
   def test_create_10_files_performance(self):
       """Test performance: 10 archivos"""
       temp_dir = tempfile.mkdtemp()
       
       start_time = time.time()
       
       for i in range(10):
           file_path = os.path.join(temp_dir, f'perf_test_{i}.py')
           result = create_operation(file_path, '', f'print("performance test {i}")')
           assert result['success'] is True
       
       end_time = time.time()
       total_time = end_time - start_time
       
       # Debe completar en menos de 2 segundos
       assert total_time < 2.0
       
       # Verificar todos los archivos
       files = os.listdir(temp_dir)
       assert len(files) == 10
       
       shutil.rmtree(temp_dir)
   
   def test_large_content_basic(self):
       """Test contenido grande básico"""
       large_content = 'print("large file test line")\n' * 5000  # ~150KB
       
       with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf:
           temp_path = tf.name
       
       os.unlink(temp_path)
       
       start_time = time.time()
       result = create_operation(temp_path, '', large_content)
       end_time = time.time()
       
       assert result['success'] is True
       assert end_time - start_time < 2.0  # Menos de 2 segundos
       
       # Verificar tamaño
       file_size = os.path.getsize(temp_path)
       assert file_size > 100000  # Al menos 100KB
       
       os.unlink(temp_path)
   
   def test_concurrent_creation_basic(self):
       """Test creación concurrente básica"""
       temp_dir = tempfile.mkdtemp()
       results = []
       
       def create_concurrent_file(index):
           file_path = os.path.join(temp_dir, f'concurrent_{index}.py')
           result = create_operation(file_path, '', f'print("concurrent {index}")')
           results.append((index, result))
       
       # Crear 5 threads
       threads = []
       for i in range(5):
           thread = threading.Thread(target=create_concurrent_file, args=(i,))
           threads.append(thread)
           thread.start()
       
       for thread in threads:
           thread.join()
       
       # Verificar resultados
       assert len(results) == 5
       assert all(r[1]['success'] for r in results)
       
       # Verificar archivos creados
       files_created = os.listdir(temp_dir)
       assert len(files_created) == 5
       
       shutil.rmtree(temp_dir)

if __name__ == "__main__":
   pytest.main([__file__, "-v", "--tb=short"])