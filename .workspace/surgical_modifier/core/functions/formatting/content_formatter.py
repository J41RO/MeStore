#!/usr/bin/env python3
"""
Content formatting functions for Google Code Style
Extracted from create.py for modular architecture
"""
import os

def apply_google_format(content: str, file_extension: str) -> str:
    """Apply Google Code Style formatting based on file type"""
    if file_extension == ".py":
        return format_python_google_style(content)
    elif file_extension in [".js", ".ts", ".jsx", ".tsx"]:
        return format_javascript_google_style(content)
    elif file_extension in [".html", ".htm"]:
        return format_html_google_style(content)
    elif file_extension in [".css", ".scss"]:
        return format_css_google_style(content)
    return content

def format_python_google_style(content: str) -> str:
    """Apply Google Style Guide for Python"""
    lines = content.split("\n")
    formatted_lines = []
    for line in lines:
        formatted_line = line.expandtabs(4)
        formatted_line = formatted_line.rstrip()
        formatted_lines.append(formatted_line)
    return "\n".join(formatted_lines)

def format_javascript_google_style(content: str) -> str:
    """Apply Google Style Guide for JavaScript/TypeScript"""
    lines = content.split("\n")
    formatted_lines = []
    for line in lines:
        formatted_line = line.expandtabs(2)
        formatted_line = formatted_line.rstrip()
        formatted_lines.append(formatted_line)
    return "\n".join(formatted_lines)

def format_html_google_style(content: str) -> str:
    """Apply Google Style Guide for HTML"""
    lines = content.split("\n")
    formatted_lines = []
    for line in lines:
        formatted_line = line.expandtabs(2)
        formatted_line = formatted_line.rstrip()
        formatted_lines.append(formatted_line)
    return "\n".join(formatted_lines)

def format_css_google_style(content: str) -> str:
    """Apply Google Style Guide for CSS"""
    lines = content.split("\n")
    formatted_lines = []
    for line in lines:
        formatted_line = line.expandtabs(2)
        formatted_line = formatted_line.rstrip()
        formatted_lines.append(formatted_line)
    return "\n".join(formatted_lines)

def get_file_extension(file_path: str) -> str:
    """Extract file extension from path"""
    return os.path.splitext(file_path)[1].lower()