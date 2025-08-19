#!/usr/bin/env python3
"""
🚀 CODECRAFT ULTIMATE v6.0 - HERRAMIENTA COLABORATIVA DEFINITIVA
==================================================================
Advanced AI-Human collaborative development tool
"""

import argparse
import sys
import json
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.engine import CodeCraftEngine
from core.command_parser import CommandParser
from core.output_formatter import OutputFormatter
# from ai_integration.context_manager import ContextManager  # Temporarily disabled


def create_parser():
    """Create the main command line parser"""
    parser = argparse.ArgumentParser(
        prog='codecraft',
        description='CodeCraft Ultimate v6.0 - Advanced AI-Human Collaborative Development Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🔧 CODECRAFT ULTIMATE v6.0 - EJEMPLOS DE USO

OPERACIONES QUIRÚRGICAS:
  codecraft create src/components/Button.tsx "export const Button = () => <button>Click</button>"
  codecraft replace src/app.py "def hello()" "def hello_world()"
  codecraft extract-method src/utils.py 10 25 "calculate_sum"

ANÁLISIS DE CÓDIGO:
  codecraft analyze-complexity src/
  codecraft find-dependencies src/main.py
  codecraft security-scan .
  codecraft project-health .

GENERACIÓN DE CÓDIGO:
  codecraft generate-component react Button --framework=react
  codecraft generate-tests src/utils.py --test-framework=pytest
  codecraft scaffold-project web my-app --template=react

REFACTORING:
  codecraft modernize-syntax src/ --target-version=ES2023
  codecraft optimize-imports src/
  codecraft apply-patterns src/ --pattern=singleton

DEBUGGING:
  codecraft find-bugs src/app.py --severity=high
  codecraft diagnose-error error.log
  codecraft suggest-fixes src/app.py "undefined variable"

OPTIMIZACIÓN:
  codecraft optimize-performance src/ --target=speed
  codecraft bundle-analysis . --bundler=webpack

🎯 Para ayuda específica: codecraft <command> --help
        """
    )
    
    # Global options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output with detailed analysis')
    parser.add_argument('--output-format', choices=['json', 'text', 'structured'],
                       default='structured', help='Output format for AI integration')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--plugin-dir', type=str, help='Additional plugin directory')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # ========================================================================
    # SURGICAL OPERATIONS (Enhanced from v5.3)
    # ========================================================================
    surgical_parser = subparsers.add_parser('surgical', help='Surgical operations')
    surgical_subparsers = surgical_parser.add_subparsers(dest='surgical_op')
    
    # Basic surgical operations
    for op in ['create', 'replace', 'after', 'before', 'append', 'delete']:
        op_parser = surgical_subparsers.add_parser(op, help=f'{op.title()} operation')
        op_parser.add_argument('file', help='Target file path')
        op_parser.add_argument('pattern', help='Pattern to match')
        if op != 'delete':
            op_parser.add_argument('content', help='Content to insert/replace')
    
    # Advanced surgical operations  
    extract_method = surgical_subparsers.add_parser('extract-method', help='Extract method refactoring')
    extract_method.add_argument('file', help='Source file')
    extract_method.add_argument('start_line', type=int, help='Start line number')
    extract_method.add_argument('end_line', type=int, help='End line number')
    extract_method.add_argument('method_name', help='New method name')
    
    extract_class = surgical_subparsers.add_parser('extract-class', help='Extract class refactoring')
    extract_class.add_argument('file', help='Source file')
    extract_class.add_argument('pattern', help='Pattern to extract')
    extract_class.add_argument('class_name', help='New class name')
    
    rename_symbol = surgical_subparsers.add_parser('rename-symbol', help='Rename symbol')
    rename_symbol.add_argument('file', help='Source file')
    rename_symbol.add_argument('old_name', help='Current symbol name')
    rename_symbol.add_argument('new_name', help='New symbol name')
    
    # ========================================================================
    # ANALYSIS OPERATIONS
    # ========================================================================
    
    # Complexity analysis
    complexity_parser = subparsers.add_parser('analyze-complexity', help='Analyze code complexity')
    complexity_parser.add_argument('target', help='File or directory to analyze')
    complexity_parser.add_argument('--format', choices=['summary', 'detailed', 'json'], default='summary')
    
    # Dependency analysis
    deps_parser = subparsers.add_parser('find-dependencies', help='Find dependencies')
    deps_parser.add_argument('file', help='File to analyze')
    deps_parser.add_argument('--include-indirect', action='store_true', help='Include indirect dependencies')
    
    # Pattern detection
    patterns_parser = subparsers.add_parser('detect-patterns', help='Detect code patterns')
    patterns_parser.add_argument('target', help='File or directory')
    patterns_parser.add_argument('--pattern-type', choices=['design', 'anti'], default='design')
    
    # Security scan
    security_parser = subparsers.add_parser('security-scan', help='Security vulnerability scan')
    security_parser.add_argument('directory', help='Directory to scan')
    security_parser.add_argument('--severity', choices=['low', 'medium', 'high'], default='medium')
    
    # Project health
    health_parser = subparsers.add_parser('project-health', help='Analyze project health')
    health_parser.add_argument('directory', help='Project directory')
    
    # ========================================================================
    # GENERATION OPERATIONS
    # ========================================================================
    
    # Component generation
    gen_component = subparsers.add_parser('generate-component', help='Generate component')
    gen_component.add_argument('type', choices=['react', 'vue', 'angular', 'generic'])
    gen_component.add_argument('name', help='Component name')
    gen_component.add_argument('--framework', help='Specific framework version')
    gen_component.add_argument('--template', help='Custom template')
    
    # API generation
    gen_api = subparsers.add_parser('generate-api', help='Generate API')
    gen_api.add_argument('specification', help='API specification file')
    gen_api.add_argument('--type', choices=['rest', 'graphql'], default='rest')
    gen_api.add_argument('--output-dir', help='Output directory')
    
    # Test generation
    gen_tests = subparsers.add_parser('generate-tests', help='Generate tests')
    gen_tests.add_argument('file', help='File to generate tests for')
    gen_tests.add_argument('--test-framework', choices=['jest', 'pytest', 'junit'], help='Test framework')
    gen_tests.add_argument('--coverage', type=int, default=80, help='Target coverage percentage')
    
    # Project scaffolding
    scaffold = subparsers.add_parser('scaffold-project', help='Scaffold new project')
    scaffold.add_argument('type', choices=['web', 'api', 'desktop', 'mobile'])
    scaffold.add_argument('name', help='Project name')
    scaffold.add_argument('--template', help='Template to use')
    
    # ========================================================================
    # REFACTORING OPERATIONS
    # ========================================================================
    
    # Modernize syntax
    modernize = subparsers.add_parser('modernize-syntax', help='Modernize code syntax')
    modernize.add_argument('target', help='File or directory')
    modernize.add_argument('--target-version', help='Target language version')
    
    # Optimize imports
    opt_imports = subparsers.add_parser('optimize-imports', help='Optimize imports')
    opt_imports.add_argument('target', help='File or directory')
    opt_imports.add_argument('--remove-unused', action='store_true')
    
    # Apply patterns
    apply_patterns = subparsers.add_parser('apply-patterns', help='Apply design patterns')
    apply_patterns.add_argument('target', help='File or directory')
    apply_patterns.add_argument('--pattern', choices=['singleton', 'factory', 'observer', 'strategy'])
    
    # ========================================================================
    # DEBUGGING OPERATIONS
    # ========================================================================
    
    # Find bugs
    find_bugs = subparsers.add_parser('find-bugs', help='Find potential bugs')
    find_bugs.add_argument('file', help='File to analyze')
    find_bugs.add_argument('--severity', choices=['low', 'medium', 'high'], default='medium')
    
    # Diagnose errors
    diagnose = subparsers.add_parser('diagnose-error', help='Diagnose error from logs')
    diagnose.add_argument('error_log', help='Error log file or error message')
    diagnose.add_argument('--context', help='Additional context files')
    
    # Suggest fixes
    suggest = subparsers.add_parser('suggest-fixes', help='Suggest fixes for issues')
    suggest.add_argument('file', help='File with issues')
    suggest.add_argument('error_description', help='Description of the error')
    
    # ========================================================================
    # OPTIMIZATION OPERATIONS
    # ========================================================================
    
    # Performance optimization
    optimize_perf = subparsers.add_parser('optimize-performance', help='Optimize performance')
    optimize_perf.add_argument('target', help='File or directory')
    optimize_perf.add_argument('--target', choices=['memory', 'speed', 'size'], default='speed')
    
    # Bundle analysis
    bundle_analysis = subparsers.add_parser('bundle-analysis', help='Analyze bundle')
    bundle_analysis.add_argument('project', help='Project directory')
    bundle_analysis.add_argument('--bundler', choices=['webpack', 'vite', 'rollup'])
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    
    # Handle special cases for backward compatibility with surgical_modifier_ultimate.py
    if len(sys.argv) > 1 and sys.argv[1] in ['create', 'replace', 'after', 'before', 'append', 'delete']:
        # Legacy surgical operations - convert to new format
        sys.argv.insert(1, 'surgical')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Initialize the engine
        engine = CodeCraftEngine(
            verbose=args.verbose,
            output_format=args.output_format,
            config_path=getattr(args, 'config', None),
            plugin_dir=getattr(args, 'plugin_dir', None)
        )
        
        # Execute the command
        result = engine.execute_command(args)
        
        # Format and output results
        formatter = OutputFormatter(args.output_format)
        output = formatter.format_result(result)
        
        print(output)
        
        return 0 if result.get('success', True) else 1
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return 1
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'timestamp': formatter.get_timestamp() if 'formatter' in locals() else None
        }
        
        if args.output_format == 'json':
            print(json.dumps(error_result, indent=2))
        else:
            print(f"❌ Error: {e}")
        
        return 1


if __name__ == '__main__':
    sys.exit(main())