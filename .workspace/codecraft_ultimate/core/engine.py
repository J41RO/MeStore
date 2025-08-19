"""
🚀 CodeCraft Ultimate v6.0 - Core Engine
Advanced AI-Human collaborative development engine
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict

from .command_parser import CommandParser
from .output_formatter import OutputFormatter
from .plugin_system import PluginSystem
from .models import OperationResult, ExecutionContext
# Temporarily comment out missing modules to test basic functionality
# from ..ai_integration.context_manager import ContextManager
# from ..analyzers.universal_analyzer import UniversalAnalyzer


class CodeCraftEngine:
    """Main engine for CodeCraft Ultimate v6.0"""
    
    def __init__(
        self, 
        verbose: bool = False,
        output_format: str = 'structured',
        config_path: Optional[str] = None,
        plugin_dir: Optional[str] = None
    ):
        self.verbose = verbose
        self.output_format = output_format
        self.config = self._load_config(config_path)
        self.session_id = self._generate_session_id()
        
        # Initialize components
        self.command_parser = CommandParser()
        self.output_formatter = OutputFormatter(output_format)
        self.plugin_system = PluginSystem(plugin_dir)
        # self.context_manager = ContextManager()
        # self.analyzer = UniversalAnalyzer()
        
        # Setup logging
        self._setup_logging()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"CodeCraft Engine v6.0 initialized (session: {self.session_id})")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or defaults"""
        default_config = {
            'general': {
                'output_format': 'structured',
                'backup_enabled': True,
                'verbose': False
            },
            'analysis': {
                'complexity_threshold': 10,
                'security_level': 'medium',
                'include_metrics': True
            },
            'generation': {
                'default_test_framework': 'pytest',
                'template_directory': './templates',
                'auto_format': True
            },
            'ai_integration': {
                'enable_suggestions': True,
                'context_window': 1000,
                'max_suggestions': 3
            },
            'operations': {
                'create_backups': True,
                'verify_syntax': True,
                'run_tests': False
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                import toml
                with open(config_path, 'r') as f:
                    file_config = toml.load(f)
                # Merge configurations (file overrides defaults)
                self._deep_merge(default_config, file_config)
            except Exception as e:
                self.logger.warning(f"Could not load config from {config_path}: {e}")
        
        return default_config
    
    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """Deep merge configuration dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"cc_{int(time.time() * 1000)}"
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('.codecraft.log'),
                logging.StreamHandler() if self.verbose else logging.NullHandler()
            ]
        )
    
    def execute_command(self, args) -> OperationResult:
        """Execute a command with full context and analysis"""
        start_time = time.time()
        
        try:
            # Create execution context
            context = ExecutionContext(
                project_root=self._find_project_root(),
                current_file=getattr(args, 'file', None),
                backup_enabled=self.config.get('operations', {}).get('create_backups', True),
                verbose=self.verbose,
                output_format=self.output_format,
                session_id=self.session_id
            )
            
            # Analyze project context (temporarily disabled)
            # project_context = self.context_manager.analyze_project_context(context.project_root)
            
            # Handle command routing
            if args.command == 'surgical':
                return self._handle_surgical_operations(context)
            elif args.command in ['analyze-complexity', 'find-dependencies', 'detect-patterns', 
                                'security-scan', 'project-health']:
                return self._handle_analysis_operations(context)
            elif args.command in ['generate-component', 'generate-api', 'generate-tests', 
                                'scaffold-project']:
                return self._handle_generation_operations(context)
            elif args.command in ['modernize-syntax', 'optimize-imports', 'apply-patterns']:
                return self._handle_refactoring_operations(context)
            elif args.command in ['find-bugs', 'diagnose-error', 'suggest-fixes']:
                return self._handle_debugging_operations(context)
            elif args.command in ['optimize-performance', 'bundle-analysis']:
                return self._handle_optimization_operations(context)
            else:
                return OperationResult(
                    success=False,
                    operation=args.command,
                    message=f"Unknown command: {args.command}",
                    errors=[f"Command '{args.command}' is not supported"]
                )
        
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                operation=getattr(args, 'command', 'unknown'),
                message=f"Execution failed: {str(e)}",
                errors=[str(e)]
            )
        
        finally:
            execution_time = time.time() - start_time
            self.logger.info(f"Command {args.command} completed in {execution_time:.2f}s")
    
    def _handle_surgical_operations(self, context: ExecutionContext) -> OperationResult:
        """Handle surgical operations (enhanced from v5.3)"""
        from ..operations.surgical.surgical_operations import SurgicalOperations
        
        surgical_ops = SurgicalOperations(context, self.config)
        return surgical_ops.execute(context.args.surgical_op, context.args)
    
    def _handle_analysis_operations(self, context: ExecutionContext) -> OperationResult:
        """Handle analysis operations"""
        from ..operations.analysis.analysis_operations import AnalysisOperations
        
        analysis_ops = AnalysisOperations(context, self.config)
        return analysis_ops.execute(context.command, context.args)
    
    def _handle_generation_operations(self, context: ExecutionContext) -> OperationResult:
        """Handle code generation operations"""
        from ..operations.generation.generation_operations import GenerationOperations
        
        generation_ops = GenerationOperations(context, self.config)
        return generation_ops.execute(context.command, context.args)
    
    def _handle_refactoring_operations(self, context: ExecutionContext) -> OperationResult:
        """Handle refactoring operations"""
        from ..operations.refactoring.refactoring_operations import RefactoringOperations
        
        refactoring_ops = RefactoringOperations(context, self.config)
        return refactoring_ops.execute(context.command, context.args)
    
    def _handle_debugging_operations(self, context: ExecutionContext) -> OperationResult:
        """Handle debugging operations"""
        from ..operations.debugging.debugging_operations import DebuggingOperations
        
        debugging_ops = DebuggingOperations(context, self.config)
        return debugging_ops.execute(context.command, context.args)
    
    def _handle_optimization_operations(self, context: ExecutionContext) -> OperationResult:
        """Handle optimization operations"""
        from ..operations.optimization.optimization_operations import OptimizationOperations
        
        optimization_ops = OptimizationOperations(context, self.config)
        return optimization_ops.execute(context.command, context.args)
    
    def _find_project_root(self) -> str:
        """Find project root directory"""
        current = Path.cwd()
        
        # Project root indicators
        indicators = [
            'package.json', 'pyproject.toml', 'Cargo.toml', 'pom.xml', 
            'go.mod', 'composer.json', 'Gemfile', '.git', '.codecraft.toml'
        ]
        
        for parent in [current] + list(current.parents):
            if any((parent / indicator).exists() for indicator in indicators):
                return str(parent)
        
        return str(current)
    
    def get_context_info(self) -> Dict[str, Any]:
        """Get current context information"""
        project_root = self._find_project_root()
        # project_context = self.context_manager.analyze_project_context(project_root)
        
        return {
            'session_id': self.session_id,
            'project_root': project_root,
            'current_dir': os.getcwd(),
            # 'project_context': project_context,
            'config': self.config,
            'timestamp': datetime.now().isoformat()
        }
    
    def validate_operation(self, operation: str, args: Any) -> List[str]:
        """Validate operation before execution"""
        warnings = []
        
        # Check if files exist
        if hasattr(args, 'file') and args.file:
            if not os.path.exists(args.file) and operation not in ['create', 'scaffold-project']:
                warnings.append(f"Target file does not exist: {args.file}")
        
        # Check if directories exist
        if hasattr(args, 'directory') and args.directory:
            if not os.path.isdir(args.directory):
                warnings.append(f"Target directory does not exist: {args.directory}")
        
        # Validate patterns for surgical operations
        if hasattr(args, 'pattern') and args.pattern and hasattr(args, 'file'):
            if os.path.exists(args.file):
                try:
                    with open(args.file, 'r') as f:
                        content = f.read()
                    if args.pattern not in content:
                        warnings.append(f"Pattern not found in file: {args.pattern}")
                except Exception as e:
                    warnings.append(f"Could not validate pattern: {e}")
        
        return warnings