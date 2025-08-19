"""
🚀 CodeCraft Ultimate v6.0 - Context Manager
AI-Human collaboration context management
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from ..analyzers.universal_analyzer import UniversalAnalyzer


@dataclass
class ProjectContext:
    """Project context information"""
    root_path: str
    project_type: str
    languages: List[str]
    frameworks: List[str]
    has_tests: bool
    has_docs: bool
    has_config: bool
    structure: Dict[str, Any]


class ContextManager:
    """Manages project context for AI collaboration"""
    
    def __init__(self):
        self.analyzer = UniversalAnalyzer()
        self.context_cache = {}
    
    def analyze_project_context(self, project_root: str) -> ProjectContext:
        """Analyze complete project context"""
        
        # Check cache first
        if project_root in self.context_cache:
            return self.context_cache[project_root]
        
        # Analyze project structure
        languages = self._detect_languages(project_root)
        frameworks = self._detect_frameworks(project_root)
        project_type = self._determine_project_type(project_root, languages, frameworks)
        
        # Check for standard directories/files
        has_tests = self._has_tests(project_root)
        has_docs = self._has_docs(project_root)
        has_config = self._has_config_files(project_root)
        
        # Analyze structure
        structure = self._analyze_directory_structure(project_root)
        
        context = ProjectContext(
            root_path=project_root,
            project_type=project_type,
            languages=languages,
            frameworks=frameworks,
            has_tests=has_tests,
            has_docs=has_docs,
            has_config=has_config,
            structure=structure
        )
        
        # Cache result
        self.context_cache[project_root] = context
        
        return context
    
    def _detect_languages(self, project_root: str) -> List[str]:
        """Detect programming languages in project"""
        languages = set()
        
        extension_mapping = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.jsx': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.cc': 'C++',
            '.cxx': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.dart': 'Dart',
            '.lua': 'Lua'
        }
        
        try:
            for root, dirs, files in os.walk(project_root):
                # Skip common build/cache directories
                dirs[:] = [d for d in dirs if d not in {
                    'node_modules', '.git', '__pycache__', '.pytest_cache',
                    'build', 'dist', '.venv', 'venv', 'target', '.idea'
                }]
                
                for file in files:
                    ext = Path(file).suffix.lower()
                    if ext in extension_mapping:
                        languages.add(extension_mapping[ext])
                        
                # Limit search depth to avoid performance issues
                if root.count(os.sep) - project_root.count(os.sep) >= 3:
                    dirs.clear()
        
        except Exception:
            pass
        
        return sorted(list(languages))
    
    def _detect_frameworks(self, project_root: str) -> List[str]:
        """Detect frameworks used in project"""
        frameworks = set()
        
        # Check package.json for JavaScript frameworks
        package_json = os.path.join(project_root, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                
                # Check dependencies
                all_deps = {}
                all_deps.update(data.get('dependencies', {}))
                all_deps.update(data.get('devDependencies', {}))
                
                js_frameworks = {
                    'react': 'React',
                    '@types/react': 'React',
                    'vue': 'Vue.js',
                    '@vue/core': 'Vue.js',
                    'angular': 'Angular',
                    '@angular/core': 'Angular',
                    'express': 'Express',
                    'next': 'Next.js',
                    'nuxt': 'Nuxt.js',
                    'svelte': 'Svelte',
                    'gatsby': 'Gatsby',
                    'nestjs': 'NestJS',
                    'fastify': 'Fastify'
                }
                
                for dep, framework in js_frameworks.items():
                    if dep in all_deps:
                        frameworks.add(framework)
            
            except Exception:
                pass
        
        # Check requirements.txt for Python frameworks  
        requirements_txt = os.path.join(project_root, 'requirements.txt')
        if os.path.exists(requirements_txt):
            try:
                with open(requirements_txt, 'r') as f:
                    content = f.read().lower()
                
                python_frameworks = {
                    'django': 'Django',
                    'flask': 'Flask',
                    'fastapi': 'FastAPI',
                    'pyramid': 'Pyramid',
                    'tornado': 'Tornado',
                    'aiohttp': 'aiohttp',
                    'sqlalchemy': 'SQLAlchemy',
                    'pytest': 'pytest',
                    'unittest': 'unittest'
                }
                
                for framework_key, framework_name in python_frameworks.items():
                    if framework_key in content:
                        frameworks.add(framework_name)
            
            except Exception:
                pass
        
        # Check Gemfile for Ruby frameworks
        gemfile = os.path.join(project_root, 'Gemfile')
        if os.path.exists(gemfile):
            try:
                with open(gemfile, 'r') as f:
                    content = f.read().lower()
                
                if 'rails' in content:
                    frameworks.add('Ruby on Rails')
                if 'sinatra' in content:
                    frameworks.add('Sinatra')
            
            except Exception:
                pass
        
        # Check pom.xml for Java frameworks
        pom_xml = os.path.join(project_root, 'pom.xml')
        if os.path.exists(pom_xml):
            try:
                with open(pom_xml, 'r') as f:
                    content = f.read().lower()
                
                if 'spring' in content:
                    frameworks.add('Spring')
                if 'junit' in content:
                    frameworks.add('JUnit')
                if 'hibernate' in content:
                    frameworks.add('Hibernate')
            
            except Exception:
                pass
        
        return sorted(list(frameworks))
    
    def _determine_project_type(self, project_root: str, languages: List[str], frameworks: List[str]) -> str:
        """Determine overall project type"""
        
        # Check for specific project indicators
        if os.path.exists(os.path.join(project_root, 'package.json')):
            if 'React' in frameworks or 'Vue.js' in frameworks or 'Angular' in frameworks:
                return 'web_frontend'
            elif 'Express' in frameworks or 'Fastify' in frameworks:
                return 'web_backend'
            else:
                return 'node_project'
        
        if os.path.exists(os.path.join(project_root, 'requirements.txt')) or os.path.exists(os.path.join(project_root, 'pyproject.toml')):
            if 'Django' in frameworks or 'Flask' in frameworks or 'FastAPI' in frameworks:
                return 'web_backend'
            else:
                return 'python_project'
        
        if os.path.exists(os.path.join(project_root, 'pom.xml')):
            return 'java_project'
        
        if os.path.exists(os.path.join(project_root, 'Cargo.toml')):
            return 'rust_project'
        
        if os.path.exists(os.path.join(project_root, 'go.mod')):
            return 'go_project'
        
        # Determine by languages
        if 'Python' in languages and len(languages) == 1:
            return 'python_project'
        elif 'JavaScript' in languages and 'TypeScript' in languages:
            return 'web_project'
        elif 'Java' in languages:
            return 'java_project'
        elif len(languages) > 2:
            return 'polyglot_project'
        else:
            return 'unknown_project'
    
    def _has_tests(self, project_root: str) -> bool:
        """Check if project has test files"""
        test_indicators = [
            'tests', 'test', '__tests__', 'spec', 'specs',
            'test.py', 'tests.py', 'test.js', 'spec.js'
        ]
        
        try:
            for root, dirs, files in os.walk(project_root):
                # Check directory names
                for dir_name in dirs:
                    if any(indicator in dir_name.lower() for indicator in test_indicators):
                        return True
                
                # Check file names
                for file_name in files:
                    if any(indicator in file_name.lower() for indicator in test_indicators):
                        return True
                
                # Limit search depth
                if root.count(os.sep) - project_root.count(os.sep) >= 2:
                    dirs.clear()
        
        except Exception:
            pass
        
        return False
    
    def _has_docs(self, project_root: str) -> bool:
        """Check if project has documentation"""
        doc_indicators = [
            'docs', 'doc', 'documentation', 'README.md', 'README.rst', 
            'CHANGELOG.md', 'API.md'
        ]
        
        try:
            items = os.listdir(project_root)
            
            for item in items:
                if any(indicator in item for indicator in doc_indicators):
                    return True
            
            # Check for docs directory
            docs_dir = os.path.join(project_root, 'docs')
            if os.path.isdir(docs_dir):
                return True
        
        except Exception:
            pass
        
        return False
    
    def _has_config_files(self, project_root: str) -> bool:
        """Check if project has configuration files"""
        config_files = [
            '.gitignore', '.editorconfig', '.env', '.env.example',
            'tsconfig.json', '.eslintrc', '.prettierrc', 'setup.cfg',
            'pyproject.toml', 'tox.ini', '.codecraft.toml'
        ]
        
        try:
            items = os.listdir(project_root)
            
            for config_file in config_files:
                if config_file in items:
                    return True
        
        except Exception:
            pass
        
        return False
    
    def _analyze_directory_structure(self, project_root: str) -> Dict[str, Any]:
        """Analyze directory structure"""
        structure = {
            'total_files': 0,
            'total_directories': 0,
            'file_types': {},
            'large_files': [],
            'empty_directories': [],
            'main_directories': []
        }
        
        try:
            for root, dirs, files in os.walk(project_root):
                # Skip hidden and build directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
                    'node_modules', '__pycache__', 'build', 'dist'
                }]
                
                structure['total_directories'] += len(dirs)
                structure['total_files'] += len(files)
                
                # Track main directories
                if root == project_root:
                    structure['main_directories'] = dirs.copy()
                
                # Analyze files
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Track file extensions
                    ext = Path(file).suffix.lower()
                    if ext:
                        structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
                    
                    # Track large files (>1MB)
                    try:
                        if os.path.getsize(file_path) > 1024 * 1024:
                            relative_path = os.path.relpath(file_path, project_root)
                            structure['large_files'].append(relative_path)
                    except Exception:
                        pass
                
                # Track empty directories
                if not dirs and not files:
                    relative_path = os.path.relpath(root, project_root)
                    structure['empty_directories'].append(relative_path)
                
                # Limit search depth for performance
                if root.count(os.sep) - project_root.count(os.sep) >= 3:
                    dirs.clear()
        
        except Exception:
            pass
        
        return structure
    
    def get_file_context(self, file_path: str) -> Dict[str, Any]:
        """Get context for a specific file"""
        if not os.path.exists(file_path):
            return {'error': 'File not found'}
        
        context = {
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'file_type': self.analyzer.detect_file_type(file_path),
            'last_modified': os.path.getmtime(file_path)
        }
        
        # Analyze file content if it's a text file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            context.update({
                'line_count': len(content.splitlines()),
                'char_count': len(content),
                'complexity': self.analyzer.analyze_complexity(content, file_path),
                'dependencies': self.analyzer.extract_dependencies(content, file_path)
            })
        
        except Exception as e:
            context['error'] = f'Could not analyze file content: {e}'
        
        return context
    
    def suggest_next_actions(self, operation_result: Dict[str, Any], context: ProjectContext) -> List[str]:
        """Suggest next actions based on operation result and context"""
        suggestions = []
        
        # Get operation details
        operation = operation_result.get('operation', '')
        success = operation_result.get('success', False)
        file_path = operation_result.get('file_path', '')
        
        if success:
            # Successful operation suggestions
            if operation in ['create', 'replace', 'after', 'before']:
                if context.has_tests:
                    suggestions.append(f"codecraft generate-tests {file_path} --test-framework=pytest")
                
                suggestions.append(f"codecraft analyze-complexity {file_path}")
                
                if 'Python' in context.languages:
                    suggestions.append("codecraft optimize-imports .")
            
            elif operation == 'generate-component':
                suggestions.append(f"codecraft generate-tests {file_path} --test-framework=jest")
                suggestions.append("codecraft analyze-dependencies .")
            
            elif operation in ['modernize-syntax', 'optimize-imports']:
                if context.has_tests:
                    suggestions.append("codecraft find-bugs . --severity=medium")
        
        else:
            # Failed operation suggestions
            if 'not found' in operation_result.get('message', '').lower():
                suggestions.append(f"codecraft analyze-complexity . --format=summary")
                suggestions.append("Use --explore flag to examine file structure")
        
        # Context-based suggestions
        if not context.has_tests and len(context.languages) > 0:
            suggestions.append("Consider adding tests for better code quality")
        
        if not context.has_docs:
            suggestions.append("codecraft generate-docs . --format=markdown")
        
        # Framework-specific suggestions
        if 'React' in context.frameworks:
            suggestions.append("codecraft bundle-analysis . --bundler=webpack")
        
        if 'Django' in context.frameworks:
            suggestions.append("codecraft security-scan . --severity=high")
        
        return suggestions[:5]  # Limit to top 5 suggestions