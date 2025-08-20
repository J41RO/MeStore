#!/usr/bin/env python3
"""
Surgical Modifier v6.0 - CLI Router
Extensible command system for all operations
"""

import click
import sys
from pathlib import Path

# Rich imports for beautiful output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version information')
@click.pass_context
def main(ctx, version):
    """
    🔥 SURGICAL MODIFIER v6.0 🔥
    The most complete code modification tool in the world
    
    Usage: made <operation> [options]
    """
    if version:
        show_version()
        return
        
    if ctx.invoked_subcommand is None:
        show_help()

def show_version():
    """Display version information"""
    version_text = """
🔥 Surgical Modifier v6.0.0 🔥
The most complete code modification tool in the world

Base: surgical_modifier_ultimate.py v5.3 (2,684 lines)
Architecture: Modular + Extensible
Command: made (global access)
Status: Production Ready
    """
    
    if RICH_AVAILABLE:
        console.print(Panel(version_text.strip(), title="Version Info", border_style="cyan"))
    else:
        print(version_text)

def show_help():
    """Display main help with available operations"""
    help_text = """
🎯 AVAILABLE OPERATIONS:

📦 BASIC OPERATIONS (Ready):
  made create <file> <content>     - Create new file with content
  made replace <file> <pattern> <new> - Replace pattern in file
  made after <file> <pattern> <content> - Insert content after pattern
  made before <file> <pattern> <content> - Insert content before pattern
  made append <file> <content>     - Append content to file
  made extract <file> <pattern> <dest> - Extract code block to new file

⚡ ADVANCED OPERATIONS (Ready):
  made move <file> <pattern> <dest> - Move code block to another file
  made duplicate <file> <pattern> [new_name] - Duplicate code block
  made batch <json_file>           - Execute multiple operations
  made delete <file> <pattern>     - Intelligently delete code block

🚀 FUTURE OPERATIONS (Modular Ready):
  made refactor, made wrap, made generate, made transform
  made suggest, made learn, made predict
  made share, made review, made template

🔧 UTILITY:
  made --version                   - Show version information
  made --help                      - Show this help

📚 Examples:
  made create components/Button.tsx "export const Button = () => <button />"
  made replace app.py "old_function" "new_function"
  made move utils.py "def helper" helpers.py
"""

    if RICH_AVAILABLE:
        console.print(Panel(help_text.strip(), title="🔥 Surgical Modifier v6.0", border_style="green"))
    else:
        print(help_text)

# Placeholder for future operations - auto-discovery system
def register_operations():
    """
    Auto-discovery system for operations
    Will automatically find and register operations from:
    - core.operations.basic.*
    - core.operations.advanced.*
    - core.operations.revolutionary.*
    """
    # TODO: Implement auto-discovery in future phases
    pass

if __name__ == "__main__":
    main()
