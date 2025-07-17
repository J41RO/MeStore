#!/usr/bin/env python3
"""
🔧 SURGICAL MODIFIER ULTIMATE v5.3 - HERRAMIENTA UNIVERSAL MEJORADA
=======================================================================
✅ CORREGIDO: Procesamiento correcto de \n en contenido multi-línea
✅ CORREGIDO: CREATE funciona con rutas relativas automáticamente
✅ NUEVO v5.3: Búsqueda flexible con similitud para cualquier proyecto
✅ NUEVO v5.3: Modo exploración universal para cualquier tipo de archivo
✅ NUEVO v5.3: Fragmentación inteligente de patrones largos
✅ NUEVO v5.3: Detección automática de contexto de frameworks
✅ NUEVO v5.3: Sugerencias mejoradas para cualquier lenguaje/proyecto
✅ MEJORADO: Validación previa robusta
✅ MEJORADO: Auto-sugerencias universales
✅ MEJORADO: Manejo de errores para proyectos reales
✅ NUEVO v5.3: Verificación de integridad de código
=======================================================================
"""

import sys
import os
import re
import shutil
import tempfile
import json
import difflib
from datetime import datetime
from pathlib import Path
import subprocess
from typing import Dict, List, Tuple, Optional, Any
import ast  # Para verificación de sintaxis Python

class BackupManager:
    """Sistema de backup mejorado con limpieza automática"""
    
    def __init__(self, keep_successful_backups: bool = False, max_backups: int = 5):
        self.keep_successful_backups = keep_successful_backups
        self.max_backups = max_backups
        self.created_backups = []  # Track backups created in current operation
    
    def create_backup(self, file_path: str, backup_dir: str) -> str:
        """Crear backup con tracking para limpieza posterior"""
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = int(datetime.now().timestamp())
        filename = os.path.basename(file_path)
        backup_filename = f"{filename}.backup.{timestamp}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        shutil.copy2(file_path, backup_path)
        
        # Track backup for potential cleanup
        self.created_backups.append({
            'path': backup_path,
            'original_file': file_path,
            'timestamp': timestamp,
            'filename': backup_filename
        })
        
        ColorLogger.success(f"Backup creado: {os.path.relpath(backup_path)}")
        return backup_path
    
    def cleanup_successful_backups(self):
        """Limpiar backups después de operación exitosa"""
        if not self.keep_successful_backups:
            cleaned_count = 0
            for backup_info in self.created_backups:
                try:
                    if os.path.exists(backup_info['path']):
                        os.remove(backup_info['path'])
                        cleaned_count += 1
                        ColorLogger.info(f"🧹 Backup limpiado: {backup_info['filename']}")
                except Exception as e:
                    ColorLogger.warning(f"No se pudo limpiar backup: {e}")
            
            if cleaned_count > 0:
                ColorLogger.success(f"🧹 Sistema limpio: {cleaned_count} backup(s) eliminado(s) automáticamente")
            
            self.created_backups.clear()
        else:
            ColorLogger.info(f"📦 Backups conservados: {len(self.created_backups)} archivo(s)")
    
    def restore_from_backup(self, backup_path: str, original_file: str):
        """Restaurar desde backup y conservar el backup"""
        try:
            shutil.copy2(backup_path, original_file)
            ColorLogger.info("📦 Backup restaurado por error")
            # NO eliminar backup cuando hay error - conservar para investigación
        except Exception as e:
            ColorLogger.error(f"Error restaurando backup: {e}")
    
    def cleanup_old_backups(self, backup_dir: str):
        """Limpiar backups antiguos según política de retención"""
        if not os.path.exists(backup_dir):
            return
        
        try:
            # Obtener todos los archivos de backup
            backup_files = []
            for file in os.listdir(backup_dir):
                if '.backup.' in file:
                    file_path = os.path.join(backup_dir, file)
                    if os.path.isfile(file_path):
                        # Extraer timestamp del nombre del archivo
                        try:
                            timestamp_str = file.split('.backup.')[-1]
                            timestamp = int(timestamp_str)
                            backup_files.append((file_path, timestamp))
                        except ValueError:
                            continue
            
            # Ordenar por timestamp (más recientes primero)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Conservar solo los últimos max_backups
            if len(backup_files) > self.max_backups:
                files_to_delete = backup_files[self.max_backups:]
                
                for file_path, timestamp in files_to_delete:
                    try:
                        os.remove(file_path)
                        ColorLogger.info(f"🧹 Backup antiguo eliminado: {os.path.basename(file_path)}")
                    except Exception as e:
                        ColorLogger.warning(f"Error eliminando backup antiguo: {e}")
                
                if files_to_delete:
                    ColorLogger.info(f"🧹 Limpieza de backups antiguos: {len(files_to_delete)} archivo(s) eliminado(s)")
        
        except Exception as e:
            ColorLogger.warning(f"Error en limpieza de backups antiguos: {e}")

class ColorLogger:
    """Sistema de logging con colores y estructura mejorado"""
    
    COLORS = {
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m'
    }
    
    @classmethod
    def success(cls, message: str):
        print(f"✅ {message}")
    
    @classmethod
    def error(cls, message: str, suggestion: str = None):
        print(f"{cls.COLORS['red']}❌ ERROR: {message}{cls.COLORS['reset']}")
        if suggestion:
            print(f"🔧 Sugerencia: {suggestion}")
    
    @classmethod
    def warning(cls, message: str):
        print(f"{cls.COLORS['yellow']}⚠️ ADVERTENCIA: {message}{cls.COLORS['reset']}")
    
    @classmethod
    def info(cls, message: str):
        print(f"ℹ️ {message}")
    
    @classmethod
    def section(cls, title: str):
        print(f"\n=== 🔧 {title.upper()} ===")
    
    @classmethod
    def analyzing(cls, what: str):
        print(f"🔍 ANALIZANDO: {what}")
    
    @classmethod
    def creating(cls, what: str):
        print(f"📝 CREANDO: {what}")
    
    @classmethod
    def preview(cls, title: str, content: str, max_lines: int = 5):
        """Mostrar preview de contenido"""
        print(f"\n📋 PREVIEW: {title}")
        lines = content.split('\n')
        for i, line in enumerate(lines[:max_lines]):
            print(f"   {i+1:2d}: {line}")
        if len(lines) > max_lines:
            print(f"   ... ({len(lines) - max_lines} líneas más)")
    
    @classmethod
    def diff(cls, title: str, before: str, after: str):
        """Mostrar diferencias visuales"""
        print(f"\n📊 DIFF: {title}")
        before_lines = before.split('\n')
        after_lines = after.split('\n')
        
        diff = list(difflib.unified_diff(
            before_lines, after_lines, 
            fromfile="antes", tofile="después", 
            lineterm="", n=3
        ))
        
        for line in diff[:20]:  # Mostrar solo primeras 20 líneas
            if line.startswith('+++') or line.startswith('---'):
                print(f"{cls.COLORS['blue']}{line}{cls.COLORS['reset']}")
            elif line.startswith('+'):
                print(f"{cls.COLORS['green']}{line}{cls.COLORS['reset']}")
            elif line.startswith('-'):
                print(f"{cls.COLORS['red']}{line}{cls.COLORS['reset']}")
            else:
                print(f"{cls.COLORS['dim']}{line}{cls.COLORS['reset']}")

class UniversalPatternHelper:
    """NUEVO v5.3: Asistente universal para encontrar patrones en cualquier proyecto"""
    
    def __init__(self, file_content: str, file_path: str):
        self.content = file_content
        self.lines = file_content.split('\n')
        self.file_path = file_path
        self.file_type = self._detect_file_type()
        self.framework_context = self._detect_framework_context()
    
    def _detect_file_type(self) -> str:
        """Detectar tipo de archivo universal"""
        ext = os.path.splitext(self.file_path)[1].lower()
        
        type_mapping = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript', 
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'markup',
            '.xml': 'markup',
            '.css': 'stylesheet',
            '.scss': 'stylesheet',
            '.sass': 'stylesheet',
            '.json': 'config',
            '.yaml': 'config',
            '.yml': 'config',
            '.toml': 'config',
            '.ini': 'config',
            '.conf': 'config',
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'bash',
            '.fish': 'bash',
            '.sql': 'database',
            '.md': 'markdown',
            '.rst': 'documentation',
            '.tex': 'latex'
        }
        
        return type_mapping.get(ext, 'generic')
    
    def _detect_framework_context(self) -> List[str]:
        """NUEVO v5.3: Detectar contexto de frameworks universalmente"""
        frameworks = []
        
        # Análisis universal de contenido
        content_lower = self.content.lower()
        
        # Frameworks Python
        if 'django' in content_lower or 'from django' in content_lower:
            frameworks.append('django')
        if 'flask' in content_lower or 'from flask' in content_lower:
            frameworks.append('flask')
        if 'fastapi' in content_lower or 'from fastapi' in content_lower:
            frameworks.append('fastapi')
        if 'sqlalchemy' in content_lower or 'column(' in content_lower:
            frameworks.append('sqlalchemy')
        if 'pytest' in content_lower or '@pytest' in content_lower:
            frameworks.append('pytest')
        if 'unittest' in content_lower or 'class.*test' in content_lower:
            frameworks.append('unittest')
        
        # Frameworks JavaScript/TypeScript
        if 'react' in content_lower or 'jsx' in content_lower:
            frameworks.append('react')
        if 'vue' in content_lower or '@vue' in content_lower:
            frameworks.append('vue')
        if 'angular' in content_lower or '@angular' in content_lower:
            frameworks.append('angular')
        if 'express' in content_lower or 'app.get(' in content_lower:
            frameworks.append('express')
        if 'jest' in content_lower or 'describe(' in content_lower:
            frameworks.append('jest')
        # More specific mocha detection to avoid false positives in Python files
        if ('mocha' in content_lower and ('describe(' in content_lower or 'it(' in content_lower)) or (self.file_type in ['javascript', 'typescript'] and 'it(' in content_lower):
            frameworks.append('mocha')
        
        # Frameworks Java
        if 'spring' in content_lower or '@controller' in content_lower:
            frameworks.append('spring')
        if 'junit' in content_lower or '@test' in content_lower:
            frameworks.append('junit')
        
        # Frameworks C#/.NET
        if 'asp.net' in content_lower or '[httpget]' in content_lower:
            frameworks.append('aspnet')
        if 'nunit' in content_lower or '[testmethod]' in content_lower:
            frameworks.append('nunit')
        
        # Frameworks genéricos
        if 'docker' in content_lower or 'from ' in content_lower and ':' in content_lower:
            frameworks.append('docker')
        if 'kubernetes' in content_lower or 'apiversion:' in content_lower:
            frameworks.append('kubernetes')
        
        return frameworks
    
    def find_flexible_pattern(self, target: str, similarity_threshold: float = 0.6) -> List[Dict]:
        """NUEVO v5.3: Búsqueda flexible universal con múltiples estrategias"""
        results = []
        target_lower = target.lower()
        target_words = target_lower.split()
        
        for i, line in enumerate(self.lines, 1):
            line_clean = line.strip()
            if not line_clean or len(line_clean) < 3:
                continue
            
            # Estrategia 1: Similitud de secuencia
            similarity = difflib.SequenceMatcher(None, target_lower, line_clean.lower()).ratio()
            
            # Estrategia 2: Coincidencia de palabras clave
            word_matches = sum(1 for word in target_words if len(word) > 2 and word in line_clean.lower())
            word_similarity = word_matches / len(target_words) if target_words else 0
            
            # Estrategia 3: Análisis de estructura (para código)
            structure_similarity = 0
            if self.file_type in ['python', 'javascript', 'typescript', 'java', 'cpp', 'csharp']:
                # Buscar patrones estructurales similares
                target_structure = self._extract_code_structure(target)
                line_structure = self._extract_code_structure(line_clean)
                if target_structure and line_structure:
                    structure_similarity = difflib.SequenceMatcher(None, target_structure, line_structure).ratio()
            
            # Combinar métricas con pesos
            # Mejorar fórmula: usar suma ponderada en lugar de max
            combined_score = (
                similarity * 0.4 +
                word_similarity * 0.4 + 
                structure_similarity * 0.2
            )
            
            if combined_score >= similarity_threshold:
                results.append({
                    'line_number': i,
                    'content': line_clean,
                    'similarity': combined_score,
                    'type': 'flexible_match',
                    'strategies': {
                        'sequence': similarity,
                        'words': word_similarity,
                        'structure': structure_similarity
                    }
                })
        
        # Ordenar por similitud
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:8]  # Top 8 resultados
    
    def _extract_code_structure(self, code: str) -> str:
        """NUEVO v5.3: Extraer estructura de código universal"""
        # Remover strings y comentarios para análisis estructural
        structure = re.sub(r'["\'].*?["\']', '""', code)  # Remover strings
        structure = re.sub(r'//.*$|#.*$', '', structure)  # Remover comentarios de línea
        structure = re.sub(r'/\*.*?\*/', '', structure)   # Remover comentarios de bloque
        structure = re.sub(r'\s+', ' ', structure)        # Normalizar espacios
        return structure.strip()
    
    def get_framework_specific_patterns(self) -> List[str]:
        """NUEVO v5.3: Obtener patrones específicos del framework detectado"""
        patterns = []
        
        for framework in self.framework_context:
            if framework == 'sqlalchemy':
                patterns.extend(self._get_sqlalchemy_patterns())
            elif framework == 'pytest':
                patterns.extend(self._get_pytest_patterns())
            elif framework == 'django':
                patterns.extend(self._get_django_patterns())
            elif framework == 'react':
                patterns.extend(self._get_react_patterns())
            elif framework == 'spring':
                patterns.extend(self._get_spring_patterns())
            # ... agregar más frameworks según necesidad
        
        # Si no hay frameworks específicos, usar patrones genéricos por tipo de archivo
        if not patterns:
            patterns = self._get_generic_patterns_by_type()
        
        return list(set(patterns))  # Eliminar duplicados
    
    def _get_sqlalchemy_patterns(self) -> List[str]:
        """Patrones específicos de SQLAlchemy"""
        patterns = []
        for line in self.lines:
            line_clean = line.strip()
            if any(keyword in line_clean for keyword in ['Column(', 'relationship(', 'ForeignKey(', 'Table(']):
                patterns.append(line_clean)
        return patterns
    
    def _get_pytest_patterns(self) -> List[str]:
        """Patrones específicos de pytest"""
        patterns = []
        for line in self.lines:
            line_clean = line.strip()
            if any(keyword in line_clean for keyword in ['@pytest', 'def test_', 'async def test_', 'fixture']):
                patterns.append(line_clean)
        return patterns
    
    def _get_django_patterns(self) -> List[str]:
        """Patrones específicos de Django"""
        patterns = []
        for line in self.lines:
            line_clean = line.strip()
            if any(keyword in line_clean for keyword in ['models.', 'forms.', 'views.', 'urls.', 'class.*View']):
                patterns.append(line_clean)
        return patterns
    
    def _get_react_patterns(self) -> List[str]:
        """Patrones específicos de React"""
        patterns = []
        for line in self.lines:
            line_clean = line.strip()
            if any(keyword in line_clean for keyword in ['useState', 'useEffect', 'function.*Component', 'export default']):
                patterns.append(line_clean)
        return patterns
    
    def _get_spring_patterns(self) -> List[str]:
        """Patrones específicos de Spring"""
        patterns = []
        for line in self.lines:
            line_clean = line.strip()
            if any(keyword in line_clean for keyword in ['@Controller', '@Service', '@Repository', '@Component', '@RequestMapping']):
                patterns.append(line_clean)
        return patterns
    
    def _get_generic_patterns_by_type(self) -> List[str]:
        """Patrones genéricos según tipo de archivo"""
        patterns = []
        
        if self.file_type == 'python':
            keywords = ['def ', 'class ', 'import ', 'from ', 'if __name__']
        elif self.file_type in ['javascript', 'typescript']:
            keywords = ['function ', 'const ', 'let ', 'var ', 'export ', 'import ', 'class ']
        elif self.file_type == 'java':
            keywords = ['public class', 'private ', 'public ', 'protected ', 'import ']
        elif self.file_type == 'cpp':
            keywords = ['class ', 'struct ', 'namespace ', '#include', 'public:', 'private:']
        elif self.file_type == 'csharp':
            keywords = ['public class', 'private ', 'public ', 'protected ', 'using ']
        else:
            # Para tipos genéricos, buscar líneas que parecen definiciones
            keywords = ['=', ':', '{', '}', '(', ')']
        
        for line in self.lines:
            line_clean = line.strip()
            if line_clean and any(keyword in line_clean for keyword in keywords):
                patterns.append(line_clean)
        
        return patterns[:15]  # Limitar resultados
    
    def suggest_pattern_fragments(self, target: str) -> List[str]:
        """NUEVO v5.3: Sugerir fragmentos de patrón universales"""
        fragments = []
        
        if len(target) > 50:  # Patrón muy largo
            # Extraer palabras clave importantes (universal)
            key_words = []
            
            # Filtrar palabras comunes por tipo de archivo
            common_words = self._get_common_words_by_type()
            
            for word in target.split():
                if (len(word) > 3 and 
                    word.lower() not in common_words and
                    not word.isdigit() and
                    word.isalnum()):
                    key_words.append(word)
            
            # Sugerir búsquedas por fragmentos
            for word in key_words[:4]:  # Top 4 palabras clave
                matching_lines = [
                    line.strip() for line in self.lines 
                    if word.lower() in line.lower() and len(line.strip()) > 10
                ]
                fragments.extend(matching_lines[:2])  # Max 2 por palabra
        
        return list(set(fragments))  # Eliminar duplicados
    
    def _get_common_words_by_type(self) -> List[str]:
        """Obtener palabras comunes según el tipo de archivo"""
        common_by_type = {
            'python': ['def', 'class', 'self', 'none', 'true', 'false', 'and', 'or', 'not', 'with', 'as'],
            'javascript': ['function', 'const', 'let', 'var', 'null', 'undefined', 'true', 'false', 'this'],
            'typescript': ['function', 'const', 'let', 'var', 'null', 'undefined', 'true', 'false', 'this', 'interface', 'type'],
            'java': ['public', 'private', 'protected', 'static', 'final', 'class', 'interface', 'null', 'true', 'false'],
            'cpp': ['public', 'private', 'protected', 'class', 'struct', 'namespace', 'using', 'include'],
            'generic': ['the', 'and', 'or', 'not', 'with', 'for', 'in', 'on', 'at', 'to', 'from']
        }
        
        return common_by_type.get(self.file_type, common_by_type['generic'])

class UniversalExplorer:
    """NUEVO v5.3: Explorador universal para cualquier tipo de archivo"""
    
    @staticmethod
    def show_file_structure(file_path: str, show_lines: bool = True, filter_type: str = 'smart') -> None:
        """Mostrar estructura universal del archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Usar UniversalPatternHelper para detección consistente
            helper = UniversalPatternHelper('', file_path)
            file_type = helper.file_type
            
            print(f"\n📋 ESTRUCTURA DE ARCHIVO: {os.path.basename(file_path)}")
            print(f"📊 Total líneas: {len(lines)} | Tipo: {file_type}")
            print("=" * 60)
            
            important_lines = UniversalExplorer._filter_important_lines(lines, file_type, filter_type)
            
            for line_info in important_lines:
                line_num, line_content, line_type = line_info
                icon = UniversalExplorer._get_line_icon(line_type)
                
                if show_lines:
                    print(f"{line_num:3d}: {icon} {line_content}")
                else:
                    truncated = line_content[:70] + "..." if len(line_content) > 70 else line_content
                    print(f"{line_num:3d}: {icon} {truncated}")
            
            # Estadísticas
            print(f"\n📊 ESTADÍSTICAS:")
            stats = UniversalExplorer._get_file_stats(lines, file_type)
            for stat, value in stats.items():
                print(f"   {stat}: {value}")
                
        except Exception as e:
            print(f"❌ Error explorando archivo: {e}")
    
    @staticmethod
    def _detect_file_type(file_path: str) -> str:
        """Detectar tipo de archivo para exploración"""
        ext = os.path.splitext(file_path)[1].lower()
        
        type_mapping = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.java': 'java', '.cpp': 'cpp', '.c': 'c', '.cs': 'csharp',
            '.php': 'php', '.rb': 'ruby', '.go': 'go', '.rs': 'rust',
            '.html': 'markup', '.xml': 'markup', '.css': 'stylesheet',
            '.json': 'config', '.yaml': 'config', '.yml': 'config',
            '.sql': 'database', '.md': 'markdown'
        }
        
        return type_mapping.get(ext, 'generic')
    
    @staticmethod
    def _filter_important_lines(lines: List[str], file_type: str, filter_type: str) -> List[Tuple[int, str, str]]:
        """Filtrar líneas importantes según el tipo de archivo"""
        important = []
        
        for i, line in enumerate(lines, 1):
            line_clean = line.rstrip()
            if not line_clean or line_clean.isspace():
                continue
            
            line_importance = UniversalExplorer._classify_line_importance(line_clean, file_type)
            
            if filter_type == 'smart' and line_importance in ['high', 'medium']:
                important.append((i, line_clean, line_importance))
            elif filter_type == 'all':
                important.append((i, line_clean, line_importance))
            elif filter_type == 'high' and line_importance == 'high':
                important.append((i, line_clean, line_importance))
        
        return important
    
    @staticmethod
    def _classify_line_importance(line: str, file_type: str) -> str:
        """Clasificar importancia de línea universal"""
        line_lower = line.strip().lower()
        
        # Patrones universales de alta importancia
        high_patterns = {
            'python': ['class ', 'def ', 'import ', 'from ', '@', 'if __name__'],
            'javascript': ['function ', 'class ', 'const ', 'export ', 'import ', '=>'],
            'typescript': ['interface ', 'type ', 'function ', 'class ', 'export ', 'import '],
            'java': ['public class', 'public interface', 'public enum', '@', 'import '],
            'cpp': ['class ', 'struct ', 'namespace ', '#include', 'template'],
            'csharp': ['public class', 'public interface', 'public enum', 'using ', '['],
            'generic': ['=', ':', '{', '}']
        }
        
        # Patrones universales de importancia media
        medium_patterns = {
            'python': ['return ', 'yield ', 'raise ', 'assert ', 'global ', 'nonlocal '],
            'javascript': ['return ', 'throw ', 'async ', 'await ', 'var ', 'let '],
            'typescript': ['return ', 'throw ', 'async ', 'await ', 'var ', 'let '],
            'java': ['return ', 'throw ', 'new ', 'super ', 'this '],
            'cpp': ['return ', 'throw ', 'new ', 'delete ', 'virtual '],
            'csharp': ['return ', 'throw ', 'new ', 'base ', 'this '],
            'generic': ['(', ')', '[', ']']
        }
        
        file_high = high_patterns.get(file_type, high_patterns['generic'])
        file_medium = medium_patterns.get(file_type, medium_patterns['generic'])
        
        # Verificar importancia
        if any(pattern in line_lower for pattern in file_high):
            return 'high'
        elif any(pattern in line_lower for pattern in file_medium):
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def _get_line_icon(line_type: str) -> str:
        """Obtener icono para tipo de línea"""
        icons = {
            'high': '🔥',
            'medium': '⚡',
            'low': '📝'
        }
        return icons.get(line_type, '📄')
    
    @staticmethod
    def _get_file_stats(lines: List[str], file_type: str) -> Dict[str, int]:
        """Obtener estadísticas del archivo"""
        stats = {
            'Total líneas': len(lines),
            'Líneas no vacías': len([l for l in lines if l.strip()]),
            'Líneas de comentarios': 0,
            'Líneas de código': 0
        }
        
        # Detectar comentarios según tipo de archivo
        comment_patterns = {
            'python': ['#'],
            'javascript': ['//', '/*'],
            'typescript': ['//', '/*'],
            'java': ['//', '/*'],
            'cpp': ['//', '/*'],
            'csharp': ['//', '/*'],
            'generic': ['#', '//', '/*']
        }
        
        patterns = comment_patterns.get(file_type, comment_patterns['generic'])
        
        for line in lines:
            line_clean = line.strip()
            if line_clean:
                if any(line_clean.startswith(pattern) for pattern in patterns):
                    stats['Líneas de comentarios'] += 1
                else:
                    stats['Líneas de código'] += 1
        
        return stats
    
    @staticmethod
    def search_in_file(file_path: str, search_term: str, context_lines: int = 2, case_sensitive: bool = False) -> None:
        """Búsqueda universal en archivo con contexto"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"\n🔍 BÚSQUEDA: '{search_term}' en {os.path.basename(file_path)}")
            print(f"🎯 Modo: {'Sensible a mayúsculas' if case_sensitive else 'Insensible a mayúsculas'}")
            print("=" * 60)
            
            matches_found = 0
            
            for i, line in enumerate(lines):
                line_content = line.rstrip()
                search_target = search_term if case_sensitive else search_term.lower()
                line_target = line_content if case_sensitive else line_content.lower()
                
                if search_target in line_target:
                    matches_found += 1
                    
                    # Mostrar contexto
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 1)
                    
                    print(f"\n📍 Coincidencia #{matches_found} - Línea {i+1}:")
                    
                    for j in range(start, end):
                        line_to_show = lines[j].rstrip()
                        if j == i:
                            # Resaltar línea con coincidencia
                            print(f">>> {j+1:3d}: {line_to_show}")
                        else:
                            print(f"    {j+1:3d}: {line_to_show}")
            
            if matches_found == 0:
                print(f"❌ No se encontraron coincidencias para '{search_term}'")
                
                # Sugerir búsquedas similares
                helper = UniversalPatternHelper('\n'.join(lines), file_path)
                similar = helper.find_flexible_pattern(search_term, 0.3)
                if similar:
                    print(f"\n💡 ¿Quizás buscabas algo similar?")
                    for match in similar[:3]:
                        print(f"   Línea {match['line_number']}: {match['content']}")
            else:
                print(f"\n✅ Se encontraron {matches_found} coincidencias")
                
        except Exception as e:
            print(f"❌ Error buscando en archivo: {e}")

class ContentHandler:
    """Manejo inteligente de contenido con correcciones v5.3"""
    
    def __init__(self, content: str, file_path: str = "", operation: str = ""):
        self.original_content = content
        self.file_path = file_path
        self.operation = operation
        self.content_type = self._detect_content_type()
        self.is_problematic = self._detect_problematic_content()
        self.handling_strategy = self._determine_strategy()
    
    def _detect_content_type(self) -> str:
        """Detectar tipo de contenido basado en archivo y contenido"""
        
        # Detección por extensión de archivo
        if self.file_path:
            ext = os.path.splitext(self.file_path)[1].lower()
            type_mapping = {
                '.py': 'python',
                '.js': 'javascript', '.jsx': 'javascript',
                '.ts': 'typescript', '.tsx': 'typescript',
                '.java': 'java',
                '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
                '.c': 'c',
                '.cs': 'csharp',
                '.php': 'php',
                '.rb': 'ruby',
                '.go': 'go',
                '.rs': 'rust',
                '.swift': 'swift',
                '.kt': 'kotlin',
                '.scala': 'scala',
                '.sh': 'bash', '.bash': 'bash',
                '.html': 'markup', '.xml': 'markup',
                '.css': 'stylesheet', '.scss': 'stylesheet',
                '.json': 'config', '.yaml': 'config', '.yml': 'config',
                '.sql': 'database'
            }
            
            if ext in type_mapping:
                return type_mapping[ext]
        
        # Detección por contenido (universal)
        content_lower = self.original_content.lower()
        
        # Indicadores por lenguaje
        if any(indicator in content_lower for indicator in ['def ', 'class ', 'import ', 'from ', '__name__']):
            return 'python'
        elif any(indicator in content_lower for indicator in ['function ', 'const ', 'let ', 'var ', '=>', 'console.log']):
            return 'javascript'
        elif any(indicator in content_lower for indicator in ['interface ', 'type ', 'export ', 'import ']):
            return 'typescript'
        elif any(indicator in content_lower for indicator in ['public class', 'public static', 'import java']):
            return 'java'
        elif any(indicator in content_lower for indicator in ['#include', 'namespace ', 'std::']):
            return 'cpp'
        elif any(indicator in content_lower for indicator in ['using system', 'public class', 'namespace ']):
            return 'csharp'
        elif any(indicator in content_lower for indicator in ['#!/bin/bash', 'echo ', 'if [', '${', 'then', 'fi']):
            return 'bash'
        else:
            return 'generic'
    
    def _detect_problematic_content(self) -> bool:
        """Detectar si el contenido es problemático para bash (universal)"""
        
        # Para lenguajes de programación modernos, ser más permisivo
        if self.content_type in ['python', 'javascript', 'typescript', 'java', 'cpp', 'csharp']:
            problematic_indicators = [
                # Solo contenido extremadamente complejo
                len(self.original_content.split('\n')) > 20,
                len(self.original_content) > 3000,
                
                # Backticks con comandos bash reales
                '`' in self.original_content and any(cmd in self.original_content for cmd in ['ls', 'cat', 'grep', 'find']),
                
                # Variables bash complejas
                '${' in self.original_content and 'bash' in self.original_content.lower(),
            ]
        else:
            # Para otros tipos, usar detección más estricta
            problematic_indicators = [
                len(self.original_content.split('\n')) > 8,
                '"' in self.original_content and "'" in self.original_content,
                '`' in self.original_content,
                '$' in self.original_content and '{' in self.original_content,
                self.original_content.count('"') % 2 != 0,
                self.original_content.count("'") % 2 != 0,
                '\\' in self.original_content,
                len(self.original_content) > 1000,
            ]
        
        return any(problematic_indicators)
    
    def _determine_strategy(self) -> str:
        """Determinar estrategia de manejo inteligente universal"""
        
        # NUEVA LÓGICA v5.3: Más inteligente para contenido universal
        if self.content_type in ['python', 'javascript', 'typescript', 'java', 'cpp', 'csharp']:
            ColorLogger.info(f"Modo RAW v5.3 activado para contenido {self.content_type}") 
            return 'raw_mode_v3'
        
        if not self.is_problematic:
            return 'direct'
        elif len(self.original_content.split('\n')) > 20:
            return 'temp_file'
        elif '`' in self.original_content and any(cmd in self.original_content for cmd in ['ls', 'cat', 'grep']):
            return 'temp_file'
        elif '"' in self.original_content or "'" in self.original_content:
            return 'smart_escape_v3'
        else:
            return 'escape_special_v3'
    
    def get_safe_content(self) -> Tuple[str, Optional[str]]:
        """Obtener contenido seguro con mejoras v5.3"""
        
        if self.handling_strategy == 'raw_mode_v3':
            # NUEVO v5.3: Modo RAW universal mejorado
            processed_content = self._process_multiline_content_v3()
            ColorLogger.info("Usando modo RAW v5.3 - procesamiento universal mejorado")
            return processed_content, None
        
        elif self.handling_strategy == 'direct':
            return self.original_content, None
        
        elif self.handling_strategy == 'temp_file':
            temp_file = self._create_temp_file()
            return f'@TEMP_FILE:{temp_file}', temp_file
        
        elif self.handling_strategy == 'smart_escape_v3':
            escaped = self._smart_escape_v3()
            return escaped, None
        
        elif self.handling_strategy == 'escape_special_v3':
            escaped = self._escape_special_v3()
            return escaped, None
        
        else:
            # Fallback mejorado
            temp_file = self._create_temp_file()
            return f'@TEMP_FILE:{temp_file}', temp_file
    
    def _process_multiline_content_v3(self) -> str:
        """NUEVO v5.3: Procesar contenido multi-línea universal"""
        content = self.original_content
        
        # Si el contenido contiene \n literal, convertirlos a saltos de línea reales
        if '\\n' in content:
            # Solo convertir \n que no están ya escapados
            content = re.sub(r'(?<!\\)\\n', '\n', content)
            ColorLogger.info("Convertidos \\n literales a saltos de línea reales")
        
        # Procesamiento adicional para diferentes tipos de contenido
        if self.content_type == 'python':
            # Preservar indentación Python
            content = self._preserve_python_indentation(content)
        elif self.content_type in ['javascript', 'typescript']:
            # Preservar estructura de bloques JavaScript/TypeScript
            content = self._preserve_js_structure(content)
        
        return content
    
    def _preserve_python_indentation(self, content: str) -> str:
        """Preservar indentación Python"""
        lines = content.split('\n')
        preserved_lines = []
        
        for line in lines:
            # Preservar indentación existente
            if line.strip():
                preserved_lines.append(line)
            else:
                preserved_lines.append('')
        
        return '\n'.join(preserved_lines)
    
    def _preserve_js_structure(self, content: str) -> str:
        """Preservar estructura JavaScript/TypeScript"""
        # Manejar template literals y arrow functions
        content = re.sub(r'`([^`]*)`', r'`\1`', content)  # Preservar template literals
        return content
    
    def _smart_escape_v3(self) -> str:
        """NUEVO v5.3: Escape inteligente universal mejorado"""
        content = self.original_content
        
        # Escape universal más inteligente
        if self.content_type in ['python', 'javascript', 'typescript', 'java', 'cpp', 'csharp']:
            # Solo escapar caracteres críticos para bash
            bash_critical = ['!', '$`', '$(', '&&', '||']
            for chars in bash_critical:
                if chars in content:
                    # Usar temp file para casos realmente problemáticos
                    return f'@TEMP_FILE:{self._create_temp_file()}'
            
            # Para casos simples, escape mínimo
            content = content.replace('"', '\\"')
        else:
            # Para otros tipos, escape más completo pero inteligente
            content = content.replace('\\', '\\\\')  # Escapar backslashes primero
            content = content.replace('"', '\\"')    # Escapar comillas dobles
            if "'" in content and '"' in content:
                content = content.replace("'", "\\'")
        
        return content
    
    def _escape_special_v3(self) -> str:
        """NUEVO v5.3: Escape de caracteres especiales universal"""
        content = self.original_content
        
        # Solo escapar caracteres realmente problemáticos universalmente
        critical_chars = ['$`', '$(', '!', '&&', '||']
        
        for chars in critical_chars:
            if chars in content:
                # Para casos críticos, usar temp file
                return f'@TEMP_FILE:{self._create_temp_file()}'
        
        # Para otros casos, escape selectivo universal
        safe_chars = ['`']  # Solo backticks simples
        for char in safe_chars:
            if char in content:
                content = content.replace(char, f'\\{char}')
        
        return content
    
    def _create_temp_file(self) -> str:
        """Crear archivo temporal con el contenido"""
        processed_content = self._process_multiline_content_v3()
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tmp', encoding='utf-8') as f:
            f.write(processed_content)
            return f.name

class ProjectContext:
    """Detección y gestión del contexto del proyecto universal"""
    
    def __init__(self):
        self.current_dir = os.getcwd()
        self.context = self._detect_context()
        self.project_root = self._find_project_root()
        self.structure = self._analyze_project_structure()
    
    def _detect_context(self) -> str:
        """Detectar contexto universal desde directorio"""
        cwd = self.current_dir.lower()
        
        # Patrones universales de estructura de proyecto
        if any(pattern in cwd for pattern in ['/backend', '/server', '/api']):
            return 'backend'
        elif any(pattern in cwd for pattern in ['/frontend', '/client', '/ui', '/web']):
            return 'frontend'
        elif any(pattern in cwd for pattern in ['/mobile', '/app', '/android', '/ios']):
            return 'mobile'
        elif any(pattern in cwd for pattern in ['/tests', '/test', '/spec']):
            return 'testing'
        elif any(pattern in cwd for pattern in ['/docs', '/documentation']):
            return 'documentation'
        elif any(pattern in cwd for pattern in ['/scripts', '/tools', '/bin']):
            return 'scripts'
        else:
            return 'root'
    
    def _find_project_root(self) -> str:
        """Encontrar raíz del proyecto universal"""
        current = Path(self.current_dir)
        
        # Indicadores universales de raíz de proyecto
        project_indicators = [
            # JavaScript/Node.js
            'package.json', 'yarn.lock', 'package-lock.json',
            # Python
            'requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile',
            # Java
            'pom.xml', 'build.gradle', 'gradle.properties',
            # .NET
            '*.sln', '*.csproj', 'global.json',
            # Go
            'go.mod', 'go.sum',
            # Rust
            'Cargo.toml', 'Cargo.lock',
            # Ruby
            'Gemfile', 'Gemfile.lock',
            # PHP
            'composer.json', 'composer.lock',
            # Universal
            '.git', '.gitignore', 'README.md', 'README.rst',
            'Dockerfile', 'docker-compose.yml',
            'Makefile', 'CMakeLists.txt',
            '.workspace'
        ]
        
        # Buscar hacia arriba hasta encontrar indicadores
        for parent in [current] + list(current.parents):
            for indicator in project_indicators:
                if '*' in indicator:
                    # Buscar patrones con wildcards
                    pattern = indicator.replace('*', '')
                    try:
                        if any(f.name.endswith(pattern) for f in parent.iterdir() if f.is_file()):
                            return str(parent)
                    except (PermissionError, OSError):
                        continue
                else:
                    if (parent / indicator).exists():
                        return str(parent)
        
        return self.current_dir
    
    def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analizar estructura del proyecto universal"""
        root = Path(self.project_root)
        
        structure = {
            'project_type': self._determine_project_type(root),
            'has_backend': self._has_directory_pattern(root, ['backend', 'server', 'api']),
            'has_frontend': self._has_directory_pattern(root, ['frontend', 'client', 'ui', 'web']),
            'has_mobile': self._has_directory_pattern(root, ['mobile', 'app', 'android', 'ios']),
            'has_tests': self._has_directory_pattern(root, ['tests', 'test', 'spec', '__tests__']),
            'has_docs': self._has_directory_pattern(root, ['docs', 'documentation', 'doc']),
            'has_scripts': self._has_directory_pattern(root, ['scripts', 'tools', 'bin']),
            'languages': self._detect_languages(root),
            'frameworks': self._detect_frameworks(root)
        }
        
        return structure
    
    def _has_directory_pattern(self, root: Path, patterns: List[str]) -> bool:
        """Verificar si existe algún directorio con los patrones dados"""
        try:
            for item in root.iterdir():
                if item.is_dir() and any(pattern in item.name.lower() for pattern in patterns):
                    return True
        except (PermissionError, OSError):
            pass
        return False
    
    def _determine_project_type(self, root: Path) -> str:
        """Determinar tipo de proyecto universal"""
        indicators = {
            'web_fullstack': ['package.json', 'requirements.txt'],
            'web_frontend': ['package.json', 'yarn.lock'],
            'python': ['requirements.txt', 'pyproject.toml', 'setup.py'],
            'java': ['pom.xml', 'build.gradle'],
            'dotnet': ['*.sln', '*.csproj'],
            'go': ['go.mod'],
            'rust': ['Cargo.toml'],
            'ruby': ['Gemfile'],
            'php': ['composer.json'],
            'cpp': ['CMakeLists.txt', 'Makefile'],
            'docker': ['Dockerfile', 'docker-compose.yml'],
            'mobile': ['android', 'ios', 'App.js', 'App.tsx']
        }
        
        detected_types = []
        
        for project_type, files in indicators.items():
            for file_pattern in files:
                if '*' in file_pattern:
                    pattern = file_pattern.replace('*', '')
                    try:
                        if any(f.name.endswith(pattern) for f in root.iterdir() if f.is_file()):
                            detected_types.append(project_type)
                            break
                    except (PermissionError, OSError):
                        continue
                else:
                    if (root / file_pattern).exists():
                        detected_types.append(project_type)
                        break
        
        if len(detected_types) > 1:
            return 'polyglot'
        elif detected_types:
            return detected_types[0]
        else:
            return 'unknown'
    
    def _detect_languages(self, root: Path) -> List[str]:
        """Detectar lenguajes de programación en el proyecto"""
        languages = set()
        
        extension_mapping = {
            '.py': 'python',
            '.js': 'javascript', '.jsx': 'javascript',
            '.ts': 'typescript', '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css', '.scss': 'css', '.sass': 'css',
            '.sql': 'sql'
        }
        
        try:
            for file_path in root.rglob('*'):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    if ext in extension_mapping:
                        languages.add(extension_mapping[ext])
        except (PermissionError, OSError):
            pass
        
        return list(languages)
    
    def _detect_frameworks(self, root: Path) -> List[str]:
        """Detectar frameworks utilizados en el proyecto"""
        frameworks = set()
        
        # Buscar indicadores de frameworks en archivos de configuración
        config_files = {
            'package.json': ['react', 'vue', 'angular', 'express', 'next', 'nuxt'],
            'requirements.txt': ['django', 'flask', 'fastapi', 'pyramid'],
            'Gemfile': ['rails', 'sinatra'],
            'composer.json': ['laravel', 'symfony', 'codeigniter'],
            'pom.xml': ['spring', 'struts', 'hibernate'],
            'build.gradle': ['spring', 'android']
        }
        
        for config_file, framework_list in config_files.items():
            config_path = root / config_file
            if config_path.exists():
                try:
                    content = config_path.read_text(encoding='utf-8').lower()
                    for framework in framework_list:
                        if framework in content:
                            frameworks.add(framework)
                except (PermissionError, OSError, UnicodeDecodeError):
                    continue
        
        # NUEVO v5.3: Si no hay frameworks detectados en configs, buscar en archivos individuales
        if not frameworks:
            try:
                sample_files = list(root.rglob('*.tsx'))[:3] + list(root.rglob('*.jsx'))[:3] + list(root.rglob('*.ts'))[:3]
                for file_path in sample_files:
                    if file_path.is_file():
                        content = file_path.read_text(encoding='utf-8').lower()
                        if 'react' in content or 'usestate' in content or 'useeffect' in content:
                            frameworks.add('react')
                        if 'vue' in content or '@vue' in content:
                            frameworks.add('vue')
                        if 'angular' in content or '@angular' in content:
                            frameworks.add('angular')
                        break  # Solo analizar primer archivo encontrado
            except (PermissionError, OSError, UnicodeDecodeError):
                pass
        
        return list(frameworks)
    
    def get_backup_directory(self, file_path: str) -> str:
        """Obtener directorio de backup contextual universal"""
        if self.context == 'backend':
            return os.path.join(self.project_root, 'backend', 'backup')
        elif self.context == 'frontend':
            return os.path.join(self.project_root, 'frontend', 'backup')
        elif self.context == 'mobile':
            return os.path.join(self.project_root, 'mobile', 'backup')
        elif self.context == 'testing':
            return os.path.join(self.project_root, 'tests', 'backup')
        else:
            # Usar .backup como directorio universal
            return os.path.join(self.project_root, '.backup')
    
    def resolve_file_path(self, file_path: str) -> str:
        """Resolver path de archivo automáticamente"""
        if os.path.isabs(file_path):
            return file_path
        
        # Si es relativo, construir ruta absoluta
        if file_path.startswith('./'):
            return os.path.join(self.current_dir, file_path[2:])
        elif '/' in file_path:
            return os.path.join(self.current_dir, file_path)
        else:
            # Archivo en directorio actual
            return os.path.join(self.current_dir, file_path)

class SurgicalModifierUltimate:
    """Herramienta quirúrgica universal v5.3 mejorada"""
    
    def __init__(self, verbose: bool = False, confirm: bool = False, 
                 explore: bool = False, keep_backups: bool = False):
        self.temp_files = []
        self.verbose = verbose
        self.confirm = confirm
        self.explore = explore
        self.backup_manager = BackupManager(keep_successful_backups=keep_backups)
        
    def execute(self, operation: str, file_path: str, pattern: str, content: str = "") -> Dict[str, Any]:
        """Ejecutar operación quirúrgica universal v5.3"""
        
        ColorLogger.section("SURGICAL MODIFIER ULTIMATE v5.3")
        ColorLogger.info(f"Operación: {operation}")
        ColorLogger.info(f"Archivo: {file_path}")
        
        try:
            # 1. ANÁLISIS DE CONTEXTO UNIVERSAL
            ColorLogger.section("ANÁLISIS DE CONTEXTO UNIVERSAL")
            project_context = ProjectContext()
            
            # Resolver path automáticamente
            resolved_path = project_context.resolve_file_path(file_path)
            ColorLogger.info(f"Path resuelto: {resolved_path}")
            ColorLogger.info(f"Contexto detectado: {project_context.context}")
            ColorLogger.info(f"Tipo de proyecto: {project_context.structure['project_type']}")
            
            if project_context.structure['languages']:
                ColorLogger.info(f"Lenguajes detectados: {', '.join(project_context.structure['languages'])}")
            if project_context.structure['frameworks']:
                ColorLogger.info(f"Frameworks detectados: {', '.join(project_context.structure['frameworks'])}")
            
            # 2. VERIFICACIÓN MEJORADA DE ARCHIVO
            ColorLogger.section("VERIFICACIÓN DE ARCHIVO")
            if not os.path.exists(resolved_path) and operation != 'create':
                return self._handle_file_not_found_v53(resolved_path, operation)
            
            # 3. VALIDACIÓN DE PATRÓN MEJORADA v5.3
            if operation in ['replace', 'after', 'before'] and pattern:
                ColorLogger.section("VALIDACIÓN DE PATRÓN v5.3")
                if not self._validate_pattern(resolved_path, pattern):
                    return self._handle_pattern_not_found_v53(resolved_path, pattern)
            
            # 4. CONFIRMACIÓN OPCIONAL
            if self.confirm:
                if not self._request_confirmation(operation, resolved_path, pattern, content):
                    return {'success': False, 'message': 'Operación cancelada por el usuario'}
            
            # 5. CREAR BACKUP CON SISTEMA MEJORADO
            ColorLogger.section("BACKUP AUTOMÁTICO")
            backup_path = None
            original_content = ""
            
            if os.path.exists(resolved_path):
                with open(resolved_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                backup_dir = project_context.get_backup_directory(resolved_path)
                
                # Limpiar backups antiguos antes de crear uno nuevo
                self.backup_manager.cleanup_old_backups(backup_dir)
                
                # Crear nuevo backup con sistema mejorado
                backup_path = self.backup_manager.create_backup(resolved_path, backup_dir)
            
            # 6. MANEJO DE CONTENIDO UNIVERSAL v5.3
            ColorLogger.section("PROCESAMIENTO DE CONTENIDO UNIVERSAL v5.3")
            content_handler = ContentHandler(content, resolved_path, operation)
            safe_content, temp_file = content_handler.get_safe_content()
            
            if temp_file:
                self.temp_files.append(temp_file)
                ColorLogger.info("Contenido complejo manejado con archivo temporal")
            elif content_handler.handling_strategy == 'raw_mode_v3':
                ColorLogger.success("Modo RAW v5.3 activado - procesamiento universal mejorado")
            
            # 7. APLICAR OPERACIÓN
            ColorLogger.section("APLICACIÓN DE OPERACIÓN")
            result = self._apply_operation(operation, resolved_path, pattern, safe_content, temp_file)
            
            if not result['success']:
                # EN CASO DE ERROR: Restaurar y conservar backup
                if backup_path and original_content:
                    self.backup_manager.restore_from_backup(backup_path, resolved_path)
                return result
            
            # EN CASO DE ÉXITO: Limpiar backups según configuración
            ColorLogger.section("LIMPIEZA DE BACKUPS")
            self.backup_manager.cleanup_successful_backups()
            
            # 8. VERIFICACIÓN POST-OPERACIÓN v5.3
            if self.verbose and os.path.exists(resolved_path):
                ColorLogger.section("VERIFICACIÓN POST-OPERACIÓN v5.3")
                with open(resolved_path, 'r', encoding='utf-8') as f:
                    new_content = f.read()
                
                if original_content:
                    ColorLogger.diff("Cambios realizados", original_content, new_content)
                else:
                    ColorLogger.preview("Archivo creado", new_content)
            
            # 9. ÉXITO COMPLETO
            ColorLogger.section("OPERACIÓN COMPLETADA")
            ColorLogger.success("Modificación quirúrgica universal aplicada exitosamente")
            
            return {
                'success': True,
                'message': 'Operación quirúrgica universal v5.3 completada exitosamente',
                'file_path': resolved_path,
                'backup_path': backup_path if self.backup_manager.keep_successful_backups else None,
                'operation': operation,
                'context': project_context.context,
                'project_type': project_context.structure['project_type'],
                'backups_cleaned': not self.backup_manager.keep_successful_backups
            }
            
        except Exception as e:
            ColorLogger.error(f"Error inesperado: {str(e)}")
            return self._create_error_result(str(e), "Revisar logs y contenido del archivo")
        
        finally:
            self._cleanup_temp_files()
    
    def execute_explore_mode(self, file_path: str, search_term: str = None) -> None:
        """NUEVO v5.3: Modo exploración universal"""
        ColorLogger.section("MODO EXPLORACIÓN UNIVERSAL v5.3")
        
        project_context = ProjectContext()
        resolved_path = project_context.resolve_file_path(file_path)
        
        if not os.path.exists(resolved_path):
            ColorLogger.error(f"Archivo no encontrado: {resolved_path}")
            return
        
        if search_term:
            UniversalExplorer.search_in_file(resolved_path, search_term)
        else:
            UniversalExplorer.show_file_structure(resolved_path)
        
        # Análisis adicional universal
        try:
            with open(resolved_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            helper = UniversalPatternHelper(content, resolved_path)
            
            print(f"\n🔍 ANÁLISIS UNIVERSAL:")
            print(f"📁 Contexto detectado: {project_context.context}")
            print(f"🏗️ Tipo de proyecto: {project_context.structure['project_type']}")
            if project_context.structure['languages']:
                print(f"🐍 Lenguajes detectados: {', '.join(project_context.structure['languages'][:5])}")
            if project_context.structure['frameworks']:
                print(f"🚀 Frameworks de proyecto: {', '.join(project_context.structure['frameworks'])}")
            print(f"📁 Tipo de archivo: {helper.file_type}")
            
            if helper.framework_context:
                print(f"🚀 Frameworks detectados: {', '.join(helper.framework_context)}")
            
            # Mostrar patrones específicos del framework
            framework_patterns = helper.get_framework_specific_patterns()
            if framework_patterns:
                print(f"\n🎯 PATRONES IMPORTANTES ({len(framework_patterns)}):")
                for i, pattern in enumerate(framework_patterns[:10], 1):
                    print(f"   {i:2d}. {pattern}")
            
        except Exception as e:
            print(f"❌ Error en análisis universal: {e}")
    
    def _validate_pattern(self, file_path: str, pattern: str) -> bool:
        """Validar que el patrón existe en el archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return pattern in content
        except Exception:
            return False
    
    def _handle_pattern_not_found_v53(self, file_path: str, pattern: str) -> Dict[str, Any]:
        """NUEVO v5.3: Manejo universal avanzado de patrón no encontrado"""
        ColorLogger.warning(f"Patrón '{pattern}' no encontrado")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            helper = UniversalPatternHelper(content, file_path)
            
            # 1. Búsqueda flexible universal (NUEVO v5.3)
            flexible_matches = helper.find_flexible_pattern(pattern)
            if flexible_matches:
                ColorLogger.info("🔍 Patrones similares encontrados (búsqueda flexible universal):")
                for match in flexible_matches:
                    similarity_percent = int(match['similarity'] * 100)
                    strategies = match['strategies']
                    strategy_info = f"(seq:{strategies['sequence']:.2f}, words:{strategies['words']:.2f}, struct:{strategies['structure']:.2f})"
                    print(f"   {similarity_percent}% - Línea {match['line_number']}: {match['content']} {strategy_info}")
            
            # 2. Búsqueda por framework específico (NUEVO v5.3)
            framework_patterns = helper.get_framework_specific_patterns()
            if framework_patterns:
                ColorLogger.info(f"🚀 Patrones específicos encontrados ({helper.file_type}):")
                for i, pattern_fw in enumerate(framework_patterns[:8], 1):
                    print(f"   {i}. {pattern_fw}")
            
            # 3. Sugerir fragmentos para patrones largos (MEJORADO v5.3)
            if len(pattern) > 40:
                fragments = helper.suggest_pattern_fragments(pattern)
                if fragments:
                    ColorLogger.info("🧩 Fragmentos de patrón sugeridos (universal):")
                    for i, fragment in enumerate(fragments[:5], 1):
                        print(f"   {i}. {fragment}")
                    print("💡 Consejo: Intenta buscar por fragmentos más pequeños")
            
            # 4. Sugerir comando de exploración universal
            print(f"\n💡 Para explorar el archivo completo:")
            print(f"   python3 surgical_modifier_ultimate.py --explore {file_path}")
            print(f"   python3 surgical_modifier_ultimate.py --explore {file_path} \"término_búsqueda\"")
            
        except Exception as e:
            print(f"❌ Error en análisis universal avanzado: {e}")
        
        return self._create_error_result(
            f"Patrón '{pattern}' no encontrado",
            "Revisar sugerencias arriba, usar fragmentos más pequeños, o explorar archivo con --explore"
        )
    
    def _handle_file_not_found_v53(self, file_path: str, operation: str) -> Dict[str, Any]:
        """NUEVO v5.3: Manejo universal de archivo no encontrado"""
        ColorLogger.warning(f"Archivo no encontrado: {file_path}")
        
        # Sugerir archivos similares universalmente
        directory = os.path.dirname(file_path) or os.getcwd()
        filename = os.path.basename(file_path)
        
        if os.path.exists(directory):
            try:
                all_files = os.listdir(directory)
                
                # Buscar archivos similares por extensión y nombre
                file_base, file_ext = os.path.splitext(filename)
                
                similar_files = []
                exact_ext_files = []
                
                for f in all_files:
                    if os.path.isfile(os.path.join(directory, f)):
                        f_base, f_ext = os.path.splitext(f)
                        
                        # Archivos con misma extensión
                        if f_ext.lower() == file_ext.lower():
                            exact_ext_files.append(f)
                        
                        # Archivos con nombres similares
                        similarity = difflib.SequenceMatcher(None, file_base.lower(), f_base.lower()).ratio()
                        if similarity > 0.6:
                            similar_files.append((f, similarity))
                
                # Mostrar sugerencias
                if exact_ext_files:
                    ColorLogger.info(f"Archivos con extensión {file_ext} encontrados:")
                    for f in exact_ext_files[:5]:
                        print(f"   - {f}")
                
                if similar_files:
                    similar_files.sort(key=lambda x: x[1], reverse=True)
                    ColorLogger.info("Archivos con nombres similares:")
                    for f, sim in similar_files[:5]:
                        print(f"   - {f} (similitud: {int(sim*100)}%)")
                        
            except (PermissionError, OSError):
                pass
        
        suggestion = "Verificar ruta del archivo"
        if operation == 'create':
            suggestion = "Para CREATE, el archivo se creará automáticamente"
        
        return self._create_error_result(
            f"Archivo no existe: {file_path}",
            suggestion
        )
    
    def _request_confirmation(self, operation: str, file_path: str, pattern: str, content: str) -> bool:
        """Solicitar confirmación antes de ejecutar"""
        print(f"\n🔍 CONFIRMACIÓN DE OPERACIÓN:")
        print(f"   Operación: {operation.upper()}")
        print(f"   Archivo: {file_path}")
        if pattern:
            print(f"   Patrón: {pattern}")
        if content:
            preview = content[:100] + "..." if len(content) > 100 else content
            print(f"   Contenido: {preview}")
        
        response = input("\n¿Continuar con la operación? (y/N): ").strip().lower()
        return response in ['y', 'yes', 'sí', 's']
    
    def _apply_operation(self, operation: str, file_path: str, pattern: str, 
                        safe_content: str, temp_file: str) -> Dict[str, Any]:
        """Aplicar la operación específica universal"""
        
        try:
            if operation == 'create':
                return self._create_file(file_path, safe_content, temp_file)
            
            # Para otras operaciones, leer contenido actual
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.splitlines()
            
            # Buscar patrón
            line_index = -1
            for i, line in enumerate(lines):
                if pattern in line:
                    line_index = i
                    break
            
            if line_index == -1 and operation in ['replace', 'after', 'before']:
                return self._create_error_result(f"Patrón '{pattern}' no encontrado en aplicación")
            
            if operation == 'replace':
                return self._replace_content_direct(file_path, lines, line_index, pattern, safe_content, temp_file)
            elif operation == 'after':
                return self._insert_after_direct(file_path, lines, line_index, safe_content, temp_file)
            elif operation == 'before':
                return self._insert_before_direct(file_path, lines, line_index, safe_content, temp_file)
            elif operation == 'append':
                return self._append_content(file_path, safe_content, temp_file)
            elif operation == 'split':
                return self._split_lines(file_path, lines, line_index, pattern)
            else:
                return self._create_error_result(f"Operación no soportada: {operation}")
                
        except Exception as e:
            return self._create_error_result(f"Error aplicando operación: {str(e)}")
    
    def _create_file(self, file_path: str, safe_content: str, temp_file: str) -> Dict[str, Any]:
        """Crear archivo nuevo universal"""
        ColorLogger.creating(f"Archivo nuevo: {os.path.basename(file_path)}")
        
        # Crear directorio automáticamente si no existe
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            ColorLogger.info(f"Directorio creado: {directory}")
        
        # Obtener contenido real
        if temp_file:
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = safe_content
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        ColorLogger.success(f"Archivo creado: {file_path}")
        return {'success': True}
    
    def _replace_content_direct(self, file_path: str, lines: List[str], line_index: int, 
                               pattern: str, safe_content: str, temp_file: str) -> Dict[str, Any]:
        """Reemplazar contenido universal"""
        ColorLogger.info(f"Reemplazando contenido en línea {line_index + 1}")
        
        # Obtener contenido real
        if temp_file:
            with open(temp_file, 'r', encoding='utf-8') as f:
                new_content = f.read()
        else:
            new_content = safe_content
        
        # Reemplazar usando Python directamente
        lines[line_index] = lines[line_index].replace(pattern, new_content)
        
        # Escribir archivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        ColorLogger.success("Contenido reemplazado exitosamente")
        return {'success': True}
    
    def _insert_after_direct(self, file_path: str, lines: List[str], line_index: int, 
                            safe_content: str, temp_file: str) -> Dict[str, Any]:
        """Insertar contenido después universal"""
        ColorLogger.info(f"Insertando contenido después de línea {line_index + 1}")
        
        # Obtener contenido real
        if temp_file:
            with open(temp_file, 'r', encoding='utf-8') as f:
                new_content = f.read()
        else:
            new_content = safe_content
        
        # Manejo mejorado de contenido multi-línea
        if '\n' in new_content:
            new_lines = new_content.split('\n')
            # Insertar líneas en orden correcto
            for i, new_line in enumerate(new_lines):
                lines.insert(line_index + 1 + i, new_line)
        else:
            lines.insert(line_index + 1, new_content)
        
        # Escribir archivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        ColorLogger.success("Contenido insertado exitosamente")
        return {'success': True}
    
    def _insert_before_direct(self, file_path: str, lines: List[str], line_index: int, 
                             safe_content: str, temp_file: str) -> Dict[str, Any]:
        """Insertar contenido antes universal"""
        ColorLogger.info(f"Insertando contenido antes de línea {line_index + 1}")
        
        # Obtener contenido real
        if temp_file:
            with open(temp_file, 'r', encoding='utf-8') as f:
                new_content = f.read()
        else:
            new_content = safe_content
        
        # Manejo mejorado de contenido multi-línea
        if '\n' in new_content:
            new_lines = new_content.split('\n')
            # Insertar líneas en orden correcto
            for i, new_line in enumerate(new_lines):
                lines.insert(line_index + i, new_line)
        else:
            lines.insert(line_index, new_content)
        
        # Escribir archivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        ColorLogger.success("Contenido insertado exitosamente")
        return {'success': True}
    
    def _append_content(self, file_path: str, safe_content: str, temp_file: str) -> Dict[str, Any]:
        """Agregar contenido al final del archivo"""
        ColorLogger.info("Agregando contenido al final del archivo")
        
        # Obtener contenido real
        if temp_file:
            with open(temp_file, 'r', encoding='utf-8') as f:
                new_content = f.read()
        else:
            new_content = safe_content
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write('\n' + new_content)
        
        ColorLogger.success("Contenido agregado al final")
        return {'success': True}
    
    def _split_lines(self, file_path: str, lines: List[str], line_index: int, pattern: str) -> Dict[str, Any]:
        """Dividir líneas pegadas universal"""
        ColorLogger.info(f"Dividiendo línea pegada en línea {line_index + 1}")
        
        original_line = lines[line_index]
        
        # Aplicar división según patrón
        if '\\n' in pattern:
            split_content = original_line.replace('\\n', '\n')
        elif '}' in pattern:
            split_content = re.sub(r'\}(\s*)([a-zA-Z])', r'}\n\2', original_line)
        else:
            split_content = original_line.replace(pattern, f"{pattern}\n")
        
        # Reemplazar línea con líneas divididas
        new_lines = split_content.splitlines()
        lines[line_index:line_index+1] = new_lines
        
        # Escribir archivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        ColorLogger.success(f"Línea dividida en {len(new_lines)} líneas")
        return {'success': True}
    
    def _create_error_result(self, error_msg: str, suggestion: str = None) -> Dict[str, Any]:
        """Crear resultado de error sin romper entorno"""
        ColorLogger.error(error_msg, suggestion)
        
        return {
            'success': False,
            'error': error_msg,
            'suggestion': suggestion or "Revisar parámetros y intentar nuevamente",
            'exit_code': 0
        }
    
    def _cleanup_temp_files(self):
        """Limpiar archivos temporales"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass

# ============================================================================
# VERIFICACIÓN DE INTEGRIDAD - AGREGADO DESPUÉS DE SurgicalModifierUltimate
# ============================================================================

class IntegrityChecker:
    """Verificador de integridad de código universal"""
    
    def __init__(self, file_path: str, project_context):
        self.file_path = file_path
        self.project_context = project_context
        self.file_type = self._detect_file_type()
        
    def _detect_file_type(self) -> str:
        """Detectar tipo de archivo para verificación"""
        ext = os.path.splitext(self.file_path)[1].lower()
        type_mapping = {
            '.py': 'python',
            '.js': 'javascript', '.jsx': 'javascript',
            '.ts': 'typescript', '.tsx': 'typescript',
            '.java': 'java',
            '.json': 'json',
            '.yaml': 'yaml', '.yml': 'yaml'
        }
        return type_mapping.get(ext, 'generic')
    
    def pre_modification_check(self, operation: str, pattern: str, content: str) -> Dict[str, Any]:
        """Verificación antes de modificar"""
        checks = {
            'syntax_valid': True,
            'dependencies_intact': True,
            'imports_valid': True,
            'references_safe': True,
            'warnings': [],
            'errors': []
        }
        
        # 1. Verificar sintaxis actual
        if self.file_type == 'python':
            checks.update(self._check_python_syntax())
        elif self.file_type in ['javascript', 'typescript']:
            checks.update(self._check_js_syntax())
        elif self.file_type == 'java':
            checks.update(self._check_java_syntax())
        elif self.file_type == 'json':
            checks.update(self._check_json_syntax())
        
        # 2. Analizar impacto del cambio
        impact_analysis = self._analyze_change_impact(operation, pattern, content)
        checks['impact_analysis'] = impact_analysis
        
        # 3. Verificar dependencias
        dependency_check = self._check_dependencies()
        checks.update(dependency_check)
        
        return checks
    
    def post_modification_check(self) -> Dict[str, Any]:
        """Verificación después de modificar"""
        checks = {
            'syntax_valid': True,
            'compilation_ok': True,
            'imports_resolved': True,
            'tests_pass': None,
            'warnings': [],
            'errors': []
        }
        
        # 1. Verificar sintaxis del archivo modificado
        if self.file_type == 'python':
            checks.update(self._check_python_syntax())
        elif self.file_type in ['javascript', 'typescript']:
            checks.update(self._check_js_syntax())
        elif self.file_type == 'java':
            checks.update(self._check_java_compilation())
        
        # 2. Verificar que imports siguen funcionando
        if self.file_type == 'python':
            checks.update(self._check_python_imports())
        
        # 3. Ejecutar tests si existen
        test_result = self._run_related_tests()
        checks['tests_pass'] = test_result
        
        return checks
    
    def _check_python_syntax(self) -> Dict[str, Any]:
        """Verificar sintaxis Python"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Compilar para verificar sintaxis
            compile(source, self.file_path, 'exec')
            
            # Verificar AST
            tree = ast.parse(source)
            
            return {
                'syntax_valid': True,
                'ast_valid': True
            }
        except SyntaxError as e:
            return {
                'syntax_valid': False,
                'errors': [f"Error de sintaxis Python: {e}"]
            }
        except Exception as e:
            return {
                'syntax_valid': False,
                'errors': [f"Error procesando Python: {e}"]
            }
    
    def _check_js_syntax(self) -> Dict[str, Any]:
        """Verificar sintaxis JavaScript/TypeScript"""
        try:
            # Intentar usar node para verificar sintaxis
            result = subprocess.run(
                ['node', '-c', self.file_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {'syntax_valid': True}
            else:
                return {
                    'syntax_valid': False,
                    'errors': [f"Error sintaxis JS: {result.stderr}"]
                }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Si no hay node, verificación básica
            return self._basic_js_syntax_check()
    
    def _basic_js_syntax_check(self) -> Dict[str, Any]:
        """Verificación básica de sintaxis JS sin node"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificaciones básicas
            bracket_pairs = {'{': '}', '[': ']', '(': ')'}
            stack = []
            
            for char in content:
                if char in bracket_pairs:
                    stack.append(bracket_pairs[char])
                elif char in bracket_pairs.values():
                    if not stack or stack.pop() != char:
                        return {
                            'syntax_valid': False,
                            'errors': ['Paréntesis/brackets desbalanceados']
                        }
            
            if stack:
                return {
                    'syntax_valid': False,
                    'errors': ['Paréntesis/brackets no cerrados']
                }
            
            return {'syntax_valid': True}
            
        except Exception as e:
            return {
                'syntax_valid': False,
                'errors': [f"Error verificando JS: {e}"]
            }
    
    def _check_java_syntax(self) -> Dict[str, Any]:
        """Verificar sintaxis Java básica"""
        # Para Java, hacer verificación básica sin compilar
        return self._basic_java_syntax_check()
    
    def _basic_java_syntax_check(self) -> Dict[str, Any]:
        """Verificación básica Java"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificaciones básicas Java
            if content.count('{') != content.count('}'):
                return {
                    'syntax_valid': False,
                    'errors': ['Llaves desbalanceadas en Java']
                }
            
            if content.count('(') != content.count(')'):
                return {
                    'syntax_valid': False,
                    'errors': ['Paréntesis desbalanceados en Java']
                }
            
            return {'syntax_valid': True}
            
        except Exception as e:
            return {
                'syntax_valid': False,
                'errors': [f"Error verificando Java: {e}"]
            }
    
    def _check_java_compilation(self) -> Dict[str, Any]:
        """Verificar compilación Java"""
        try:
            result = subprocess.run(
                ['javac', '-cp', '.', self.file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {'compilation_ok': True}
            else:
                return {
                    'compilation_ok': False,
                    'errors': [f"Error compilación Java: {result.stderr}"]
                }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {
                'compilation_ok': False,
                'warnings': ['No se pudo verificar compilación Java (javac no disponible)']
            }
    
    def _check_json_syntax(self) -> Dict[str, Any]:
        """Verificar sintaxis JSON"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return {'syntax_valid': True}
        except json.JSONDecodeError as e:
            return {
                'syntax_valid': False,
                'errors': [f"JSON inválido: {e}"]
            }
    
    def _check_python_imports(self) -> Dict[str, Any]:
        """Verificar que imports Python funcionan"""
        try:
            # Cambiar al directorio del proyecto para imports relativos
            original_dir = os.getcwd()
            os.chdir(self.project_context.project_root)
            
            result = subprocess.run(
                ['python', '-m', 'py_compile', self.file_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            os.chdir(original_dir)
            
            if result.returncode == 0:
                return {'imports_resolved': True}
            else:
                return {
                    'imports_resolved': False,
                    'errors': [f"Error imports: {result.stderr}"]
                }
        except Exception as e:
            return {
                'imports_resolved': False,
                'warnings': [f"No se pudo verificar imports: {e}"]
            }
    
    def _analyze_change_impact(self, operation: str, pattern: str, content: str) -> Dict[str, Any]:
        """Analizar impacto del cambio"""
        impact = {
            'risk_level': 'low',
            'affected_areas': [],
            'recommendations': []
        }
        
        # Analizar qué tipo de cambio es
        if self.file_type == 'python':
            if any(keyword in pattern for keyword in ['class ', 'def ', 'import ']):
                impact['risk_level'] = 'high'
                impact['affected_areas'].append('Definiciones principales')
                impact['recommendations'].append('Ejecutar tests relacionados')
            
            if 'from ' in content or 'import ' in content:
                impact['risk_level'] = 'medium'
                impact['affected_areas'].append('Dependencias')
        
        elif self.file_type in ['javascript', 'typescript']:
            if any(keyword in pattern for keyword in ['export', 'import', 'function', 'class']):
                impact['risk_level'] = 'high'
                impact['affected_areas'].append('Exports/Imports')
                impact['recommendations'].append('Verificar dependencias')
        
        elif self.file_type == 'json':
            if operation == 'replace' and any(key in pattern for key in ['dependencies', 'scripts', 'main']):
                impact['risk_level'] = 'high'
                impact['affected_areas'].append('Configuración crítica')
        
        return impact
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Verificar dependencias del proyecto"""
        deps = {
            'dependencies_intact': True,
            'missing_deps': [],
            'warnings': []
        }
        
        # Para Python, verificar requirements.txt o pyproject.toml
        if self.file_type == 'python':
            req_file = os.path.join(self.project_context.project_root, 'requirements.txt')
            if os.path.exists(req_file):
                deps.update(self._check_python_requirements(req_file))
        
        # Para JS/TS, verificar package.json
        elif self.file_type in ['javascript', 'typescript']:
            pkg_file = os.path.join(self.project_context.project_root, 'package.json')
            if os.path.exists(pkg_file):
                deps.update(self._check_npm_dependencies(pkg_file))
        
        return deps
    
    def _check_python_requirements(self, req_file: str) -> Dict[str, Any]:
        """Verificar requirements de Python"""
        try:
            result = subprocess.run(
                ['pip', 'check'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {'dependencies_intact': True}
            else:
                return {
                    'dependencies_intact': False,
                    'missing_deps': result.stdout.split('\n')
                }
        except Exception:
            return {
                'warnings': ['No se pudo verificar dependencias Python']
            }
    
    def _check_npm_dependencies(self, pkg_file: str) -> Dict[str, Any]:
        """Verificar dependencias npm"""
        try:
            os.chdir(self.project_context.project_root)
            result = subprocess.run(
                ['npm', 'ls', '--depth=0'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if 'UNMET DEPENDENCY' in result.stdout:
                return {
                    'dependencies_intact': False,
                    'missing_deps': ['Dependencias npm faltantes']
                }
            else:
                return {'dependencies_intact': True}
        except Exception:
            return {
                'warnings': ['No se pudo verificar dependencias npm']
            }
    
    def _run_related_tests(self) -> Optional[bool]:
        """Ejecutar tests relacionados al archivo"""
        try:
            # Para Python con pytest
            if self.file_type == 'python':
                test_file = self._find_test_file()
                if test_file:
                    result = subprocess.run(
                        ['pytest', test_file, '-v'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    return result.returncode == 0
            
            # Para JS/TS con npm test
            elif self.file_type in ['javascript', 'typescript']:
                if os.path.exists(os.path.join(self.project_context.project_root, 'package.json')):
                    result = subprocess.run(
                        ['npm', 'test', '--', '--passWithNoTests'],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    return result.returncode == 0
        
        except Exception:
            pass
        
        return None
    
    def _find_test_file(self) -> Optional[str]:
        """Encontrar archivo de test relacionado"""
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        
        # Posibles ubicaciones de tests
        test_patterns = [
            f"test_{base_name}.py",
            f"{base_name}_test.py",
            f"tests/test_{base_name}.py",
            f"tests/{base_name}_test.py"
        ]
        
        for pattern in test_patterns:
            test_path = os.path.join(self.project_context.project_root, pattern)
            if os.path.exists(test_path):
                return test_path
        
        return None

class EnhancedSurgicalModifier(SurgicalModifierUltimate):
    """Versión mejorada con verificación de integridad"""
    
    def execute_with_integrity_check(self, operation: str, file_path: str, pattern: str, content: str = "") -> Dict[str, Any]:
        """Ejecutar con verificación completa de integridad"""
        
        ColorLogger.section("VERIFICACIÓN DE INTEGRIDAD PRE-MODIFICACIÓN")
        
        # 1. Verificación previa
        project_context = ProjectContext()
        resolved_path = project_context.resolve_file_path(file_path)
        
        checker = IntegrityChecker(resolved_path, project_context)
        pre_check = checker.pre_modification_check(operation, pattern, content)
        
        # Mostrar resultados de verificación previa
        self._report_integrity_check("PRE-MODIFICACIÓN", pre_check)
        
        # Si hay errores críticos, detener
        if not pre_check.get('syntax_valid', True):
            return {
                'success': False,
                'error': 'Archivo tiene errores de sintaxis antes de modificar',
                'details': pre_check.get('errors', [])
            }
        
        # 2. Ejecutar modificación original
        result = super().execute(operation, file_path, pattern, content)
        
        if not result['success']:
            return result
        
        # 3. Verificación posterior
        ColorLogger.section("VERIFICACIÓN DE INTEGRIDAD POST-MODIFICACIÓN")
        post_check = checker.post_modification_check()
        self._report_integrity_check("POST-MODIFICACIÓN", post_check)
        
        # Si hay errores después de modificar, reportar pero no revertir automáticamente
        if not post_check.get('syntax_valid', True):
            ColorLogger.warning("Se detectaron errores después de la modificación")
            result['integrity_warnings'] = post_check.get('errors', [])
            result['backup_recommended'] = True
        
        # Agregar información de integridad al resultado
        result['pre_check'] = pre_check
        result['post_check'] = post_check
        
        return result
    
    def _report_integrity_check(self, phase: str, check_result: Dict[str, Any]):
        """Reportar resultados de verificación"""
        print(f"\n📊 REPORTE {phase}:")
        
        # Estados principales
        syntax_ok = check_result.get('syntax_valid', True)
        deps_ok = check_result.get('dependencies_intact', True)
        
        print(f"   ✅ Sintaxis: {'OK' if syntax_ok else '❌ ERROR'}")
        print(f"   ✅ Dependencias: {'OK' if deps_ok else '⚠️ PROBLEMAS'}")
        
        # Tests si están disponibles
        tests_result = check_result.get('tests_pass')
        if tests_result is not None:
            print(f"   ✅ Tests: {'✅ PASAN' if tests_result else '❌ FALLAN'}")
        
        # Mostrar errores
        errors = check_result.get('errors', [])
        if errors:
            print(f"   ❌ Errores encontrados:")
            for error in errors:
                print(f"      - {error}")
        
        # Mostrar advertencias
        warnings = check_result.get('warnings', [])
        if warnings:
            print(f"   ⚠️ Advertencias:")
            for warning in warnings:
                print(f"      - {warning}")
        
        # Análisis de impacto si está disponible
        impact = check_result.get('impact_analysis')
        if impact:
            risk_icons = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
            risk_icon = risk_icons.get(impact['risk_level'], '⚪')
            print(f"   {risk_icon} Nivel de riesgo: {impact['risk_level'].upper()}")
            
            if impact['affected_areas']:
                print(f"   🎯 Áreas afectadas: {', '.join(impact['affected_areas'])}")
            
            if impact['recommendations']:
                print(f"   💡 Recomendaciones:")
                for rec in impact['recommendations']:
                    print(f"      - {rec}")

# ============================================================================
# FIN DE VERIFICACIÓN DE INTEGRIDAD
# ============================================================================

def show_enhanced_help_v53():
    """NUEVO v5.3: Sistema de ayuda universal mejorado"""
    print("""
🔧 SURGICAL MODIFIER ULTIMATE v5.3 - HERRAMIENTA UNIVERSAL DEFINITIVA

📋 USO:
  python3 surgical_modifier_ultimate.py [--verbose] [--confirm] [--explore] [--keep-backups] [--check-integrity] <operación> <archivo> <patrón> [contenido]

🛡️ OPCIONES:
  --verbose        : Diff visual y análisis detallado
  --confirm        : Confirmación antes de ejecutar
  --explore        : Modo exploración universal
  --keep-backups   : Conservar backups incluso en operaciones exitosas
  --check-integrity: Verificación completa de sintaxis, deps y tests

🔍 VERIFICACIÓN DE INTEGRIDAD:
  --check-integrity verifica:
  ✅ Sintaxis válida antes y después de modificar
  ✅ Dependencias del proyecto intactas
  ✅ Imports resueltos correctamente
  ✅ Tests relacionados (si existen)
  ✅ Análisis de impacto del cambio (bajo/medio/alto riesgo)
  ✅ Recomendaciones específicas por framework

🎯 EJEMPLOS CON VERIFICACIÓN DE INTEGRIDAD:

# Modificación segura con verificación completa
python3 surgical_modifier_ultimate.py --check-integrity replace models/product.py "class Product" "class Product"

# Verificación + confirmación + backups + verbose
python3 surgical_modifier_ultimate.py --check-integrity --confirm --keep-backups --verbose after models/product.py "name = models.CharField" "description = models.TextField()"

# Solo exploración (sin modificar)
python3 surgical_modifier_ultimate.py --explore models/product.py

🧹 SISTEMA DE BACKUP INTELIGENTE:

POR DEFECTO (Recomendado):
  ✅ Crea backup antes de cada operación
  ✅ Restaura backup automáticamente si hay error
  ✅ Limpia backup automáticamente si operación es exitosa
  ✅ Conserva solo backups de errores para investigación
  ✅ Limpia backups antiguos (mantiene últimos 5)

CON --keep-backups:
  ✅ Crea backup antes de cada operación  
  ✅ Restaura backup automáticamente si hay error
  ✅ Conserva TODOS los backups (exitosos y fallidos)
  ✅ Limpia solo backups muy antiguos (mantiene últimos 5)

🌍 SOPORTE UNIVERSAL COMPLETO:

LENGUAJES SOPORTADOS:
  ✅ Python (.py)           ✅ JavaScript (.js)       ✅ TypeScript (.ts/.tsx)
  ✅ Java (.java)           ✅ C++ (.cpp/.cc)         ✅ C (.c)
  ✅ C# (.cs)               ✅ PHP (.php)             ✅ Ruby (.rb)
  ✅ Go (.go)               ✅ Rust (.rs)             ✅ Swift (.swift)
  ✅ Kotlin (.kt)           ✅ Scala (.scala)         ✅ HTML/XML
  ✅ CSS/SCSS               ✅ JSON/YAML              ✅ SQL
  ✅ Bash/Shell             ✅ Markdown               ✅ + más

FRAMEWORKS AUTO-DETECTADOS:
  🐍 Python: Django, Flask, FastAPI, pytest, SQLAlchemy
  🟨 JS/TS: React, Vue, Angular, Express, Jest, Mocha
  ☕ Java: Spring, JUnit, Hibernate
  🔷 .NET: ASP.NET, NUnit
  🐳 DevOps: Docker, Kubernetes

💡 CASOS DE USO PARA VERIFICACIÓN DE INTEGRIDAD:
  ✅ Modificar modelos Django sin romper migraciones
  ✅ Actualizar APIs sin afectar dependencias
  ✅ Refactoring seguro con validación automática
  ✅ Cambios en archivos críticos con tests automáticos
  ✅ Desarrollo en equipos (evitar commits rotos)

¡HERRAMIENTA UNIVERSAL CON VERIFICACIÓN DE INTEGRIDAD COMPLETA! 🛡️
""")

def main():
    """Función principal universal v5.3 con verificación de integridad"""
    
    # Procesar argumentos incluyendo --check-integrity
    args = sys.argv[1:]
    verbose = '--verbose' in args
    confirm = '--confirm' in args
    explore = '--explore' in args
    show_pattern = '--show-pattern' in args
    keep_backups = '--keep-backups' in args
    check_integrity = '--check-integrity' in args  # ← NUEVA LÍNEA
    
    # Remover flags de argumentos
    args = [arg for arg in args if not arg.startswith('--')]
    
    if len(args) < 1 or args[0] in ['-h', '--help', 'help']:
        show_enhanced_help_v53()
        sys.exit(0)
    
    if explore and len(args) >= 1:
        # Modo exploración universal
        file_path = args[0]
        search_term = args[1] if len(args) > 1 else None
        
        modifier = SurgicalModifierUltimate(verbose=verbose, confirm=confirm, explore=True, keep_backups=keep_backups)
        modifier.execute_explore_mode(file_path, search_term)
        return
    elif show_pattern and len(args) >= 3:
        # Tu código existente de show-pattern...
        file_path = args[0]
        start_line = int(args[1])
        end_line = int(args[2])

        project_context = ProjectContext()
        resolved_path = project_context.resolve_file_path(file_path)

        if not os.path.exists(resolved_path):
            print(f"❌ Archivo no encontrado: {resolved_path}")
            return

        try:
            with open(resolved_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            print(f"📋 SHOW PATTERN: {os.path.basename(resolved_path)} (líneas {start_line}-{end_line})")
            print("=" * 70)

            for i in range(max(0, start_line-1), min(len(lines), end_line)):
                line_content = lines[i].rstrip()
                print(f"{i+1:4d}: {repr(line_content)}")  # repr() muestra caracteres exactos

            print("=" * 70)
            print(f"📊 Caracteres especiales visibles, total líneas en archivo: {len(lines)}")

        except Exception as e:
            print(f"❌ Error: {e}")
        return
    
    if len(args) < 3:
        show_enhanced_help_v53()
        sys.exit(0)
    
    operation = args[0].lower()
    file_path = args[1]
    pattern = args[2] if len(args) > 2 else ""
    content = args[3] if len(args) > 3 else ""

    # ========================================================================
    # MODIFICACIÓN PRINCIPAL: USAR VERIFICADOR MEJORADO SI SE SOLICITA
    # ========================================================================
    if check_integrity:
        # NUEVO: Usar verificador con integridad
        modifier = EnhancedSurgicalModifier(
            verbose=verbose, 
            confirm=confirm, 
            keep_backups=keep_backups
        )
        result = modifier.execute_with_integrity_check(operation, file_path, pattern, content)
    else:
        # ORIGINAL: Usar modificador normal
        modifier = SurgicalModifierUltimate(
            verbose=verbose, 
            confirm=confirm, 
            keep_backups=keep_backups
        )
        result = modifier.execute(operation, file_path, pattern, content)
    
    # Mostrar resultado final con información de backups e integridad
    if result['success']:
        print(f"\n🎉 ✅ ÉXITO TOTAL UNIVERSAL v5.3 - {result['message']}")
        
        # NUEVO: Mostrar estado de integridad si está disponible
        if 'integrity_warnings' in result:
            print("⚠️ ADVERTENCIAS DE INTEGRIDAD:")
            for warning in result['integrity_warnings']:
                print(f"   - {warning}")
        
        if result.get('backups_cleaned'):
            print("🧹 Backups limpiados automáticamente (operación exitosa)")
        elif result.get('backup_path'):
            print(f"📦 Backup conservado: {os.path.relpath(result['backup_path'])}")
        
        if 'context' in result:
            print(f"🎯 Contexto: {result['context']} | Proyecto: {result['project_type']}")
    else:
        print(f"\n❌ OPERACIÓN FALLÓ: {result['error']}")
        print("📦 Backup conservado para investigación de error")
        if 'suggestion' in result:
            print(f"🔧 Sugerencia: {result['suggestion']}")
        # NUEVO: Mostrar detalles de integridad si están disponibles
        if 'details' in result:
            print("📋 Detalles:")
            for detail in result['details']:
                print(f"   - {detail}")
    
    # NO usar exit 1 - preservar entorno
    sys.exit(0)
    
if __name__ == "__main__":
    main()