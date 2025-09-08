import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging

logger = logging.getLogger(__name__)

class DependencyAnalyzer:
    """
    Analizador avanzado de dependencias de package.json.
    
    Analiza dependencias y detecta:
    - Frameworks (React, Vue, Angular, etc.)
    - Herramientas de desarrollo
    - Librerías de testing
    - Herramientas de build
    - Librerías de UI/styling
    """
    
    # Definiciones de patrones para detección
    FRAMEWORK_PATTERNS = {
        'react': {
            'primary': ['react'],
            'related': ['@types/react', 'react-dom', '@types/react-dom'],
            'ecosystem': ['react-router', 'react-router-dom', 'react-query', '@tanstack/react-query']
        },
        'vue': {
            'primary': ['vue'],
            'related': ['@vue/cli', '@vue/cli-service', 'vue-router', 'vuex'],
            'ecosystem': ['pinia', 'vue-template-compiler', '@vue/composition-api']
        },
        'angular': {
            'primary': ['@angular/core'],
            'related': ['@angular/cli', '@angular/common', '@angular/platform-browser'],
            'ecosystem': ['@angular/material', '@angular/cdk', '@ngrx/store']
        },
        'svelte': {
            'primary': ['svelte'],
            'related': ['@sveltejs/kit', '@sveltejs/adapter-auto'],
            'ecosystem': ['svelte-preprocess', 'svelte-check']
        },
        'next': {
            'primary': ['next'],
            'related': ['next/router', 'next/head'],
            'ecosystem': ['@next/bundle-analyzer', '@next/font']
        },
        'nuxt': {
            'primary': ['nuxt'],
            'related': ['@nuxt/cli', '@nuxt/kit'],
            'ecosystem': ['@nuxtjs/tailwindcss', '@pinia/nuxt']
        },
        'gatsby': {
            'primary': ['gatsby'],
            'related': ['gatsby-cli', 'gatsby-plugin-react-helmet'],
            'ecosystem': ['gatsby-source-filesystem', 'gatsby-transformer-remark']
        }
    }
    
    BUILD_TOOLS = {
        'vite': ['vite', '@vitejs/plugin-react', '@vitejs/plugin-vue'],
        'webpack': ['webpack', 'webpack-cli', 'webpack-dev-server'],
        'rollup': ['rollup', '@rollup/plugin-node-resolve'],
        'parcel': ['parcel', 'parcel-bundler'],
        'esbuild': ['esbuild', '@esbuild/plugin-react'],
        'turbopack': ['turbo', '@turbo/gen']
    }
    
    TESTING_FRAMEWORKS = {
        'jest': ['jest', '@types/jest', 'jest-environment-jsdom'],
        'vitest': ['vitest', '@vitest/ui'],
        'cypress': ['cypress', '@cypress/react'],
        'playwright': ['playwright', '@playwright/test'],
        'testing-library': ['@testing-library/react', '@testing-library/vue', '@testing-library/user-event'],
        'mocha': ['mocha', '@types/mocha'],
        'jasmine': ['jasmine', '@types/jasmine']
    }
    
    UI_LIBRARIES = {
        'tailwindcss': ['tailwindcss', '@tailwindcss/forms', '@tailwindcss/typography'],
        'bootstrap': ['bootstrap', 'react-bootstrap', 'vue-bootstrap'],
        'material-ui': ['@mui/material', '@material-ui/core'],
        'ant-design': ['antd', '@ant-design/icons'],
        'chakra-ui': ['@chakra-ui/react', '@chakra-ui/core'],
        'styled-components': ['styled-components', '@types/styled-components'],
        'emotion': ['@emotion/react', '@emotion/styled']
    }
    
    TYPESCRIPT_INDICATORS = [
        'typescript', '@types/node', '@typescript-eslint/parser', 'ts-node'
    ]
    
    def __init__(self, project_path: str = '.'):
        """
        Inicializa el analizador en el directorio especificado.
        
        Args:
            project_path: Ruta del proyecto a analizar
        """
        self.project_path = Path(project_path).resolve()
        self.package_data = None
        self.dependencies = {}
        self.dev_dependencies = {}
        self.all_dependencies = {}
        
    def load_package_json(self) -> bool:
        """
        Carga el archivo package.json del proyecto.
        
        Returns:
            True si se cargó exitosamente, False en caso contrario
        """
        package_path = self.project_path / 'package.json'
        
        if not package_path.exists():
            logger.warning(f'No se encontró package.json en {self.project_path}')
            return False
            
        try:
            with open(package_path, 'r', encoding='utf-8') as f:
                self.package_data = json.load(f)
                
            self.dependencies = self.package_data.get('dependencies', {})
            self.dev_dependencies = self.package_data.get('devDependencies', {})
            self.all_dependencies = {**self.dependencies, **self.dev_dependencies}
            
            logger.info(f'Package.json cargado: {len(self.all_dependencies)} dependencias totales')
            return True
            
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f'Error cargando package.json: {e}')
            return False
    
    def detect_frameworks(self) -> Dict[str, Dict[str, any]]:
        """
        Detecta frameworks y sus detalles en las dependencias.
        
        Returns:
            Diccionario con frameworks detectados y su información
        """
        if not self.all_dependencies:
            return {}
            
        detected_frameworks = {}
        
        for framework_name, patterns in self.FRAMEWORK_PATTERNS.items():
            detection_result = self._analyze_framework_presence(framework_name, patterns)
            if detection_result['detected']:
                detected_frameworks[framework_name] = detection_result
                
        return detected_frameworks
    
    def _analyze_framework_presence(self, framework_name: str, patterns: Dict[str, List[str]]) -> Dict[str, any]:
        """Analiza la presencia y completitud de un framework específico."""
        primary_found = []
        related_found = []
        ecosystem_found = []
        
        # Verificar dependencias principales
        for dep in patterns['primary']:
            if dep in self.all_dependencies:
                primary_found.append({
                    'name': dep,
                    'version': self.all_dependencies[dep],
                    'in_prod': dep in self.dependencies
                })
        
        # Verificar dependencias relacionadas
        for dep in patterns['related']:
            if dep in self.all_dependencies:
                related_found.append({
                    'name': dep,
                    'version': self.all_dependencies[dep],
                    'in_prod': dep in self.dependencies
                })
        
        # Verificar ecosistema
        for dep in patterns['ecosystem']:
            if dep in self.all_dependencies:
                ecosystem_found.append({
                    'name': dep,
                    'version': self.all_dependencies[dep],
                    'in_prod': dep in self.dependencies
                })
        
        detected = len(primary_found) > 0
        completeness_score = self._calculate_completeness_score(
            len(primary_found), len(related_found), len(ecosystem_found),
            len(patterns['primary']), len(patterns['related']), len(patterns['ecosystem'])
        )
        
        return {
            'detected': detected,
            'primary_dependencies': primary_found,
            'related_dependencies': related_found,
            'ecosystem_dependencies': ecosystem_found,
            'completeness_score': completeness_score,
            'total_related_packages': len(primary_found) + len(related_found) + len(ecosystem_found)
        }
    
    def _calculate_completeness_score(self, found_primary: int, found_related: int, found_ecosystem: int,
                                    total_primary: int, total_related: int, total_ecosystem: int) -> float:
        """Calcula un score de completitud del framework (0-100)."""
        if total_primary == 0:
            return 0.0
            
        # Peso mayor a dependencias principales
        primary_score = (found_primary / total_primary) * 60
        related_score = (found_related / max(total_related, 1)) * 25 if total_related > 0 else 0
        ecosystem_score = (found_ecosystem / max(total_ecosystem, 1)) * 15 if total_ecosystem > 0 else 0
        
        return round(primary_score + related_score + ecosystem_score, 1)
    
    def detect_build_tools(self) -> Dict[str, List[Dict[str, str]]]:
        """Detecta herramientas de build configuradas."""
        detected_tools = {}
        
        for tool_name, tool_packages in self.BUILD_TOOLS.items():
            found_packages = []
            for package in tool_packages:
                if package in self.all_dependencies:
                    found_packages.append({
                        'name': package,
                        'version': self.all_dependencies[package],
                        'in_prod': package in self.dependencies
                    })
            
            if found_packages:
                detected_tools[tool_name] = found_packages
                
        return detected_tools
    
    def detect_testing_frameworks(self) -> Dict[str, List[Dict[str, str]]]:
        """Detecta frameworks de testing configurados."""
        detected_testing = {}
        
        for framework_name, framework_packages in self.TESTING_FRAMEWORKS.items():
            found_packages = []
            for package in framework_packages:
                if package in self.all_dependencies:
                    found_packages.append({
                        'name': package,
                        'version': self.all_dependencies[package],
                        'in_prod': package in self.dependencies
                    })
            
            if found_packages:
                detected_testing[framework_name] = found_packages
                
        return detected_testing
    
    def detect_ui_libraries(self) -> Dict[str, List[Dict[str, str]]]:
        """Detecta librerías de UI/styling."""
        detected_ui = {}
        
        for ui_name, ui_packages in self.UI_LIBRARIES.items():
            found_packages = []
            for package in ui_packages:
                if package in self.all_dependencies:
                    found_packages.append({
                        'name': package,
                        'version': self.all_dependencies[package],
                        'in_prod': package in self.dependencies
                    })
            
            if found_packages:
                detected_ui[ui_name] = found_packages
                
        return detected_ui
    
    def is_typescript_project(self) -> Tuple[bool, List[str]]:
        """
        Determina si es un proyecto TypeScript.
        
        Returns:
            Tupla con (es_typescript, lista_de_paquetes_typescript_encontrados)
        """
        typescript_packages = []
        
        for package in self.TYPESCRIPT_INDICATORS:
            if package in self.all_dependencies:
                typescript_packages.append(package)
        
        return len(typescript_packages) > 0, typescript_packages
    
    def analyze_scripts(self) -> Dict[str, any]:
        """Analiza los scripts definidos en package.json."""
        if not self.package_data:
            return {}
            
        scripts = self.package_data.get('scripts', {})
        
        analysis = {
            'total_scripts': len(scripts),
            'has_dev_script': 'dev' in scripts or 'start' in scripts,
            'has_build_script': 'build' in scripts,
            'has_test_script': 'test' in scripts,
            'has_lint_script': any('lint' in script_name for script_name in scripts.keys()),
            'scripts': scripts
        }
        
        # Detectar herramientas por scripts
        script_content = ' '.join(scripts.values()).lower()
        if 'vite' in script_content:
            analysis['detected_build_tool_from_scripts'] = 'vite'
        elif 'webpack' in script_content:
            analysis['detected_build_tool_from_scripts'] = 'webpack'
        elif 'next' in script_content:
            analysis['detected_build_tool_from_scripts'] = 'next'
        
        return analysis
    
    def get_dependency_stats(self) -> Dict[str, any]:
        """Obtiene estadísticas generales de dependencias."""
        if not self.all_dependencies:
            return {}
            
        # Categorizar dependencias por tipo
        prod_count = len(self.dependencies)
        dev_count = len(self.dev_dependencies)
        
        # Analizar versiones
        version_patterns = {
            'exact': 0,  # 1.2.3
            'caret': 0,  # ^1.2.3
            'tilde': 0,  # ~1.2.3
            'range': 0,  # >=1.0.0 <2.0.0
            'latest': 0, # latest, *
            'beta': 0    # versiones beta/alpha
        }
        
        for version in self.all_dependencies.values():
            if version.startswith('^'):
                version_patterns['caret'] += 1
            elif version.startswith('~'):
                version_patterns['tilde'] += 1
            elif any(op in version for op in ['>=', '<=', '>', '<']):
                version_patterns['range'] += 1
            elif version in ['latest', '*']:
                version_patterns['latest'] += 1
            elif any(tag in version.lower() for tag in ['beta', 'alpha', 'rc']):
                version_patterns['beta'] += 1
            else:
                version_patterns['exact'] += 1
        
        return {
            'total_dependencies': len(self.all_dependencies),
            'production_dependencies': prod_count,
            'development_dependencies': dev_count,
            'version_patterns': version_patterns,
            'has_peer_dependencies': 'peerDependencies' in (self.package_data or {}),
            'has_optional_dependencies': 'optionalDependencies' in (self.package_data or {})
        }
    
    def get_complete_analysis(self) -> Dict[str, any]:
        """
        Realiza un análisis completo de las dependencias.
        
        Returns:
            Diccionario con análisis completo del proyecto
        """
        if not self.load_package_json():
            return {'error': 'No se pudo cargar package.json'}
            
        analysis = {
            'project_info': {
                'name': self.package_data.get('name', ''),
                'version': self.package_data.get('version', ''),
                'description': self.package_data.get('description', ''),
                'main': self.package_data.get('main', ''),
                'type': self.package_data.get('type', 'commonjs')
            },
            'frameworks': self.detect_frameworks(),
            'build_tools': self.detect_build_tools(),
            'testing_frameworks': self.detect_testing_frameworks(),
            'ui_libraries': self.detect_ui_libraries(),
            'typescript': {
                'is_typescript': self.is_typescript_project()[0],
                'typescript_packages': self.is_typescript_project()[1]
            },
            'scripts_analysis': self.analyze_scripts(),
            'dependency_stats': self.get_dependency_stats(),
            'project_path': str(self.project_path)
        }
        
        # Resumen ejecutivo
        frameworks_list = list(analysis['frameworks'].keys())
        build_tools_list = list(analysis['build_tools'].keys())
        
        analysis['summary'] = {
            'primary_framework': frameworks_list[0] if frameworks_list else None,
            'all_frameworks': frameworks_list,
            'primary_build_tool': build_tools_list[0] if build_tools_list else None,
            'is_typescript': analysis['typescript']['is_typescript'],
            'has_tests': len(analysis['testing_frameworks']) > 0,
            'project_complexity': self._calculate_project_complexity(analysis)
        }
        
        return analysis
    
    def _calculate_project_complexity(self, analysis: Dict) -> str:
        """Calcula la complejidad del proyecto basado en dependencias y configuraciones."""
        complexity_score = 0
        
        # Frameworks (+2 cada uno)
        complexity_score += len(analysis['frameworks']) * 2
        
        # Build tools (+1 cada uno)
        complexity_score += len(analysis['build_tools'])
        
        # TypeScript (+2)
        if analysis['typescript']['is_typescript']:
            complexity_score += 2
            
        # Testing frameworks (+1 cada uno)
        complexity_score += len(analysis['testing_frameworks'])
        
        # Total de dependencias (escalado)
        total_deps = analysis['dependency_stats'].get('total_dependencies', 0)
        if total_deps > 100:
            complexity_score += 3
        elif total_deps > 50:
            complexity_score += 2
        elif total_deps > 20:
            complexity_score += 1
        
        # Categorizar complejidad
        if complexity_score >= 10:
            return 'high'
        elif complexity_score >= 6:
            return 'medium'
        elif complexity_score >= 3:
            return 'low'
        else:
            return 'minimal'
