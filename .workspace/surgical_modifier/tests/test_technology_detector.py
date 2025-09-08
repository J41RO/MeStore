import pytest
import os
import tempfile
from pathlib import Path
from functions.analysis.technology_detector import (
    detect_technology_by_extension,
    detect_project_technology,
    get_coordinator_for_technology,
    analyze_file_context
)
from coordinators.typescript_react import TypeScriptReactCoordinator


class TestTechnologyDetector:
    """Test suite for technology detection functionality"""
    
    def test_detect_by_extension(self):
        """Test detection by file extension"""
        # Test TypeScript/React extensions
        assert detect_technology_by_extension('component.tsx') == 'typescript_react'
        assert detect_technology_by_extension('utils.ts') == 'typescript'
        
        # Test JavaScript/React extensions
        assert detect_technology_by_extension('component.jsx') == 'javascript_react'
        assert detect_technology_by_extension('script.js') == 'javascript'
        
        # Test Python extension
        assert detect_technology_by_extension('main.py') == 'python'
        
        # Test other extensions
        assert detect_technology_by_extension('App.vue') == 'vue'
        assert detect_technology_by_extension('Component.svelte') == 'svelte'
        
        # Test unknown extension
        assert detect_technology_by_extension('file.unknown') == 'unknown'
        assert detect_technology_by_extension('') == 'unknown'
        assert detect_technology_by_extension(None) == 'unknown'
    
    def test_get_coordinator_for_technology(self):
        """Test coordinator mapping for different technologies"""
        assert get_coordinator_for_technology('typescript_react') == 'typescript_react'
        assert get_coordinator_for_technology('python') == 'python'
        assert get_coordinator_for_technology('javascript') == 'javascript'
        assert get_coordinator_for_technology('unknown') == 'base'
        assert get_coordinator_for_technology('') == 'base'
    
    def test_typescript_coordinator_instantiation(self):
        """Test TypeScript coordinator can be instantiated"""
        coordinator = TypeScriptReactCoordinator()
        assert coordinator is not None
        assert hasattr(coordinator, 'execute')
        assert hasattr(coordinator, 'analyze_jsx_context')
        assert hasattr(coordinator, 'detect_hooks')
        assert hasattr(coordinator, 'validate_typescript_syntax')
    
    def test_analyze_jsx_context_with_temp_file(self):
        """Test JSX context analysis with temporary file"""
        # Create temporary TypeScript React file
        tsx_content = '''import React, { useState } from 'react';
        
interface Props {
    title: string;
    count: number;
}

const MyComponent: React.FC<Props> = ({ title, count }) => {
    const [value, setValue] = useState<string>('');
    
    return (
        <div>
            <h1>{title}</h1>
            <p>Count: {count}</p>
            <input value={value} onChange={(e) => setValue(e.target.value)} />
        </div>
    );
};

export default MyComponent;'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsx', delete=False) as f:
            f.write(tsx_content)
            temp_file = f.name
        
        try:
            coordinator = TypeScriptReactCoordinator()
            context = coordinator.analyze_jsx_context(temp_file)
            
            # Verify context analysis
            assert context['has_jsx'] == True
            assert context['has_typescript'] == True
            assert 'useState' in context['hooks_used']
            assert len(context['components']) > 0
            
        finally:
            os.unlink(temp_file)
    
    def test_analyze_file_context(self):
        """Test file context analysis"""
        # Test with JavaScript content
        js_content = '''import React from 'react';
const App = () => <div>Hello World</div>;
export default App;'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsx', delete=False) as f:
            f.write(js_content)
            temp_file = f.name
        
        try:
            context = analyze_file_context(temp_file)
            assert context['technology'] == 'javascript_react'
            assert context['has_jsx'] == True
            assert context['framework'] == 'react'
            assert len(context['imports']) > 0
            
        finally:
            os.unlink(temp_file)
    
    def test_detect_project_technology(self):
        """Test project technology detection"""
        # Create temporary directory with package.json
        with tempfile.TemporaryDirectory() as temp_dir:
            package_json = {
                'dependencies': {
                    'react': '^18.0.0',
                    'typescript': '^4.0.0'
                }
            }
            
            package_path = Path(temp_dir) / 'package.json'
            with open(package_path, 'w') as f:
                import json
                json.dump(package_json, f)
            
            # Test detection
            result = detect_project_technology(temp_dir)
            assert result['primary'] == 'typescript_react'
            assert 'package.json' in result['config_files']
    
    def test_cli_integration_simulation(self):
        """Test CLI integration by simulating the get_technology_coordinator function"""
        # Import the CLI function
        import sys
        import os
        
        # Add the CLI path
        cli_path = os.path.dirname(os.path.abspath(__file__))
        parent_path = os.path.dirname(cli_path)
        sys.path.insert(0, parent_path)
        
        try:
            # This would normally be imported from cli.py, but we'll simulate it
            def get_technology_coordinator_test(file_path):
                technology = detect_technology_by_extension(file_path)
                coordinator_name = get_coordinator_for_technology(technology)
                
                if coordinator_name == 'typescript_react':
                    return TypeScriptReactCoordinator(), technology
                else:
                    # Simulate fallback
                    return None, technology
            
            # Test TypeScript React detection
            coordinator, tech = get_technology_coordinator_test('app.tsx')
            assert tech == 'typescript_react'
            assert coordinator is not None
            assert isinstance(coordinator, TypeScriptReactCoordinator)
            
            # Test Python detection
            coordinator, tech = get_technology_coordinator_test('main.py')
            assert tech == 'python'
            
        finally:
            if parent_path in sys.path:
                sys.path.remove(parent_path)
    
    def test_fallback_behavior(self):
        """Test fallback behavior for unknown technologies"""
        # Test unknown extension
        tech = detect_technology_by_extension('file.unknown')
        assert tech == 'unknown'
        
        coordinator_name = get_coordinator_for_technology(tech)
        assert coordinator_name == 'base'
        
        # Test empty or None input
        assert detect_technology_by_extension('') == 'unknown'
        assert detect_technology_by_extension(None) == 'unknown'
    
    def test_typescript_syntax_validation(self):
        """Test TypeScript syntax validation"""
        coordinator = TypeScriptReactCoordinator()
        
        # Test valid JSX
        valid_content = '<div><span>Hello</span></div>'
        validation = coordinator.validate_typescript_syntax(valid_content)
        assert validation['valid'] == True
        
        # Test invalid JSX (unbalanced tags)
        invalid_content = '<div><span>Hello</div>'
        validation = coordinator.validate_typescript_syntax(invalid_content)
        assert validation['valid'] == False
        assert len(validation['errors']) > 0
    
    def test_hook_detection(self):
        """Test React hook detection"""
        coordinator = TypeScriptReactCoordinator()
        
        # Content with hooks
        content_with_hooks = '''
        const [state, setState] = useState(0);
        const value = useEffect(() => {}, []);
        const data = useContext(MyContext);
        '''
        
        hooks = coordinator.detect_hooks(content_with_hooks)
        assert len(hooks) >= 3  # Should detect useState, useEffect, useContext
        
        # Content without hooks
        content_without_hooks = 'const x = 5; console.log(x);'
        hooks = coordinator.detect_hooks(content_without_hooks)
        assert len(hooks) == 0


# Integration tests for CLI commands
class TestCLIIntegration:
    """Test CLI integration with technology detection"""
    
    def test_cli_help_available(self):
        """Test that CLI help is available"""
        import subprocess
        import sys
        
        # Test CLI help command
        result = subprocess.run([
            sys.executable, 'cli.py', '--help'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
        
        assert result.returncode == 0
        assert 'Surgical Modifier v6.0' in result.stdout


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
