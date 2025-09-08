"""
File Explorer Module for CLI Analysis
Provides functionality to read and explore files with line-based operations.
"""

import os
from typing import List, Optional, Tuple


class FileExplorer:
    """
    Handles file exploration operations including line-based reading,
    range extraction, and context-aware content display.
    """
    
    def __init__(self):
        """Initialize FileExplorer instance."""
        pass
    
    def read_file_lines(self, file_path: str) -> List[str]:
        """
        Read file and return list of lines.
        
        Args:
            file_path (str): Path to the file to read
            
        Returns:
            List[str]: List of lines from the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file can't be read
            UnicodeDecodeError: If file encoding is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                # Keep newlines for proper formatting
                return lines
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {file_path}")
        except UnicodeDecodeError as e:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    lines = file.readlines()
                    return lines
            except Exception:
                raise UnicodeDecodeError(f"Unable to decode file: {file_path}. Error: {e}")
    
    def get_lines_range(self, lines: List[str], start: int, end: int) -> List[str]:
        """
        Extract specific range of lines.
        
        Args:
            lines (List[str]): List of all lines
            start (int): Starting line number (1-based)
            end (int): Ending line number (1-based, inclusive)
            
        Returns:
            List[str]: Lines in the specified range
            
        Raises:
            ValueError: If range is invalid
        """
        if start < 1:
            raise ValueError("Start line must be >= 1")
            
        if end < start:
            raise ValueError("End line must be >= start line")
            
        total_lines = len(lines)
        if start > total_lines:
            raise ValueError(f"Start line {start} exceeds file length {total_lines}")
            
        # Convert to 0-based indexing and handle end bounds
        start_idx = start - 1
        end_idx = min(end, total_lines)  # end is inclusive, but list slicing is exclusive
        
        return lines[start_idx:end_idx]
    
    def get_context_around(self, lines: List[str], line_number: int, context: int) -> Tuple[List[str], int]:
        """
        Get lines around a specific line number with context.
        
        Args:
            lines (List[str]): List of all lines
            line_number (int): Central line number (1-based)
            context (int): Number of lines before and after
            
        Returns:
            Tuple[List[str], int]: (context_lines, actual_start_line_number)
            
        Raises:
            ValueError: If line_number is invalid
        """
        total_lines = len(lines)
        
        if line_number < 1 or line_number > total_lines:
            raise ValueError(f"Line number {line_number} is out of range (1-{total_lines})")
            
        if context < 0:
            raise ValueError("Context must be non-negative")
            
        # Calculate range with bounds checking
        start_line = max(1, line_number - context)
        end_line = min(total_lines, line_number + context)
        
        # Extract the range
        context_lines = self.get_lines_range(lines, start_line, end_line)
        
        return context_lines, start_line
    
    def format_output(self, lines: List[str], start_line: int = 1, highlight_line: Optional[int] = None) -> str:
        """
        Format lines with line numbers for display.
        
        Args:
            lines (List[str]): Lines to format
            start_line (int): Starting line number for numbering
            highlight_line (Optional[int]): Line number to highlight (1-based from start_line)
            
        Returns:
            str: Formatted output with line numbers
        """
        if not lines:
            return "No lines to display."
            
        # Calculate width for line number padding
        max_line_num = start_line + len(lines) - 1
        width = len(str(max_line_num))
        
        formatted_lines = []
        for i, line in enumerate(lines):
            line_num = start_line + i
            # Remove trailing newline for consistent formatting
            clean_line = line.rstrip('\n\r')
            
            # Add highlighting if specified
            prefix = "→" if highlight_line and line_num == highlight_line else " "
            
            formatted_line = f"{prefix}{line_num:>{width}}: {clean_line}"
            formatted_lines.append(formatted_line)
        
        return "\n".join(formatted_lines)
    
    def parse_lines_range(self, lines_str: str) -> Tuple[int, int]:
        """
        Parse lines range string in format "start:end".
        
        Args:
            lines_str (str): Range string like "10:20"
            
        Returns:
            Tuple[int, int]: (start, end) line numbers
            
        Raises:
            ValueError: If format is invalid
        """
        if ':' not in lines_str:
            raise ValueError("Lines range must be in format 'start:end'")
            
        try:
            parts = lines_str.split(':')
            if len(parts) != 2:
                raise ValueError("Lines range must be in format 'start:end'")
                
            start = int(parts[0].strip())
            end = int(parts[1].strip())
            
            if start < 1 or end < 1:
                raise ValueError("Line numbers must be positive")
                
            return start, end
            
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError("Line numbers must be integers")
            raise