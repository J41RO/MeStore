import pytest
import tempfile
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from coordinators.prototype_create import CreateCoordinatorPrototype
from coordinators.prototype_replace import ReplaceCoordinatorPrototype

class TestRealCoordinatorReuse:
    """Test reutilización functions content por coordinadores REALES"""
    
    def test_create_coordinator_reuses_functions(self):
        """Test prototipo CREATE reutiliza functions"""
        coordinator = CreateCoordinatorPrototype()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            temp_path = f.name
        
        try:
            result = coordinator.execute_create(temp_path, 'def test(): pass')
            assert result['success'] is True
            assert result['coordinator'] == 'CREATE (prototype)'
            assert 'ContentWriter' in result['functions_reused']
            assert 'ContentValidator' in result['functions_reused']
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_replace_coordinator_reuses_cuarteto_completo(self):
        """Test prototipo REPLACE reutiliza cuarteto completo"""
        coordinator = ReplaceCoordinatorPrototype()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write('def old_function(): pass')
            temp_path = f.name
        
        try:
            result = coordinator.execute_replace(temp_path, 'old_function', 'new_function')
            assert result['success'] is True
            assert result['coordinator'] == 'REPLACE_PROTOTYPE'
            assert result['cuarteto_completo'] is True
            assert len(result['functions_reused']) == 4
        finally:
            os.unlink(temp_path)