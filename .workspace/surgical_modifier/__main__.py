#!/usr/bin/env python3
"""
Surgical Modifier v6.0 - Enhanced Entry Point
Global command: made

Features:
- Robust error handling
- Development vs production mode detection
- Rich error reporting
- Performance monitoring
- Plugin system integration
"""

import sys
import os
import time
from pathlib import Path

# Add current directory to path for development
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Rich imports for error handling
try:
    from rich.console import Console
    from rich.traceback import install as install_rich_tracebacks
    from rich.panel import Panel
    RICH_AVAILABLE = True
    console = Console()
    install_rich_tracebacks(show_locals=False)
except ImportError:
    RICH_AVAILABLE = False
    console = None

def detect_mode():
    """Detect if running in development or production mode"""
    # Development indicators
    dev_indicators = [
        os.path.exists(os.path.join(current_dir, 'setup.py')),
        os.path.exists(os.path.join(current_dir, 'pyproject.toml')),
        '.workspace' in current_dir,
        os.path.basename(current_dir) == 'surgical_modifier'
    ]
    return any(dev_indicators)

def setup_environment():
    """Setup environment and imports"""
    try:
        # Try to import logger
        try:
            from utils.logger import logger
        except ImportError:
            # Create basic logger if utils.logger not available
            import logging
            logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
            logger = logging.getLogger(__name__)
        
        # Try to import plugin manager
        try:
            from utils.plugin_system import plugin_manager
        except ImportError:
            plugin_manager = None
        
        # Log startup info
        is_dev = detect_mode()
        mode = "Development" if is_dev else "Production"
        logger.info(f"🚀 Surgical Modifier v6.0 starting in {mode} mode")
        
        return True, logger, plugin_manager
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"❌ [red]Environment setup failed: {e}[/red]")
        else:
            print(f"ERROR: Environment setup failed: {e}")
        return False, None, None

def main():
    """
    Main entry point with enhanced error handling and monitoring
    """
    start_time = time.time()
    
    try:
        # Setup environment
        success, logger, plugin_manager = setup_environment()
        if not success:
            sys.exit(1)
            
        # Import CLI after environment setup
        from cli import main as cli_main, register_operations
        
        # Register available operations
        register_operations()
        
        # Performance monitoring
        setup_time = time.time() - start_time
        if setup_time > 0.1:  # If startup takes more than 100ms
            logger.warning(f"Slow startup detected: {setup_time:.3f}s")
        
        # Run CLI
        cli_main()
        
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print("\n👋 [yellow]Goodbye![/yellow]")
        else:
            print("\nGoodbye!")
        sys.exit(0)
        
    except ImportError as e:
        error_msg = f"Module import failed: {e}"
        if RICH_AVAILABLE:
            console.print(Panel(
                f"❌ {error_msg}\n\n💡 Try running from the correct directory or installing dependencies",
                title="Import Error",
                border_style="red"
            ))
        else:
            print(f"ERROR: {error_msg}")
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        if RICH_AVAILABLE:
            console.print(Panel(
                f"❌ {error_msg}\n\n🐛 This is likely a bug. Please report it.",
                title="Critical Error",
                border_style="red"
            ))
        else:
            print(f"CRITICAL ERROR: {error_msg}")
        
        # In development mode, show full traceback
        if detect_mode():
            raise
        sys.exit(1)

if __name__ == "__main__":
    main()
