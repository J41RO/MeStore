"""
Surgical Modifier v6.0 - Advanced Project Context System
Intelligent multi-framework detection with persistent caching and dependency analysis
"""

import os
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib

try:
    from utils.logger import logger
    from utils.path_resolver import path_resolver
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    logger = None
    path_resolver = None

@dataclass
class FrameworkInfo:
    """Information about a detected framework"""
    name: str
    version: Optional[str]
    confidence: float  # 0.0 to 1.0
    indicators: List[str]
    dependencies: List[str]
    config_files: List[str]
    typical_structure: List[str]

@dataclass
class ProjectMetadata:
    """Complete project metadata"""
    project_root: str
    project_name: str
    frameworks: List[FrameworkInfo]
    primary_language: str
    dependencies: Dict[str, List[str]]
    build_system: Optional[str]
    version_control: Optional[str]
    ci_cd_system: Optional[str]
    size_mb: float
    file_count: int
    last_modified: str
    scan_timestamp: str
    cache_version: str

class AdvancedProjectContext:
    """
    Advanced project context with intelligent multi-framework detection,
    persistent caching, and dependency analysis
    """
    
    def __init__(self):
        self.cache_version = "1.4.0"
        self.cache_dir = self._initialize_cache_directory()
        self.framework_detectors = self._initialize_framework_detectors()
        self.dependency_parsers = self._initialize_dependency_parsers()
        self.build_system_detectors = self._initialize_build_system_detectors()
        self.ci_cd_detectors = self._initialize_ci_cd_detectors()
        self.cache_ttl = timedelta(hours=6)  # Cache valid for 6 hours
        self.scan_stats = {
            'files_scanned': 0,
            'frameworks_detected': 0,
            'dependencies_found': 0,
            'scan_time': 0.0
        }
    
    def _initialize_cache_directory(self) -> Path:
        """Initialize cache directory with fallback options"""
        # Primary: User home directory
        primary_cache = Path.home() / '.surgical_modifier' / 'cache'
        
        # Secondary: Project-local cache
        secondary_cache = Path.cwd() / '.surgical_modifier_cache'
        
        # Tertiary: System temp directory
        import tempfile
        tertiary_cache = Path(tempfile.gettempdir()) / 'surgical_modifier_cache'
        
        for cache_path in [primary_cache, secondary_cache, tertiary_cache]:
            try:
                cache_path.mkdir(parents=True, exist_ok=True)
                # Test write access
                test_file = cache_path / '.write_test'
                test_file.write_text('test')
                test_file.unlink()
                
                if INTEGRATION_AVAILABLE and logger:
                    logger.info(f"Cache directory initialized: {cache_path}")
                return cache_path
            except (PermissionError, OSError):
                continue
        
        # If all fail, use in-memory cache (no persistence)
        if INTEGRATION_AVAILABLE and logger:
            logger.warning("Could not create persistent cache directory, using in-memory cache")
        return None
    
    def _initialize_framework_detectors(self) -> Dict[str, Dict]:
        """Initialize comprehensive framework detection rules"""
        return {
            'react': {
                'indicators': [
                    'package.json', 'src/App.js', 'src/App.tsx', 'src/index.js',
                    'public/index.html', 'src/components/', 'jsx', 'tsx'
                ],
                'dependencies': [
                    'react', 'react-dom', 'react-scripts', '@types/react'
                ],
                'config_files': [
                    'package.json', 'tsconfig.json', 'webpack.config.js',
                    'craco.config.js', 'vite.config.js'
                ],
                'file_patterns': [r'\.jsx?$', r'\.tsx?$'],
                'content_patterns': [
                    r'import.*react', r'from [\'"]react[\'"]',
                    r'React\.Component', r'useState', r'useEffect'
                ],
                'typical_structure': ['src/', 'public/', 'node_modules/']
            },
            
            'nextjs': {
                'indicators': [
                    'next.config.js', 'pages/', 'app/', 'next.config.mjs'
                ],
                'dependencies': ['next', 'react', 'react-dom'],
                'config_files': ['next.config.js', 'next.config.mjs', 'package.json'],
                'file_patterns': [r'pages/.*\.jsx?$', r'app/.*\.jsx?$'],
                'content_patterns': [r'from [\'"]next/', r'import.*next/'],
                'typical_structure': ['pages/', 'public/', 'styles/']
            },
            
            'vue': {
                'indicators': [
                    'vue.config.js', 'src/main.js', 'src/App.vue',
                    'package.json', 'src/components/', 'src/views/'
                ],
                'dependencies': ['vue', '@vue/cli', 'vuex', 'vue-router'],
                'config_files': ['vue.config.js', 'package.json', 'vite.config.js'],
                'file_patterns': [r'\.vue$'],
                'content_patterns': [
                    r'import.*vue', r'from [\'"]vue[\'"]',
                    r'<template>', r'<script>', r'Vue\.component'
                ],
                'typical_structure': ['src/', 'public/', 'dist/']
            },
            
            'angular': {
                'indicators': [
                    'angular.json', 'src/main.ts', 'src/app/app.module.ts',
                    'src/app/app.component.ts', 'package.json'
                ],
                'dependencies': [
                    '@angular/core', '@angular/cli', '@angular/common',
                    '@angular/router', 'typescript'
                ],
                'config_files': [
                    'angular.json', 'tsconfig.json', 'package.json',
                    'karma.conf.js', 'protractor.conf.js'
                ],
                'file_patterns': [r'\.component\.ts$', r'\.service\.ts$', r'\.module\.ts$'],
                'content_patterns': [
                    r'import.*@angular', r'@Component', r'@Injectable',
                    r'@NgModule', r'@Directive'
                ],
                'typical_structure': ['src/app/', 'src/assets/', 'e2e/']
            },
            
            'django': {
                'indicators': [
                    'manage.py', 'settings.py', 'urls.py', 'wsgi.py',
                    'models.py', 'views.py', 'admin.py'
                ],
                'dependencies': [
                    'django', 'djangorestframework', 'django-cors-headers',
                    'psycopg2', 'gunicorn'
                ],
                'config_files': [
                    'settings.py', 'urls.py', 'wsgi.py', 'asgi.py',
                    'requirements.txt', 'Pipfile'
                ],
                'file_patterns': [r'models\.py$', r'views\.py$', r'admin\.py$'],
                'content_patterns': [
                    r'from django', r'import django',
                    r'django\.db\.models', r'django\.http'
                ],
                'typical_structure': ['manage.py', 'static/', 'templates/', 'media/']
            },
            
            'fastapi': {
                'indicators': [
                    'main.py', 'app.py', 'requirements.txt', 'uvicorn'
                ],
                'dependencies': [
                    'fastapi', 'uvicorn', 'pydantic', 'starlette'
                ],
                'config_files': ['main.py', 'requirements.txt', 'pyproject.toml'],
                'file_patterns': [r'main\.py$', r'app\.py$'],
                'content_patterns': [
                    r'from fastapi', r'import fastapi',
                    r'FastAPI\(\)', r'@app\.'
                ],
                'typical_structure': ['app/', 'routers/', 'models/']
            },
            
            'flask': {
                'indicators': [
                    'app.py', 'run.py', 'requirements.txt', 'templates/', 'static/'
                ],
                'dependencies': [
                    'flask', 'flask-sqlalchemy', 'flask-migrate',
                    'flask-login', 'jinja2'
                ],
                'config_files': ['app.py', 'config.py', 'requirements.txt'],
                'file_patterns': [r'app\.py$', r'run\.py$'],
                'content_patterns': [
                    r'from flask', r'import flask',
                    r'Flask\(__name__\)', r'@app\.route'
                ],
                'typical_structure': ['templates/', 'static/', 'instance/']
            },
            
            'spring_boot': {
                'indicators': [
                    'pom.xml', 'build.gradle', 'src/main/java/',
                    'application.properties', 'application.yml'
                ],
                'dependencies': [
                    'spring-boot-starter', 'spring-boot-starter-web',
                    'spring-boot-starter-data-jpa'
                ],
                'config_files': [
                    'pom.xml', 'build.gradle', 'application.properties',
                    'application.yml', 'application-dev.yml'
                ],
                'file_patterns': [r'Application\.java$', r'Controller\.java$'],
                'content_patterns': [
                    r'@SpringBootApplication', r'@RestController',
                    r'@Service', r'@Repository'
                ],
                'typical_structure': ['src/main/java/', 'src/main/resources/', 'src/test/']
            },
            
            'express': {
                'indicators': [
                    'package.json', 'server.js', 'app.js', 'index.js'
                ],
                'dependencies': [
                    'express', 'body-parser', 'cors', 'helmet'
                ],
                'config_files': ['package.json', 'server.js', 'app.js'],
                'file_patterns': [r'server\.js$', r'app\.js$'],
                'content_patterns': [
                    r'require\([\'"]express[\'"]\)', r'express\(\)',
                    r'app\.get', r'app\.post'
                ],
                'typical_structure': ['routes/', 'middleware/', 'models/']
            }
        }
    
    def _initialize_dependency_parsers(self) -> Dict[str, callable]:
        """Initialize dependency file parsers"""
        return {
            'package.json': self._parse_package_json,
            'requirements.txt': self._parse_requirements_txt,
            'Pipfile': self._parse_pipfile,
            'pom.xml': self._parse_pom_xml,
            'build.gradle': self._parse_build_gradle,
            'composer.json': self._parse_composer_json,
            'Gemfile': self._parse_gemfile,
            'go.mod': self._parse_go_mod
        }
    
    def _initialize_build_system_detectors(self) -> Dict[str, List[str]]:
        """Initialize build system detection"""
        return {
            'npm': ['package.json', 'package-lock.json'],
            'yarn': ['yarn.lock', 'package.json'],
            'pnpm': ['pnpm-lock.yaml', 'package.json'],
            'pip': ['requirements.txt', 'setup.py', 'pyproject.toml'],
            'pipenv': ['Pipfile', 'Pipfile.lock'],
            'poetry': ['pyproject.toml', 'poetry.lock'],
            'maven': ['pom.xml', 'mvnw'],
            'gradle': ['build.gradle', 'gradlew'],
            'make': ['Makefile', 'makefile'],
            'webpack': ['webpack.config.js', 'webpack.config.ts'],
            'vite': ['vite.config.js', 'vite.config.ts'],
            'rollup': ['rollup.config.js'],
            'docker': ['Dockerfile', 'docker-compose.yml']
        }
    
    def _initialize_ci_cd_detectors(self) -> Dict[str, List[str]]:
        """Initialize CI/CD system detection"""
        return {
            'github_actions': ['.github/workflows/', '.github/actions/'],
            'gitlab_ci': ['.gitlab-ci.yml', '.gitlab/'],
            'jenkins': ['Jenkinsfile', 'jenkins/'],
            'travis': ['.travis.yml'],
            'circleci': ['.circleci/config.yml', '.circleci/'],
            'azure_devops': ['azure-pipelines.yml', '.azure/'],
            'bitbucket': ['bitbucket-pipelines.yml'],
            'drone': ['.drone.yml'],
            'buildkite': ['.buildkite/'],
            'teamcity': ['.teamcity/']
        }
    
    # ========== FRAMEWORK DETECTION SYSTEM ==========
    
    def detect_frameworks(self, project_root: Optional[Path] = None) -> List[FrameworkInfo]:
        """
        Detect all frameworks in the project with confidence scoring
        """
        if project_root is None:
            if INTEGRATION_AVAILABLE and path_resolver:
                project_root = path_resolver.find_project_root() or Path.cwd()
            else:
                project_root = Path.cwd()
        
        detected_frameworks = []
        start_time = time.time()
        
        for framework_name, detector_config in self.framework_detectors.items():
            framework_info = self._detect_single_framework(
                framework_name, detector_config, project_root
            )
            
            if framework_info and framework_info.confidence > 0.3:  # Minimum confidence threshold
                detected_frameworks.append(framework_info)
        
        # Sort by confidence (highest first)
        detected_frameworks.sort(key=lambda x: x.confidence, reverse=True)
        
        self.scan_stats['frameworks_detected'] = len(detected_frameworks)
        self.scan_stats['scan_time'] = time.time() - start_time
        
        if INTEGRATION_AVAILABLE and logger:
            logger.info(f"Framework detection completed: {len(detected_frameworks)} frameworks found in {self.scan_stats['scan_time']:.2f}s")
        
        return detected_frameworks
    
    def _detect_single_framework(self, framework_name: str, config: Dict, 
                                project_root: Path) -> Optional[FrameworkInfo]:
        """Detect a single framework with confidence scoring"""
        confidence_score = 0.0
        found_indicators = []
        found_dependencies = []
        found_config_files = []
        framework_version = None
        
        # Check file/directory indicators
        for indicator in config['indicators']:
            indicator_path = project_root / indicator
            if indicator_path.exists():
                found_indicators.append(indicator)
                confidence_score += 0.2
        
        # Check dependencies
        for dep_file, parser in self.dependency_parsers.items():
            dep_path = project_root / dep_file
            if dep_path.exists():
                try:
                    dependencies = parser(dep_path)
                    for framework_dep in config['dependencies']:
                        if framework_dep in dependencies:
                            found_dependencies.append(framework_dep)
                            confidence_score += 0.15
                            
                            # Try to extract version
                            if isinstance(dependencies, dict) and framework_dep in dependencies:
                                framework_version = dependencies[framework_dep]
                except Exception:
                    continue
        
        # Check config files
        for config_file in config['config_files']:
            config_path = project_root / config_file
            if config_path.exists():
                found_config_files.append(config_file)
                confidence_score += 0.1
        
        # Check file patterns and content
        if 'file_patterns' in config and 'content_patterns' in config:
            pattern_score = self._check_content_patterns(
                project_root, config['file_patterns'], config['content_patterns']
            )
            confidence_score += pattern_score * 0.3
        
        # Check typical project structure
        structure_score = self._check_project_structure(
            project_root, config.get('typical_structure', [])
        )
        confidence_score += structure_score * 0.1
        
        # Cap confidence at 1.0
        confidence_score = min(confidence_score, 1.0)
        
        if confidence_score > 0.0:
            return FrameworkInfo(
                name=framework_name,
                version=framework_version,
                confidence=confidence_score,
                indicators=found_indicators,
                dependencies=found_dependencies,
                config_files=found_config_files,
                typical_structure=config.get('typical_structure', [])
            )
        
        return None
    
    def _check_content_patterns(self, project_root: Path, 
                               file_patterns: List[str], 
                               content_patterns: List[str]) -> float:
        """Check for framework-specific content patterns in files"""
        matches = 0
        total_files = 0
        
        try:
            for file_pattern in file_patterns:
                pattern_regex = re.compile(file_pattern)
                
                for file_path in project_root.rglob('*'):
                    if file_path.is_file() and pattern_regex.search(str(file_path)):
                        total_files += 1
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(1024)  # Read first 1KB only for performance
                                
                                for content_pattern in content_patterns:
                                    if re.search(content_pattern, content, re.IGNORECASE):
                                        matches += 1
                                        break  # One match per file is enough
                        except (UnicodeDecodeError, PermissionError):
                            continue
                        
                        # Limit file scanning for performance
                        if total_files > 20:
                            break
        except Exception:
            pass
        
        return matches / max(total_files, 1) if total_files > 0 else 0.0
    
    def _check_project_structure(self, project_root: Path, 
                                typical_structure: List[str]) -> float:
        """Check how well the project matches typical framework structure"""
        if not typical_structure:
            return 0.0
        
        structure_matches = 0
        for structure_item in typical_structure:
            structure_path = project_root / structure_item
            if structure_path.exists():
                structure_matches += 1
        
        return structure_matches / len(typical_structure)
    
    # ========== DEPENDENCY PARSERS ==========
    
    def _parse_package_json(self, file_path: Path) -> Dict[str, str]:
        """Parse package.json dependencies"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                dependencies = {}
                dependencies.update(data.get('dependencies', {}))
                dependencies.update(data.get('devDependencies', {}))
                return dependencies
        except Exception:
            return {}
    
    def _parse_requirements_txt(self, file_path: Path) -> Dict[str, str]:
        """Parse requirements.txt dependencies"""
        try:
            dependencies = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '>=' in line:
                            name, version = line.split('>=', 1)
                        elif '==' in line:
                            name, version = line.split('==', 1)
                        else:
                            name, version = line, None
                        dependencies[name.strip()] = version.strip() if version else None
            return dependencies
        except Exception:
            return {}
    
    def _parse_pipfile(self, file_path: Path) -> Dict[str, str]:
        """Parse Pipfile dependencies"""
        try:
            import toml
            with open(file_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
                dependencies = {}
                dependencies.update(data.get('packages', {}))
                dependencies.update(data.get('dev-packages', {}))
                return dependencies
        except Exception:
            return {}
    
    def _parse_pom_xml(self, file_path: Path) -> Dict[str, str]:
        """Parse pom.xml dependencies (basic)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Basic regex extraction (not full XML parsing)
                dependencies = {}
                artifact_pattern = r'<artifactId>(.*?)</artifactId>'
                version_pattern = r'<version>(.*?)</version>'
                
                artifacts = re.findall(artifact_pattern, content)
                versions = re.findall(version_pattern, content)
                
                for i, artifact in enumerate(artifacts):
                    version = versions[i] if i < len(versions) else None
                    dependencies[artifact] = version
                
                return dependencies
        except Exception:
            return {}
    
    def _parse_build_gradle(self, file_path: Path) -> Dict[str, str]:
        """Parse build.gradle dependencies (basic)"""
        try:
            dependencies = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Basic regex for gradle dependencies
                dep_pattern = r'implementation [\'"]([^:\'"]+):([^:\'"]+):([^\'"\s]+)[\'"]'
                matches = re.findall(dep_pattern, content)
                
                for group, artifact, version in matches:
                    dependencies[f"{group}:{artifact}"] = version
                
                return dependencies
        except Exception:
            return {}
    
    def _parse_composer_json(self, file_path: Path) -> Dict[str, str]:
        """Parse composer.json dependencies"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                dependencies = {}
                dependencies.update(data.get('require', {}))
                dependencies.update(data.get('require-dev', {}))
                return dependencies
        except Exception:
            return {}
    
    def _parse_gemfile(self, file_path: Path) -> Dict[str, str]:
        """Parse Gemfile dependencies (basic)"""
        try:
            dependencies = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('gem '):
                        # Basic parsing: gem 'name', 'version'
                        parts = line.split(',')
                        if len(parts) >= 1:
                            gem_name = parts[0].replace('gem ', '').strip('\'" ')
                            version = parts[1].strip('\'" ') if len(parts) > 1 else None
                            dependencies[gem_name] = version
            return dependencies
        except Exception:
            return {}
    
    def _parse_go_mod(self, file_path: Path) -> Dict[str, str]:
        """Parse go.mod dependencies"""
        try:
            dependencies = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                in_require_block = False
                for line in f:
                    line = line.strip()
                    if line.startswith('require ('):
                        in_require_block = True
                        continue
                    elif line == ')':
                        in_require_block = False
                        continue
                    elif in_require_block and line:
                        parts = line.split()
                        if len(parts) >= 2:
                            dependencies[parts[0]] = parts[1]
                    elif line.startswith('require '):
                        parts = line.replace('require ', '').split()
                        if len(parts) >= 2:
                            dependencies[parts[0]] = parts[1]
            return dependencies
        except Exception:
            return {}
    
    # ========== CACHE SYSTEM ==========
    
    def _get_cache_key(self, project_root: Path) -> str:
        """Generate cache key for project"""
        # Use project root path + last modification time as cache key
        try:
            path_hash = hashlib.md5(str(project_root).encode()).hexdigest()
            return f"project_context_{path_hash}"
        except Exception:
            return f"project_context_default"
    
    def _load_cache(self, project_root: Path) -> Optional[ProjectMetadata]:
        """Load project metadata from cache"""
        if not self.cache_dir:
            return None
        
        cache_key = self._get_cache_key(project_root)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check cache version compatibility
            if cache_data.get('cache_version') != self.cache_version:
                return None
            
            # Check cache age
            scan_time = datetime.fromisoformat(cache_data['scan_timestamp'])
            if datetime.now() - scan_time > self.cache_ttl:
                return None
            
            # Convert back to ProjectMetadata
            # Convert FrameworkInfo list
            frameworks_data = cache_data.get('frameworks', [])
            frameworks = []
            for fw_data in frameworks_data:
                frameworks.append(FrameworkInfo(**fw_data))
            
            cache_data['frameworks'] = frameworks
            return ProjectMetadata(**cache_data)
            
        except Exception as e:
            if INTEGRATION_AVAILABLE and logger:
                logger.warning(f"Failed to load cache: {e}")
            return None
    
    def _save_cache(self, metadata: ProjectMetadata) -> None:
        """Save project metadata to cache"""
        if not self.cache_dir:
            return
        
        try:
            cache_key = self._get_cache_key(Path(metadata.project_root))
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            # Convert to serializable format
            cache_data = asdict(metadata)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            if INTEGRATION_AVAILABLE and logger:
                logger.info(f"Project metadata cached: {cache_file}")
                
        except Exception as e:
            if INTEGRATION_AVAILABLE and logger:
                logger.warning(f"Failed to save cache: {e}")
    
    # ========== MAIN INTERFACE METHODS ==========
    
    def analyze_project(self, project_root: Optional[Path] = None, 
                       use_cache: bool = True) -> ProjectMetadata:
        """
        Complete project analysis with framework detection, dependency analysis, and caching
        """
        if project_root is None:
            if INTEGRATION_AVAILABLE and path_resolver:
                project_root = path_resolver.find_project_root() or Path.cwd()
            else:
                project_root = Path.cwd()
        
        # Try to load from cache first
        if use_cache:
            cached_metadata = self._load_cache(project_root)
            if cached_metadata:
                if INTEGRATION_AVAILABLE and logger:
                    logger.info(f"Using cached project metadata")
                return cached_metadata
        
        # Perform full analysis
        start_time = time.time()
        
        if INTEGRATION_AVAILABLE and logger:
            logger.operation_start("Project Analysis", f"Analyzing project at {project_root}")
        
        # Basic project info
        project_name = project_root.name
        size_mb = self._calculate_project_size(project_root)
        file_count = self._count_project_files(project_root)
        
        # Framework detection
        frameworks = self.detect_frameworks(project_root)
        
        # Dependency analysis
        dependencies = self._analyze_all_dependencies(project_root)
        
        # Build system detection
        build_system = self._detect_build_system(project_root)
        
        # Version control detection
        version_control = self._detect_version_control(project_root)
        
        # CI/CD detection
        ci_cd_system = self._detect_ci_cd_system(project_root)
        
        # Primary language detection
        primary_language = self._detect_primary_language(frameworks, dependencies)
        
        # Create metadata
        metadata = ProjectMetadata(
            project_root=str(project_root),
            project_name=project_name,
            frameworks=frameworks,
            primary_language=primary_language,
            dependencies=dependencies,
            build_system=build_system,
            version_control=version_control,
            ci_cd_system=ci_cd_system,
            size_mb=size_mb,
            file_count=file_count,
            last_modified=datetime.now().isoformat(),
            scan_timestamp=datetime.now().isoformat(),
            cache_version=self.cache_version
        )
        
        # Save to cache
        if use_cache:
            self._save_cache(metadata)
        
        analysis_time = time.time() - start_time
        self.scan_stats['scan_time'] = analysis_time
        
        if INTEGRATION_AVAILABLE and logger:
            logger.operation_end("Project Analysis", success=True)
            logger.success(f"Project analysis completed: {len(frameworks)} frameworks, {sum(len(deps) for deps in dependencies.values())} dependencies in {analysis_time:.2f}s")
        
        return metadata
    
    def _calculate_project_size(self, project_root: Path) -> float:
        """Calculate project size in MB"""
        try:
            total_size = 0
            for file_path in project_root.rglob('*'):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                    except (OSError, PermissionError):
                        continue
            return round(total_size / (1024 * 1024), 2)
        except Exception:
            return 0.0
    
    def _count_project_files(self, project_root: Path) -> int:
        """Count total number of files in project"""
        try:
            return sum(1 for _ in project_root.rglob('*') if _.is_file())
        except Exception:
            return 0
    
    def _analyze_all_dependencies(self, project_root: Path) -> Dict[str, List[str]]:
        """Analyze all dependency files in project"""
        all_dependencies = {}
        
        for dep_file, parser in self.dependency_parsers.items():
            dep_path = project_root / dep_file
            if dep_path.exists():
                try:
                    dependencies = parser(dep_path)
                    if dependencies:
                        all_dependencies[dep_file] = list(dependencies.keys())
                        self.scan_stats['dependencies_found'] += len(dependencies)
                except Exception:
                    continue
        
        return all_dependencies
    
    def _detect_build_system(self, project_root: Path) -> Optional[str]:
        """Detect build system used in project"""
        for build_system, indicators in self.build_system_detectors.items():
            for indicator in indicators:
                if (project_root / indicator).exists():
                    return build_system
        return None
    
    def _detect_version_control(self, project_root: Path) -> Optional[str]:
        """Detect version control system"""
        if (project_root / '.git').exists():
            return 'git'
        elif (project_root / '.svn').exists():
            return 'svn'
        elif (project_root / '.hg').exists():
            return 'mercurial'
        return None
    
    def _detect_ci_cd_system(self, project_root: Path) -> Optional[str]:
        """Detect CI/CD system"""
        for ci_system, indicators in self.ci_cd_detectors.items():
            for indicator in indicators:
                if (project_root / indicator).exists():
                    return ci_system
        return None
    
    def _detect_primary_language(self, frameworks: List[FrameworkInfo], 
                                dependencies: Dict[str, List[str]]) -> str:
        """Detect primary programming language"""
        # Language scoring based on frameworks and dependencies
        language_scores = {
            'python': 0,
            'javascript': 0,
            'typescript': 0,
            'java': 0,
            'php': 0,
            'ruby': 0,
            'go': 0,
            'unknown': 0
        }
        
        # Score based on frameworks
        framework_language_map = {
            'django': 'python',
            'fastapi': 'python',
            'flask': 'python',
            'react': 'javascript',
            'nextjs': 'javascript',
            'vue': 'javascript',
            'angular': 'typescript',
            'spring_boot': 'java',
            'express': 'javascript'
        }
        
        for framework in frameworks:
            lang = framework_language_map.get(framework.name, 'unknown')
            language_scores[lang] += framework.confidence * 10
        
        # Score based on dependency files
        dependency_language_map = {
            'package.json': 'javascript',
            'requirements.txt': 'python',
            'Pipfile': 'python',
            'pom.xml': 'java',
            'build.gradle': 'java',
            'composer.json': 'php',
            'Gemfile': 'ruby',
            'go.mod': 'go'
        }
        
        for dep_file in dependencies.keys():
            lang = dependency_language_map.get(dep_file, 'unknown')
            language_scores[lang] += 5
        
        # Return language with highest score
        primary_lang = max(language_scores, key=language_scores.get)
        return primary_lang if language_scores[primary_lang] > 0 else 'unknown'
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get project context analysis statistics"""
        return {
            'scan_stats': self.scan_stats.copy(),
            'cache_available': self.cache_dir is not None,
            'cache_directory': str(self.cache_dir) if self.cache_dir else None,
            'supported_frameworks': list(self.framework_detectors.keys()),
            'supported_dependency_files': list(self.dependency_parsers.keys()),
            'supported_build_systems': list(self.build_system_detectors.keys()),
            'supported_ci_cd_systems': list(self.ci_cd_detectors.keys()),
            'cache_ttl_hours': self.cache_ttl.total_seconds() / 3600,
            'cache_version': self.cache_version
        }
    
    def clear_cache(self, project_root: Optional[Path] = None) -> bool:
        """Clear project metadata cache"""
        if not self.cache_dir:
            return False
        
        try:
            if project_root:
                # Clear specific project cache
                cache_key = self._get_cache_key(project_root)
                cache_file = self.cache_dir / f"{cache_key}.json"
                if cache_file.exists():
                    cache_file.unlink()
            else:
                # Clear all cache files
                for cache_file in self.cache_dir.glob("project_context_*.json"):
                    cache_file.unlink()
            
            if INTEGRATION_AVAILABLE and logger:
                logger.info("Project context cache cleared")
            return True
        except Exception as e:
            if INTEGRATION_AVAILABLE and logger:
                logger.error(f"Failed to clear cache: {e}")
            return False

# Global project context instance
project_context = AdvancedProjectContext()
