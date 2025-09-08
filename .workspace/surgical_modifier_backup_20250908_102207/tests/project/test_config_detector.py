import unittest
import tempfile
import os
from pathlib import Path
import json
from functions.project.config_detector import ConfigDetector

class TestConfigDetector(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.detector = ConfigDetector(self.test_dir)
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_detect_config_files_empty_dir(self):
        """Test detección en directorio vacío"""
        result = self.detector.detect_config_files()
        self.assertIsInstance(result, dict)
        self.assertFalse(any(result.values()))  # Todos deben ser False
    
    def test_detect_config_files_with_package_json(self):
        """Test detección con package.json presente"""
        package_json_path = Path(self.test_dir) / 'package.json'
        package_json_path.write_text('{"name": "test", "version": "1.0.0"}')
        
        result = self.detector.detect_config_files()
        self.assertTrue(result.get('package.json', False))
    
    def test_analyze_package_json_valid(self):
        """Test análisis de package.json válido"""
        package_data = {
            'name': 'test-project',
            'version': '1.0.0',
            'dependencies': {'react': '^18.0.0'},
            'devDependencies': {'typescript': '^4.0.0'}
        }
        package_json_path = Path(self.test_dir) / 'package.json'
        package_json_path.write_text(json.dumps(package_data))
        
        result = self.detector.analyze_package_json()
        self.assertIsNotNone(result)
        self.assertTrue(result['exists'])
        self.assertEqual(result['name'], 'test-project')
        self.assertIn('react', result['frameworks'])
    
    def test_analyze_tsconfig_valid(self):
        """Test análisis de tsconfig.json válido"""
        tsconfig_data = {
            'compilerOptions': {
                'strict': True,
                'target': 'es6',
                'paths': {'@/*': ['src/*']}
            }
        }
        tsconfig_path = Path(self.test_dir) / 'tsconfig.json'
        tsconfig_path.write_text(json.dumps(tsconfig_data))
        
        result = self.detector.analyze_tsconfig()
        self.assertIsNotNone(result)
        self.assertTrue(result['exists'])
        self.assertTrue(result['strict_mode'])
        self.assertEqual(result['target'], 'es6')
    
    def test_get_project_summary(self):
        """Test resumen completo del proyecto"""
        summary = self.detector.get_project_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn('project_path', summary)
        self.assertIn('config_files_found', summary)
        self.assertIn('total_config_files', summary)

if __name__ == '__main__':
    unittest.main()
