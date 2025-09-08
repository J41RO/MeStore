import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ConfigDetector:
    """
    Detector de archivos de configuración de proyecto.
    
    Detecta y analiza archivos como:
    - tsconfig.json (configuración TypeScript)
    - package.json (dependencias Node.js)
    - Otros archivos de configuración relevantes
    """
    
    def __init__(self, project_path: str = '.'):
        """
        Inicializa el detector en el directorio especificado.
        
        Args:
            project_path: Ruta del proyecto a analizar (por defecto directorio actual)
        """
        self.project_path = Path(project_path).resolve()
        self.config_files = {}
        self.detected_configs = {}
        
    def detect_config_files(self) -> Dict[str, bool]:
        """
        Detecta la presencia de archivos de configuración comunes.
        
        Returns:
            Diccionario con nombres de archivos y su existencia
        """
        config_files_to_check = [
            'tsconfig.json',
            'package.json',
            'jsconfig.json',
            'vite.config.js',
            'vite.config.ts',
            'webpack.config.js',
            '.env',
            '.env.local',
            'tailwind.config.js',
            'next.config.js',
            'vue.config.js',
            'angular.json'
        ]
        
        self.config_files = {}
        for config_file in config_files_to_check:
            file_path = self.project_path / config_file
            self.config_files[config_file] = file_path.exists()
            
        logger.info(f'Archivos de configuración detectados: {sum(self.config_files.values())} de {len(self.config_files)}')
        return self.config_files
    
    def analyze_tsconfig(self) -> Optional[Dict[str, Any]]:
        """
        Analiza el archivo tsconfig.json si existe.
        
        Returns:
            Diccionario con configuración TypeScript o None si no existe
        """
        tsconfig_path = self.project_path / 'tsconfig.json'
        
        if not tsconfig_path.exists():
            return None
            
        try:
            with open(tsconfig_path, 'r', encoding='utf-8') as f:
                tsconfig = json.load(f)
                
            analysis = {
                'exists': True,
                'strict_mode': tsconfig.get('compilerOptions', {}).get('strict', False),
                'target': tsconfig.get('compilerOptions', {}).get('target', 'es5'),
                'module': tsconfig.get('compilerOptions', {}).get('module', 'commonjs'),
                'lib': tsconfig.get('compilerOptions', {}).get('lib', []),
                'paths': tsconfig.get('compilerOptions', {}).get('paths', {}),
                'base_url': tsconfig.get('compilerOptions', {}).get('baseUrl', ''),
                'jsx': tsconfig.get('compilerOptions', {}).get('jsx'),
                'include': tsconfig.get('include', []),
                'exclude': tsconfig.get('exclude', [])
            }
            
            self.detected_configs['tsconfig'] = analysis
            logger.info(f'TSConfig analizado: strict={analysis["strict_mode"]}, target={analysis["target"]}')
            return analysis
            
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f'Error leyendo tsconfig.json: {e}')
            return {'exists': True, 'error': str(e)}
    
    def analyze_package_json(self) -> Optional[Dict[str, Any]]:
        """
        Analiza el archivo package.json si existe.
        
        Returns:
            Diccionario con información del package.json o None si no existe
        """
        package_path = self.project_path / 'package.json'
        
        if not package_path.exists():
            return None
            
        try:
            with open(package_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            all_deps = {**dependencies, **dev_dependencies}
            
            analysis = {
                'exists': True,
                'name': package_data.get('name', ''),
                'version': package_data.get('version', ''),
                'scripts': package_data.get('scripts', {}),
                'dependencies': dependencies,
                'dev_dependencies': dev_dependencies,
                'total_dependencies': len(all_deps),
                'frameworks': self._detect_frameworks(all_deps),
                'build_tools': self._detect_build_tools(all_deps),
                'testing_frameworks': self._detect_testing_frameworks(all_deps)
            }
            
            self.detected_configs['package'] = analysis
            logger.info(f'Package.json analizado: {len(all_deps)} dependencias, frameworks: {analysis["frameworks"]}')
            return analysis
            
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f'Error leyendo package.json: {e}')
            return {'exists': True, 'error': str(e)}
    
    def _detect_frameworks(self, dependencies: Dict[str, str]) -> List[str]:
        """Detecta frameworks en las dependencias."""
        frameworks = []
        framework_indicators = {
            'react': ['react', '@types/react'],
            'vue': ['vue', '@vue/cli'],
            'angular': ['@angular/core', '@angular/cli'],
            'svelte': ['svelte', '@sveltejs/kit'],
            'next': ['next'],
            'nuxt': ['nuxt'],
            'gatsby': ['gatsby']
        }
        
        for framework, indicators in framework_indicators.items():
            if any(dep in dependencies for dep in indicators):
                frameworks.append(framework)
                
        return frameworks
    
    def _detect_build_tools(self, dependencies: Dict[str, str]) -> List[str]:
        """Detecta herramientas de build en las dependencias."""
        build_tools = []
        build_indicators = {
            'vite': ['vite'],
            'webpack': ['webpack'],
            'rollup': ['rollup'],
            'parcel': ['parcel'],
            'esbuild': ['esbuild'],
            'turbopack': ['@next/bundle-analyzer']
        }
        
        for tool, indicators in build_indicators.items():
            if any(dep in dependencies for dep in indicators):
                build_tools.append(tool)
                
        return build_tools
    
    def _detect_testing_frameworks(self, dependencies: Dict[str, str]) -> List[str]:
        """Detecta frameworks de testing en las dependencias."""
        testing_frameworks = []
        testing_indicators = {
            'jest': ['jest', '@types/jest'],
            'vitest': ['vitest'],
            'cypress': ['cypress'],
            'playwright': ['playwright'],
            'testing-library': ['@testing-library/react', '@testing-library/vue']
        }
        
        for framework, indicators in testing_indicators.items():
            if any(dep in dependencies for dep in indicators):
                testing_frameworks.append(framework)
                
        return testing_frameworks
    
    def get_project_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen completo de la configuración del proyecto.
        
        Returns:
            Diccionario con resumen de toda la configuración detectada
        """
        # Detectar archivos de configuración
        self.detect_config_files()
        
        # Analizar configuraciones específicas
        tsconfig_analysis = self.analyze_tsconfig()
        package_analysis = self.analyze_package_json()
        
        summary = {
            'project_path': str(self.project_path),
            'config_files_found': [f for f, exists in self.config_files.items() if exists],
            'total_config_files': sum(self.config_files.values()),
            'typescript_project': tsconfig_analysis is not None,
            'node_project': package_analysis is not None,
            'configurations': {
                'tsconfig': tsconfig_analysis,
                'package': package_analysis
            }
        }
        
        # Agregar información de tecnologías detectadas
        if package_analysis:
            summary['detected_frameworks'] = package_analysis.get('frameworks', [])
            summary['detected_build_tools'] = package_analysis.get('build_tools', [])
            summary['detected_testing'] = package_analysis.get('testing_frameworks', [])
        
        return summary
    
    def is_typescript_project(self) -> bool:
        """Verifica si es un proyecto TypeScript."""
        return (self.project_path / 'tsconfig.json').exists()
    
    def is_node_project(self) -> bool:
        """Verifica si es un proyecto Node.js."""
        return (self.project_path / 'package.json').exists()
    
    def get_aliases_info(self) -> Dict[str, str]:
        """
        Obtiene información sobre alias de rutas configurados.
        
        Returns:
            Diccionario con alias configurados
        """
        aliases = {}
        
        # Revisar tsconfig paths
        if self.detected_configs.get('tsconfig'):
            paths = self.detected_configs['tsconfig'].get('paths', {})
            base_url = self.detected_configs['tsconfig'].get('base_url', '')
            
            for alias, paths_list in paths.items():
                if paths_list:
                    # Limpiar el alias (quitar /*)
                    clean_alias = alias.replace('/*', '')
                    # Limpiar la ruta (quitar /*)
                    clean_path = paths_list[0].replace('/*', '')
                    # Combinar con baseUrl si existe
                    if base_url:
                        full_path = os.path.join(base_url, clean_path)
                    else:
                        full_path = clean_path
                    aliases[clean_alias] = full_path
        
        return aliases
