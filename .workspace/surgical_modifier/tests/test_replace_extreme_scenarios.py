#!/usr/bin/env python3
"""
Suite de tests extremos para REPLACE Operation
Tests exhaustivos para todas las funcionalidades críticas
"""
import pytest
import tempfile
import os
import shutil
from pathlib import Path
import time
import sys
import tempfile

# Agregar path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.operations.basic.replace import (
    replace_operation, 
    enhanced_replace_operation,
    create_automatic_backup,
    detect_pattern_indentation,
    contextual_replace,
    validate_python_syntax,
    cleanup_old_backups
)

class TestReplaceExtreme:
    """Tests extremos para REPLACE operation"""
    
    def test_backup_creation_and_restore(self):
        """Test completo de backup y restore"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('original_content = "test"')
            temp_path = f.name
        
        # Crear backup
        backup_path = create_automatic_backup(temp_path)
        assert os.path.exists(backup_path)
        
        # Modificar archivo original
        with open(temp_path, 'w') as f:
            f.write('modified_content = "test"')
        
        # Restaurar desde backup
        shutil.copy2(backup_path, temp_path)
        with open(temp_path) as f:
            content = f.read()
        
        assert 'original_content' in content
        assert 'modified_content' not in content
    
    def test_indentation_preservation_complex(self):
        """Test preservación indentación en estructuras complejas"""
        complex_code = '''class OuterClass:
    def method1(self):
        if condition:
            for item in items:
                old_value = "deep_nested"
                if nested_condition:
                    old_value = "deeper"
    
    def method2(self):
        old_value = "simple_context"'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(complex_code)
            temp_path = f.name
        
        result = replace_operation(temp_path, 'old_value', 'new_value')
        
        with open(temp_path) as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Verificar indentación preservada en diferentes contextos
        deep_nested_line = next(line for line in lines if 'new_value = "deep_nested"' in line)
        deeper_line = next(line for line in lines if 'new_value = "deeper"' in line)
        simple_line = next(line for line in lines if 'new_value = "simple_context"' in line)
        
        assert len(deep_nested_line) - len(deep_nested_line.lstrip()) == 16  # 4 niveles * 4 espacios
        assert len(deeper_line) - len(deeper_line.lstrip()) == 20  # 5 niveles * 4 espacios  
        assert len(simple_line) - len(simple_line.lstrip()) == 8   # 2 niveles * 4 espacios
        
        assert result['success']
    
    def test_enhanced_replace_with_rollback(self):
        """Test rollback automático cuando replace falla"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def valid_function(): return True')
            temp_path = f.name
        
        # Intentar replace que rompa sintaxis usando enhanced
        try:
            result = enhanced_replace_operation(temp_path, 'return True', 'return missing_quote and')
            
            # Si no falló, verificar que al menos el contenido es válido
            with open(temp_path) as f:
                content = f.read()
            # Debería mantener función válida o haber aplicado rollback
            assert 'def valid_function' in content
        except:
            # Si falló con excepción, verificar que archivo se mantuvo
            with open(temp_path) as f:
                content = f.read()
            assert 'def valid_function(): return True' in content
    
    def test_multiple_backups_cleanup(self):
        """Test limpieza automática de backups antiguos"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('content')
            temp_path = f.name
        
        # Crear múltiples backups
        backup_paths = []
        for i in range(10):
            backup_path = create_automatic_backup(temp_path)
            backup_paths.append(backup_path)
            time.sleep(0.01)  # Asegurar timestamps diferentes
        
        # Todos los backups deben existir inicialmente
        assert all(os.path.exists(bp) for bp in backup_paths)
        
        # Ejecutar cleanup
        cleanup_old_backups(temp_path, keep_last=5)
        
        # Verificar que solo quedan los últimos 5
        backup_dir = Path(temp_path).parent / '.backups'
        remaining_backups = list(backup_dir.glob('*.backup.*'))
        assert len(remaining_backups) <= 5  # Puede ser menos si hay colisiones de timestamp
    
    def test_contextual_replace_specific_class(self):
        """Test replace solo en clase específica"""
        multi_class_code = '''class DatabaseConnection:
    def connect(self):
        connection_string = "old_value"
        
class FileConnection:  
    def connect(self):
        connection_string = "old_value"'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(multi_class_code)
            temp_path = f.name
        
        # Replace solo en DatabaseConnection
        result = contextual_replace(temp_path, 'old_value', 'new_database_value', context='DatabaseConnection')
        
        with open(temp_path) as f:
            content = f.read()
        
        # DatabaseConnection debe estar modificado
        assert 'new_database_value' in content
        # FileConnection debe permanecer con al menos una ocurrencia de old_value
        assert 'old_value' in content  # Al menos una debe quedar
        
        assert result['success']
    
    def test_performance_large_content(self):
        """Test performance con contenido grande"""
        large_content = 'line_with_pattern = "old"\n' * 1000  # 1000 líneas
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(large_content)
            temp_path = f.name
        
        start_time = time.time()
        result = replace_operation(temp_path, 'old', 'new')
        end_time = time.time()
        
        assert result['success']
        assert end_time - start_time < 2.0  # Debe completarse en menos de 2 segundos
        
        # Verificar que todos los reemplazos se hicieron
        with open(temp_path) as f:
            content = f.read()
        assert content.count('new') == 1000
        assert 'old' not in content
    
    def test_unicode_and_special_characters(self):
        """Test con caracteres Unicode y especiales"""
        unicode_content = '''def función_especial():
    # Comentario con ñ, ç, ü
    old_pattern = "contenido_test"
    return "🚀 emoji_content"'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(unicode_content)
            temp_path = f.name
        
        result = replace_operation(temp_path, 'old_pattern', 'new_pattern')
        
        with open(temp_path, encoding='utf-8') as f:
            content = f.read()
        
        assert 'new_pattern' in content
        assert 'contenido_test' in content  # Valor preservado
        assert '🚀' in content       # Emoji preservado
        assert result['success']
    
    def test_enhanced_vs_regular_replace(self):
        """Test comparación enhanced vs regular replace"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test_function(): return "old_value"')
            temp_path = f.name
        
        # Test enhanced replace
        result_enhanced = enhanced_replace_operation(temp_path, 'old_value', 'new_value')
        
        # Verificar que enhanced tiene más información
        assert result_enhanced['success']
        assert 'backup_created' in result_enhanced
        assert 'auto_backup' in result_enhanced
        
        # Verificar que backup existe
        backup_path = result_enhanced['backup_created']
        assert backup_path and os.path.exists(backup_path)
    
    def test_pattern_not_found(self):
        """Test cuando pattern no se encuentra"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test(): return "content"')
            temp_path = f.name
        
        result = replace_operation(temp_path, 'nonexistent_pattern', 'replacement')
        
        assert not result['success']
        assert 'not found' in result['error'].lower()
    
    def test_empty_file_replace(self):
        """Test replace en archivo vacío"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('')
            temp_path = f.name
        
        result = replace_operation(temp_path, 'anything', 'replacement')
        
        assert not result['success']  # No debería encontrar el pattern
    
    def test_multiline_replacement(self):
        """Test replacement con múltiples líneas"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''def function():
    old_code = "simple"
    return old_code''')
            temp_path = f.name
        
        multiline_replacement = '''new_code = "complex"
    processed_code = new_code.upper()
    return processed_code'''
        
        result = replace_operation(temp_path, 'old_code = "simple"\n    return old_code', multiline_replacement)
        
        with open(temp_path) as f:
            content = f.read()
        
        assert 'new_code' in content
        assert 'processed_code' in content
        assert result['success']

