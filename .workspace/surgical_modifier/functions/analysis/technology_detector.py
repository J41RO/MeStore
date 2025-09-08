import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from config import DEFAULT_CONFIG


def detect_technology_by_extension(file_path: str) -> str:
    """
    Detecta la tecnología basada en la extensión del archivo.
    
    Args:
        file_path: Ruta del archivo a analizar
        
    Returns:
        str: Tecnología detectada ('python', 'typescript_react', etc.)
    """
    if not file_path:
        return 'unknown'
        
    # Obtener extensión del archivo
    file_extension = Path(file_path).suffix.lower()
    
    # Obtener mapeo de tecnologías desde config
    technology_mapping = DEFAULT_CONFIG.get('technology_mapping', {})
    
    # Detectar tecnología por extensión
    technology = technology_mapping.get(file_extension, 'unknown')
    
    return technology


def detect_project_technology(project_root: str) -> Dict[str, Any]:
    """
    Detecta la tecnología principal del proyecto analizando archivos de configuración.
    
    Args:
        project_root: Directorio raíz del proyecto
        
    Returns:
        Dict con información de tecnologías detectadas
    """
    project_path = Path(project_root)
    detected_technologies = {
        'primary': 'unknown',
        'secondary': [],
        'config_files': [],
        'package_managers': []
    }
    
    # Verificar archivos de configuración comunes
    config_indicators = {
        'tsconfig.json': 'typescript',
        'package.json': 'javascript',
        'requirements.txt': 'python',
        'pyproject.toml': 'python',
        'Cargo.toml': 'rust',
        'go.mod': 'go',
        'pom.xml': 'java'
    }
    
    for config_file, tech in config_indicators.items():
        config_path = project_path / config_file
        if config_path.exists():
            detected_technologies['config_files'].append(config_file)
            if detected_technologies['primary'] == 'unknown':
                detected_technologies['primary'] = tech
            elif tech not in detected_technologies['secondary']:
                detected_technologies['secondary'].append(tech)
    
    # Analizar package.json para detectar React/Vue/Angular
    package_json_path = project_path / 'package.json'
    if package_json_path.exists():
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                
            dependencies = {**package_data.get('dependencies', {}), 
                          **package_data.get('devDependencies', {})}
            
            if 'react' in dependencies:
                detected_technologies['primary'] = 'typescript_react' if 'typescript' in dependencies else 'javascript_react'
            elif 'vue' in dependencies:
                detected_technologies['primary'] = 'vue'
            elif '@angular/core' in dependencies:
                detected_technologies['primary'] = 'angular'
                
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    return detected_technologies


def get_coordinator_for_technology(technology: str) -> str:
    """
    Mapea tecnología detectada a coordinador específico.
    
    Args:
        technology: Tecnología detectada
        
    Returns:
        str: Nombre del coordinador a usar
    """
    coordinator_mapping = {
        'python': 'python',
        'typescript_react': 'typescript_react',
        'typescript': 'typescript',
        'javascript_react': 'javascript_react', 
        'javascript': 'javascript',
        'vue': 'vue',
        'svelte': 'svelte',
        'unknown': 'base'  # Fallback al coordinador base
    }
    
    return coordinator_mapping.get(technology, 'base')


def analyze_file_context(file_path: str) -> Dict[str, Any]:
    """
    Analiza contexto adicional del archivo para detección más precisa.
    
    Args:
        file_path: Ruta del archivo a analizar
        
    Returns:
        Dict con contexto del archivo
    """
    context = {
        'technology': 'unknown',
        'framework': None,
        'has_jsx': False,
        'has_typescript': False,
        'imports': []
    }
    
    if not os.path.exists(file_path):
        return context
        
    # Detectar por extensión primero
    context['technology'] = detect_technology_by_extension(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Detectar JSX
        jsx_indicators = ['<', 'jsx', 'React.createElement', 'createElement']
        context['has_jsx'] = any(indicator in content for indicator in jsx_indicators if '<' in content and '>' in content)
        
        # Detectar TypeScript
        ts_indicators = [': string', ': number', ': boolean', 'interface ', 'type ', 'enum ']
        context['has_typescript'] = any(indicator in content for indicator in ts_indicators)
        
        # Extraer imports básicos
        lines = content.split('\n')
        for line in lines[:20]:  # Solo primeras 20 líneas
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                context['imports'].append(line)
                
        # Detectar framework por imports
        if any('react' in imp.lower() for imp in context['imports']):
            context['framework'] = 'react'
        elif any('vue' in imp.lower() for imp in context['imports']):
            context['framework'] = 'vue'
        elif any('angular' in imp.lower() for imp in context['imports']):
            context['framework'] = 'angular'
            
    except (UnicodeDecodeError, FileNotFoundError):
        pass
        
    return context
