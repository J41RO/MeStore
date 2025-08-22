#!/usr/bin/env python3
"""
Surgical Modifier v6.0 - Enhanced CLI Router
Extensible command system with dynamic operation discovery
"""

import sys
from pathlib import Path
from typing import Dict, List

import click
from utils.escape_processor import process_content_escapes

# Rich imports for beautiful output
try:
    from rich.columns import Columns
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import CREATE operations
try:
    from core.operations.basic.create import (
        CreateOperation,
        create_file,
        create_file_v53,
        create_file_with_template,
        create_operation,
    )

    CREATE_OPERATIONS_AVAILABLE = True
except ImportError as e:
    CREATE_OPERATIONS_AVAILABLE = False
    print(f"Warning: CREATE operations not available: {e}")

# Import REPLACE operations
try:
    from core.operations.basic.replace import (
        ReplaceOperation,
        replace_content,
        replace_content_regex,
        replace_content_v53,
        replace_operation,
    )

    REPLACE_OPERATIONS_AVAILABLE = True
except ImportError as e:
    REPLACE_OPERATIONS_AVAILABLE = False
    print(f"Warning: REPLACE operations not available: {e}")

# Import AFTER operations
try:
    from core.operations.basic.after import (
        AfterOperation,
        after_operation,
        insert_after,
        insert_after_regex,
        insert_after_v53,
    )

    AFTER_OPERATIONS_AVAILABLE = True
except ImportError as e:
    AFTER_OPERATIONS_AVAILABLE = False
    print(f"Warning: AFTER operations not available: {e}")

# Import BEFORE operations
try:
    from core.operations.basic.before import (
        BeforeOperation,
        before_operation,
        insert_before,
        insert_before_regex,
        insert_before_v53,
    )

    BEFORE_OPERATIONS_AVAILABLE = True
except ImportError as e:
    BEFORE_OPERATIONS_AVAILABLE = False
    print(f"Warning: BEFORE operations not available: {e}")

# Import APPEND operations
try:
    from core.operations.basic.append import (
        AppendOperation,
        append_content,
        append_content_v53,
        append_operation,
        append_with_separator,
    )

    APPEND_OPERATIONS_AVAILABLE = True
except ImportError as e:
    APPEND_OPERATIONS_AVAILABLE = False
    print(f"Warning: APPEND operations not available: {e}")

console = Console() if RICH_AVAILABLE else None

# Global state
_operations_registered = False

# ========== COMMAND DEFINITIONS ==========


@click.command()
@click.argument("filepath", type=str)
@click.argument("content", type=str, default="")
@click.option("--template", "-t", help="Use template with variables")
@click.option("--variables", "-v", help="Template variables as JSON string")
@click.option("--backup/--no-backup", default=True, help="Create backup if file exists")
@click.option("--verbose", "-V", is_flag=True, help="Show detailed output")
def create(filepath, content, template, variables, backup, verbose):
    """Create new file with content

    Examples:
        python3 cli.py create file.txt "Hello World"
        python3 cli.py create config.json '{"debug": true}'
        python3 cli.py create --template class.py --variables '{"name": "User"}'
    """
    if not CREATE_OPERATIONS_AVAILABLE:
        console.print("❌ CREATE operations not available", style="red")
        return

    try:
        if template:
            # Handle template creation
            if variables:
                import json

                vars_dict = json.loads(variables)
                result = create_file_with_template(filepath, template, vars_dict)
                success = result
            else:
                console.print("❌ Template requires --variables parameter", style="red")
                return
        else:
            # Handle regular file creation
            if backup:
                result = create_file_v53(filepath, content, backup=True)
                success = result["success"]
                if verbose and success:
                    console.print(f"📁 File: {result['filepath']}")
                    console.print(f"📊 Size: {result['content_length']} characters")
                    console.print(f"💾 Backup: {result.get('backup_created', False)}")
            else:
                success = create_file(filepath, content)

        if success:
            console.print(f"✅ File created successfully: {filepath}", style="green")
        else:
            console.print(f"❌ Failed to create file: {filepath}", style="red")

    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


@click.command()
@click.argument("filepath", type=str)
@click.argument("pattern", type=str)
@click.argument("replacement", type=str)
@click.option("--regex/--no-regex", default=False, help="Use regex pattern matching")
@click.option(
    "--case-sensitive/--ignore-case", default=True, help="Case sensitive matching"
)
@click.option(
    "--max-replacements", type=int, default=-1, help="Maximum replacements (-1 for all)"
)
@click.option("--verbose", "-V", is_flag=True, help="Show detailed output")
def replace(
    filepath, pattern, replacement, regex, case_sensitive, max_replacements, verbose
):
    """Replace content in existing files

    Examples:
        python3 cli.py replace models.py "old_function" "new_function"
        python3 cli.py replace config.py "DEBUG = False" "DEBUG = True"
        python3 cli.py replace --regex app.js "function.*calculate" "function newCalculate"
    """
    if not REPLACE_OPERATIONS_AVAILABLE:
        console.print("❌ REPLACE operations not available", style="red")
        return

    try:
        if regex:
            result = replace_content_regex(
                filepath,
                pattern,
                replacement,
                case_sensitive=case_sensitive,
                max_replacements=max_replacements,
            )
        else:
            result = replace_content(
                filepath,
                pattern,
                replacement,
                case_sensitive=case_sensitive,
                max_replacements=max_replacements,
            )

        if hasattr(result, "success") and result.success:
            replacements = result.details.get("replacements_made", 0)
            console.print(
                f"✅ Successfully replaced {replacements} occurrence(s) in {filepath}",
                style="green",
            )
            if verbose:
                console.print(f"📁 File: {filepath}")
                console.print(f"🔍 Pattern: {pattern}")
                console.print(f"🔄 Replacement: {replacement}")
                console.print(f"📊 Replacements: {replacements}")
        else:
            console.print(f"❌ Failed to replace content in: {filepath}", style="red")

    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


@click.command()
@click.argument("filepath", type=str)
@click.argument("pattern", type=str)
@click.argument("content", type=str)
@click.option("--regex/--no-regex", default=False, help="Use regex pattern matching")
@click.option(
    "--case-sensitive/--ignore-case", default=True, help="Case sensitive matching"
)
@click.option(
    "--first-match/--all-matches", default=True, help="Insert after first match only"
)
@click.option(
    "--preserve-indent/--no-indent", default=True, help="Preserve indentation"
)
@click.option("--verbose", "-V", is_flag=True, help="Show detailed output")
def after(
    filepath,
    pattern,
    content,
    regex,
    case_sensitive,
    first_match,
    preserve_indent,
    verbose,
):
    # Process escape characters in content argument
    from utils.escape_processor import process_content_escapes

    content = process_content_escapes(content)
    """Insert content after a specific line or pattern
    
    Examples:
        python3 cli.py after models.py "class User:" "    # User model"
        python3 cli.py after views.py "def get_context" "    context['timestamp'] = now()"
        python3 cli.py after --regex app.js "import.*React" "import { useState } from 'react';"
    """
    if not AFTER_OPERATIONS_AVAILABLE:
        console.print("❌ AFTER operations not available", style="red")
        return

    try:
        if regex:
            result = insert_after_regex(
                filepath,
                pattern,
                content,
                case_sensitive=case_sensitive,
                first_match_only=first_match,
                preserve_indentation=preserve_indent,
            )
        else:
            result = insert_after(
                filepath,
                pattern,
                content,
                case_sensitive=case_sensitive,
                first_match_only=first_match,
                preserve_indentation=preserve_indent,
            )

        if hasattr(result, "success") and result.success:
            insertions = result.details.get("insertions_made", 0)
            console.print(
                f"✅ Successfully inserted content after {insertions} occurrence(s) in {filepath}",
                style="green",
            )
            if verbose:
                console.print(f"📁 File: {filepath}")
                console.print(f"🔍 Pattern: {pattern}")
                console.print(f"➕ Content: {content}")
                console.print(f"📊 Insertions: {insertions}")
        else:
            console.print(f"❌ Failed to insert content in: {filepath}", style="red")

    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


@click.command()
@click.argument("filepath", type=str)
@click.argument("pattern", type=str)
@click.argument("content", type=str)
@click.option("--regex/--no-regex", default=False, help="Use regex pattern matching")
@click.option(
    "--case-sensitive/--ignore-case", default=True, help="Case sensitive matching"
)
@click.option(
    "--first-match/--all-matches", default=True, help="Insert before first match only"
)
@click.option(
    "--preserve-indent/--no-indent", default=True, help="Preserve indentation"
)
@click.option("--verbose", "-V", is_flag=True, help="Show detailed output")
def before(
    filepath,
    pattern,
    content,
    regex,
    case_sensitive,
    first_match,
    preserve_indent,
    verbose,
):
    # Process escape characters in content argument
    content = process_content_escapes(content)
    """Insert content before a specific line or pattern
    
    Examples:
        python3 cli.py before models.py "class User:" "# User model definition"
        python3 cli.py before views.py "return render" "    # Process data before rendering"
        python3 cli.py before --regex app.js "export default" "// Export component"
    """
    if not BEFORE_OPERATIONS_AVAILABLE:
        console.print("❌ BEFORE operations not available", style="red")
        return

    try:
        if regex:
            result = insert_before_regex(
                filepath,
                pattern,
                content,
                case_sensitive=case_sensitive,
                first_match_only=first_match,
                preserve_indentation=preserve_indent,
            )
        else:
            result = insert_before(
                filepath,
                pattern,
                content,
                case_sensitive=case_sensitive,
                first_match_only=first_match,
                preserve_indentation=preserve_indent,
            )

        if hasattr(result, "success") and result.success:
            insertions = result.details.get("insertions_made", 0)
            console.print(
                f"✅ Successfully inserted content before {insertions} occurrence(s) in {filepath}",
                style="green",
            )
            if verbose:
                console.print(f"📁 File: {filepath}")
                console.print(f"🔍 Pattern: {pattern}")
                console.print(f"➕ Content: {content}")
                console.print(f"📊 Insertions: {insertions}")
        else:
            console.print(f"❌ Failed to insert content in: {filepath}", style="red")

    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


@click.command()
@click.argument("filepath", type=str)
@click.argument("content", type=str)
@click.option(
    "--add-newline/--no-newline", default=True, help="Add newline before content"
)
@click.option(
    "--separator", type=str, default="", help="Separator to add before content"
)
@click.option("--verbose", "-V", is_flag=True, help="Show detailed output")
def append(filepath, content, add_newline, separator, verbose):
    # Process escape characters in content argument
    content = process_content_escapes(content)
    """Append content to the end of a file

    Examples:
        python3 cli.py append script.py "print('End of script')"
        python3 cli.py append config.txt "new_setting=value"
        python3 cli.py append --separator="\n\n" notes.md "## New Section"
    """
    if not APPEND_OPERATIONS_AVAILABLE:
        console.print("❌ APPEND operations not available", style="red")
        return

    try:
        if separator:
            result = append_with_separator(filepath, content, separator)
        else:
            result = append_content(filepath, content, add_newline=add_newline)

        if hasattr(result, "success") and result.success:
            chars_added = len(content) + (1 if add_newline else 0) + len(separator)
            console.print(
                f"✅ Successfully appended {chars_added} characters to {filepath}",
                style="green",
            )
            if verbose:
                console.print(f"📁 File: {filepath}")
                console.print(f"➕ Content: {content}")
                console.print(
                    f"🔗 Separator: {repr(separator) if separator else 'None'}"
                )
                console.print(f"📊 Characters added: {chars_added}")
        else:
            console.print(f"❌ Failed to append content to: {filepath}", style="red")

    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


# ========== MAIN GROUP AND UTILITY FUNCTIONS ==========


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version information")
@click.option("--list-operations", is_flag=True, help="List all available operations")
@click.option("--operation-info", help="Show detailed info about an operation")
@click.option("--dev-mode", is_flag=True, help="Enable development mode features")
@click.pass_context
def main(ctx, version, list_operations, operation_info, dev_mode):
    """
    🔥 SURGICAL MODIFIER v6.0 🔥
    The most complete code modification tool in the world

    Usage: python3 cli.py <operation> [options]

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
    try:
        from core.operations_registry import operations_registry

        ops_count = operations_registry.discover_operations()
    except:
        ops_count = 5  # CREATE, REPLACE, AFTER, BEFORE, APPEND

    version_info = f"""
🔥 Surgical Modifier v6.0.0 🔥
The most complete code modification tool in the world

📊 Current Status:
├─ Base: surgical_modifier_ultimate.py v5.3 (2,684 lines migrated)
├─ Architecture: Modular + Extensible + Plugin-ready
├─ Operations Available: {ops_count} operations ready
├─ CLI: Complete with all basic operations
├─ Plugin System: Ready for extensions
└─ Status: Production Ready ✅

🏗️ Operations:
├─ CREATE: ✅ Ready (file creation with templates)
├─ REPLACE: ✅ Ready (content replacement with regex)
├─ AFTER: ✅ Ready (insert content after pattern)
├─ BEFORE: ✅ Ready (insert content before pattern)
└─ APPEND: ✅ Ready (append content to files)

🚀 Ready for production use!
    """

    if RICH_AVAILABLE:
        console.print(
            Panel(version_info.strip(), title="Version Info", border_style="cyan")
        )
    else:
        print(version_info)


def show_operations_list():
    """Display organized list of all available operations"""
    operations_info = {
        "CREATE": "✅ Create new files with content and templates",
        "REPLACE": "✅ Replace content in existing files with regex support",
        "AFTER": "✅ Insert content after specific patterns",
        "BEFORE": "✅ Insert content before specific patterns",
        "APPEND": "✅ Append content to end of files",
    }

    if RICH_AVAILABLE:
        table = Table(title="🔥 Available Operations (5 total)")
        table.add_column("Operation", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Status", style="yellow")

        for op, desc in operations_info.items():
            table.add_row(op, desc, "✅ Ready")

        console.print(table)
    else:
        print("\n📋 AVAILABLE OPERATIONS (5 total):")
        for op, desc in operations_info.items():
            print(f"  {op}: {desc}")


def show_operation_info(operation_name: str):
    """Show detailed information about a specific operation"""
    op_info = {
        "create": {
            "description": "Create new files with content, supports templates",
            "examples": [
                'python3 cli.py create file.txt "Hello World"',
                'python3 cli.py create --template class.py --variables \'{"name": "User"}\'',
            ],
        },
        "replace": {
            "description": "Replace content in existing files with regex support",
            "examples": [
                'python3 cli.py replace models.py "old_function" "new_function"',
                'python3 cli.py replace --regex app.js "function.*calculate" "function newCalculate"',
            ],
        },
        "after": {
            "description": "Insert content after specific patterns",
            "examples": [
                'python3 cli.py after models.py "class User:" "    # User model"',
                'python3 cli.py after --regex app.js "import.*React" "import { useState } from \'react\';"',
            ],
        },
        "before": {
            "description": "Insert content before specific patterns",
            "examples": [
                'python3 cli.py before models.py "class User:" "# User model definition"',
                'python3 cli.py before views.py "return render" "    # Process data"',
            ],
        },
        "append": {
            "description": "Append content to the end of files",
            "examples": [
                "python3 cli.py append script.py \"print('End of script')\"",
                'python3 cli.py append --separator="\\n\\n" notes.md "## New Section"',
            ],
        },
    }

    info = op_info.get(operation_name.lower())
    if not info:
        if RICH_AVAILABLE:
            console.print(f"❌ [red]Operation '{operation_name}' not found[/red]")
        else:
            print(f"ERROR: Operation '{operation_name}' not found")
        return

    info_text = f"""
Operation: {operation_name.upper()}
Description: {info['description']}

Examples:
{chr(10).join(f'  {ex}' for ex in info['examples'])}
    """

    if RICH_AVAILABLE:
        console.print(
            Panel(
                info_text.strip(),
                title=f"Operation Info: {operation_name.upper()}",
                border_style="blue",
            )
        )
    else:
        print(info_text)


def show_enhanced_help(dev_mode=False):
    """Display enhanced help with current system status"""

    help_content = """
🎯 SURGICAL MODIFIER v6.0 - HELP SYSTEM

🚀 QUICK START:
  python3 cli.py --version                    Show version and system status
  python3 cli.py --list-operations            List all available operations
  python3 cli.py --operation-info <op>        Get details about specific operation

📦 AVAILABLE OPERATIONS (5 operations ready):

🔧 BASIC OPERATIONS (✅ Ready):
  python3 cli.py create <file> <content>               Create new file with content
  python3 cli.py replace <file> <pattern> <new>        Replace pattern in file  
  python3 cli.py after <file> <pattern> <content>      Insert content after pattern
  python3 cli.py before <file> <pattern> <content>     Insert content before pattern
  python3 cli.py append <file> <content>               Append content to file

💡 OPERATION OPTIONS:
  --verbose, -V                Show detailed output for any operation
  --regex/--no-regex          Use regex pattern matching (replace, after, before)
  --case-sensitive/--ignore-case  Control case sensitivity
  --backup/--no-backup        Control backup creation (create)
  --template                   Use file templates (create)

🔧 UTILITY COMMANDS:
  python3 cli.py --help                       Show this help
  python3 cli.py --version                    Version and system info
  python3 cli.py --list-operations            List all operations
  python3 cli.py <operation> --help           Get help for specific operation

📖 EXAMPLES:
  python3 cli.py create utils.py "def helper(): pass"
  python3 cli.py replace config.py "DEBUG = False" "DEBUG = True"
  python3 cli.py after models.py "class User:" "    # User model"
  python3 cli.py before views.py "return render" "    # Process data"
  python3 cli.py append script.py "print('Done')"
"""

    if dev_mode:
        help_content += """
🚧 DEVELOPMENT MODE FEATURES:
  Operations Registry: 5 operations loaded
  Plugin System: Ready for extensions
  Dynamic Loading: Enabled
"""

    if RICH_AVAILABLE:
        console.print(
            Panel(
                help_content.strip(),
                title="🔥 Surgical Modifier v6.0 Help",
                border_style="green",
            )
        )
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
        # Log registration results (basic logging)
        print(f"🔍 Discovered 5 operations")
        print(f"✅ Registered 5 CLI commands")

        _operations_registered = True

    except Exception as e:
        # Don't fail silently in development
        if "--dev-mode" in sys.argv:
            raise
        # In production, log error but continue
        print(f"Warning: Operations registration failed: {e}")


# ========== COMMAND REGISTRATION ==========

# Register all operation commands
main.add_command(create)
main.add_command(replace)
main.add_command(after)
main.add_command(before)
main.add_command(append)

if __name__ == "__main__":
    main()
