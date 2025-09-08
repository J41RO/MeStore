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

def get_coordinator_for_technology(technology: str) -> str:
    """
    Retorna el nombre del coordinador para una tecnología específica.
    Args:
        technology: Tecnología detectada
    Returns:
        str: Nombre del coordinador
    """
    coordinator_mapping = {
        'python': 'python',
        'typescript': 'typescript',
        'typescript_react': 'typescript_react',
        'javascript': 'javascript',
        'javascript_react': 'javascript_react',
        'vue': 'vue',
        'svelte': 'svelte'
    }
    return coordinator_mapping.get(technology, 'base')  # fallback a base

def analyze_file_context(file_path: str) -> Dict[str, Any]:
    """
    Analiza el contexto de un archivo específico.
    Args:
        file_path: Ruta del archivo a analizar
    Returns:
        Dict con información del contexto del archivo
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Detectar framework
        framework = 'unknown'
        if 'react' in content.lower() or 'import React' in content:
            framework = 'react'
        elif 'vue' in content.lower() or '@vue' in content:
            framework = 'vue'
        elif 'angular' in content.lower() or '@angular' in content:
            framework = 'angular'
        
        context = {
            'file_path': file_path,
            'extension': Path(file_path).suffix,
            'technology': detect_technology_by_extension(file_path),
            'framework': framework,
            'lines_count': len(content.split('\n')),
            'has_imports': 'import ' in content,
            'has_functions': 'def ' in content or 'function ' in content,
            'has_classes': 'class ' in content,
            'has_jsx': '<' in content and '>' in content and Path(file_path).suffix in ['.jsx', '.tsx'],
            'has_typescript': ': ' in content and Path(file_path).suffix in ['.ts', '.tsx'],
            'content_preview': content[:200] if content else '',
            'file_size': len(content.encode('utf-8')),
            'imports': [line.strip() for line in content.split('\n') if line.strip().startswith('import ')]
        }
        
        return context
    except Exception as e:
        return {
            'file_path': file_path,
            'error': str(e),
            'technology': 'unknown',
            'framework': 'unknown',
            'extension': Path(file_path).suffix if file_path else '',
            'lines_count': 0,
            'has_imports': False,
            'has_functions': False,
            'has_classes': False,
            'has_jsx': False,
            'has_typescript': False,
            'content_preview': '',
            'file_size': 0,
            'imports': []
        }

def _extract_tsconfig_aliases(tsconfig_path: Path) -> Dict[str, str]:
    """Extrae alias de paths desde tsconfig.json"""
    try:
        with open(tsconfig_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Remover comentarios // antes de parsear JSON
            lines = []
            for line in content.split('\n'):
                comment_pos = line.find('//')
                if comment_pos != -1:
                    line = line[:comment_pos].rstrip()
                lines.append(line)
            clean_content = '\n'.join(lines)
            tsconfig_data = json.loads(clean_content)
        
        compiler_options = tsconfig_data.get('compilerOptions', {})
        paths = compiler_options.get('paths', {})
        
        aliases = {}
        for alias, path_list in paths.items():
            if alias.endswith('/*') and path_list:
                # @/* -> src/* se convierte en @ -> src
                clean_alias = alias[:-2]  # Quitar /*
                clean_path = path_list[0].replace('/*', '')  # Quitar /*
                aliases[clean_alias] = clean_path
        
        return aliases
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        return {}

def _analyze_python_frameworks(requirements_path: Path) -> Dict[str, Any]:
    """Analiza requirements.txt para detectar frameworks Python específicos"""
    try:
        with open(requirements_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frameworks = []
        web_frameworks = []
        
        # Detectar frameworks web
        if 'fastapi' in content.lower():
            frameworks.append('fastapi')
            web_frameworks.append('fastapi')
        elif 'django' in content.lower():
            frameworks.append('django')
            web_frameworks.append('django')
        elif 'flask' in content.lower():
            frameworks.append('flask')
            web_frameworks.append('flask')
        
        # Detectar otras tecnologías
        if 'sqlalchemy' in content.lower():
            frameworks.append('sqlalchemy')
        if 'pydantic' in content.lower():
            frameworks.append('pydantic')
        
        return {
            'frameworks': frameworks,
            'web_frameworks': web_frameworks,
            'is_web_project': len(web_frameworks) > 0
        }
    except (FileNotFoundError, UnicodeDecodeError):
        return {'frameworks': [], 'web_frameworks': [], 'is_web_project': False}

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
        'package_managers': [],
        'aliases': {},
        'subdirectories': [],
        'python_frameworks': [],
        'web_frameworks': [],
        'is_backend_project': False
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
            
            # Análisis específico para requirements.txt
            if config_file == 'requirements.txt':
                python_analysis = _analyze_python_frameworks(config_path)
                detected_technologies['python_frameworks'] = python_analysis['frameworks']
                detected_technologies['web_frameworks'] = python_analysis['web_frameworks']
                detected_technologies['is_backend_project'] = python_analysis['is_web_project']

    # Buscar en subdirectorios comunes (frontend/, backend/, client/, server/)
    common_subdirs = ['frontend', 'backend', 'client', 'server', 'web', 'api']
    for subdir in common_subdirs:
        subdir_path = project_path / subdir
        if subdir_path.exists() and subdir_path.is_dir():
            detected_technologies['subdirectories'].append(subdir)
            # Buscar archivos de configuración en subdirectorio
            for config_file, tech in config_indicators.items():
                subdir_config_path = subdir_path / config_file
                if subdir_config_path.exists():
                    detected_technologies['config_files'].append(f'{subdir}/{config_file}')
                    if tech == 'typescript' and 'typescript' not in detected_technologies['secondary']:
                        detected_technologies['secondary'].append('typescript')
                        # Extraer alias de tsconfig.json
                        if config_file == 'tsconfig.json':
                            detected_technologies['aliases'].update(_extract_tsconfig_aliases(subdir_config_path))
    
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