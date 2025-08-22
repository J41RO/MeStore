"""
Surgical Modifier v6.0 - Enhanced Rich Logger System
Beautiful and detailed output for all operations with advanced features
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from rich.align import Align
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import (
        BarColumn,
        MofNCompleteColumn,
        Progress,
        SpinnerColumn,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
    )
    from rich.rule import Rule
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.text import Text
    from rich.tree import Tree

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class EnhancedSurgicalLogger:
    """
    Enhanced Rich logger with advanced features:
    - Progress bars for long operations
    - Syntax highlighted diffs
    - Operation tracking
    - Performance monitoring
    - Visual file operations
    """

    def __init__(self, enable_performance_tracking=True):
        self.console = Console() if RICH_AVAILABLE else None
        self.verbose = False
        self.enable_performance_tracking = enable_performance_tracking
        self.operation_start_times = {}
        self.operation_counts = {
            "info": 0,
            "success": 0,
            "warning": 0,
            "error": 0,
            "operations": 0,
            "files_modified": 0,
        }

    # ========== BASIC LOGGING (MAINTAIN COMPATIBILITY) ==========

    def info(self, message: str, title: Optional[str] = None):
        """Info message with optional title"""
        self.operation_counts["info"] += 1
        if RICH_AVAILABLE:
            if title:
                self.console.print(Panel(message, title=title, border_style="blue"))
            else:
                self.console.print(f"ℹ️  {message}", style="blue")
        else:
            print(f"INFO: {message}")

    def success(self, message: str, title: Optional[str] = None):
        """Success message"""
        self.operation_counts["success"] += 1
        if RICH_AVAILABLE:
            if title:
                self.console.print(Panel(message, title=title, border_style="green"))
            else:
                self.console.print(f"✅ {message}", style="green")
        else:
            print(f"SUCCESS: {message}")

    def warning(self, message: str, title: Optional[str] = None):
        """Warning message"""
        self.operation_counts["warning"] += 1
        if RICH_AVAILABLE:
            if title:
                self.console.print(Panel(message, title=title, border_style="yellow"))
            else:
                self.console.print(f"⚠️  {message}", style="yellow")
        else:
            print(f"WARNING: {message}")

    def error(self, message: str, title: Optional[str] = None):
        """Error message"""
        self.operation_counts["error"] += 1
        if RICH_AVAILABLE:
            if title:
                self.console.print(Panel(message, title=title, border_style="red"))
            else:
                self.console.print(f"❌ {message}", style="red")
        else:
            print(f"ERROR: {message}")

    # ========== ENHANCED LOGGING FEATURES ==========

    def operation_start(self, operation_name: str, description: str = ""):
        """Start tracking an operation"""
        self.operation_counts["operations"] += 1
        if self.enable_performance_tracking:
            self.operation_start_times[operation_name] = time.time()

        if RICH_AVAILABLE:
            self.console.print(Rule(f"🚀 Starting: {operation_name}"))
            if description:
                self.info(description, title=f"Operation: {operation_name}")
        else:
            print(f"OPERATION START: {operation_name} - {description}")

    def operation_end(self, operation_name: str, success: bool = True):
        """End tracking an operation"""
        elapsed_time = None
        if (
            self.enable_performance_tracking
            and operation_name in self.operation_start_times
        ):
            elapsed_time = time.time() - self.operation_start_times[operation_name]
            del self.operation_start_times[operation_name]

        status = "✅ Completed" if success else "❌ Failed"
        time_info = f" ({elapsed_time:.3f}s)" if elapsed_time else ""

        if RICH_AVAILABLE:
            style = "green" if success else "red"
            self.console.print(f"{status}: {operation_name}{time_info}", style=style)
            self.console.print(Rule(style=style))
        else:
            print(f"OPERATION END: {operation_name} - {status}{time_info}")

    def file_operation(self, operation: str, file_path: str, details: str = ""):
        """Log file operations with enhanced details"""
        self.operation_counts["files_modified"] += 1

        operation_emojis = {
            "create": "📄",
            "read": "👁️",
            "write": "✏️",
            "update": "🔄",
            "delete": "🗑️",
            "move": "📦",
            "copy": "📋",
            "backup": "💾",
        }

        emoji = operation_emojis.get(operation.lower(), "📁")

        if RICH_AVAILABLE:
            table = Table.grid(padding=1)
            table.add_column(style="cyan", no_wrap=True)
            table.add_column(style="white")

            table.add_row("Operation:", f"{emoji} {operation.upper()}")
            table.add_row("File:", file_path)
            if details:
                table.add_row("Details:", details)

            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                table.add_row("Size:", f"{size} bytes")

            self.console.print(
                Panel(table, title="File Operation", border_style="cyan")
            )
        else:
            print(f"FILE {operation.upper()}: {file_path} - {details}")

    def show_operation_summary(self):
        """Show summary of all operations performed"""
        if not RICH_AVAILABLE:
            print("OPERATION SUMMARY:")
            for key, value in self.operation_counts.items():
                print(f"  {key}: {value}")
            return

        table = Table(title="🎯 Operation Summary")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Count", style="green", justify="right")

        emoji_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "operations": "🚀",
            "files_modified": "📁",
        }

        for metric, count in self.operation_counts.items():
            emoji = emoji_map.get(metric, "📊")
            table.add_row(f"{emoji} {metric.replace('_', ' ').title()}", str(count))

        self.console.print(Panel(table, border_style="blue"))

    def detailed_failure_analysis(self, exception: Exception, context: dict = None) -> dict:
        """
        Analiza detalladamente fallos con stack traces y contexto.
        
        Args:
            exception: La excepción a analizar
            context: Contexto adicional (operación, archivo, parámetros, etc.)
            
        Returns:
            Dict con análisis completo del fallo
        """
        import traceback
        import re
        
        analysis = {
            'error_type': type(exception).__name__,
            'error_message': str(exception),
            'error_category': self._categorize_error(exception),
            'stack_trace': traceback.format_exc(),
            'context': context or {},
            'timestamp': datetime.now().isoformat(),
            'suggestions': self._get_error_suggestions(exception)
        }
        
        # Log análisis detallado
        self.error(f"Detailed failure analysis: {analysis['error_category']}")
        if context:
            self.info(f"Context: {context}")
        
        return analysis
    
    def log_operation_failure(self, operation_name: str, error: Exception, 
                            file_path: str = None, pattern: str = None, 
                            attempt_number: int = 1) -> str:
        """
        Registra fallo de operación con categorización y contexto.
        
        Returns:
            Categoría del error para tracking
        """
        category = self._categorize_error(error)
        context = {
            'operation': operation_name,
            'file': file_path,
            'pattern': pattern,
            'attempt': attempt_number,
            'error_type': type(error).__name__
        }
        
        # Incrementar contador de errores por categoría
        error_key = f"error_{category.lower()}"
        self.operation_counts[error_key] = self.operation_counts.get(error_key, 0) + 1
        
        # Log con formato rico
        self.error(f"Operation '{operation_name}' failed [{category}]")
        if file_path:
            self.warning(f"File: {file_path}")
        if pattern:
            self.warning(f"Pattern: {pattern}")
        
        return category
    
    def _categorize_error(self, error: Exception) -> str:
        """Categoriza errores en tipos específicos."""
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        if error_type in ['SyntaxError', 'IndentationError', 'TabError']:
            return 'SYNTAX_ERROR'
        elif error_type in ['FileNotFoundError', 'PermissionError', 'IsADirectoryError']:
            return 'FILE_ERROR'
        elif 'pattern' in error_msg or 'regex' in error_msg or 'match' in error_msg:
            return 'PATTERN_ERROR'
        elif 'validation' in error_msg or 'invalid' in error_msg:
            return 'VALIDATION_ERROR'
        else:
            return 'UNKNOWN_ERROR'
    
    def _get_error_suggestions(self, error: Exception) -> list:
        """Proporciona sugerencias basadas en el tipo de error."""
        error_type = type(error).__name__
        suggestions = []
        
        if error_type == 'SyntaxError':
            suggestions = [
                "Check syntax near the reported line",
                "Verify parentheses and brackets are balanced",
                "Check for missing colons after function/class definitions"
            ]
        elif error_type == 'FileNotFoundError':
            suggestions = [
                "Verify file path exists",
                "Check file permissions",
                "Ensure working directory is correct"
            ]
        elif 'pattern' in str(error).lower():
            suggestions = [
                "Verify regex pattern syntax",
                "Test pattern with online regex tools",
                "Check for special characters that need escaping"
            ]
        else:
            suggestions = ["Review error message and context for clues"]
        
        return suggestions
    
    
# Global enhanced logger instance
logger = EnhancedSurgicalLogger()

# Maintain backward compatibility
SurgicalLogger = EnhancedSurgicalLogger
