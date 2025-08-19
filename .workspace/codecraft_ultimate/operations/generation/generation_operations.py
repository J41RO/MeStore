"""
🚀 CodeCraft Ultimate v6.0 - Generation Operations
Intelligent code generation and scaffolding
"""

import os
import json
from typing import Any, Dict, List
from ...core.engine import ExecutionContext, OperationResult


class GenerationOperations:
    """Code generation operations"""
    
    def __init__(self, context: ExecutionContext, config: Dict[str, Any]):
        self.context = context
        self.config = config
    
    def execute(self, operation: str, args: Any) -> OperationResult:
        """Execute generation operation"""
        
        if operation == 'generate-component':
            return self._generate_component(args.type, args.name, getattr(args, 'framework', None))
        elif operation == 'generate-api':
            return self._generate_api(args.specification, getattr(args, 'type', 'rest'))
        elif operation == 'generate-tests':
            return self._generate_tests(args.file, getattr(args, 'test_framework', None))
        elif operation == 'scaffold-project':
            return self._scaffold_project(args.type, args.name, getattr(args, 'template', None))
        else:
            return OperationResult(
                success=False,
                operation=operation,
                message=f"Unknown generation operation: {operation}"
            )
    
    def _generate_component(self, comp_type: str, name: str, framework: str) -> OperationResult:
        """Generate a component"""
        
        if comp_type == 'react':
            content = self._generate_react_component(name, framework)
            file_path = f"src/components/{name}.tsx"
        elif comp_type == 'vue':
            content = self._generate_vue_component(name)
            file_path = f"src/components/{name}.vue"
        else:
            return OperationResult(
                success=False,
                operation='generate-component',
                message=f"Unsupported component type: {comp_type}"
            )
        
        # Create the file
        full_path = os.path.join(self.context.project_root, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return OperationResult(
            success=True,
            operation='generate-component',
            message=f"Generated {comp_type} component: {name}",
            data={
                'component_type': comp_type,
                'component_name': name,
                'file_path': file_path,
                'framework': framework
            },
            suggestions=[
                f"codecraft generate-tests {file_path} --test-framework=jest",
                f"Add component to your main app or router"
            ]
        )
    
    def _generate_tests(self, file_path: str, test_framework: str) -> OperationResult:
        """Generate tests for a file"""
        
        if not os.path.exists(file_path):
            return OperationResult(
                success=False,
                operation='generate-tests',
                message=f"Source file not found: {file_path}"
            )
        
        # Determine test framework if not specified
        if not test_framework:
            if file_path.endswith('.py'):
                test_framework = 'pytest'
            elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                test_framework = 'jest'
        
        # Generate test content
        test_content = self._generate_test_content(file_path, test_framework)
        
        # Determine test file path
        if test_framework == 'pytest':
            test_file = f"tests/test_{os.path.basename(file_path)}"
        else:
            test_file = file_path.replace('.', '.test.')
        
        # Write test file
        full_test_path = os.path.join(self.context.project_root, test_file)
        os.makedirs(os.path.dirname(full_test_path), exist_ok=True)
        
        with open(full_test_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        return OperationResult(
            success=True,
            operation='generate-tests',
            message=f"Generated tests for {file_path}",
            data={
                'source_file': file_path,
                'test_file': test_file,
                'test_framework': test_framework
            }
        )
    
    def _generate_react_component(self, name: str, framework: str) -> str:
        """Generate React component code"""
        return f'''import React from 'react';

interface {name}Props {{
  // Add your props here
}}

const {name}: React.FC<{name}Props> = (props) => {{
  return (
    <div className="{name.lower()}">
      <h2>{name}</h2>
      {/* Component content */}
    </div>
  );
}};

export default {name};
'''
    
    def _generate_vue_component(self, name: str) -> str:
        """Generate Vue component code"""
        return f'''<template>
  <div class="{name.lower()}">
    <h2>{name}</h2>
    <!-- Component content -->
  </div>
</template>

<script lang="ts">
import {{ defineComponent }} from 'vue';

export default defineComponent({{
  name: '{name}',
  props: {{
    // Add your props here
  }},
  setup(props) {{
    // Component logic
    return {{}};
  }}
}});
</script>

<style scoped>
.{name.lower()} {{
  /* Component styles */
}}
</style>
'''
    
    def _generate_test_content(self, file_path: str, test_framework: str) -> str:
        """Generate test content for a file"""
        
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        if test_framework == 'pytest':
            return f'''import pytest
from {file_name} import *


class Test{file_name.title()}:
    """Tests for {file_name} module"""
    
    def test_example(self):
        """Example test case"""
        assert True  # Replace with actual test
    
    def test_another_example(self):
        """Another example test case"""
        pass  # Add your test implementation
'''
        
        elif test_framework == 'jest':
            return f'''import {{ {file_name} }} from './{file_name}';

describe('{file_name}', () => {{
  test('should work correctly', () => {{
    // Add your test implementation
    expect(true).toBe(true);
  }});
  
  test('should handle edge cases', () => {{
    // Add more test cases
  }});
}});
'''
        
        return "// Add your tests here\n"
    
    def _scaffold_web_project(self, project_dir: str, name: str, template: str):
        """Scaffold a web project"""
        
        # Create package.json
        package_json = {
            "name": name,
            "version": "1.0.0",
            "description": f"{name} web application",
            "main": "src/index.js",
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0"
            },
            "devDependencies": {
                "@types/react": "^18.0.0",
                "@types/react-dom": "^18.0.0",
                "typescript": "^5.0.0"
            }
        }
        
        with open(os.path.join(project_dir, 'package.json'), 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Create basic structure
        os.makedirs(os.path.join(project_dir, 'src'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'public'), exist_ok=True)
        
        # Create index.tsx
        index_content = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''
        
        with open(os.path.join(project_dir, 'src', 'index.tsx'), 'w') as f:
            f.write(index_content)
        
        # Create App.tsx
        app_content = f'''import React from 'react';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to {name}</h1>
        <p>Your CodeCraft generated application is ready!</p>
      </header>
    </div>
  );
}}

export default App;
'''
        
        with open(os.path.join(project_dir, 'src', 'App.tsx'), 'w') as f:
            f.write(app_content)