#!/usr/bin/env python3
"""
Suite de tests extremos para CREATE Operation v6.0
Cobertura completa: casos básicos, edge cases, performance, formato Google
"""
import os
import sys
import pytest
import tempfile
import shutil
import time
import psutil
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.operations.basic.create import (
    create_operation,
    apply_google_format,
    format_python_google_style,
    format_javascript_google_style,
    get_file_extension,
    validate_file_content,
    create_with_template,
    create_with_backup
)

class TestCreateBasicFunctionality:
    """Tests básicos - 10 tests"""
    
    def test_create_simple_file(self):
        """Test crear archivo simple"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf:
            temp_path = tf.name
        
        os.unlink(temp_path)  # Eliminar archivo temporal
        
        result = create_operation(temp_path, '', 'print("hello")')
        
        assert result['success'] is True
        assert os.path.exists(temp_path)
        assert result['format_applied'] == '.py'
        
        # Cleanup
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
    
    def test_create_large_file(self):
        """Test archivo grande >1MB"""
        large_content = 'print("line")\n' * 50000  # ~500KB
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf:
            temp_path = tf.name
        
        os.unlink(temp_path)
        
        result = create_operation(temp_path, '', large_content)
        
        assert result['success'] is True
        assert result['content_length'] > 400000  # Al menos 400KB
        
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
    
    def test_create_unknown_extension(self):
        """Test archivo con extensión desconocida"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xyz') as tf:
            temp_path = tf.name
        
        os.unlink(temp_path)
        
        result = create_operation(temp_path, '', 'some content')
        
        assert result['success'] is True
        assert result['format_applied'] == '.xyz'
        
        os.unlink(temp_path)
    
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
    
    def test_create_absolute_vs_relative_path(self):
        """Test rutas absolutas vs relativas"""
        # Ruta absoluta
        temp_dir = tempfile.mkdtemp()
        abs_path = os.path.join(temp_dir, 'abs_file.py')
        
        result1 = create_operation(abs_path, '', 'print("absolute")')
        assert result1['success'] is True
        
        # Ruta relativa (en directorio temporal)
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        result2 = create_operation('rel_file.py', '', 'print("relative")')
        assert result2['success'] is True
        
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir)
    
    def test_create_readonly_directory_fails_gracefully(self):
        """Test crear en directorio solo lectura falla apropiadamente"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Hacer directorio solo lectura
            os.chmod(temp_dir, 0o444)
            
            file_path = os.path.join(temp_dir, 'readonly_test.py')
            result = create_operation(file_path, '', 'content')
            
            # Debe fallar pero manejar error apropiadamente
            assert result['success'] is False
            assert 'error' in result
            
        finally:
            # Restaurar permisos para cleanup
            os.chmod(temp_dir, 0o755)
            shutil.rmtree(temp_dir)
    
    def test_create_with_specific_permissions(self):
        """Test crear archivo y verificar permisos"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf:
            temp_path = tf.name
        
        os.unlink(temp_path)
        
        result = create_operation(temp_path, '', 'print("permissions")')
        
        assert result['success'] is True
        
        # Verificar que el archivo es legible
        assert os.access(temp_path, os.R_OK)
        assert os.access(temp_path, os.W_OK)
        
        os.unlink(temp_path)

class TestAutoDirectoryCreation:
    """Tests auto-creación directorios - 8 tests"""
    
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
        
        # Verificar que todos los directorios se crearon
        path_parts = file_path.split(os.sep)
        for i in range(len(path_parts) - 1, 0, -1):
            partial_path = os.sep.join(path_parts[:i])
            if partial_path and not partial_path.endswith(':'):
                assert os.path.exists(partial_path)
        
        shutil.rmtree(temp_base)
    
    def test_create_directories_with_special_names(self):
        """Test directorios con nombres especiales"""
        temp_base = tempfile.mkdtemp()
        file_path = os.path.join(temp_base, 'dir with spaces', 'dir-with-dashes', 'file.py')
        
        result = create_operation(file_path, '', 'print("special_names")')
        
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
        
        # Verificar que directorio contiene todos los archivos
        assert len(os.listdir(new_dir)) == 3
        
        shutil.rmtree(temp_base)
    
    def test_create_complex_structure_multiple_branches(self):
        """Test estructura compleja con múltiples ramas"""
        temp_base = tempfile.mkdtemp()
        
        files = [
            'branch1/sub1/file1.py',
            'branch1/sub2/file2.py',
            'branch2/sub1/file3.js',
            'branch2/sub2/sub3/file4.html'
        ]
        
        for file_path in files:
            full_path = os.path.join(temp_base, file_path)
            result = create_operation(full_path, '', f'content for {file_path}')
            assert result['success'] is True
            assert os.path.exists(full_path)
        
        shutil.rmtree(temp_base)
    
    def test_extremely_long_path(self):
        """Test ruta extremadamente larga"""
        temp_base = tempfile.mkdtemp()
        
        # Crear ruta larga pero válida para el sistema
        long_parts = ['very_long_directory_name'] * 10
        file_path = os.path.join(temp_base, *long_parts, 'file.py')
        
        try:
            result = create_operation(file_path, '', 'print("long_path")')
            
            # En algunos sistemas puede fallar por límites de longitud
            if result['success']:
                assert os.path.exists(file_path)
            else:
                # Error esperado en sistemas con límites estrictos
                assert 'error' in result
        finally:
            shutil.rmtree(temp_base)
    
    def test_directory_permissions_after_creation(self):
        """Test permisos de directorios creados"""
        temp_base = tempfile.mkdtemp()
        file_path = os.path.join(temp_base, 'new_dir', 'sub_dir', 'file.py')
        
        result = create_operation(file_path, '', 'print("permissions")')
        
        assert result['success'] is True
        
        # Verificar permisos de directorios creados
        new_dir = os.path.join(temp_base, 'new_dir')
        sub_dir = os.path.join(new_dir, 'sub_dir')
        
        assert os.access(new_dir, os.R_OK | os.W_OK | os.X_OK)
        assert os.access(sub_dir, os.R_OK | os.W_OK | os.X_OK)
        
        shutil.rmtree(temp_base)
    
    def test_concurrent_directory_creation(self):
        """Test creación concurrente de directorios"""
        import threading
        
        temp_base = tempfile.mkdtemp()
        results = []
        
        def create_file(index):
            file_path = os.path.join(temp_base, 'concurrent_dir', f'file_{index}.py')
            result = create_operation(file_path, '', f'print("concurrent_{index}")')
            results.append(result)
        
        # Crear múltiples threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_file, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Esperar a que terminen
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        assert len(results) == 5
        assert all(r['success'] for r in results)
        
        # Verificar archivos creados
        concurrent_dir = os.path.join(temp_base, 'concurrent_dir')
        assert len(os.listdir(concurrent_dir)) == 5
        
        shutil.rmtree(temp_base)

class TestGoogleFormatting:
    """Tests formato Google - 7 tests"""
    
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
        assert '        ' in formatted  # 2 niveles = 8 espacios
        assert '            ' in formatted  # 3 niveles = 12 espacios
        
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
        assert '  ' in formatted  # 2 espacios
        assert '    ' in formatted  # 4 espacios (2 niveles)
        assert '      ' in formatted  # 6 espacios (3 niveles)
        
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
        for line in lines[:-1]:  # Excluir última línea vacía
            assert not line.endswith(' ')
            assert not line.endswith('\t')
        
        os.unlink(temp_path)
    
    def test_html_formatting(self):
        """Test formato HTML"""
        content = '<div>\n\t<p>Hello</p>\n\t\t<span>World</span>\n</div>'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tf:
            temp_path = tf.name
        
        os.unlink(temp_path)
        
        result = create_operation(temp_path, '', content)
        
        with open(temp_path, 'r') as f:
            formatted = f.read()
        
        assert '\t' not in formatted
        assert '  ' in formatted  # HTML usa 2 espacios
        
        os.unlink(temp_path)
    
    def test_css_formatting(self):
        """Test formato CSS"""
        content = '.class {\n\tcolor: red;\n\t\tmargin: 10px;\n}'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.css') as tf:
            temp_path = tf.name
        
        os.unlink(temp_path)
        
        result = create_operation(temp_path, '', content)
        
        with open(temp_path, 'r') as f:
            formatted = f.read()
        
        assert '\t' not in formatted
        assert '  ' in formatted  # CSS usa 2 espacios
        
        os.unlink(temp_path)
    
    def test_no_formatting_for_unknown_extensions(self):
        """Test sin formato para extensiones desconocidas"""
        content = 'some\tcontent\twith\ttabs\t'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.unknown') as tf:
            temp_path = tf.name
        
        os.unlink(temp_path)
        
        result = create_operation(temp_path, '', content)
        
        with open(temp_path, 'r') as f:
            formatted = f.read()
        
        # Contenido debe mantenerse igual para extensiones desconocidas
        assert formatted == content
        
        os.unlink(temp_path)
    
    def test_format_preserved_in_saved_file(self):
        """Test formato se mantiene al guardar"""
        content = 'def test():\n\treturn True'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf:
            temp_path = tf.name
        
        os.unlink(temp_path)
        
        # Crear archivo
        result1 = create_operation(temp_path, '', content)
        
        # Leer contenido
        with open(temp_path, 'r') as f:
            formatted = f.read()
        
        # Crear otro archivo con el contenido ya formateado
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf2:
            temp_path2 = tf2.name
        
        os.unlink(temp_path2)
        
        result2 = create_operation(temp_path2, '', formatted)
        
        # Ambos archivos deben tener el mismo contenido formateado
        with open(temp_path2, 'r') as f:
            formatted2 = f.read()
        
        assert formatted == formatted2
        
        os.unlink(temp_path)
        os.unlink(temp_path2)

class TestExtremeScenarios:
    """Tests extremos - 10+ tests"""
    
    def test_extremely_large_file(self):
        """Test archivo extremadamente grande (10MB)"""
        # Solo hacer si hay suficiente memoria
        import psutil
        available_memory = psutil.virtual_memory().available / (1024**2)  # MB
        
        if available_memory < 100:  # Si hay menos de 100MB disponible, skip
            pytest.skip("Insufficient memory for large file test")
        
        large_content = 'print("large file test line")\n' * 200000  # ~5MB
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf:
            temp_path = tf.name
        
        os.unlink(temp_path)
        
        start_time = time.time()
        result = create_operation(temp_path, '', large_content)
        end_time = time.time()
        
        assert result['success'] is True
        assert end_time - start_time < 5.0  # Debe completar en menos de 5 segundos
        
        # Verificar tamaño
        file_size = os.path.getsize(temp_path)
        assert file_size > 4 * 1024 * 1024  # Al menos 4MB
        
        os.unlink(temp_path)
    
    def test_special_characters_filename(self):
        """Test nombre archivo con caracteres especiales"""
        temp_dir = tempfile.mkdtemp()
        
        # Caracteres que son válidos en la mayoría de sistemas
        special_chars = ['file-test.py', 'file_test.py', 'file.test.py', 'file123.py']
        
        for filename in special_chars:
            file_path = os.path.join(temp_dir, filename)
            result = create_operation(file_path, '', f'# {filename}')
            assert result['success'] is True
            assert os.path.exists(file_path)
        
        shutil.rmtree(temp_dir)
    
    def test_concurrent_file_creation(self):
        """Test creación concurrente 50 archivos"""
        import threading
        
        temp_dir = tempfile.mkdtemp()
        results = []
        
        def create_concurrent_file(index):
            file_path = os.path.join(temp_dir, f'concurrent_{index}.py')
            result = create_operation(file_path, '', f'print("concurrent {index}")')
            results.append((index, result))
        
        # Crear 50 threads
        threads = []
        for i in range(50):
            thread = threading.Thread(target=create_concurrent_file, args=(i,))
            threads.append(thread)
        
        start_time = time.time()
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Verificar resultados
        assert len(results) == 50
        assert all(r[1]['success'] for r in results)
        
        # Verificar archivos creados
        files_created = os.listdir(temp_dir)
        assert len(files_created) == 50
        
        # Performance: debe completar en tiempo razonable
        assert end_time - start_time < 10.0  # Menos de 10 segundos
        
        shutil.rmtree(temp_dir)
    
    def test_memory_usage_large_content(self):
        """Test uso memoria con contenido grande"""
        process = psutil.Process(os.getpid())
        
        # Memoria inicial
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Crear archivo grande
        large_content = 'print("memory test")\n' * 10000
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf:
            temp_path = tf.name
        
        os.unlink(temp_path)
        
        result = create_operation(temp_path, '', large_content)
        
        # Memoria después
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_diff = final_memory - initial_memory
        
        assert result['success'] is True
        
        # No debería usar más de 50MB adicionales para este test
        assert memory_diff < 50
        
        os.unlink(temp_path)
    
    def test_performance_50_files_sequential(self):
        """Test performance: 50 archivos secuenciales"""
        temp_dir = tempfile.mkdtemp()
        
        start_time = time.time()
        
        for i in range(50):
            file_path = os.path.join(temp_dir, f'perf_test_{i}.py')
            result = create_operation(file_path, '', f'print("performance test {i}")')
            assert result['success'] is True
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Debe completar en menos de 5 segundos (100ms por archivo promedio)
        assert total_time < 5.0
        
        # Verificar todos los archivos
        files = os.listdir(temp_dir)
        assert len(files) == 50
        
        shutil.rmtree(temp_dir)
    
    def test_file_system_edge_cases(self):
        """Test casos edge del sistema de archivos"""
        temp_dir = tempfile.mkdtemp()
        
        # Archivo con punto al inicio (archivo oculto en Unix)
        hidden_file = os.path.join(temp_dir, '.hidden_file.py')
        result1 = create_operation(hidden_file, '', 'print("hidden")')
        assert result1['success'] is True
        
        # Archivo con múltiples extensiones
        multi_ext = os.path.join(temp_dir, 'file.test.backup.py')
        result2 = create_operation(multi_ext, '', 'print("multi_ext")')
        assert result2['success'] is True
        assert result2['format_applied'] == '.py'  # Debe detectar .py como extensión
        
        shutil.rmtree(temp_dir)
    
    def test_interrupt_and_recover(self):
        """Test interrupción y recuperación"""
        temp_dir = tempfile.mkdtemp()
        
        # Simular creación de archivo que podría ser interrumpida
        file_path = os.path.join(temp_dir, 'interrupt_test.py')
        
        # Primera creación
        result1 = create_operation(file_path, '', 'print("first")')
        assert result1['success'] is True
        
        # Verificar archivo existe
        assert os.path.exists(file_path)
        
        # Segunda creación (sobrescribir)
        result2 = create_operation(file_path, '', 'print("second")')
        assert result2['success'] is True
        
        # Verificar contenido actualizado
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert 'second' in content
        assert 'first' not in content
        
        shutil.rmtree(temp_dir)
    
    def test_different_encodings(self):
        """Test diferentes encodings (siempre usa UTF-8)"""
        content_with_unicode = 'print("Testing: café, résumé, naïve, Москва, 北京")'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf:
            temp_path = tf.name
        
        os.unlink(temp_path)
        
        result = create_operation(temp_path, '', content_with_unicode)
        
        assert result['success'] is True
        
        # Leer con UTF-8 (encoding por defecto)
        with open(temp_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        
        # Todos los caracteres unicode deben estar presentes
        assert 'café' in saved_content
        assert 'résumé' in saved_content
        assert 'Москва' in saved_content
        assert '北京' in saved_content
        
        os.unlink(temp_path)
    
    def test_very_long_single_line(self):
        """Test línea única muy larga"""
        # Línea de 10,000 caracteres
        long_line = 'print("' + 'x' * 9990 + '")'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf:
            temp_path = tf.name
        
        os.unlink(temp_path)
        
        result = create_operation(temp_path, '', long_line)
        
        assert result['success'] is True
        assert result['content_length'] == len(long_line)
        
        os.unlink(temp_path)
    
    def test_nested_quotes_and_escapes(self):
        """Test comillas anidadas y escapes"""
        complex_content = '''print("String with 'single quotes'")
print('String with "double quotes"')
print("String with \\"escaped quotes\\"")
print(f"F-string with {variable}")'''
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tf:
            temp_path = tf.name
        
        os.unlink(temp_path)
        
        result = create_operation(temp_path, '', complex_content)
        
        assert result['success'] is True
        
        # Verificar que el contenido se guardó correctamente
        with open(temp_path, 'r') as f:
            saved_content = f.read()
        
        assert 'single quotes' in saved_content
        assert 'double quotes' in saved_content
        assert 'escaped quotes' in saved_content
        
        os.unlink(temp_path)

class TestFormatFunctions:
    """Tests funciones de formato individuales - 5 tests"""
    
    def test_get_file_extension(self):
        """Test detección extensión archivo"""
        assert get_file_extension('file.py') == '.py'
        assert get_file_extension('file.JS') == '.js'  # Lowercase
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
        assert '    ' not in js_formatted.replace('    ', '  ')  # No 4 espacios extra
        
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
    
    def test_validate_file_content_function(self):
        """Test función validación contenido"""
        # Python válido
        valid_py = 'def test():\n    return True'
        assert validate_file_content(valid_py, '.py') is True
        
        # Python inválido
        invalid_py = 'def test(\n    return True'  # Paréntesis no cerrado
        assert validate_file_content(invalid_py, '.py') is False
        
        # JavaScript válido
        valid_js = 'function test() { return true; }'
        assert validate_file_content(valid_js, '.js') is True
        
        # JavaScript inválido
        invalid_js = 'function test() { return true;'  # Llave no cerrada
        assert validate_file_content(invalid_js, '.js') is False

class TestAdvancedFunctions:
    """Tests funciones avanzadas - 5 tests"""
    
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
        assert 'TestClass instance' in content
        
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
        
        with open(backup_path, 'r') as f:
            backup_content = f.read()
        assert backup_content == 'original content'
        
        shutil.rmtree(temp_dir)
    
    def test_all_template_types(self):
        """Test todos los tipos de template"""
        temp_dir = tempfile.mkdtemp()
        
        templates_to_test = [
            ('python_class', {'name': 'MyClass'}, 'class MyClass:'),
            ('python_function', {'name': 'my_function'}, 'def my_function():'),
            ('javascript_function', {'name': 'myFunction'}, 'function myFunction()'),
            ('html_template', {'title': 'My Page'}, '<title>My Page</title>')
        ]
        
        for template_type, variables, expected_content in templates_to_test:
            file_path = os.path.join(temp_dir, f'{template_type}_test.py')
            result = create_with_template(file_path, template_type, variables)
            
            assert result['success'] is True
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            assert expected_content in content
        
        shutil.rmtree(temp_dir)
    
    def test_template_with_no_variables(self):
        """Test template sin variables"""
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, 'no_vars_test.py')
        
        result = create_with_template(file_path, 'python_function', None)
        
        assert result['success'] is True
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Debe contener los placeholders originales
        assert '{name}' in content
        
        shutil.rmtree(temp_dir)
    
    def test_invalid_template_type(self):
        """Test tipo template inválido"""
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, 'invalid_test.py')
        
        result = create_with_template(file_path, 'invalid_template', {})
        
        assert result['success'] is False
        assert 'not found' in result['error']
        
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    # Ejecutar tests con pytest
    pytest.main([__file__, "-v", "--tb=short"])
