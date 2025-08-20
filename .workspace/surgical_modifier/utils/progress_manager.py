"""
Surgical Modifier v6.0 - Progress Management System
Advanced progress tracking for long operations
"""

import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

try:
    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import (
        BarColumn,
        FileSizeColumn,
        MofNCompleteColumn,
        Progress,
        SpinnerColumn,
        TaskProgressColumn,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
        TransferSpeedColumn,
    )
    from rich.table import Table

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class ProgressManager:
    """
    Advanced progress management for complex operations
    """

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.active_progresses = {}
        self.operation_stats = {}

    @contextmanager
    def operation_progress(
        self, operation_name: str, total_steps: int, description: str = ""
    ):
        """
        Context manager for operation progress tracking
        """
        if not RICH_AVAILABLE:
            print(f"PROGRESS: {operation_name} starting ({total_steps} steps)")
            yield DummyProgressTracker(operation_name, total_steps)
            print(f"PROGRESS: {operation_name} completed")
            return

        # Create rich progress
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=self.console,
        )

        with progress:
            task_id = progress.add_task(
                description or operation_name, total=total_steps
            )

            tracker = RichProgressTracker(progress, task_id, operation_name)
            self.active_progresses[operation_name] = tracker

            start_time = time.time()
            try:
                yield tracker
            finally:
                end_time = time.time()
                self.operation_stats[operation_name] = {
                    "duration": end_time - start_time,
                    "steps": total_steps,
                    "completed": tracker.completed_steps,
                }
                if operation_name in self.active_progresses:
                    del self.active_progresses[operation_name]


class RichProgressTracker:
    """Rich progress tracker for individual operations"""

    def __init__(self, progress: Progress, task_id: int, name: str):
        self.progress = progress
        self.task_id = task_id
        self.name = name
        self.completed_steps = 0

    def step(self, description: str = "", advance: int = 1):
        """Advance progress by one or more steps"""
        self.progress.update(self.task_id, advance=advance, description=description)
        self.completed_steps += advance

    def set_description(self, description: str):
        """Update the task description"""
        self.progress.update(self.task_id, description=description)

    def complete(self):
        """Mark task as completed"""
        self.progress.update(self.task_id, completed=True)


class DummyProgressTracker:
    """Dummy progress tracker when Rich is not available"""

    def __init__(self, name: str, total: int):
        self.name = name
        self.total = total
        self.current = 0
        self.completed_steps = 0

    def step(self, description: str = "", advance: int = 1):
        self.current += advance
        self.completed_steps += advance
        print(f"PROGRESS: {self.name} ({self.current}/{self.total}) - {description}")

    def set_description(self, description: str):
        print(f"PROGRESS: {self.name} - {description}")

    def complete(self):
        print(f"PROGRESS COMPLETE: {self.name}")


# Global progress manager
progress_manager = ProgressManager()
