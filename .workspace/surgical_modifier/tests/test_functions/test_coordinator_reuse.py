# Crear tests/test_functions/test_coordinator_reuse.py
import pytest
import tempfile
import os
import sys

# Agregar path del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from coordinators.prototype_replace import ReplaceCoordinatorPrototype
from coordinators.create import CreateCoordinator

class TestCoordinatorReuse:
    """Test reutilización modular de functions content por coordinadores"""
    
    def test_replace_coordinator_reuses_cuarteto_completo(self):
        """Test que REPLACE reutiliza las 4 functions del cuarteto"""
        coordinator = ReplaceCoordinatorPrototype()
        
        # Crear archivo temporal para test
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write('def old_function():\n    pass\n')
            temp_path = f.name
        
        try:
            # Ejecutar reemplazo
            result = coordinator.execute_replace(temp_path, 'old_function', 'new_function')
            
            # Verificaciones
            assert result['success'] is True
            assert result['coordinator'] == 'REPLACE_PROTOTYPE'
            assert result['cuarteto_completo'] is True
            assert len(result['functions_reused']) == 4
            
            # Verificar que todas las functions fueron usadas
            expected_functions = ['ContentReader', 'ContentWriter', 'ContentCache', 'ContentValidator']
            for func in expected_functions:
                assert func in result['functions_reused']
            
            # Verificar que el reemplazo se aplicó
            with open(temp_path, 'r') as f:
                content = f.read()
            assert 'new_function' in content
            assert 'old_function' not in content
            
        finally:
            os.unlink(temp_path)
    
    def test_create_coordinator_enhanced_reuse(self):
        """Test que CREATE mejorado reutiliza functions modulares"""
        coordinator = CreateCoordinator()
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            temp_path = f.name
        
        # Eliminar archivo para test de creación limpia
        os.unlink(temp_path)
        
        try:
            # Ejecutar creación
            result = coordinator.execute_create(temp_path, 'def test_function():\n    return "test"', validate=True)
            
            # Verificaciones
            assert result['success'] is True
            assert result['coordinator'] == 'CREATE_ENHANCED'
            assert result['verification_completed'] is True
            assert len(result['functions_reused']) == 4
            
            # Verificar archivo creado
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                content = f.read()
            assert 'test_function' in content
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_functions_independence(self):
        """Test que functions son independientes y modulares"""
        from functions.content.reader import ContentReader
        from functions.content.writer import ContentWriter
        from functions.content.cache import ContentCache
        from functions.content.validator import ContentValidator
        
        # Cada function debe ser instanciable independientemente
        reader = ContentReader()
        writer = ContentWriter()
        cache = ContentCache()
        validator = ContentValidator()
        
        assert reader is not None
        assert writer is not None
        assert cache is not None
        assert validator is not None
        
        # Test de uso individual
        test_content = "def test(): pass"
        validation = validator.validate_content(test_content, ['not_empty'])
        assert validation['valid'] is True
    
    def test_modular_reuse_patterns(self):
        """Test patrones de reutilización modular"""
        replace_coord = ReplaceCoordinatorPrototype()
        create_coord = CreateCoordinator()
        
        # Obtener información de reutilización
        replace_info = replace_coord.get_reuse_info()
        create_info = create_coord.get_reuse_info()
        
        # Verificar que ambos coordinadores reutilizan functions
        assert replace_info['total_functions_reused'] == 4
        assert create_info['total_functions_reused'] == 4
        assert replace_info['modular_design'] is True
        assert create_info['modular_reuse'] is True
        
        # Verificar que pueden usar diferentes combinaciones
        assert 'ContentReader' in replace_info['functions']
        assert 'ContentWriter' in create_info['functions']