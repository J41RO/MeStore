"""
Tests para TypeScript Coordinator
=================================
Verificación completa del coordinador TypeScript especializado
"""

import pytest
import os
import tempfile
from pathlib import Path
from coordinators.typescript.typescript_coordinator import TypeScriptCoordinator

class TestTypeScriptCoordinator:
    """Test suite para TypeScriptCoordinator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = TypeScriptCoordinator()
        self.temp_dir = tempfile.mkdtemp()
        
    def test_coordinator_initialization(self):
        """Test inicialización del coordinador"""
        assert self.coordinator.technology == 'typescript'
        assert '.ts' in self.coordinator.file_extensions
        assert '.tsx' not in self.coordinator.file_extensions  # Solo .ts, no .tsx
        
    def test_can_handle_ts_files(self):
        """Test que coordinador maneja archivos .ts"""
        assert self.coordinator.can_handle('test.ts') == True
        assert self.coordinator.can_handle('component.tsx') == False  # No debe manejar .tsx
        assert self.coordinator.can_handle('script.py') == False
        
    def test_typescript_syntax_validation(self):
        """Test validación sintaxis TypeScript"""
        # Sintaxis válida
        valid_content = 'interface User { name: string; age: number; }'
        result = self.coordinator.validate_typescript_syntax(valid_content)
        assert result['valid'] == True
        assert len(result['errors']) == 0
        
        # Sintaxis inválida
        invalid_content = 'interface User { name: string; age: number'  # Sin cierre
        result = self.coordinator.validate_typescript_syntax(invalid_content)
        assert result['valid'] == False
        assert len(result['errors']) > 0
        
    def test_execute_create_interface(self):
        """Test crear archivo con interface TypeScript"""
        file_path = os.path.join(self.temp_dir, 'user.ts')
        content = 'interface User {\n  name: string;\n  age: number;\n}'
        
        result = self.coordinator.execute_create(file_path, content)
        
        assert result['success'] == True
        assert os.path.exists(file_path)
        
        with open(file_path, 'r') as f:
            created_content = f.read()
        assert 'interface User' in created_content
        assert 'name: string' in created_content
        
    def test_execute_create_type_alias(self):
        """Test crear archivo con type alias TypeScript"""
        file_path = os.path.join(self.temp_dir, 'types.ts')
        content = 'type Status = \'active\' | \'inactive\';'
        
        result = self.coordinator.execute_create(file_path, content)
        
        assert result['success'] == True
        assert os.path.exists(file_path)
        
    def test_execute_replace_valid(self):
        """Test reemplazar contenido TypeScript válido"""
        file_path = os.path.join(self.temp_dir, 'replace_test.ts')
        initial_content = 'type Status = \'draft\';'
        
        # Crear archivo inicial
        with open(file_path, 'w') as f:
            f.write(initial_content)
            
        # Reemplazar contenido
        result = self.coordinator.execute_replace(
            file_path, 
            'draft', 
            'published'
        )
        
        assert result['success'] == True
        
        with open(file_path, 'r') as f:
            updated_content = f.read()
        assert 'published' in updated_content
        assert 'draft' not in updated_content
        
    def test_execute_replace_pattern_not_found(self):
        """Test reemplazo cuando patrón no existe"""
        file_path = os.path.join(self.temp_dir, 'not_found_test.ts')
        content = 'interface User { name: string; }'
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        result = self.coordinator.execute_replace(
            file_path,
            'nonexistent_pattern',
            'replacement'
        )
        
        assert result['success'] == False
        assert 'Pattern not found' in result['error']
        
    def test_execute_operation_mapping(self):
        """Test mapeo de operaciones del coordinador"""
        # Test operación create
        result = self.coordinator.execute(
            'create',
            file_path=os.path.join(self.temp_dir, 'operation_test.ts'),
            content='interface Test { id: number; }'
        )
        assert result['success'] == True
        
        # Test operación no soportada
        result = self.coordinator.execute('unsupported_operation')
        assert result['success'] == False
        assert 'not supported' in result['error']
        
    def test_get_info(self):
        """Test información del coordinador"""
        info = self.coordinator.get_info()
        
        assert info['name'] == 'TypeScriptCoordinator'
        assert info['technology'] == 'typescript'
        assert '.ts' in info['file_extensions']
        assert len(info['features']) > 0
        
    def teardown_method(self):
        """Cleanup después de cada test"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

# Tests adicionales para verificar separación con React
def test_typescript_coordinator_separation():
    """Verificar que TypeScript coordinator no maneja React"""
    coordinator = TypeScriptCoordinator()
    
    # No debe manejar archivos .tsx
    assert coordinator.can_handle('component.tsx') == False
    assert coordinator.can_handle('app.tsx') == False
    
    # Solo debe manejar .ts
    assert coordinator.can_handle('utils.ts') == True
    assert coordinator.can_handle('types.ts') == True
