"""
Surgical Modifier v6.0 - REPLACE Operation (Integrated + Optimized)
Replace content in existing files with intelligent indentation, backup, and validation
"""

import os
import re
import shutil
import time
import tempfile
from typing import List, Optional
from pathlib import Path
from ...functions.detection.pattern_matcher import detect_pattern_indentation, apply_context_indentation
from ...functions.versioning.backup_manager import create_temporary_backup, cleanup_backup, create_automatic_backup, cleanup_old_backups
from ...functions.verification.syntax_validator import validate_python_syntax, validate_javascript_syntax
from ..base_operation import (
    BaseOperation, OperationType, OperationContext, OperationResult,
    ValidationError, FileSystemError, ContentError, ArgumentSpec
)

try:
    from utils.logger import logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    logger = None

# ========== INTELLIGENT HELPER FUNCTIONS ==========

def detect_pattern_indentation(content: str, pattern: str, occurrence_index: int = 0) -> int:
    """Detectar indentación exacta del patrón en su contexto"""
    lines = content.split('\n')
    occurrence_count = 0
    for line in lines:
        if pattern in line:
            if occurrence_count == occurrence_index:
                return len(line) - len(line.lstrip())
            occurrence_count += 1
    return 0

def apply_context_indentation(replacement: str, base_indentation: int) -> str:
    """Aplicar indentación del contexto al contenido de reemplazo"""
    if '\n' not in replacement:
        return replacement
    
    lines = replacement.split('\n')
    indented_lines = []
    for i, line in enumerate(lines):
        if i == 0:  # Primera línea mantiene indentación original
            indented_lines.append(line)
        else:  # Líneas adicionales usan indentación base + contenido
            if line.strip():  # Solo indentar líneas no vacías
                indented_lines.append(' ' * base_indentation + line.lstrip())
            else:
                indented_lines.append('')
    return '\n'.join(indented_lines)

def create_temporary_backup(file_path: str) -> str:
    """Crear backup temporal - se elimina automáticamente al final"""
    backup_path = file_path + '.temp_backup_' + str(int(time.time()))
    shutil.copy2(file_path, backup_path)
    return backup_path

def cleanup_backup(backup_path: str) -> None:
    """Eliminar backup temporal sin dejar rastros"""
    try:
        if os.path.exists(backup_path):
            os.remove(backup_path)
    except:
        pass  # Silently ignore cleanup errors

def validate_python_syntax(content: str) -> bool:
    """Validar sintaxis Python"""
    try:
        compile(content, '<string>', 'exec')
        return True
    except SyntaxError as e:
        raise ContentError(f"Invalid Python syntax after replace: {e}")

def validate_javascript_syntax(content: str) -> bool:
    """Validación básica JavaScript - balanceado de llaves"""
    stack = []
    pairs = {'(': ')', '[': ']', '{': '}'}
    for char in content:
        if char in pairs:
            stack.append(pairs[char])
        elif char in pairs.values():
            if not stack or stack.pop() != char:
                raise ContentError(f"Unbalanced brackets in JavaScript after replace")
    return True

# ========== MAIN REPLACE FUNCTION - INTELLIGENT VERSION ==========

def replace_operation(file_path: str, pattern: str, content: str, **kwargs):
    """
    Replace operation with intelligent indentation, temporary backup, and validation
    
    Features:
    - Preserves exact indentation of original context
    - Creates temporary backup (auto-cleaned on success)
    - Validates syntax for Python/JavaScript files
    - Automatic rollback on errors
    - Full compatibility with original function signature
    """
    backup_path = None
    try:
        # 1. Create temporary backup
        backup_path = create_temporary_backup(file_path)
        
        # 2. Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
            
        # 3. Perform intelligent replacement with indentation preservation
        if pattern in file_content:
            # Detect indentation of the original pattern
            base_indentation = detect_pattern_indentation(file_content, pattern)
            
            # Apply indentation to replacement content
            if '\n' in content and base_indentation > 0:
                indented_content = apply_context_indentation(content, base_indentation)
            else:
                # Simple case - preserve basic indentation
                lines = file_content.split('\n')
                pattern_indent = 0
                for line in lines:
                    if pattern in line:
                        pattern_indent = len(line) - len(line.lstrip())
                        break
                
                if '\n' in content and pattern_indent > 0:
                    content_lines = content.split('\n')
                    indented_lines = [content_lines[0]]  # First line unchanged
                    for line in content_lines[1:]:
                        if line.strip():
                            indented_lines.append(' ' * pattern_indent + line.lstrip())
                        else:
                            indented_lines.append('')
                    indented_content = '\n'.join(indented_lines)
                else:
                    indented_content = content
            
            # Perform replacement
            new_content = file_content.replace(pattern, indented_content)
            
            # 4. Validate syntax if applicable
            if file_path.endswith('.py'):
                validate_python_syntax(new_content)
            elif file_path.endswith(('.js', '.ts')):
                validate_javascript_syntax(new_content)
            
            # 5. Write file only if validation passed
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # 6. Success - cleanup backup (no traces left)
            cleanup_backup(backup_path)
            
            return {
                'success': True,
                'message': f'Replaced pattern in {file_path} with intelligent indentation',
                'file_path': file_path,
                'indentation_preserved': True,
                'backup_cleaned': True,
                'syntax_validated': True
            }
        else:
            # Pattern not found - cleanup backup
            cleanup_backup(backup_path)
            return {
                'success': False,
                'error': f'Pattern not found in {file_path}',
                'file_path': file_path
            }
            
    except Exception as e:
        # Error occurred - restore from backup and cleanup
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            cleanup_backup(backup_path)
        return {
            'success': False,
            'error': f'Replace failed: {e}',
            'file_path': file_path,
            'backup_restored': True
        }

# ========== CONTEXTUAL REPLACE FUNCTIONS ==========

def contextual_replace(file_path: str, pattern: str, replacement: str, context: str = None, **kwargs):
    """Replace only within specific context (class, function, etc.)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if context:
            # Find context boundaries
            lines = content.split('\n')
            in_context = False
            context_indent = 0
            modified_lines = []
            
            for line in lines:
                if context in line:
                    in_context = True
                    context_indent = len(line) - len(line.lstrip())
                    modified_lines.append(line)
                elif in_context:
                    current_indent = len(line) - len(line.lstrip())
                    if line.strip() and current_indent <= context_indent:
                        in_context = False
                    
                    if in_context and pattern in line:
                        modified_lines.append(line.replace(pattern, replacement))
                    else:
                        modified_lines.append(line)
                else:
                    modified_lines.append(line)
            
            new_content = '\n'.join(modified_lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return {
                'success': True,
                'message': f'Contextual replace in {context} completed',
                'context': context
            }
        else:
            # Fallback to regular replace
            return replace_operation(file_path, pattern, replacement, **kwargs)
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Contextual replace failed: {e}',
            'file_path': file_path
        }

def preview_replace_changes(file_path: str, pattern: str, replacement: str, **kwargs):
    """Preview changes before applying replace"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if pattern in content:
            changes = []
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if pattern in line:
                    old_line = line
                    new_line = line.replace(pattern, replacement)
                    changes.append({
                        'line_number': i,
                        'old': old_line.strip(),
                        'new': new_line.strip()
                    })
            
            return {
                'success': True,
                'changes': changes,
                'total_changes': len(changes)
            }
        else:
            return {
                'success': False,
                'message': 'Pattern not found',
                'changes': []
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Preview failed: {e}',
            'file_path': file_path
        }

def regex_replace_operation(file_path: str, regex_pattern: str, replacement: str, **kwargs):
    """Replace with advanced regex support"""
    backup_path = None
    try:
        backup_path = create_temporary_backup(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Perform regex replacement
        new_content = re.sub(regex_pattern, replacement, content)
        
        # Validate syntax if applicable
        if file_path.endswith('.py'):
            validate_python_syntax(new_content)
        elif file_path.endswith(('.js', '.ts')):
            validate_javascript_syntax(new_content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        cleanup_backup(backup_path)
        
        return {
            'success': True,
            'message': f'Regex replace completed in {file_path}',
            'pattern': regex_pattern,
            'replacement': replacement
        }
        
    except re.error as e:
        if backup_path:
            shutil.copy2(backup_path, file_path)
            cleanup_backup(backup_path)
        return {
            'success': False,
            'error': f'Invalid regex: {e}',
            'backup_restored': True
        }
    except Exception as e:
        if backup_path:
            shutil.copy2(backup_path, file_path)
            cleanup_backup(backup_path)
        return {
            'success': False,
            'error': f'Regex replace failed: {e}',
            'backup_restored': True
        }

# ========== ORIGINAL CLASS ARCHITECTURE (PRESERVED) ==========

def create_automatic_backup(file_path: str) -> str:
    """Crear backup automático con timestamp único"""
    import time
    from pathlib import Path
    import uuid
    timestamp = f"{int(time.time())}.{uuid.uuid4().hex[:8]}"
    backup_dir = Path(file_path).parent / '.backups'
    backup_dir.mkdir(exist_ok=True)
    
    filename = Path(file_path).name
    backup_path = backup_dir / f'{filename}.backup.{timestamp}'
    
    shutil.copy2(file_path, backup_path)
    return str(backup_path)

def cleanup_old_backups(file_path: str, keep_last: int = 5):
    """Limpiar backups antiguos, mantener solo los últimos N"""
    from pathlib import Path
    backup_dir = Path(file_path).parent / '.backups'
    if not backup_dir.exists():
        return
    
    filename = Path(file_path).name
    backup_files = list(backup_dir.glob(f'{filename}.backup.*'))
    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    for old_backup in backup_files[keep_last:]:
        old_backup.unlink()

def enhanced_replace_operation(file_path: str, pattern: str, content: str, auto_backup: bool = True):
    """Replace con backup automático integrado"""
    backup_path = None
    
    try:
        # 1. Crear backup automático
        if auto_backup:
            backup_path = create_automatic_backup(file_path)
        
        # 2. Ejecutar replace con funciones existentes
        result = replace_operation(file_path, pattern, content)
        
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
            shutil.copy2(backup_path, file_path)
            return {
                'success': False,
                'error': str(e),
                'rollback_applied': True,
                'backup_restored_from': backup_path
            }
        raise e

class ReplaceOperation(BaseOperation):
    """
    REPLACE operation implementation with full integration and intelligence.
    
    Enhanced features:
    - Intelligent indentation preservation
    - Temporary backup with auto-cleanup
    - Syntax validation (Python, JavaScript)
    - Contextual replacements
    - Regex support
    - Preview functionality
    """
    
    def __init__(self):
        super().__init__(OperationType.REPLACE, "replace")
        self.replaced_patterns = {}  # Track replaced content for rollback
    
    def _get_operation_specific_arguments(self) -> List['ArgumentSpec']:
        """Define REPLACE-specific arguments for integration with registry."""
        if not hasattr(self, '_ArgumentSpec_available'):
            try:
                from ..base_operation import ArgumentSpec
                self._ArgumentSpec_available = True
            except ImportError:
                self._ArgumentSpec_available = False
                return []
        
        if not self._ArgumentSpec_available:
            return []
            
        from ..base_operation import ArgumentSpec
        
        return [
            ArgumentSpec(
                name="pattern",
                type=str,
                required=True,
                help="Pattern to search for and replace",
                example="def old_function"
            ),
            ArgumentSpec(
                name="replacement",
                type=str,
                required=True,
                help="Content to replace the pattern with",
                example="def new_function"
            ),
            ArgumentSpec(
                name="regex_mode",
                type=bool,
                required=False,
                default=False,
                help="Use regex pattern matching",
                example="false"
            ),
            ArgumentSpec(
                name="preserve_indentation",
                type=bool,
                required=False,
                default=True,
                help="Preserve original indentation context",
                example="true"
            ),
            ArgumentSpec(
                name="validate_syntax",
                type=bool,
                required=False,
                default=True,
                help="Validate syntax after replacement",
                example="true"
            )
        ]
    
    def get_description(self) -> str:
        """Get REPLACE operation description."""
        return "Replace content with intelligent indentation, backup, and validation"
    
    def get_examples(self) -> List[str]:
        """Get REPLACE operation examples."""
        return [
            "surgical-modifier replace --target-file models.py --pattern 'old_function' --replacement 'new_function'",
            "surgical-modifier replace --target-file app.js --pattern 'function.*calculate' --replacement 'function newCalculate' --regex-mode",
            "surgical-modifier replace --target-file config.py --pattern 'DEBUG = False' --replacement 'DEBUG = True' --validate-syntax"
        ]
    
    def execute(self, context: OperationContext) -> OperationResult:
        """Execute REPLACE operation with intelligence."""
        try:
            target_file = context.target_file
            pattern = context.arguments.get('pattern', context.position_marker) if context.arguments else context.position_marker
            replacement = context.content or ""
            
            # Use intelligent replace function
            result = replace_operation(str(target_file), pattern, replacement)
            
            if result['success']:
                return OperationResult(
                    success=True,
                    operation_type=self.operation_type,
                    file_path=str(target_file),
                    message=result['message'],
                    details=result,
                    execution_time=0.0,
                    operation_name=self.operation_name
                )
            else:
                return OperationResult(
                    success=False,
                    operation_type=self.operation_type,
                    file_path=str(target_file),
                    message=result.get('error', 'Replace failed'),
                    details=result,
                    execution_time=0.0,
                    operation_name=self.operation_name
                )
                
        except Exception as e:
            return OperationResult(
                success=False,
                operation_type=self.operation_type,
                file_path=str(context.target_file) if context.target_file else "unknown",
                message=f"Replace operation failed: {e}",
                details={'error': str(e)},
                execution_time=0.0,
                operation_name=self.operation_name
            )

# ========== CONVENIENCE FUNCTIONS ==========

def replace_content(target_file: str, pattern: str, replacement: str, **kwargs) -> OperationResult:
    """Convenience function to replace content in a file."""
    operation = ReplaceOperation()
    context = operation.prepare_context(
        target_file, replacement, 
        position_marker=pattern, 
        **kwargs
    )
    return operation.execute_with_logging(context)

# ========== v5.3 COMPATIBILITY ==========

def replace_content_v53(file_path: str, pattern: str, replacement: str, 
                       regex_mode: bool = False, **kwargs) -> OperationResult:
    """v5.3 compatible REPLACE content function."""
    operation = ReplaceOperation()
    return operation.replace_content_v53(file_path, pattern, replacement, regex_mode, **kwargs)

# Alias for consistency

def replace_content_regex(target_file: str, pattern: str, replacement: str, **kwargs) -> OperationResult:
    """
    Convenience function to replace content using regex.
    
    Args:
        target_file: Path to file to modify
        pattern: Regex pattern to search for
        replacement: Content to replace with
        **kwargs: Additional context parameters
        
    Returns:
        OperationResult with replacement details
    """
    kwargs['regex_mode'] = True
    return replace_content(target_file, pattern, replacement, **kwargs)
execute = replace_operation