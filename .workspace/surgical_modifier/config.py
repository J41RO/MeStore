"""
Configuración del sistema Surgical Modifier
"""

from pathlib import Path
import os
from functions.project.config_detector import ConfigDetector
from functions.project.dependency_analyzer import DependencyAnalyzer
from functions.project.alias_resolver import AliasResolver

# Configuración del proyecto
PROJECT_ROOT = Path(__file__).parent
CONFIG_DIR = PROJECT_ROOT / "config"
LOGS_DIR = PROJECT_ROOT / "logs"
BACKUP_DIR = PROJECT_ROOT / "backups"

# Configuración por defecto
DEFAULT_CONFIG = {
    "version": "0.1.0",
    "backup_enabled": True,
    "verbose": False,
    "dry_run": False,
    "max_backup_files": 10,
    "backup_retention_days": 30,
    "logging_level": "INFO",
    "supported_extensions": [".py", ".js", ".ts", ".json", ".yaml", ".yml"],
    "excluded_dirs": ["__pycache__", ".git", "node_modules", ".pytest_cache"],
    "max_file_size_mb": 10,
    "log_level": "INFO",
    "encoding": "utf-8",
    "technology_mapping": {
        ".py": "python",
        ".tsx": "typescript_react", 
        ".ts": "typescript",
        ".jsx": "javascript_react",
        ".js": "javascript",
        ".vue": "vue",
        ".svelte": "svelte"
    }
}

# Constantes requeridas por los tests
LOG_LEVEL = DEFAULT_CONFIG["log_level"]

# Extensiones soportadas
SUPPORTED_EXTENSIONS = DEFAULT_CONFIG["supported_extensions"]

# Directorios excluidos  
EXCLUDED_DIRS = DEFAULT_CONFIG["excluded_dirs"]

def get_config():
    """Obtener configuración actual"""
    return DEFAULT_CONFIG.copy()

def update_config(updates):
    """Actualizar configuración"""
    DEFAULT_CONFIG.update(updates)
    return DEFAULT_CONFIG

def get_coordinator_config():
    """Obtener configuración para coordinadores"""
    return {
        "max_retries": 3,
        "timeout": 30,
        "log_level": LOG_LEVEL
    }

# Constante adicional requerida por tests
MAX_FILE_SIZE = DEFAULT_CONFIG["max_file_size_mb"] * 1024 * 1024  # En bytes

def validate_config(config_dict=None):
    """Validar configuración del sistema"""
    if config_dict is None:
        config_dict = DEFAULT_CONFIG
    
    required_fields = [
        "version", "backup_enabled", "verbose", "dry_run",
        "max_backup_files", "backup_retention_days", "supported_extensions",
        "excluded_dirs", "log_level", "max_file_size_mb"
    ]
    
    for field in required_fields:
        if field not in config_dict:
            raise ValueError(f"Missing required config field: {field}")
    
    return True

# Constante ENCODING requerida por tests
ENCODING = DEFAULT_CONFIG["encoding"]


def detect_project_config(project_path: str = '.') -> dict:
    """
    Detecta automáticamente la configuración del proyecto basada en archivos presentes.
    
    Args:
        project_path: Ruta del proyecto a analizar (por defecto directorio actual)
        
    Returns:
        Diccionario con configuración detectada automáticamente
    """
    try:
        # Inicializar detectores
        config_detector = ConfigDetector(project_path)
        dependency_analyzer = DependencyAnalyzer(project_path)
        alias_resolver = AliasResolver(project_path)
        
        # Obtener análisis completo
        project_summary = config_detector.get_project_summary()
        dependency_analysis = dependency_analyzer.get_complete_analysis()
        alias_analysis = alias_resolver.get_complete_analysis()
        
        # Configuración detectada
        detected_config = {
            'project_type': _determine_project_type(project_summary, dependency_analysis),
            'technology_stack': _extract_technology_stack(dependency_analysis),
            'build_configuration': _extract_build_config(dependency_analysis),
            'alias_configuration': _extract_alias_config(alias_analysis),
            'recommended_settings': _generate_recommended_settings(project_summary, dependency_analysis)
        }
        
        return {
            'detected': True,
            'project_path': project_path,
            'config': detected_config,
            'raw_analysis': {
                'config_files': project_summary,
                'dependencies': dependency_analysis,
                'aliases': alias_analysis
            }
        }
        
    except Exception as e:
        return {
            'detected': False,
            'error': str(e),
            'project_path': project_path
        }

def _determine_project_type(project_summary: dict, dependency_analysis: dict) -> str:
    """Determina el tipo principal del proyecto."""
    # Verificar frameworks detectados
    if dependency_analysis and 'summary' in dependency_analysis:
        primary_framework = dependency_analysis['summary'].get('primary_framework')
        if primary_framework:
            return f'{primary_framework}_project'
    
    # Verificar por archivos de configuración
    if project_summary.get('typescript_project'):
        return 'typescript_project'
    elif project_summary.get('node_project'):
        return 'javascript_project'
    else:
        return 'unknown_project'

def _extract_technology_stack(dependency_analysis: dict) -> dict:
    """Extrae el stack tecnológico detectado."""
    if not dependency_analysis:
        return {}
        
    return {
        'frameworks': list(dependency_analysis.get('frameworks', {}).keys()),
        'build_tools': list(dependency_analysis.get('build_tools', {}).keys()),
        'testing': list(dependency_analysis.get('testing_frameworks', {}).keys()),
        'ui_libraries': list(dependency_analysis.get('ui_libraries', {}).keys()),
        'is_typescript': dependency_analysis.get('typescript', {}).get('is_typescript', False)
    }

def _extract_build_config(dependency_analysis: dict) -> dict:
    """Extrae configuración de build detectada."""
    if not dependency_analysis:
        return {}
        
    build_tools = dependency_analysis.get('build_tools', {})
    scripts = dependency_analysis.get('scripts_analysis', {})
    
    return {
        'primary_build_tool': list(build_tools.keys())[0] if build_tools else None,
        'has_dev_script': scripts.get('has_dev_script', False),
        'has_build_script': scripts.get('has_build_script', False),
        'detected_from_scripts': scripts.get('detected_build_tool_from_scripts')
    }

def _extract_alias_config(alias_analysis: dict) -> dict:
    """Extrae configuración de alias detectada."""
    if not alias_analysis:
        return {}
        
    return {
        'total_aliases': alias_analysis.get('alias_count', 0),
        'has_typescript_config': alias_analysis.get('has_typescript_config', False),
        'has_javascript_config': alias_analysis.get('has_javascript_config', False),
        'common_aliases': list(alias_analysis.get('common_aliases', {}).keys()),
        'suggestions': alias_analysis.get('suggestions', [])
    }

def _generate_recommended_settings(project_summary: dict, dependency_analysis: dict) -> dict:
    """Genera configuraciones recomendadas basadas en lo detectado."""
    recommendations = {
        'typescript_strict': False,
        'recommended_extensions': ['.py'],
        'exclude_patterns': ['node_modules', '__pycache__', '.git'],
        'backup_strategy': 'standard'
    }
    
    # Ajustar según tecnologías detectadas
    if project_summary.get('typescript_project'):
        recommendations['typescript_strict'] = True
        recommendations['recommended_extensions'].extend(['.ts', '.tsx'])
        
    if project_summary.get('node_project'):
        recommendations['recommended_extensions'].extend(['.js', '.jsx', '.json'])
        recommendations['exclude_patterns'].append('dist')
        
    # Ajustar según frameworks
    if dependency_analysis and 'frameworks' in dependency_analysis:
        frameworks = dependency_analysis['frameworks']
        if 'react' in frameworks:
            recommendations['recommended_extensions'].extend(['.jsx', '.tsx'])
        if 'vue' in frameworks:
            recommendations['recommended_extensions'].extend(['.vue'])
            
    return recommendations


def get_full_config():
    """Obtener configuración completa del sistema"""
    return {
        **DEFAULT_CONFIG,
        "project_root": str(PROJECT_ROOT),
        "config_dir": str(CONFIG_DIR),
        "logs_dir": str(LOGS_DIR),
        "backup_dir": str(BACKUP_DIR)
    }