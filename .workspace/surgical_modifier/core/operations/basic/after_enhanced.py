"""
Surgical Modifier v6.0 - AFTER Operation (Enhanced with Industrial Features)
Insert content after a specific line/pattern with enhanced indentation preservation
"""

import os
import re
import shutil
import time
from pathlib import Path
from typing import List, Optional

from utils.escape_processor import process_content_escapes

from ..base_operation import (
    ArgumentSpec,
    BaseOperation,
    ContentError,
    FileSystemError,
    OperationContext,
    OperationResult,
    OperationType,
    ValidationError,
)

try:
    from utils.logger import logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    logger = None


# ========== FUNCIONES DE PRESERVACIÓN INTELIGENTE DE INDENTACIÓN ==========

def detect_pattern_indentation(content: str, pattern: str, occurrence_index: int = 0) -> int:
    """Detectar indentación exacta del patrón en su contexto"""
    lines = content.split(chr(10))
    occurrence_count = 0
    for line in lines:
        if pattern in line:
            if occurrence_count == occurrence_index:
                return len(line) - len(line.lstrip())
            occurrence_count += 1
    return 0


def apply_context_indentation(new_content: str, base_indentation: int) -> str:
    """Aplicar indentación del contexto al contenido nuevo"""
    if chr(10) not in new_content:
        return chr(32) * base_indentation + new_content
    
    lines = new_content.split(chr(10))
    indented_lines = []
    for i, line in enumerate(lines):
        if line.strip():  # Solo indentar líneas no vacías
            indented_lines.append(chr(32) * base_indentation + line.lstrip())
        else:
            indented_lines.append(chr(34) + chr(34))
    return chr(10).join(indented_lines)


# ========== FUNCIONES DE BACKUP AUTOMÁTICO ==========

def create_automatic_backup(file_path: str) -> str:
    """Crear backup automático con timestamp único"""
    timestamp = int(time.time())
    backup_dir = Path(file_path).parent / '.backups'
    backup_dir.mkdir(exist_ok=True)
    
    filename = Path(file_path).name
    backup_path = backup_dir / f'{filename}.backup.{timestamp}'
    
    shutil.copy2(file_path, backup_path)
    return str(backup_path)


def cleanup_old_backups(file_path: str, keep_last: int = 5):
    """Limpiar backups antiguos, mantener solo los últimos N"""
    backup_dir = Path(file_path).parent / '.backups'
    if not backup_dir.exists():
        return
    
    filename = Path(file_path).name
    backup_files = list(backup_dir.glob(f'{filename}.backup.*'))
    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    for old_backup in backup_files[keep_last:]:
        old_backup.unlink()


# ========== FUNCIONES DE VALIDACIÓN SINTÁCTICA ==========

def validate_python_syntax(content: str) -> bool:
    """Validar sintaxis Python"""
    try:
        compile(content, chr(60) + chr(115) + chr(116) + chr(114) + chr(105) + chr(110) + chr(103) + chr(62), chr(101) + chr(120) + chr(101) + chr(99))
        return True
    except SyntaxError as e:
        raise ContentError(f"Invalid Python syntax after insertion: {e}")


def validate_javascript_syntax(content: str) -> bool:
    """Validación básica JavaScript"""
    stack = []
    pairs = {chr(40): chr(41), chr(91): chr(93), chr(123): chr(125)}
    for char in content:
        if char in pairs:
            stack.append(pairs[char])
        elif char in pairs.values():
            if not stack or stack.pop() != char:
                raise ContentError(chr(85) + chr(110) + chr(98) + chr(97) + chr(108) + chr(97) + chr(110) + chr(99) + chr(101) + chr(100) + chr(32) + chr(98) + chr(114) + chr(97) + chr(99) + chr(107) + chr(101) + chr(116) + chr(115))
    return True


# ========== OPERACIONES BEFORE MEJORADAS CON FUNCIONALIDAD INDUSTRIAL ==========

def enhanced_after_operation(file_path: str, pattern: str, content: str, preserve_indentation: bool = True):
    """AFTER mejorada con preservación de indentación"""
    try:
        # Leer contenido original
        with open(file_path, chr(114), encoding=chr(117) + chr(116) + chr(102) + chr(45) + chr(56)) as f:
            original_content = f.read()
        
        lines = original_content.split(chr(10))
        
        # Buscar patrón y detectar indentación
        for i, line in enumerate(lines):
            if pattern in line:
                if preserve_indentation:
                    # Detectar indentación del contexto
                    base_indent = detect_pattern_indentation(original_content, pattern)
                    # Aplicar indentación al nuevo contenido
                    formatted_content = apply_context_indentation(content, base_indent)
                else:
                    formatted_content = content
                
                # Insertar DESPUÉS de la línea encontrada
                if chr(10) in formatted_content:
                    new_lines = formatted_content.split(chr(10))
                    for j, new_line in enumerate(new_lines):
                        lines.insert(i + 1 + j, new_line)
                else:
                    lines.insert(i + 1, formatted_content)
                break
        
        # Escribir archivo modificado
        with open(file_path, chr(119), encoding=chr(117) + chr(116) + chr(102) + chr(45) + chr(56)) as f:
            f.write(chr(10).join(lines))
        
        return {
            chr(115) + chr(117) + chr(99) + chr(99) + chr(101) + chr(115) + chr(115): True,
            chr(109) + chr(101) + chr(115) + chr(115) + chr(97) + chr(103) + chr(101): f"Content inserted after pattern in {file_path}",
            chr(102) + chr(105) + chr(108) + chr(101) + chr(95) + chr(112) + chr(97) + chr(116) + chr(104): file_path,
            chr(105) + chr(110) + chr(100) + chr(101) + chr(110) + chr(116) + chr(97) + chr(116) + chr(105) + chr(111) + chr(110) + chr(95) + chr(112) + chr(114) + chr(101) + chr(115) + chr(101) + chr(114) + chr(118) + chr(101) + chr(100): preserve_indentation
        }
        
    except Exception as e:
        return {
            chr(115) + chr(117) + chr(99) + chr(99) + chr(101) + chr(115) + chr(115): False,
            chr(101) + chr(114) + chr(114) + chr(111) + chr(114): str(e),
            chr(102) + chr(105) + chr(108) + chr(101) + chr(95) + chr(112) + chr(97) + chr(116) + chr(104): file_path
        }


def enhanced_after_operation_with_backup(file_path: str, pattern: str, content: str, auto_backup: bool = True):
    """AFTER con backup automático integrado"""
    backup_path = None
    
    try:
        # 1. Crear backup automático
        if auto_backup:
            backup_path = create_automatic_backup(file_path)
        
        # 2. Ejecutar inserción mejorada
        result = enhanced_after_operation(file_path, pattern, content)
        
        if result.get('success'):
            # 3. Limpiar backups antiguos
            if auto_backup:
                cleanup_old_backups(file_path)
            
            # 4. Añadir info de backup al resultado
            result['backup_created'] = backup_path
            result['auto_backup'] = auto_backup
        
        return result
        
    except Exception as e:
        # 5. Rollback automático si algo falló
        if backup_path and Path(backup_path).exists():
            import shutil
            shutil.copy2(backup_path, file_path)
            return {
                'success': False,
                'error': str(e),
                'rollback_applied': True,
                'backup_restored_from': backup_path
            }
        raise e


def enhanced_after_operation_with_validation(file_path: str, pattern: str, content: str, validate: bool = True):
    """AFTER con validación sintáctica"""
    backup_path = None
    
    try:
        # 1. Backup automático
        backup_path = create_automatic_backup(file_path)
        
        # 2. Ejecutar inserción con backup
        result = enhanced_after_operation_with_backup(file_path, pattern, content, auto_backup=False)
        
        if not result.get('success'):
            return result
        
        # 3. Validación sintáctica
        if validate:
            with open(file_path, 'r', encoding='utf-8') as f:
                new_content = f.read()
            
            if file_path.endswith('.py'):
                validate_python_syntax(new_content)
            elif file_path.endswith(('.js', '.ts')):
                validate_javascript_syntax(new_content)
        
        # 4. Éxito - limpiar backup
        cleanup_old_backups(file_path)
        
        result['validated'] = validate
        result['backup_created'] = backup_path
        
        return result
        
    except Exception as e:
        # 5. Rollback automático por error de validación
        if backup_path and Path(backup_path).exists():
            import shutil
            shutil.copy2(backup_path, file_path)
        
        return {
            'success': False,
            'error': str(e),
            'rollback_applied': True,
            'validation_failed': True
        }
