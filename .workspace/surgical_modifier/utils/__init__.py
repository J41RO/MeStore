"""
Surgical Modifier v6.0 - Utils Module
"""

from .logger import logger
from .path_resolver import path_resolver

__all__ = ["logger", "path_resolver"]

# Plugin system (future)
from .plugin_system import plugin_manager

__all__.append("plugin_manager")

# Progress manager
from .progress_manager import progress_manager

__all__.append("progress_manager")
# Diff visualizer
from .diff_visualizer import diff_visualizer

__all__.append("diff_visualizer")

# File finder utilities
from .file_finder import find_files, get_file_finder, search_content, smart_search

__all__.extend(["get_file_finder", "find_files", "search_content", "smart_search"])

# Content handler extremo
from .content_handler import content_handler, ContentType, ContentValidationResult

# Template engine inteligente  
from .template_engine import template_engine

__all__.extend(['content_handler', 'ContentType', 'ContentValidationResult', 'template_engine'])

# Project context
from .project_context import project_context, ProjectMetadata, FrameworkInfo

__all__.extend(['project_context', 'ProjectMetadata', 'FrameworkInfo'])

# Integration preparation
from .integration_preparation import integration_preparation, GitInfo, CiCdInfo

__all__.extend(['integration_preparation', 'GitInfo', 'CiCdInfo'])
