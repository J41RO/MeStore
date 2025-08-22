#!/usr/bin/env python3
"""
Entry point for the 'made' command - Surgical Modifier v6.0
"""
import sys
import os

# Add current directory to path to import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for the made command"""
    try:
        # Import and run the CLI directly
        from cli import main as cli_main
        cli_main()
    except ImportError:
        try:
            # Fallback: try importing from __main__
            import __main__
            if hasattr(__main__, 'main'):
                __main__.main()
            else:
                print("Error: Cannot find main function")
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
