"""
Surgical Modifier v6.0 - Visual Diff System
Advanced diff visualization with syntax highlighting
"""

import difflib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from rich.columns import Columns
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.rule import Rule
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class DiffVisualizer:
    """
    Advanced diff visualization with syntax highlighting
    """

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None

        # Language mapping for syntax highlighting
        self.language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "jsx",
            ".tsx": "tsx",
            ".html": "html",
            ".css": "css",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".php": "php",
            ".rb": "ruby",
            ".go": "go",
            ".rs": "rust",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "bash",
            ".sql": "sql",
            ".json": "json",
            ".xml": "xml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".md": "markdown",
        }

    def detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
        suffix = Path(filename).suffix.lower()
        return self.language_map.get(suffix, "text")

    def show_side_by_side_diff(self, before: str, after: str, filename: str = "file"):
        """Show side-by-side diff with syntax highlighting"""
        if not RICH_AVAILABLE:
            self._show_simple_diff(before, after, filename)
            return

        language = self.detect_language(filename)

        # Create layout for side-by-side comparison
        layout = Layout()
        layout.split_row(Layout(name="before"), Layout(name="after"))

        # Syntax highlighted before
        before_syntax = Syntax(
            before, language, theme="monokai", line_numbers=True, word_wrap=True
        )
        layout["before"].update(
            Panel(before_syntax, title="📄 Before", border_style="red")
        )

        # Syntax highlighted after
        after_syntax = Syntax(
            after, language, theme="monokai", line_numbers=True, word_wrap=True
        )
        layout["after"].update(
            Panel(after_syntax, title="📄 After", border_style="green")
        )

        self.console.print(
            Panel(layout, title=f"🔄 Diff: {filename}", border_style="blue")
        )

    def show_change_summary(self, before: str, after: str, filename: str = "file"):
        """Show summary of changes made"""
        before_lines = before.splitlines()
        after_lines = after.splitlines()

        # Calculate statistics
        stats = {
            "lines_before": len(before_lines),
            "lines_after": len(after_lines),
            "lines_added": 0,
            "lines_removed": 0,
            "lines_modified": 0,
        }

        # Analyze changes
        matcher = difflib.SequenceMatcher(None, before_lines, after_lines)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "delete":
                stats["lines_removed"] += i2 - i1
            elif tag == "insert":
                stats["lines_added"] += j2 - j1
            elif tag == "replace":
                stats["lines_modified"] += max(i2 - i1, j2 - j1)

        if not RICH_AVAILABLE:
            print(f"CHANGE SUMMARY for {filename}:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            return

        # Create summary table
        table = Table(title=f"📊 Change Summary: {filename}")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Count", style="green", justify="right")

        # Add emoji mappings
        emoji_map = {
            "lines_before": "📄",
            "lines_after": "📄",
            "lines_added": "➕",
            "lines_removed": "➖",
            "lines_modified": "🔄",
        }

        for metric, count in stats.items():
            emoji = emoji_map.get(metric, "📊")
            display_name = metric.replace("_", " ").title()

            # Color based on change type
            if "added" in metric:
                style = "green"
            elif "removed" in metric:
                style = "red"
            elif "modified" in metric:
                style = "yellow"
            else:
                style = "white"

            table.add_row(f"{emoji} {display_name}", f"[{style}]{count}[/{style}]")

        self.console.print(Panel(table, border_style="blue"))

    def _show_simple_diff(self, before: str, after: str, filename: str):
        """Simple diff for when Rich is not available"""
        print(f"DIFF: {filename}")
        print("=" * 40)

        before_lines = before.splitlines()
        after_lines = after.splitlines()

        diff = difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm="",
        )

        for line in diff:
            print(line)


# Global diff visualizer
diff_visualizer = DiffVisualizer()
