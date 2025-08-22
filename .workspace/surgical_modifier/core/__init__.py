"""
Surgical Modifier v6.0 - Core Module
Central module for all core functionality
"""

# Operations registry
from .operations_registry import operations_registry

# Argument parser
from .argument_parser import argument_parser

__all__ = ['operations_registry', 'argument_parser']


