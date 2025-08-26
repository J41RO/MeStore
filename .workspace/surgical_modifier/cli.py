#!/usr/bin/env python3
"""
CLI Modular v6.0 - Sistema de routing dinámico
"""

import sys
import argparse
from typing import Dict, Callable

class ModularCLI:
    def __init__(self):
        self.operations = {}
        self._load_operations()
    
    def _load_operations(self):
        try:
            from core.operations.basic import (
                after_operation, before_operation, create_operation, 
                replace_operation, append_operation
            )
            
            self.operations = {
                'create': create_operation,
                'replace': replace_operation,
                'after': after_operation,
                'before': before_operation,
                'append': append_operation,
            }
        except ImportError as e:
            print(f'Error: {e}')
            sys.exit(1)
    
    def execute_operation(self, operation: str, **kwargs):
        if operation not in self.operations:
            raise ValueError(f'Operation {operation} not found')
        return self.operations[operation](**kwargs)

def main():
    parser = argparse.ArgumentParser(description='CLI Modular v6.0')
    
    cli = ModularCLI()
    operations = list(cli.operations.keys())
    
    parser.add_argument('operation', choices=operations)
    parser.add_argument('file', help='Target file')
    parser.add_argument('pattern', help='Pattern to search')
    parser.add_argument('content', nargs='?', default='', help='Content')
    parser.add_argument('--verbose', action='store_true')
    
    args = parser.parse_args()
    
    try:
        result = cli.execute_operation(
            args.operation,
            file_path=args.file,
            pattern=args.pattern,
            content=args.content
        )
        if args.verbose:
            print(f'Operation completed: {result}')
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
