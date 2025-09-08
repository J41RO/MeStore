import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, Mock

# Agregar path del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from functions.validation.path_checker import PathChecker, validate_path, check_permissions, ensure_parent_dirs


class TestPathChecker:
    """Tests unitarios para PathChecker - validación de rutas y permisos"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.path_checker = PathChecker()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup después de cada test"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_path_valid_file(self):
        """Test validación de ruta válida para archivo"""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        result = self.path_checker.validate_path(test_file)
        
        assert result['success'] is True
        assert result['path'] == os.path.normpath(test_file)
        assert 'absolute_path' in result
        assert result['parent_exists'] is True
        assert result['parent_writable'] is True
        assert not result['errors']
    
    def test_validate_path_existing_file(self):
        """Test validación de archivo existente"""
        test_file = os.path.join(self.temp_dir, 'existing.txt')
        with open(test_file, 'w') as f:
            f.write('test')
            
        result = self.path_checker.validate_path(test_file)
        
        assert result['success'] is True
        assert result['exists'] is True
        assert result['is_file'] is True
        assert result['is_directory'] is False
    
    def test_validate_path_existing_directory(self):
        """Test validación falla cuando path es directorio"""
        test_dir = os.path.join(self.temp_dir, 'testdir')
        os.makedirs(test_dir)
        
        result = self.path_checker.validate_path(test_dir)
        
        assert result['success'] is False
        assert result['is_directory'] is True
        assert 'Path is directory, not file' in str(result['errors'])
    
    def test_validate_path_nonexistent_parent(self):
        """Test validación falla cuando directorio padre no existe"""
        test_file = os.path.join(self.temp_dir, 'nonexistent', 'deep', 'test.txt')
        result = self.path_checker.validate_path(test_file)
        
        assert result['success'] is False
        assert result['parent_exists'] is False
        assert any('Parent directory does not exist' in str(error) for error in result['errors'])
    
    def test_validate_path_invalid_filename_empty(self):
        """Test validación falla con nombre de archivo vacío"""
        test_path = os.path.join(self.temp_dir, 'file_without_extension')
        # Crear path que resulte en filename vacío de otra manera
        import pathlib
        empty_path = pathlib.Path(test_path).parent / ''
        result = self.path_checker.validate_path(str(empty_path))
        
        # Debe fallar porque es directorio, no archivo
        assert result['success'] is False
        assert result['is_directory'] is True
    
    def test_validate_path_invalid_characters(self):
        """Test validación falla con caracteres inválidos"""
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        
        for char in invalid_chars:
            test_file = os.path.join(self.temp_dir, f'test{char}file.txt')
            result = self.path_checker.validate_path(test_file)
            
            assert result['success'] is False
            assert any('Invalid characters' in str(error) for error in result['errors'])
    
    def test_validate_path_normalize_path(self):
        """Test normalización de rutas con ~ y .."""
        with patch('os.path.expanduser') as mock_expand:
            mock_expand.return_value = '/home/user/test.txt'
            
            result = self.path_checker.validate_path('~/test.txt')
            
            assert 'test.txt' in result['path']
            mock_expand.assert_called_once()
    
    def test_validate_path_exception_handling(self):
        """Test manejo de excepciones durante validación"""
        with patch('pathlib.Path') as mock_path:
            mock_path.side_effect = Exception("Test exception")
            
            result = self.path_checker.validate_path('/any/path')
            
            assert result['success'] is False
            assert 'Validation exception' in str(result['errors'])
    
    def test_check_permissions_valid_directory(self):
        """Test verificación de permisos en directorio válido"""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        result = self.path_checker.check_permissions(test_file)
        
        assert result['success'] is True
        assert result['parent_exists'] is True
        assert result['parent_writable'] is True
        assert result['parent_readable'] is True
        assert result['can_create'] is True
    
    def test_check_permissions_existing_file(self):
        """Test verificación de permisos en archivo existente"""
        test_file = os.path.join(self.temp_dir, 'existing.txt')
        with open(test_file, 'w') as f:
            f.write('test')
            
        result = self.path_checker.check_permissions(test_file)
        
        assert result['file_exists'] is True
        assert result['file_readable'] is True
        assert result['file_writable'] is True
    
    def test_check_permissions_nonexistent_parent(self):
        """Test verificación de permisos falla con padre inexistente"""
        test_file = '/nonexistent/directory/test.txt'
        result = self.path_checker.check_permissions(test_file)
        
        assert result['success'] is False
        assert result['parent_exists'] is False
        assert 'Parent directory not accessible' in str(result['errors'])
    
    def test_check_permissions_directory_as_file(self):
        """Test verificación falla cuando se pasa directorio como archivo"""
        result = self.path_checker.check_permissions(self.temp_dir)
        
        assert result['success'] is False
        assert 'Path is directory, expected file' in str(result['errors'])
    
    @patch('os.access')
    def test_check_permissions_no_write_access(self, mock_access):
        """Test verificación detecta falta de permisos de escritura"""
        def access_side_effect(path, mode):
            if mode == os.W_OK:
                return False
            return True
            
        mock_access.side_effect = access_side_effect
        
        test_file = os.path.join(self.temp_dir, 'test.txt')
        result = self.path_checker.check_permissions(test_file)
        
        assert result['parent_writable'] is False
        assert result['can_create'] is False
    
    def test_check_permissions_exception_handling(self):
        """Test manejo de excepciones en verificación de permisos"""
        with patch('pathlib.Path') as mock_path:
            mock_path.side_effect = Exception("Permission test exception")
            
            result = self.path_checker.check_permissions('/any/path')
            
            assert result['success'] is False
            assert 'Permission check exception' in str(result['errors'])
    
    def test_ensure_parent_dirs_already_exists(self):
        """Test creación de directorios cuando ya existen"""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        result = self.path_checker.ensure_parent_dirs(test_file)
        
        assert result['success'] is True
        assert result['existed_before'] is True
        assert result['created_dirs'] == []
        assert result['parent_path'] == self.temp_dir
    
    def test_ensure_parent_dirs_create_single(self):
        """Test creación de directorio padre único"""
        new_dir = os.path.join(self.temp_dir, 'newdir')
        test_file = os.path.join(new_dir, 'test.txt')
        
        result = self.path_checker.ensure_parent_dirs(test_file)
        
        assert result['success'] is True
        assert result['existed_before'] is False
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)
    
    def test_ensure_parent_dirs_create_nested(self):
        """Test creación de directorios anidados"""
        nested_path = os.path.join(self.temp_dir, 'level1', 'level2', 'level3')
        test_file = os.path.join(nested_path, 'test.txt')
        
        result = self.path_checker.ensure_parent_dirs(test_file)
        
        assert result['success'] is True
        assert result['existed_before'] is False
        assert os.path.exists(nested_path)
        assert os.path.isdir(nested_path)
    
    def test_ensure_parent_dirs_custom_mode(self):
        """Test creación de directorios con permisos personalizados"""
        new_dir = os.path.join(self.temp_dir, 'custom_mode')
        test_file = os.path.join(new_dir, 'test.txt')
        
        result = self.path_checker.ensure_parent_dirs(test_file, mode=0o750)
        
        assert result['success'] is True
        assert os.path.exists(new_dir)
        # Verificar permisos (puede variar según sistema)
        stat_info = os.stat(new_dir)
        assert stat_info.st_mode & 0o777 == 0o750
    
    @patch('pathlib.Path.mkdir')
    def test_ensure_parent_dirs_permission_error(self, mock_mkdir):
        """Test manejo de error de permisos al crear directorios"""
        mock_mkdir.side_effect = PermissionError("Permission denied")
        
        test_file = os.path.join(self.temp_dir, 'restricted', 'test.txt')
        result = self.path_checker.ensure_parent_dirs(test_file)
        
        assert result['success'] is False
        assert 'Permission denied' in str(result['errors'])
    
    def test_ensure_parent_dirs_exception_handling(self):
        """Test manejo de excepciones generales en creación"""
        with patch('pathlib.Path') as mock_path:
            mock_path.side_effect = Exception("Creation test exception")
            
            result = self.path_checker.ensure_parent_dirs('/any/path')
            
            assert result['success'] is False
            assert 'Directory creation exception' in str(result['errors'])


class TestPathCheckerConvenienceFunctions:
    """Tests para funciones de conveniencia"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup después de cada test"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_path_convenience_function(self):
        """Test función de conveniencia validate_path"""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        result = validate_path(test_file)
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'path' in result
    
    def test_check_permissions_convenience_function(self):
        """Test función de conveniencia check_permissions"""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        result = check_permissions(test_file)
        
        assert isinstance(result, dict)
        assert 'parent_exists' in result
        assert 'can_create' in result
    
    def test_ensure_parent_dirs_convenience_function(self):
        """Test función de conveniencia ensure_parent_dirs"""
        test_file = os.path.join(self.temp_dir, 'newdir', 'test.txt')
        result = ensure_parent_dirs(test_file)
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'parent_path' in result


class TestPathCheckerEdgeCases:
    """Tests para casos edge y situaciones especiales"""
    
    def test_validate_path_root_directory(self):
        """Test validación de directorio root"""
        checker = PathChecker()
        result = checker.validate_path('/')
        
        assert result['success'] is False
        assert result['is_directory'] is True
    
    def test_validate_path_very_long_path(self):
        """Test validación de rutas muy largas"""
        checker = PathChecker()
        long_filename = 'a' * 300  # Nombre muy largo
        result = checker.validate_path(f'/tmp/{long_filename}')
        
        # Debería manejar rutas largas sin crash
        assert isinstance(result, dict)
        assert 'success' in result
    
    def test_validate_path_unicode_characters(self):
        """Test validación con caracteres Unicode"""
        checker = PathChecker()
        unicode_file = '/tmp/test_file_ñáéíóú_中文.txt'
        result = checker.validate_path(unicode_file)
        
        assert isinstance(result, dict)
        assert 'success' in result
        # Unicode debería ser válido
    
    def test_validate_path_relative_paths(self):
        """Test validación de rutas relativas"""
        checker = PathChecker()
        relative_path = '../test/file.txt'
        result = checker.validate_path(relative_path)
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'absolute_path' in result
    
    @patch('os.path.normpath')
    def test_validate_path_normpath_exception(self, mock_normpath):
        """Test manejo de excepción en normalización de rutas"""
        mock_normpath.side_effect = Exception("Normpath error")
        
        checker = PathChecker()
        result = checker.validate_path('/any/path')
        
        assert result['success'] is False
        assert 'Validation exception' in str(result['errors'])