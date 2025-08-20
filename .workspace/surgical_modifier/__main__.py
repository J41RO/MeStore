#!/usr/bin/env python3
"""
Surgical Modifier v6.0 - Entry Point
Global command: made
"""

import sys
import os

# Add current directory to path for development
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import main

if __name__ == "__main__":
    main()
