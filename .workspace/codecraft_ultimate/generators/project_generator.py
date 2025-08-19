"""
🚀 CodeCraft Ultimate v6.0 - Generador de Proyectos
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from ..core.config import config
from ..core.exceptions import GenerationError


class ProjectGenerator:
    """Generador de proyectos completos"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates" / "projects"
        self.supported_types = {
            'web': self._generate_web_project,
            'api': self._generate_api_project,
            'cli': self._generate_cli_project,
            'library': self._generate_library_project,
            'microservice': self._generate_microservice_project
        }
    
    def generate_project(self, project_type: str, name: str, path: str, **options) -> Dict[str, Any]:
        """Generar proyecto completo"""
        
        if project_type not in self.supported_types:
            raise GenerationError(f"Unsupported project type: {project_type}")
        
        project_path = Path(path) / name
        
        if project_path.exists():
            raise GenerationError(f"Project directory already exists: {project_path}")
        
        try:
            # Crear directorio del proyecto
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Generar estructura específica del tipo
            generator = self.supported_types[project_type]
            result = generator(name, project_path, **options)
            
            # Generar archivos comunes
            self._generate_common_files(name, project_path, project_type, **options)
            
            return {
                'success': True,
                'project_name': name,
                'project_path': str(project_path),
                'project_type': project_type,
                'files_created': result.get('files_created', []),
                'next_steps': result.get('next_steps', [])
            }
            
        except Exception as e:
            # Limpiar en caso de error
            if project_path.exists():
                import shutil
                shutil.rmtree(project_path, ignore_errors=True)
            
            raise GenerationError(f"Project generation failed: {e}")
    
    def _generate_web_project(self, name: str, path: Path, **options) -> Dict[str, Any]:
        """Generar proyecto web"""
        
        framework = options.get('framework', 'react')
        
        if framework == 'react':
            return self._generate_react_project(name, path, **options)
        elif framework == 'vue':
            return self._generate_vue_project(name, path, **options)
        elif framework == 'vanilla':
            return self._generate_vanilla_project(name, path, **options)
        else:
            raise GenerationError(f"Unsupported web framework: {framework}")
    
    def _generate_react_project(self, name: str, path: Path, **options) -> Dict[str, Any]:
        """Generar proyecto React"""
        
        files_created = []
        
        # Crear estructura de directorios
        directories = [
            'src/components',
            'src/hooks',
            'src/utils',
            'src/styles',
            'public',
            'tests'
        ]
        
        for dir_path in directories:
            (path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # package.json
        package_json = {
            "name": name,
            "version": "1.0.0",
            "description": f"{name} React application",
            "main": "src/index.js",
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "^5.0.1"
            },
            "devDependencies": {
                "@testing-library/jest-dom": "^5.16.4",
                "@testing-library/react": "^13.3.0",
                "@testing-library/user-event": "^14.2.0"
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            }
        }
        
        with open(path / 'package.json', 'w') as f:
            json.dump(package_json, f, indent=2)
        files_created.append('package.json')
        
        # src/index.js
        index_content = f'''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''
        
        with open(path / 'src' / 'index.js', 'w') as f:
            f.write(index_content)
        files_created.append('src/index.js')
        
        # src/App.js
        app_content = f'''import React from 'react';
import './styles/App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to {name}</h1>
        <p>Your React application is ready!</p>
      </header>
    </div>
  );
}}

export default App;
'''
        
        with open(path / 'src' / 'App.js', 'w') as f:
            f.write(app_content)
        files_created.append('src/App.js')
        
        # CSS básico
        css_content = '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
'''
        
        with open(path / 'src' / 'styles' / 'App.css', 'w') as f:
            f.write(css_content)
        files_created.append('src/styles/App.css')
        
        with open(path / 'src' / 'styles' / 'index.css', 'w') as f:
            f.write(css_content)
        files_created.append('src/styles/index.css')
        
        # public/index.html
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{name}</title>
</head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
</body>
</html>
'''
        
        with open(path / 'public' / 'index.html', 'w') as f:
            f.write(html_content)
        files_created.append('public/index.html')
        
        return {
            'files_created': files_created,
            'next_steps': [
                'npm install',
                'npm start',
                'Visit http://localhost:3000'
            ]
        }
    
    def _generate_api_project(self, name: str, path: Path, **options) -> Dict[str, Any]:
        """Generar proyecto API"""
        
        framework = options.get('framework', 'fastapi')
        
        files_created = []
        
        # Crear estructura
        directories = [
            'app/api',
            'app/core',
            'app/models',
            'app/services',
            'tests'
        ]
        
        for dir_path in directories:
            (path / dir_path).mkdir(parents=True, exist_ok=True)
        
        if framework == 'fastapi':
            # requirements.txt
            requirements = '''fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
'''
            
            with open(path / 'requirements.txt', 'w') as f:
                f.write(requirements)
            files_created.append('requirements.txt')
            
            # main.py
            main_content = f'''from fastapi import FastAPI
from app.api import router

app = FastAPI(
    title="{name} API",
    description="API para {name}",
    version="1.0.0"
)

app.include_router(router.api_router, prefix="/api")

@app.get("/")
async def root():
    return {{"message": "Welcome to {name} API"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
            
            with open(path / 'main.py', 'w') as f:
                f.write(main_content)
            files_created.append('main.py')
            
        return {
            'files_created': files_created,
            'next_steps': [
                'pip install -r requirements.txt',
                'python main.py',
                'Visit http://localhost:8000/docs'
            ]
        }
    
    def _generate_cli_project(self, name: str, path: Path, **options) -> Dict[str, Any]:
        """Generar proyecto CLI"""
        
        files_created = []
        
        # Crear estructura
        directories = [
            f'{name}/commands',
            f'{name}/utils',
            'tests'
        ]
        
        for dir_path in directories:
            (path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # setup.py
        setup_content = f'''from setuptools import setup, find_packages

setup(
    name="{name}",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0"
    ],
    entry_points={{
        'console_scripts': [
            '{name}={name}.cli:main',
        ],
    }},
)
'''
        
        with open(path / 'setup.py', 'w') as f:
            f.write(setup_content)
        files_created.append('setup.py')
        
        return {
            'files_created': files_created,
            'next_steps': [
                'pip install -e .',
                f'{name} --help'
            ]
        }
    
    def _generate_common_files(self, name: str, path: Path, project_type: str, **options):
        """Generar archivos comunes a todos los proyectos"""
        
        # .gitignore
        gitignore_content = '''# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
build/
dist/
*.egg-info/

# Logs
*.log
logs/
'''
        
        with open(path / '.gitignore', 'w') as f:
            f.write(gitignore_content)
        
        # README.md
        readme_content = f'''# {name}

## Description
{options.get('description', f'A {project_type} project generated with CodeCraft Ultimate v6.0')}

## Installation
```bash
# Installation instructions here
```

## Usage
```bash
# Usage instructions here
```

## Development
```bash
# Development setup instructions here
```

## Generated with CodeCraft Ultimate v6.0
This project was generated using CodeCraft Ultimate v6.0 - AI-human collaborative development tool.
'''
        
        with open(path / 'README.md', 'w') as f:
            f.write(readme_content)