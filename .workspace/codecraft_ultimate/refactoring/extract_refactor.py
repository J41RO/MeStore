"""
🚀 CodeCraft Ultimate v6.0 - Surgical Operations
Enhanced surgical code modification operations
"""

import os
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ...core.engine import ExecutionContext, OperationResult
from ...analyzers.universal_analyzer import UniversalAnalyzer


class SurgicalOperations:
    """Enhanced surgical operations from v5.3"""
    
    def __init__(self, context: ExecutionContext, config: Dict[str, Any]):
        self.context = context
        self.config = config
        self.analyzer = UniversalAnalyzer()
        self.backup_files = []
    
    def execute(self, operation: str, args: Any) -> OperationResult:
        """Execute surgical operation"""
        
        try:
            # Route to specific operation
            if operation == 'create':
                return self._create_file(args.file, args.content)
            elif operation == 'replace':
                return self._replace_content(args.file, args.pattern, args.content)
            elif operation == 'after':
                return self._insert_after(args.file, args.pattern, args.content)
            elif operation == 'before':
                return self._insert_before(args.file, args.pattern, args.content)
            elif operation == 'append':
                return self._append_content(args.file, args.content)
            elif operation == 'delete':
                return self._delete_pattern(args.file, args.pattern)
            elif operation == 'extract-method':
                return self._extract_method(args.file, args.start_line, args.end_line, args.method_name)
            elif operation == 'extract-class':
                return self._extract_class(args.file, args.pattern, args.class_name)
            elif operation == 'rename-symbol':
                return self._rename_symbol(args.file, args.old_name, args.new_name)
            else:
                return OperationResult(
                    success=False,
                    operation=operation,
                    message=f"Unknown surgical operation: {operation}",
                    errors=[f"Operation '{operation}' is not supported"]
                )
        
        except Exception as e:
            return OperationResult(
                success=False,
                operation=operation,
                message=f"Surgical operation failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _create_file(self, file_path: str, content: str) -> OperationResult:
        """Create a new file"""
        
        # Resolve full path
        full_path = self._resolve_path(file_path)
        
        # Check if file already exists
        if os.path.exists(full_path):
            return OperationResult(
                success=False,
                operation='create',
                message=f"File already exists: {file_path}",
                errors=[f"Cannot create file, already exists: {file_path}"]
            )
        
        # Create directory if needed
        directory = os.path.dirname(full_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Write file
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Analyze created file
            file_context = self._analyze_file_context(full_path, content)
            
            return OperationResult(
                success=True,
                operation='create',
                message=f"File created successfully: {file_path}",
                data={
                    'file_path': full_path,
                    'lines_added': len(content.splitlines()),
                    'file_size': len(content),
                    'file_type': self.analyzer.detect_file_type(full_path)
                },
                context=file_context,
                suggestions=self._generate_create_suggestions(full_path, content)
            )
        
        except Exception as e:
            return OperationResult(
                success=False,
                operation='create',
                message=f"Failed to create file: {str(e)}",
                errors=[str(e)]
            )
    
    def _replace_content(self, file_path: str, pattern: str, new_content: str) -> OperationResult:
        """Replace pattern in file"""
        
        full_path = self._resolve_path(file_path)
        
        if not os.path.exists(full_path):
            return OperationResult(
                success=False,
                operation='replace',
                message=f"File not found: {file_path}",
                errors=[f"File does not exist: {file_path}"]
            )
        
        # Create backup
        backup_path = self._create_backup(full_path)
        
        try:
            # Read original content
            with open(full_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Check if pattern exists
            if pattern not in original_content:
                # Clean up backup
                if backup_path:
                    os.remove(backup_path)
                
                return OperationResult(
                    success=False,
                    operation='replace',
                    message=f"Pattern not found: {pattern}",
                    errors=[f"Pattern '{pattern}' not found in file"],
                    suggestions=self._suggest_similar_patterns(original_content, pattern)
                )
            
            # Perform replacement
            modified_content = original_content.replace(pattern, new_content)
            
            # Write modified content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            # Analyze changes
            changes = self._analyze_changes(original_content, modified_content)
            file_context = self._analyze_file_context(full_path, modified_content)
            
            return OperationResult(
                success=True,
                operation='replace',
                message=f"Content replaced successfully in {file_path}",
                data={
                    'file_path': full_path,
                    'pattern_replaced': pattern,
                    'replacement_content': new_content,
                    'backup_created': backup_path,
                    **changes
                },
                context=file_context,
                suggestions=self._generate_modification_suggestions(full_path, 'replace')
            )
        
        except Exception as e:
            # Restore from backup on error
            if backup_path and os.path.exists(backup_path):
                shutil.copy2(backup_path, full_path)
            
            return OperationResult(
                success=False,
                operation='replace',
                message=f"Replace operation failed: {str(e)}",
                errors=[str(e)]
            )
    
    # Helper methods
    
    def _resolve_path(self, file_path: str) -> str:
        """Resolve file path relative to project root or current directory"""
        if os.path.isabs(file_path):
            return file_path
        
        # Try relative to project root first
        project_path = os.path.join(self.context.project_root, file_path)
        if os.path.exists(project_path) or not os.path.exists(file_path):
            return project_path
        
        # Fallback to current directory
        return os.path.abspath(file_path)
    
    def _create_backup(self, file_path: str) -> Optional[str]:
        """Create backup of file"""
        if not self.config['operations']['create_backups']:
            return None
        
        try:
            backup_dir = os.path.join(self.context.project_root, '.codecraft_backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{os.path.basename(file_path)}.{timestamp}.backup"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            shutil.copy2(file_path, backup_path)
            self.backup_files.append(backup_path)
            
            return backup_path
        
        except Exception:
            return None
    
    def _analyze_changes(self, original: str, modified: str) -> Dict[str, Any]:
        """Analyze changes between original and modified content"""
        original_lines = original.splitlines()
        modified_lines = modified.splitlines()
        
        return {
            'lines_before': len(original_lines),
            'lines_after': len(modified_lines),
            'lines_added': len(modified_lines) - len(original_lines),
            'chars_before': len(original),
            'chars_after': len(modified),
            'chars_changed': len(modified) - len(original)
        }
    
    def _analyze_file_context(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze file context for AI suggestions"""
        file_type = self.analyzer.detect_file_type(file_path)
        complexity = self.analyzer.analyze_complexity(content, file_path)
        dependencies = self.analyzer.extract_dependencies(content, file_path)
        
        return {
            'file_type': file_type,
            'complexity_score': complexity.complexity_score,
            'lines_of_code': complexity.lines_of_code,
            'functions': complexity.functions,
            'classes': complexity.classes,
            'dependencies': [dep.name for dep in dependencies[:5]],  # Top 5 deps
            'file_size_bytes': len(content.encode('utf-8'))
        }
    
    def _generate_create_suggestions(self, file_path: str, content: str) -> List[str]:
        """Generate suggestions after file creation"""
        suggestions = []
        file_type = self.analyzer.detect_file_type(file_path)
        
        if file_type == 'python':
            suggestions.append(f"codecraft generate-tests {file_path} --test-framework=pytest")
            suggestions.append(f"codecraft analyze-complexity {file_path}")
        elif file_type in ['javascript', 'typescript']:
            suggestions.append(f"codecraft generate-tests {file_path} --test-framework=jest")
            suggestions.append("codecraft optimize-imports .")
        
        suggestions.append(f"codecraft find-dependencies {file_path}")
        
        return suggestions
    
    def _generate_modification_suggestions(self, file_path: str, operation: str) -> List[str]:
        """Generate suggestions after modification"""
        suggestions = []
        
        if operation in ['replace', 'after', 'before']:
            suggestions.append(f"codecraft analyze-complexity {file_path}")
            suggestions.append("codecraft find-bugs . --severity=medium")
        
        return suggestions
    
    def _suggest_similar_patterns(self, content: str, pattern: str) -> List[str]:
        """Suggest similar patterns when exact match not found"""
        suggestions = []
        lines = content.splitlines()
        
        # Simple fuzzy matching
        pattern_words = pattern.lower().split()
        
        for line in lines[:50]:  # Check first 50 lines
            line_lower = line.lower()
            
            # Check if line contains any pattern words
            matches = sum(1 for word in pattern_words if word in line_lower)
            
            if matches > 0 and len(line.strip()) > 3:
                similarity = matches / len(pattern_words)
                if similarity >= 0.3:  # 30% similarity threshold
                    suggestions.append(f"Similar: {line.strip()}")
        
        return suggestions[:3]  # Return top 3 suggestions