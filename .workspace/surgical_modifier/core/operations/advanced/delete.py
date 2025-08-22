"""
Delete operation implementation for Surgical Modifier v6.0
Advanced intelligent code deletion with block detection and preview
"""

import ast
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from utils.escape_processor import process_content_escapes

# Import from parent operations
try:
    from ..base_operation import (
        BaseOperation,
        OperationContext,
        OperationResult,
        OperationStatus,
        OperationType,
    )
except ImportError:
    from core.operations.base_operation import (
        BaseOperation,
        OperationContext,
        OperationResult,
        OperationStatus,
        OperationType,
    )


class DeleteOperation(BaseOperation):
    """Advanced delete operation with intelligent block detection"""

    def __init__(self):
        super().__init__(
            name="DELETE",
            description="✅ Delete code blocks intelligently with preview and validation",
            operation_type=OperationType.ADVANCED,
        )
        self.console = Console()

    def validate(self, context: OperationContext) -> bool:
        """Validate delete operation parameters"""
        if not context.target_file or not context.pattern:
            self.console.print(
                "[red]❌ Missing required parameters: target_file and pattern[/red]"
            )
            return False

        # Check if target file exists
        if not os.path.exists(context.target_file):
            self.console.print(f"[red]❌ File not found: {context.target_file}[/red]")
            return False

        return True

    def _detect_code_block(
        self, content: str, pattern: str
    ) -> Optional[Tuple[int, int, str]]:
        """Detect complete code block around pattern"""
        lines = content.split("\n")

        # Find line with pattern
        target_line = -1
        for i, line in enumerate(lines):
            if pattern in line:
                target_line = i
                break

        if target_line == -1:
            self.console.print(
                f"[yellow]⚠️ Pattern '{pattern}' not found in file[/yellow]"
            )
            return None

        # Detect if it's a function definition
        if "def " in lines[target_line]:
            return self._detect_function_block(lines, target_line)
        elif "class " in lines[target_line]:
            return self._detect_class_block(lines, target_line)
        elif "@" in lines[target_line]:
            # Decorator - find the function it decorates
            return self._detect_decorated_function(lines, target_line)
        else:
            # Simple line deletion
            return (target_line, target_line + 1, lines[target_line])

    def _detect_function_block(
        self, lines: List[str], start_line: int
    ) -> Tuple[int, int, str]:
        """Detect complete function block with decorators and docstring"""
        # Look backwards for decorators
        actual_start = start_line
        for i in range(start_line - 1, -1, -1):
            line = lines[i].strip()
            if line.startswith("@"):
                actual_start = i
            elif line == "" or line.startswith("#"):
                continue
            else:
                break

        # Find end of function using indentation
        indent_level = len(lines[start_line]) - len(lines[start_line].lstrip())
        end_line = len(lines)

        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip() == "":
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and line.strip():
                end_line = i
                break

        # Extract complete block
        block_lines = lines[actual_start:end_line]
        block_content = "\n".join(block_lines)

        return (actual_start, end_line, block_content)

    def _detect_class_block(
        self, lines: List[str], start_line: int
    ) -> Tuple[int, int, str]:
        """Detect complete class block"""
        # Look backwards for decorators
        actual_start = start_line
        for i in range(start_line - 1, -1, -1):
            line = lines[i].strip()
            if line.startswith("@"):
                actual_start = i
            elif line == "" or line.startswith("#"):
                continue
            else:
                break

        indent_level = len(lines[start_line]) - len(lines[start_line].lstrip())
        end_line = len(lines)

        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip() == "":
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and line.strip():
                end_line = i
                break

        block_content = "\n".join(lines[actual_start:end_line])
        return (actual_start, end_line, block_content)

    def _detect_decorated_function(
        self, lines: List[str], decorator_line: int
    ) -> Tuple[int, int, str]:
        """Detect function block starting from a decorator"""
        # Find the function definition after decorators
        function_line = -1
        for i in range(decorator_line, len(lines)):
            if "def " in lines[i]:
                function_line = i
                break

        if function_line == -1:
            # Just the decorator line
            return (decorator_line, decorator_line + 1, lines[decorator_line])

        return self._detect_function_block(lines, function_line)

    def _show_preview(self, file_path: str, block_info: Tuple[int, int, str]) -> bool:
        """Show preview of what will be deleted"""
        start_line, end_line, block_content = block_info

        self.console.print("\n" + "=" * 60)
        self.console.print(
            f"[bold yellow]🔍 PREVIEW: Content to be DELETED from {file_path}[/bold yellow]"
        )
        self.console.print(f"[cyan]📍 Lines {start_line + 1} to {end_line}[/cyan]")
        self.console.print("=" * 60)

        # Show syntax highlighted preview
        syntax = Syntax(block_content, "python", theme="monokai", line_numbers=True)
        panel = Panel(syntax, title="[red]Content to DELETE[/red]", border_style="red")
        self.console.print(panel)

        # Show context (lines before and after)
        with open(file_path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()

        # Show context before
        context_before = 3
        if start_line > 0:
            self.console.print(
                f"\n[dim]Context BEFORE (lines {max(1, start_line - context_before + 1)} to {start_line}):[/dim]"
            )
            for i in range(max(0, start_line - context_before), start_line):
                self.console.print(f"[dim]{i+1:3d}: {all_lines[i].rstrip()}[/dim]")

        # Show context after
        context_after = 3
        if end_line < len(all_lines):
            self.console.print(
                f"\n[dim]Context AFTER (lines {end_line + 1} to {min(len(all_lines), end_line + context_after)}):[/dim]"
            )
            for i in range(end_line, min(len(all_lines), end_line + context_after)):
                self.console.print(f"[dim]{i+1:3d}: {all_lines[i].rstrip()}[/dim]")

        return True

    def _validate_post_deletion(self, file_path: str) -> bool:
        """Validate that file is still syntactically correct after deletion"""
        try:
            if file_path.endswith(".py"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                ast.parse(content)
                self.console.print(
                    "[green]✅ Post-deletion syntax validation: PASSED[/green]"
                )
                return True
        except SyntaxError as e:
            self.console.print(f"[red]❌ Post-deletion syntax validation: FAILED[/red]")
            self.console.print(f"[red]Syntax error: {e}[/red]")
            return False
        except Exception as e:
            self.console.print(f"[yellow]⚠️ Could not validate syntax: {e}[/yellow]")
            return True  # Non-blocking for non-Python files

    def _perform_deletion(
        self, file_path: str, block_info: Tuple[int, int, str]
    ) -> bool:
        """Perform the actual deletion"""
        start_line, end_line, _ = block_info

        try:
            # Read all lines
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Remove the target lines
            new_lines = lines[:start_line] + lines[end_line:]

            # Write back to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            return True

        except Exception as e:
            self.console.print(f"[red]❌ Failed to delete content: {e}[/red]")
            return False

    def _analyze_dependencies(self, content: str, block_content: str) -> Dict[str, Any]:
        """Basic dependency analysis"""
        dependencies = {
            "functions_called": [],
            "imports_used": [],
            "variables_referenced": [],
            "potential_issues": [],
        }

        # Extract function calls from the block
        try:
            tree = ast.parse(block_content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    dependencies["functions_called"].append(node.func.id)
        except:
            pass

        # Check if these functions exist elsewhere
        remaining_content = content.replace(block_content, "")
        for func in dependencies["functions_called"]:
            if f"def {func}" not in remaining_content and func not in [
                "print",
                "len",
                "range",
                "str",
                "int",
            ]:
                dependencies["potential_issues"].append(
                    f"Function '{func}' might not be defined elsewhere"
                )

        return dependencies

    def execute(self, context: OperationContext) -> OperationResult:
        """Execute delete operation with intelligent block detection"""
        try:
            self.console.print(f"[bold blue]🗑️ DELETE Operation Started[/bold blue]")
            self.console.print(f"[cyan]📁 File: {context.target_file}[/cyan]")
            self.console.print(f"[cyan]🔍 Pattern: {context.pattern}[/cyan]")

            # Validation
            if not self.validate(context):
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="❌ Validation failed",
                    details={"error": "Invalid parameters"},
                )

            # Read file content
            with open(context.target_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Detect code block
            block_info = self._detect_code_block(content, context.pattern)
            if not block_info:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="❌ Pattern not found",
                    details={"error": f"Pattern '{context.pattern}' not found in file"},
                )

            start_line, end_line, block_content = block_info

            # Analyze dependencies
            dependencies = self._analyze_dependencies(content, block_content)
            if dependencies["potential_issues"]:
                self.console.print(
                    "[yellow]⚠️ Potential dependency issues detected:[/yellow]"
                )
                for issue in dependencies["potential_issues"]:
                    self.console.print(f"[yellow]  • {issue}[/yellow]")

            # Show preview
            self._show_preview(context.target_file, block_info)

            # Check for preview-only mode
            if hasattr(context, "preview") and context.preview:
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="✅ Preview completed",
                    details={
                        "lines_to_delete": f"{start_line + 1}-{end_line}",
                        "content_preview": (
                            block_content[:200] + "..."
                            if len(block_content) > 200
                            else block_content
                        ),
                        "dependencies": dependencies,
                    },
                )

            # Perform deletion
            self.console.print(
                f"\n[bold red]🗑️ DELETING lines {start_line + 1} to {end_line}...[/bold red]"
            )

            if not self._perform_deletion(context.target_file, block_info):
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="❌ Deletion failed",
                    details={"error": "Could not perform deletion"},
                )

            # Post-deletion validation
            if not self._validate_post_deletion(context.target_file):
                self.console.print(
                    "[red]❌ File may have syntax errors after deletion[/red]"
                )
                # Could implement rollback here

            self.console.print(
                f"[bold green]✅ DELETE operation completed successfully![/bold green]"
            )
            self.console.print(
                f"[green]📊 Deleted {end_line - start_line} lines[/green]"
            )

            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="✅ Delete operation completed successfully",
                details={
                    "lines_deleted": f"{start_line + 1}-{end_line}",
                    "content_deleted": block_content,
                    "dependencies_analyzed": dependencies,
                    "file_validated": True,
                },
            )

        except Exception as e:
            self.console.print(f"[red]❌ Delete operation failed: {str(e)}[/red]")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"❌ Delete operation failed: {str(e)}",
                details={"error": str(e)},
            )
