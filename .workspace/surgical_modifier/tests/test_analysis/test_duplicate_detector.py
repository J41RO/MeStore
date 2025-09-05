import pytest
import tempfile
import os

from functions.analysis.duplicate_detector import DuplicateDetector

class TestDuplicateDetector:
    """Tests para DuplicateDetector"""
    
    def setup_method(self):
        self.detector = DuplicateDetector()
        
    def test_detector_initialization(self):
        """Test básico de inicialización"""
        assert self.detector is not None
        
    def test_find_typescript_interface_duplicates(self):
        """Test de detección de interfaces TypeScript duplicadas"""
        ts_content = '''
interface User {
    name: string;
}

interface User {
    age: number;
}

interface Product {
    id: number;
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write(ts_content)
            f.flush()
            
            issues = self.detector.find_duplicate_interfaces(f.name, ts_content)
            assert len(issues) == 1
            assert issues[0].type == 'duplicate_interface'
            assert 'User' in issues[0].message
            assert '2 veces' in issues[0].message
            
        os.unlink(f.name)
        
    def test_find_python_function_duplicates(self):
        """Test de detección de funciones Python duplicadas"""
        python_content = '''
def calculate_total(items):
    return sum(items)

def process_data(data):
    return data.strip()

def calculate_total(values):
    return sum(values) * 1.1
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_content)
            f.flush()
            
            issues = self.detector.find_duplicate_functions(f.name, python_content)
            assert len(issues) == 1
            assert issues[0].type == 'duplicate_function'
            assert 'calculate_total' in issues[0].message
            
        os.unlink(f.name)
        
    def test_find_javascript_function_duplicates(self):
        """Test de detección de funciones JavaScript duplicadas"""
        js_content = '''
function processData(data) {
    return data.filter(x => x > 0);
}

const calculateSum = (values) => {
    return values.reduce((a, b) => a + b, 0);
};

function processData(input) {
    return input.map(x => x * 2);
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(js_content)
            f.flush()
            
            issues = self.detector.find_duplicate_functions(f.name, js_content)
            assert len(issues) == 1
            assert issues[0].type == 'duplicate_function'
            assert 'processData' in issues[0].message
            
        os.unlink(f.name)
        
    def test_no_duplicates_clean_file(self):
        """Test con archivo sin duplicados"""
        clean_content = '''
interface User {
    name: string;
}

interface Product {
    id: number;
}

function processUser(user) {
    return user.name;
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write(clean_content)
            f.flush()
            
            issues = self.detector.detect_all_duplicates(f.name, clean_content)
            assert len(issues) == 0
            
        os.unlink(f.name)
        
    def test_get_duplicate_summary(self):
        """Test de generación de resumen"""
        # Crear issues de prueba
        from functions.analysis.types import StructuralIssue
        
        issues = [
            StructuralIssue(
                type='duplicate_interface',
                severity='warning',
                file_path='/test/file.ts',
                line_number=1,
                message='Interface duplicada: User',
                details={}
            ),
            StructuralIssue(
                type='duplicate_function',
                severity='warning',
                file_path='/test/file.js',
                line_number=5,
                message='Función duplicada: process',
                details={}
            )
        ]
        
        summary = self.detector.get_duplicate_summary(issues)
        assert summary['total_duplicates'] == 2
        assert summary['by_type']['duplicate_interface'] == 1
        assert summary['by_type']['duplicate_function'] == 1
        assert summary['by_severity']['warning'] == 2
        assert summary['files_affected'] == 2