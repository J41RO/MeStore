"""
Surgical Modifier v6.0 - Rich Logger System
Beautiful and detailed output for all operations
"""

import os
import sys
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class SurgicalLogger:
    """Rich logger for beautiful output"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.verbose = False

    def info(self, message, title=None):
        """Info message with optional title"""
        if RICH_AVAILABLE:
            if title:
                self.console.print(Panel(message, title=title, border_style="blue"))
            else:
                self.console.print(f"ℹ️  {message}", style="blue")
        else:
            print(f"INFO: {message}")

    def success(self, message, title=None):
        """Success message"""
        if RICH_AVAILABLE:
            if title:
                self.console.print(Panel(message, title=title, border_style="green"))
            else:
                self.console.print(f"✅ {message}", style="green")
        else:
            print(f"SUCCESS: {message}")

    def warning(self, message, title=None):
        """Warning message"""
        if RICH_AVAILABLE:
            if title:
                self.console.print(Panel(message, title=title, border_style="yellow"))
            else:
                self.console.print(f"⚠️  {message}", style="yellow")
        else:
            print(f"WARNING: {message}")

    def error(self, message, title=None):
        """Error message"""
        if RICH_AVAILABLE:
            if title:
                self.console.print(Panel(message, title=title, border_style="red"))
            else:
                self.console.print(f"❌ {message}", style="red")
        else:
            print(f"ERROR: {message}")


# Global logger instance
logger = SurgicalLogger()
