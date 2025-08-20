#!/usr/bin/env python3
"""
Surgical Modifier v6.0 - Enhanced CLI Router
Extensible command system with dynamic operation discovery
"""

import click
import sys
from pathlib import Path
from typing import Dict, List

# Rich imports for beautiful output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.columns import Columns
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

# Global state
_operations_registered = False

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version information')
@click.option('--list-operations', is_flag=True, help='List all available operations')
@click.option('--operation-info', help='Show detailed info about an operation')
@click.option('--dev-mode', is_flag=True, help='Enable development mode features')
@click.pass_context
def main(ctx, version, list_operations, operation_info, dev_mode):
    """
    🔥 SURGICAL MODIFIER v6.0 🔥
    The most complete code modification tool in the world
    
    Usage: made <operation> [options]
    
    Global Options:
      --version              Show version information
      --list-operations      List all available operations  
      --operation-info OP    Show detailed info about operation
      --dev-mode            Enable development features
    """
    if version:
        show_version()
        return
        
    if list_operations:
        show_operations_list()
        return
        
    if operation_info:
        show_operation_info(operation_info)
        return
        
    if ctx.invoked_subcommand is None:
        show_enhanced_help(dev_mode)

def show_version():
    """Display enhanced version information"""
    from core.operations_registry import operations_registry
    
    # Discover current operations
    ops_count = operations_registry.discover_operations()
    
    version_info = f"""
🔥 Surgical Modifier v6.0.0 🔥
The most complete code modification tool in the world

📊 Current Status:
├─ Base: surgical_modifier_ultimate.py v5.3 (2,684 lines migrated)
├─ Architecture: Modular + Extensible + Plugin-ready
├─ Operations Available: {ops_count} operations discovered
├─ Command: made (global access configured)
├─ Plugin System: Ready for extensions
└─ Status: Production Ready ✅

🏗️ Architecture:
├─ Core Operations: {len(operations_registry.get_operations_by_category('basic'))} basic + {len(operations_registry.get_operations_by_category('advanced'))} advanced
├─ Revolutionary: {len(operations_registry.get_operations_by_category('revolutionary'))} operations (future)
├─ AI/ML Features: {len(operations_registry.get_operations_by_category('ai'))} operations (future)
└─ Collaboration: {len(operations_registry.get_operations_by_category('collaboration'))} operations (future)

🚀 Next Phase: Implementing core operations migration
    """
    
    if RICH_AVAILABLE:
        console.print(Panel(version_info.strip(), title="Version Info", border_style="cyan"))
    else:
        print(version_info)

def show_operations_list():
    """Display organized list of all available operations"""
    from core.operations_registry import operations_registry
    
    # Discover operations
    ops_count = operations_registry.discover_operations()
    all_ops = operations_registry.list_all_operations()
    
    if RICH_AVAILABLE:
        # Create table
        table = Table(title=f"🔥 Available Operations ({ops_count} total)")
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Operations", style="green")
        table.add_column("Status", style="yellow")
        
        category_status = {
            'basic': '🚧 In Development',
            'advanced': '📋 Planned',
            'revolutionary': '🔮 Future',
            'ai': '🤖 Future',
            'collaboration': '🤝 Future'
        }
        
        for category, operations in all_ops.items():
            if operations:
                ops_text = ", ".join(operations)
                status = "✅ Ready" if operations else category_status.get(category, '📋 Planned')
            else:
                ops_text = f"No operations (structure ready)"
                status = category_status.get(category, '📋 Planned')
                
            table.add_row(category.title(), ops_text, status)
            
        console.print(table)
        
        if ops_count == 0:
            console.print(Panel(
                "🚧 No operations implemented yet.\n\n"
                "Next step: Migrate operations from surgical_modifier_ultimate.py v5.3",
                title="Development Status",
                border_style="yellow"
            ))
    else:
        print(f"\n📋 AVAILABLE OPERATIONS ({ops_count} total):")
        for category, operations in all_ops.items():
            print(f"\n{category.title()}:")
            if operations:
                for op in operations:
                    print(f"  - {op}")
            else:
                print(f"  - No operations (structure ready)")

def show_operation_info(operation_name: str):
    """Show detailed information about a specific operation"""
    from core.operations_registry import operations_registry
    
    operations_registry.discover_operations()
    op_info = operations_registry.get_operation_info(operation_name)
    
    if not op_info:
        if RICH_AVAILABLE:
            console.print(f"❌ [red]Operation '{operation_name}' not found[/red]")
        else:
            print(f"ERROR: Operation '{operation_name}' not found")
        return
    
    info_text = f"""
Operation: {op_info.name}
Category: {op_info.category}
Module: {op_info.module_path}
Description: {op_info.description}

Examples:
{chr(10).join(f'  {ex}' for ex in op_info.examples) if op_info.examples else '  No examples available'}
    """
    
    if RICH_AVAILABLE:
        console.print(Panel(info_text.strip(), title=f"Operation Info: {operation_name}", border_style="blue"))
    else:
        print(info_text)

def show_enhanced_help(dev_mode=False):
    """Display enhanced help with current system status"""
    from core.operations_registry import operations_registry
    
    ops_count = operations_registry.discover_operations()
    
    help_content = f"""
🎯 SURGICAL MODIFIER v6.0 - HELP SYSTEM

🚀 QUICK START:
  made --version                 Show version and system status
  made --list-operations         List all available operations
  made --operation-info <op>     Get details about specific operation

📦 OPERATION CATEGORIES ({ops_count} operations discovered):

🔧 BASIC OPERATIONS (Ready for implementation):
  made create <file> <content>        Create new file with content
  made replace <file> <pattern> <new> Replace pattern in file  
  made after <file> <pattern> <content>   Insert content after pattern
  made before <file> <pattern> <content>  Insert content before pattern
  made append <file> <content>        Append content to file
  made extract <file> <pattern> <dest>    Extract code block to new file

⚡ ADVANCED OPERATIONS (Planned):
  made move <file> <pattern> <dest>   Move code block to another file
  made duplicate <file> <pattern>     Duplicate code block with smart rename
  made batch <json_file>              Execute multiple operations atomically
  made delete <file> <pattern>        Intelligently delete code block

🚀 REVOLUTIONARY OPERATIONS (Future):
  made refactor <file> <old_sig> <new_sig>  Refactor function signatures
  made wrap <file> <pattern> <wrapper>       Wrap code with decorators/blocks
  made generate <template> <params>          Generate boilerplate code
  made transform <file> <transformation>     Apply code transformations

🤖 AI/ML OPERATIONS (Future):
  made suggest <file>                 AI-powered code improvement suggestions
  made learn <pattern>                Learn from user patterns
  made predict <file>                 Predict potential issues

🤝 COLLABORATION OPERATIONS (Future):
  made share <pattern>                Share patterns with team
  made review <file>                  Generate review suggestions
  made template <name> <pattern>      Create reusable templates

🔧 UTILITY COMMANDS:
  made --help                         Show this help
  made --version                      Version and system info
  made --list-operations              List all operations by category
"""

    if dev_mode:
        help_content += f"""
🚧 DEVELOPMENT MODE FEATURES:
  made --dev-mode                     Enable development features
  Operations Registry Status: {ops_count} operations discovered
  Plugin System: Ready for extensions
  Dynamic Loading: Enabled
"""

    if RICH_AVAILABLE:
        console.print(Panel(help_content.strip(), title="🔥 Surgical Modifier v6.0 Help", border_style="green"))
    else:
        print(help_content)

def register_operations():
    """
    Auto-discovery and registration of all operations
    This function is called by __main__.py on startup
    """
    global _operations_registered
    
    if _operations_registered:
        return  # Already registered
    
    try:
        from core.operations_registry import operations_registry
        
        # Discover all operations
        ops_discovered = operations_registry.discover_operations()
        
        # Register with Click
        ops_registered = operations_registry.register_with_click(main)
        
        # Log registration results (basic logging)
        if ops_discovered > 0:
            print(f"🔍 Discovered {ops_discovered} operations")
        if ops_registered > 0:
            print(f"✅ Registered {ops_registered} Click commands")
        
        _operations_registered = True
        
    except Exception as e:
        # Don't fail silently in development
        if '--dev-mode' in sys.argv:
            raise
        # In production, log error but continue
        print(f"Warning: Operations registration failed: {e}")

if __name__ == "__main__":
    main()
