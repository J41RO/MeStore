"""
🚀 CodeCraft Ultimate v6.0 - Output Formatter
Structured output formatting for AI integration
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax
from rich.progress import Progress
from rich.text import Text

from .models import OperationResult


class OutputFormatter:
    """Advanced output formatter for different output modes"""
    
    def __init__(self, format_type: str = 'structured'):
        self.format_type = format_type
        self.console = Console()
    
    def format_result(self, result: OperationResult) -> str:
        """Format operation result based on output type"""
        # Add timestamp if not present
        if not result.timestamp:
            result.timestamp = datetime.now().isoformat()
        
        if self.format_type == 'json':
            return self._format_json(result)
        elif self.format_type == 'text':
            return self._format_text(result)
        else:  # structured
            return self._format_structured(result)
    
    def _format_json(self, result: OperationResult) -> str:
        """Format as JSON for AI consumption"""
        # Create comprehensive JSON structure
        json_output = {
            "operation": result.operation,
            "status": "success" if result.success else "error",
            "timestamp": result.timestamp,
            "execution_time": result.execution_time,
            "message": result.message
        }
        
        # Add data if present
        if result.data:
            json_output.update(result.data)
        
        # Add context information
        if result.context:
            json_output["context"] = result.context
        
        # Add suggestions for next steps
        if result.suggestions:
            json_output["next_suggestions"] = result.suggestions
        
        # Add warnings and errors
        if result.warnings:
            json_output["warnings"] = result.warnings
        
        if result.errors:
            json_output["errors"] = result.errors
        
        return json.dumps(json_output, indent=2, ensure_ascii=False)
    
    def _format_text(self, result: OperationResult) -> str:
        """Format as plain text"""
        lines = []
        
        # Status header
        status_icon = "✅" if result.success else "❌"
        lines.append(f"{status_icon} {result.operation.upper()}: {result.message}")
        
        # Timestamp and execution time
        if result.timestamp:
            lines.append(f"⏰ Executed at: {result.timestamp}")
        
        if result.execution_time:
            lines.append(f"⚡ Completed in: {result.execution_time:.2f}s")
        
        # Data section
        if result.data:
            lines.append("\n📊 RESULTS:")
            for key, value in result.data.items():
                if isinstance(value, (list, dict)):
                    lines.append(f"   {key}: {json.dumps(value, indent=2)}")
                else:
                    lines.append(f"   {key}: {value}")
        
        # Context information
        if result.context:
            lines.append("\n🎯 CONTEXT:")
            for key, value in result.context.items():
                lines.append(f"   {key}: {value}")
        
        # Suggestions
        if result.suggestions:
            lines.append("\n💡 NEXT SUGGESTIONS:")
            for i, suggestion in enumerate(result.suggestions, 1):
                lines.append(f"   {i}. {suggestion}")
        
        # Warnings
        if result.warnings:
            lines.append("\n⚠️ WARNINGS:")
            for warning in result.warnings:
                lines.append(f"   - {warning}")
        
        # Errors
        if result.errors:
            lines.append("\n❌ ERRORS:")
            for error in result.errors:
                lines.append(f"   - {error}")
        
        return "\n".join(lines)
    
    def _format_structured(self, result: OperationResult) -> str:
        """Format with rich formatting for human readability"""
        # Capture output to string
        with self.console.capture() as capture:
            self._render_structured(result)
        
        return capture.get()
    
    def _render_structured(self, result: OperationResult):
        """Render structured output with rich formatting"""
        # Main status panel
        status_color = "green" if result.success else "red"
        status_icon = "✅" if result.success else "❌"
        
        title = f"{status_icon} CodeCraft v6.0 - {result.operation.upper()}"
        
        # Create main panel content
        main_content = []
        main_content.append(f"[bold]{result.message}[/bold]")
        
        if result.timestamp:
            main_content.append(f"⏰ {result.timestamp}")
        
        if result.execution_time:
            main_content.append(f"⚡ Completed in {result.execution_time:.2f}s")
        
        main_panel = Panel(
            "\n".join(main_content),
            title=title,
            border_style=status_color,
            padding=(1, 2)
        )
        
        self.console.print(main_panel)
        
        # Data section with tables
        if result.data:
            self._render_data_section(result.data)
        
        # Context information
        if result.context:
            self._render_context_section(result.context)
        
        # Suggestions
        if result.suggestions:
            self._render_suggestions_section(result.suggestions)
        
        # Warnings and errors
        if result.warnings or result.errors:
            self._render_issues_section(result.warnings, result.errors)
    
    def _render_data_section(self, data: Dict[str, Any]):
        """Render data section with tables and syntax highlighting"""
        self.console.print("\n📊 [bold cyan]RESULTS[/bold cyan]")
        
        for key, value in data.items():
            if isinstance(value, dict) and len(value) > 3:
                # Render as table for complex data
                table = Table(title=key.replace('_', ' ').title())
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="white")
                
                for k, v in value.items():
                    table.add_row(str(k), str(v))
                
                self.console.print(table)
            
            elif isinstance(value, list) and len(value) > 0:
                # Render as list
                self.console.print(f"\n[bold cyan]{key.replace('_', ' ').title()}:[/bold cyan]")
                for i, item in enumerate(value[:10], 1):  # Limit to 10 items
                    self.console.print(f"  {i}. {item}")
                
                if len(value) > 10:
                    self.console.print(f"  ... and {len(value) - 10} more items")
            
            elif isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                # Try to render as syntax-highlighted JSON
                try:
                    parsed = json.loads(value)
                    syntax = Syntax(json.dumps(parsed, indent=2), "json", theme="monokai")
                    panel = Panel(syntax, title=key.replace('_', ' ').title())
                    self.console.print(panel)
                except:
                    self.console.print(f"[cyan]{key}:[/cyan] {value}")
            
            else:
                # Simple key-value display
                self.console.print(f"[cyan]{key.replace('_', ' ').title()}:[/cyan] {value}")
    
    def _render_context_section(self, context: Dict[str, Any]):
        """Render context information as a tree"""
        self.console.print("\n🎯 [bold magenta]CONTEXT[/bold magenta]")
        
        tree = Tree("Project Context")
        
        for key, value in context.items():
            if isinstance(value, dict):
                branch = tree.add(f"[bold]{key.replace('_', ' ').title()}[/bold]")
                for k, v in value.items():
                    branch.add(f"{k}: [green]{v}[/green]")
            elif isinstance(value, list):
                branch = tree.add(f"[bold]{key.replace('_', ' ').title()}[/bold]")
                for item in value[:5]:  # Show first 5 items
                    branch.add(f"[green]{item}[/green]")
                if len(value) > 5:
                    branch.add(f"... and {len(value) - 5} more")
            else:
                tree.add(f"[bold]{key.replace('_', ' ').title()}:[/bold] [green]{value}[/green]")
        
        self.console.print(tree)
    
    def _render_suggestions_section(self, suggestions: List[str]):
        """Render suggestions as a formatted list"""
        self.console.print("\n💡 [bold yellow]NEXT SUGGESTIONS[/bold yellow]")
        
        for i, suggestion in enumerate(suggestions, 1):
            # Parse command suggestions to highlight them
            if suggestion.startswith('codecraft'):
                # Highlight the command
                parts = suggestion.split(' ', 1)
                command = f"[bold green]{parts[0]}[/bold green]"
                rest = f" {parts[1]}" if len(parts) > 1 else ""
                suggestion_text = f"{command}{rest}"
            else:
                suggestion_text = suggestion
            
            self.console.print(f"  {i}. {suggestion_text}")
    
    def _render_issues_section(self, warnings: Optional[List[str]], errors: Optional[List[str]]):
        """Render warnings and errors"""
        if warnings:
            self.console.print("\n⚠️ [bold yellow]WARNINGS[/bold yellow]")
            for warning in warnings:
                self.console.print(f"  • [yellow]{warning}[/yellow]")
        
        if errors:
            self.console.print("\n❌ [bold red]ERRORS[/bold red]") 
            for error in errors:
                self.console.print(f"  • [red]{error}[/red]")
    
    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()
    
    def format_progress(self, operation: str, current: int, total: int) -> None:
        """Show progress for long-running operations"""
        if self.format_type != 'structured':
            return
        
        with Progress() as progress:
            task = progress.add_task(f"[cyan]{operation}...", total=total)
            progress.update(task, completed=current)
    
    def format_diff(self, before: str, after: str, file_path: str = "") -> str:
        """Format code differences"""
        if self.format_type == 'json':
            return json.dumps({
                "type": "diff",
                "file_path": file_path,
                "before": before,
                "after": after
            }, indent=2)
        
        # For structured and text output, show side-by-side diff
        before_lines = before.split('\n')
        after_lines = after.split('\n')
        
        output = []
        if file_path:
            output.append(f"📝 Changes in {file_path}")
            output.append("=" * 50)
        
        max_lines = max(len(before_lines), len(after_lines))
        
        for i in range(max_lines):
            before_line = before_lines[i] if i < len(before_lines) else ""
            after_line = after_lines[i] if i < len(after_lines) else ""
            
            if before_line != after_line:
                output.append(f"- {before_line}")
                output.append(f"+ {after_line}")
            else:
                output.append(f"  {before_line}")
        
        return "\n".join(output)