
#!/usr/bin/env python3
"""
ProjectAuditor - Comprehensive analysis tool for Surgical Modifier v6.0 project
Analyzes project structure, dependencies, and health metrics
"""

import os
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
import subprocess

class ProjectAuditor:
   """Comprehensive project auditor for Surgical Modifier codebase"""
   
   def __init__(self, project_root: str = None):
       self.project_root = Path(project_root) if project_root else Path('.')
       self.results = {}
       self.python_files = []
       self.backup_files = []
       self.functional_files = []
       self.dependencies = {}
       
   def analyze_project(self) -> Dict[str, Any]:
       """Execute complete project analysis"""
       print("Iniciando análisis completo del proyecto...")
       
       self.results = {
           'timestamp': datetime.now().isoformat(),
           'project_root': str(self.project_root),
           'file_inventory': self._analyze_files(),
           'dependency_mapping': self._map_dependencies(),
           'code_quality': self._analyze_code_quality(),
           'backup_analysis': self._analyze_backups(),
           'test_analysis': self._analyze_tests(),
           'functionality_status': self._check_functionality(),
           'recommendations': self._generate_recommendations()
       }
       
       print(f"Análisis completado: {len(self.python_files)} archivos Python analizados")
       return self.results
   
   def _analyze_files(self) -> Dict[str, Any]:
       """Analyze all project files"""
       file_analysis = {
           'total_files': 0,
           'python_files': [],
           'backup_files': [],
           'config_files': [],
           'test_files': [],
           'temporary_files': []
       }
       
       for file_path in self.project_root.rglob('*'):
           if file_path.is_file():
               file_analysis['total_files'] += 1
               rel_path = str(file_path.relative_to(self.project_root))
               
               if file_path.suffix == '.py':
                   file_analysis['python_files'].append(rel_path)
                   self.python_files.append(file_path)
               elif any(marker in file_path.name.lower() for marker in ['.backup', '.bak', 'backup_', 'pre_']):
                   file_analysis['backup_files'].append(rel_path)
                   self.backup_files.append(file_path)
               elif file_path.suffix in ['.json', '.yaml', '.yml', '.toml', '.ini']:
                   file_analysis['config_files'].append(rel_path)
               elif 'test' in file_path.name.lower():
                   file_analysis['test_files'].append(rel_path)
               elif file_path.suffix in ['.tmp', '.temp'] or file_path.name.startswith('.'):
                   file_analysis['temporary_files'].append(rel_path)
       
       return file_analysis
   
   def _map_dependencies(self) -> Dict[str, List[str]]:
       """Map dependencies between Python files"""
       dependencies = {}
       
       for py_file in self.python_files:
           try:
               with open(py_file, 'r', encoding='utf-8') as f:
                   content = f.read()
               
               imports = []
               # Find import statements
               for line in content.split('\n'):
                   line = line.strip()
                   if line.startswith('import ') or line.startswith('from '):
                       imports.append(line)
               
               rel_path = str(py_file.relative_to(self.project_root))
               dependencies[rel_path] = imports
               
           except Exception as e:
               print(f"Error analyzing {py_file}: {e}")
       
       return dependencies
   
   def _analyze_code_quality(self) -> Dict[str, Any]:
       """Analyze code quality metrics"""
       quality_metrics = {
           'total_lines': 0,
           'avg_file_size': 0,
           'large_files': [],
           'duplicated_code': [],
           'todo_fixme_count': 0
       }
       
       line_counts = []
       
       for py_file in self.python_files:
           try:
               with open(py_file, 'r', encoding='utf-8') as f:
                   lines = f.readlines()
               
               line_count = len(lines)
               line_counts.append(line_count)
               quality_metrics['total_lines'] += line_count
               
               if line_count > 500:  # Large file threshold
                   rel_path = str(py_file.relative_to(self.project_root))
                   quality_metrics['large_files'].append({'file': rel_path, 'lines': line_count})
               
               # Count TODO/FIXME
               content = ''.join(lines)
               todos = len(re.findall(r'(TODO|FIXME|XXX)', content, re.IGNORECASE))
               quality_metrics['todo_fixme_count'] += todos
               
           except Exception as e:
               print(f"Error in quality analysis for {py_file}: {e}")
       
       if line_counts:
           quality_metrics['avg_file_size'] = sum(line_counts) / len(line_counts)
       
       return quality_metrics
   
   def _analyze_backups(self) -> Dict[str, Any]:
       """Analyze backup files and cleanup opportunities"""
       backup_analysis = {
           'total_backup_files': len(self.backup_files),
           'backup_patterns': {},
           'cleanup_candidates': [],
           'size_savings': 0
       }
       
       patterns = {}
       for backup_file in self.backup_files:
           # Identify backup patterns
           name = backup_file.name
           if '.backup' in name:
               pattern = '.backup'
           elif '.PRE_' in name:
               pattern = '.PRE_*'
           elif '.BACKUP' in name:
               pattern = '.BACKUP*'
           else:
               pattern = 'other'
           
           patterns[pattern] = patterns.get(pattern, 0) + 1
           
           # Calculate size for cleanup estimation
           try:
               size = backup_file.stat().st_size
               backup_analysis['size_savings'] += size
               rel_path = str(backup_file.relative_to(self.project_root))
               backup_analysis['cleanup_candidates'].append({
                   'file': rel_path,
                   'size': size,
                   'pattern': pattern
               })
           except Exception:
               pass
       
       backup_analysis['backup_patterns'] = patterns
       return backup_analysis
   
   def _analyze_tests(self) -> Dict[str, Any]:
       """Analyze test coverage and status"""
       test_analysis = {
           'test_files_found': 0,
           'test_directories': [],
           'pytest_available': False,
           'coverage_available': False
       }
       
       # Find test directories
       test_dirs = []
       for item in self.project_root.iterdir():
           if item.is_dir() and 'test' in item.name.lower():
               test_dirs.append(str(item.relative_to(self.project_root)))
               
       test_analysis['test_directories'] = test_dirs
       test_analysis['test_files_found'] = len([f for f in self.results.get('file_inventory', {}).get('test_files', [])])
       
       # Check for pytest
       try:
           subprocess.run(['python3', '-m', 'pytest', '--version'], capture_output=True, check=True)
           test_analysis['pytest_available'] = True
       except:
           test_analysis['pytest_available'] = False
           
       # Check for coverage
       try:
           subprocess.run(['python3', '-m', 'coverage', '--version'], capture_output=True, check=True)
           test_analysis['coverage_available'] = True
       except:
           test_analysis['coverage_available'] = False
       
       return test_analysis
   
   def _check_functionality(self) -> Dict[str, Any]:
       """Check core functionality status"""
       functionality = {
           'cli_functional': False,
           'operations_available': [],
           'critical_files_present': True,
           'import_errors': []
       }
       
       # Check cli.py
       cli_path = self.project_root / 'cli.py'
       if cli_path.exists():
           try:
               result = subprocess.run(['python3', str(cli_path), '--help'], 
                                     capture_output=True, text=True, timeout=10)
               if result.returncode == 0:
                   functionality['cli_functional'] = True
                   # Extract operations from help text
                   help_text = result.stdout
                   if 'create' in help_text:
                       functionality['operations_available'].append('create')
                   if 'replace' in help_text:
                       functionality['operations_available'].append('replace')
                   if 'before' in help_text:
                       functionality['operations_available'].append('before')
                   if 'after' in help_text:
                       functionality['operations_available'].append('after')
                   if 'append' in help_text:
                       functionality['operations_available'].append('append')
           except Exception as e:
               functionality['import_errors'].append(f"cli.py: {str(e)}")
       
       return functionality
   
   def _generate_recommendations(self) -> List[str]:
       """Generate improvement recommendations"""
       recommendations = []
       
       if len(self.backup_files) > 20:
           recommendations.append(f"CLEANUP: {len(self.backup_files)} archivos backup encontrados - implementar CleanupManager")
       
       if self.results.get('code_quality', {}).get('todo_fixme_count', 0) > 10:
           recommendations.append("CODE QUALITY: Resolver TODOs y FIXMEs pendientes")
       
       large_files = self.results.get('code_quality', {}).get('large_files', [])
       if len(large_files) > 5:
           recommendations.append(f"REFACTOR: {len(large_files)} archivos grandes detectados - considerar modularización")
       
       if not self.results.get('functionality_status', {}).get('cli_functional', False):
           recommendations.append("CRITICAL: cli.py no funcional - requiere reparación inmediata")
       
       if len(self.results.get('functionality_status', {}).get('operations_available', [])) < 5:
           recommendations.append("FUNCTIONALITY: Operaciones básicas incompletas")
       
       recommendations.append("READY: Implementar CleanupManager para limpieza segura")
       recommendations.append("NEXT: Proceder con reestructuración modular v6.0")
       
       return recommendations
   
   def generate_report(self, output_file: str = None) -> str:
       """Generate comprehensive analysis report"""
       if not self.results:
           self.analyze_project()
       
       report_data = {
           'project_audit_report': self.results,
           'summary': {
               'total_python_files': len(self.python_files),
               'total_backup_files': len(self.backup_files),
               'cli_status': 'functional' if self.results.get('functionality_status', {}).get('cli_functional', False) else 'needs_repair',
               'cleanup_priority': 'high' if len(self.backup_files) > 20 else 'medium',
               'ready_for_v6': self.results.get('functionality_status', {}).get('cli_functional', False)
           }
       }
       
       if output_file:
           os.makedirs(os.path.dirname(output_file), exist_ok=True)
           with open(output_file, 'w', encoding='utf-8') as f:
               json.dump(report_data, f, indent=2, ensure_ascii=False)
           print(f"Reporte guardado en: {output_file}")
       
       return json.dumps(report_data, indent=2, ensure_ascii=False)

if __name__ == '__main__':
   auditor = ProjectAuditor()
   report = auditor.generate_report('reports/project_audit.json')
   print("\nRESUMEN DEL PROYECTO:")
   print(f"Python files: {len(auditor.python_files)}")
   print(f"Backup files: {len(auditor.backup_files)}")
   print(f"CLI functional: {auditor.results.get('functionality_status', {}).get('cli_functional', False)}")