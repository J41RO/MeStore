#!/usr/bin/env python3
"""
CleanupManager - Safe cleanup tool for Surgical Modifier v6.0 project
Handles backup files, temporary files, and project organization
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime
import hashlib
import subprocess

class CleanupManager:
    """Safe cleanup manager for Surgical Modifier codebase"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path('.')
        self.backup_dir = self.project_root / '.cleanup_backups'
        self.log_file = self.project_root / 'cleanup.log'
        self.cleanup_report = {}
        
    def create_safety_backup(self) -> str:
        """Create complete project backup before cleanup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pre_cleanup_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        print(f"Creando backup de seguridad en: {backup_path}")
        
        # Create backup directory
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Copy important files (excluding existing backups)
        important_patterns = [
            '*.py', '*.json', '*.yaml', '*.yml', '*.toml', 
            '*.md', '*.txt', '*.ini', '*.cfg'
        ]
        
        copied_files = []
        for pattern in important_patterns:
            for file_path in self.project_root.rglob(pattern):
                # Skip if it's already a backup file
                if any(marker in str(file_path) for marker in ['.backup', '.bak', 'backup_', '.PRE_', '.BACKUP']):
                    continue
                
                rel_path = file_path.relative_to(self.project_root)
                backup_file_path = backup_path / rel_path
                backup_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.copy2(file_path, backup_file_path)
                    copied_files.append(str(rel_path))
                except Exception as e:
                    self._log(f"Error copying {file_path}: {e}")
        
        # Create backup manifest
        manifest = {
            'timestamp': timestamp,
            'backup_name': backup_name,
            'files_backed_up': len(copied_files),
            'file_list': copied_files
        }
        
        manifest_path = backup_path / 'backup_manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        self._log(f"Backup de seguridad creado: {len(copied_files)} archivos respaldados")
        return str(backup_path)
    
    def identify_cleanup_candidates(self) -> Dict[str, List[str]]:
        """Identify files that can be safely cleaned up"""
        candidates = {
            'backup_files': [],
            'temporary_files': [],
            'cache_files': [],
            'log_files': [],
            'compiled_files': []
        }
        
        backup_patterns = ['.backup', '.bak', 'backup_', '.PRE_', '.BACKUP', '.STEP', '_BACKUP']
        temp_patterns = ['.tmp', '.temp', '~', '.swp', '.swo']
        
        for file_path in self.project_root.rglob('*'):
            if not file_path.is_file():
                continue
                
            file_str = str(file_path)
            rel_path = str(file_path.relative_to(self.project_root))
            
            # Backup files
            if any(pattern in file_str for pattern in backup_patterns):
                candidates['backup_files'].append(rel_path)
            
            # Temporary files
            elif any(file_str.endswith(pattern) for pattern in temp_patterns):
                candidates['temporary_files'].append(rel_path)
            
            # Cache files
            elif '__pycache__' in file_str or file_path.suffix == '.pyc':
                candidates['cache_files'].append(rel_path)
            
            # Log files (but preserve main logs)
            elif file_path.suffix == '.log' and 'cleanup.log' not in file_str:
                candidates['log_files'].append(rel_path)
            
            # Compiled files
            elif file_path.suffix in ['.pyc', '.pyo', '.so']:
                candidates['compiled_files'].append(rel_path)
        
        return candidates
    
    def validate_cleanup_safety(self, candidates: Dict[str, List[str]]) -> Dict[str, Any]:
        """Validate that cleanup won't break functionality"""
        validation = {
            'safe_to_proceed': True,
            'warnings': [],
            'critical_files_found': [],
            'size_to_free': 0,
            'size_savings': 0
        }
        
        # Check if any critical files are marked for deletion
        critical_patterns = ['cli.py', '__init__.py', 'setup.py', 'requirements']
        
        all_candidates = []
        for file_list in candidates.values():
            all_candidates.extend(file_list)
        
        for candidate in all_candidates:
            # Skip files in backup directories - they're safe to delete
            if any(backup_dir in candidate for backup_dir in ['.cleanup_backups/', '.backup/', '.backups/', 'backup_']):
                # Calculate size but don't mark as critical
                try:
                    file_path = self.project_root / candidate
                    if file_path.exists():
                        file_size = file_path.stat().st_size
                        validation['size_to_free'] += file_size
                        validation['size_savings'] += file_size
                except Exception:
                    pass
                continue
                
            # Check if it's a critical file in the main project
            if any(pattern in candidate.lower() for pattern in critical_patterns):
                # Only flag if it's not clearly a backup
                if not any(marker in candidate.lower() for marker in ['.backup', '.bak', 'backup_', '.pre_']):
                    validation['critical_files_found'].append(candidate)
                    validation['safe_to_proceed'] = False
            
            # Calculate size
            try:
                file_path = self.project_root / candidate
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    validation['size_to_free'] += file_size
                    validation['size_savings'] += file_size
            except Exception:
                pass
        
        # Add warnings for large cleanup operations
        total_files = len(all_candidates)
        if total_files > 100:
            validation['warnings'].append(f"Gran cantidad de archivos para eliminar: {total_files}")
        
        if validation['size_savings'] > 10 * 1024 * 1024:  # 10MB
            size_mb = validation['size_savings'] / (1024 * 1024)
            validation['warnings'].append(f"Gran cantidad de espacio a liberar: {size_mb:.1f}MB")
        
        return validation
    
    def execute_cleanup(self, candidates: Dict[str, List[str]], confirm: bool = True) -> Dict[str, Any]:
        """Execute the cleanup operation"""
        if confirm:
            total_files = sum(len(files) for files in candidates.values())
            response = input(f"¿Eliminar {total_files} archivos? (yes/no): ")
            if response.lower() not in ['yes', 'y', 'si', 's']:
                return {'status': 'cancelled', 'message': 'Operación cancelada por el usuario'}
        
        results = {
            'status': 'completed',
            'files_deleted': 0,
            'errors': [],
            'categories_cleaned': {}
        }
        
        for category, file_list in candidates.items():
            deleted_count = 0
            category_errors = []
            
            for rel_path in file_list:
                file_path = self.project_root / rel_path
                try:
                    if file_path.exists():
                        file_path.unlink()
                        deleted_count += 1
                        self._log(f"Eliminado: {rel_path}")
                except Exception as e:
                    error_msg = f"Error eliminando {rel_path}: {e}"
                    category_errors.append(error_msg)
                    self._log(error_msg)
            
            results['categories_cleaned'][category] = {
                'files_deleted': deleted_count,
                'errors': category_errors
            }
            results['files_deleted'] += deleted_count
            results['errors'].extend(category_errors)
        
        # Clean empty directories
        self._clean_empty_directories()
        
        return results
    
    def _clean_empty_directories(self):
        """Remove empty directories after cleanup"""
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            for directory in dirs:
                dir_path = Path(root) / directory
                try:
                    if dir_path.is_dir() and not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        self._log(f"Directorio vacío eliminado: {dir_path.relative_to(self.project_root)}")
                except Exception as e:
                    self._log(f"Error eliminando directorio vacío {dir_path}: {e}")
    
    def verify_post_cleanup_integrity(self) -> Dict[str, Any]:
        """Verify that the project is still functional after cleanup"""
        integrity_check = {
            'cli_functional': False,
            'critical_files_present': True,
            'tests_passing': False,
            'import_errors': []
        }
        
        # Check cli.py functionality
        cli_path = self.project_root / 'cli.py'
        if cli_path.exists():
            try:
                result = subprocess.run(
                    ['python3', str(cli_path), '--help'], 
                    capture_output=True, text=True, timeout=10
                )
                integrity_check['cli_functional'] = result.returncode == 0
            except Exception as e:
                integrity_check['import_errors'].append(f"cli.py: {str(e)}")
        else:
            integrity_check['critical_files_present'] = False
        
        # Check critical files
        critical_files = ['cli.py', 'core/__init__.py', 'setup.py']
        for critical_file in critical_files:
            if not (self.project_root / critical_file).exists():
                integrity_check['critical_files_present'] = False
                break
        
        # Try running tests
        try:
            result = subprocess.run(
                ['python3', '-m', 'pytest', 'tests/', '-q'], 
                capture_output=True, text=True, timeout=60
            )
            integrity_check['tests_passing'] = result.returncode == 0
        except Exception as e:
            integrity_check['import_errors'].append(f"pytest: {str(e)}")
        
        return integrity_check
    
    def generate_cleanup_report(self) -> Dict[str, Any]:
        """Generate comprehensive cleanup report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'cleanup_summary': self.cleanup_report,
            'recommendations': self._generate_cleanup_recommendations()
        }
        
        return report
    
    def _generate_cleanup_recommendations(self) -> List[str]:
        """Generate recommendations based on cleanup results"""
        recommendations = []
        
        if self.cleanup_report.get('files_deleted', 0) > 50:
            recommendations.append("ÉXITO: Limpieza masiva completada - proyecto más organizado")
        
        if self.cleanup_report.get('errors', []):
            recommendations.append("REVISAR: Algunos archivos no pudieron eliminarse - verificar permisos")
        
        recommendations.append("SIGUIENTE: Ejecutar tests completos para verificar integridad")
        recommendations.append("VALIDAR: Confirmar que cli.py sigue funcional")
        
        return recommendations
    
    def _log(self, message: str):
        """Log cleanup operations"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        print(log_entry.strip())
    
    def full_cleanup_workflow(self) -> Dict[str, Any]:
        """Execute complete cleanup workflow"""
        print("=== INICIANDO FLUJO COMPLETO DE LIMPIEZA ===")
        
        # Step 1: Create safety backup
        backup_path = self.create_safety_backup()
        
        # Step 2: Identify cleanup candidates
        candidates = self.identify_cleanup_candidates()
        
        # Step 3: Validate safety
        validation = self.validate_cleanup_safety(candidates)
        
        if not validation['safe_to_proceed']:
            return {
                'status': 'aborted',
                'reason': 'Archivos críticos encontrados en candidatos de limpieza',
                'critical_files': validation['critical_files_found']
            }
        
        # Step 4: Execute cleanup
        cleanup_results = self.execute_cleanup(candidates, confirm=False)
        self.cleanup_report = cleanup_results
        
        # Step 5: Verify integrity
        integrity = self.verify_post_cleanup_integrity()
        
        return {
            'status': 'completed',
            'backup_created': backup_path,
            'cleanup_results': cleanup_results,
            'integrity_check': integrity,
            'recommendations': self._generate_cleanup_recommendations()
        }

if __name__ == '__main__':
    cleaner = CleanupManager()
    result = cleaner.full_cleanup_workflow()
    print("\nRESULTADO DE LIMPIEZA:")
    print(f"Estado: {result['status']}")
    if result['status'] == 'completed':
        print(f"Archivos eliminados: {result['cleanup_results']['files_deleted']}")
        print(f"CLI funcional: {result['integrity_check']['cli_functional']}")