import unittest
import tempfile
import os
from coordinators.react.react_coordinator import ReactCoordinator

class TestReactCoordinator(unittest.TestCase):
    
    def setUp(self):
        self.coordinator = ReactCoordinator()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Cleanup temp files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_react_coordinator_create(self):
        """Test crear componente React"""
        file_path = os.path.join(self.temp_dir, 'TestComponent.tsx')
        content = "const TestComponent = () => <div>Test</div>;"
        
        result = self.coordinator.execute('create', file_path, content=content)
        
        self.assertTrue(result.get('success', False))
        self.assertTrue(os.path.exists(file_path))
        
    def test_jsx_analysis(self):
        """Test análisis JSX"""
        content = "const Button = ({onClick}) => <button onClick={onClick}>Click</button>;"
        analysis = self.coordinator._analyze_react_content('test.jsx', content)
        
        self.assertTrue(analysis['has_jsx'])
        self.assertTrue(analysis['has_react_imports'] == False)  # No import in this example
        self.assertIn(analysis['component_type'], ['functional_arrow', 'functional_declaration'])
        
    def test_typescript_integration(self):
        """Test que React usa capacidades TypeScript"""
        # Verify inheritance from TypeScriptReactCoordinator
        from coordinators.typescript_react import TypeScriptReactCoordinator
        self.assertIsInstance(self.coordinator, TypeScriptReactCoordinator)

if __name__ == '__main__':
    unittest.main()
