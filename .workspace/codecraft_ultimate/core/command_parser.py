"""
🚀 CodeCraft Ultimate v6.0 - Command Parser
Intelligent command parsing and validation
"""

import re
import shlex
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    """Parsed command structure"""
    operation: str
    primary_args: List[str]
    options: Dict[str, Any]
    flags: List[str]
    raw_command: str


class CommandParser:
    """Advanced command parser for CodeCraft operations"""
    
    def __init__(self):
        self.command_patterns = self._initialize_patterns()
        self.operation_aliases = self._initialize_aliases()
    
    def _initialize_patterns(self) -> Dict[str, str]:
        """Initialize regex patterns for command parsing"""
        return {
            'file_path': r'([^\s]+\.(?:py|js|ts|tsx|jsx|java|cpp|c|cs|php|rb|go|rs|html|css|json|yaml|yml|md))',
            'line_numbers': r'(\d+)(?:\s+(\d+))?',
            'quoted_string': r'"([^"]*?)"|\'([^\']*?)\'',
            'option_flag': r'--?([a-zA-Z0-9-_]+)(?:=([^\s]+)|\s+([^\s-][^\s]*))?',
            'pattern_match': r'(?:"([^"]+)"|\'([^\']+)\'|(\S+))'
        }
    
    def _initialize_aliases(self) -> Dict[str, str]:
        """Initialize command aliases"""
        return {
            # Surgical operation aliases
            'c': 'create',
            'r': 'replace', 
            'a': 'after',
            'b': 'before',
            'app': 'append',
            'd': 'delete',
            
            # Analysis aliases
            'complexity': 'analyze-complexity',
            'deps': 'find-dependencies',
            'security': 'security-scan',
            'health': 'project-health',
            
            # Generation aliases
            'gen-comp': 'generate-component',
            'gen-api': 'generate-api',
            'gen-tests': 'generate-tests',
            'scaffold': 'scaffold-project',
            
            # Refactoring aliases
            'modernize': 'modernize-syntax',
            'opt-imports': 'optimize-imports',
            'patterns': 'apply-patterns',
            
            # Debugging aliases
            'bugs': 'find-bugs',
            'diagnose': 'diagnose-error',
            'fix': 'suggest-fixes',
            
            # Optimization aliases
            'perf': 'optimize-performance',
            'bundle': 'bundle-analysis'
        }
    
    def parse_command(self, command_line: str) -> ParsedCommand:
        """Parse a command line into structured components"""
        # Tokenize the command line
        try:
            tokens = shlex.split(command_line)
        except ValueError:
            # Fallback for complex quoting issues
            tokens = command_line.split()
        
        if not tokens:
            return ParsedCommand('', [], {}, [], command_line)
        
        # Extract operation (first token, resolve aliases)
        operation = tokens[0].lower()
        operation = self.operation_aliases.get(operation, operation)
        
        # Parse remaining tokens
        args = []
        options = {}
        flags = []
        
        i = 1
        while i < len(tokens):
            token = tokens[i]
            
            if token.startswith('--'):
                # Long option
                if '=' in token:
                    key, value = token[2:].split('=', 1)
                    options[key] = self._parse_value(value)
                else:
                    key = token[2:]
                    # Check if next token is a value
                    if i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                        options[key] = self._parse_value(tokens[i + 1])
                        i += 1
                    else:
                        flags.append(key)
            
            elif token.startswith('-') and len(token) > 1:
                # Short option(s)
                if len(token) == 2:
                    # Single short option
                    key = token[1]
                    if i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                        options[key] = self._parse_value(tokens[i + 1])
                        i += 1
                    else:
                        flags.append(key)
                else:
                    # Multiple short flags
                    for char in token[1:]:
                        flags.append(char)
            
            else:
                # Regular argument
                args.append(token)
            
            i += 1
        
        return ParsedCommand(operation, args, options, flags, command_line)
    
    def _parse_value(self, value: str) -> Any:
        """Parse a string value to appropriate type"""
        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Try to parse as boolean
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Return as string
        return value
    
    def validate_surgical_command(self, parsed: ParsedCommand) -> Tuple[bool, List[str]]:
        """Validate surgical operation commands"""
        errors = []
        
        surgical_ops = ['create', 'replace', 'after', 'before', 'append', 'delete',
                       'extract-method', 'extract-class', 'rename-symbol']
        
        if parsed.operation not in surgical_ops:
            return True, []  # Not a surgical operation
        
        # Basic surgical operations need file and pattern
        basic_ops = ['create', 'replace', 'after', 'before', 'append', 'delete']
        
        if parsed.operation in basic_ops:
            if len(parsed.primary_args) < 2:
                errors.append(f"Operation '{parsed.operation}' requires at least file and pattern arguments")
            
            if parsed.operation != 'delete' and len(parsed.primary_args) < 3:
                errors.append(f"Operation '{parsed.operation}' requires content argument")
        
        # Extract method needs specific arguments
        elif parsed.operation == 'extract-method':
            if len(parsed.primary_args) < 4:
                errors.append("extract-method requires: file, start_line, end_line, method_name")
            else:
                try:
                    int(parsed.primary_args[1])  # start_line
                    int(parsed.primary_args[2])  # end_line
                except ValueError:
                    errors.append("extract-method requires numeric line numbers")
        
        # Extract class needs file, pattern, class_name
        elif parsed.operation == 'extract-class':
            if len(parsed.primary_args) < 3:
                errors.append("extract-class requires: file, pattern, class_name")
        
        # Rename symbol needs file, old_name, new_name
        elif parsed.operation == 'rename-symbol':
            if len(parsed.primary_args) < 3:
                errors.append("rename-symbol requires: file, old_name, new_name")
        
        return len(errors) == 0, errors
    
    def validate_analysis_command(self, parsed: ParsedCommand) -> Tuple[bool, List[str]]:
        """Validate analysis operation commands"""
        errors = []
        
        analysis_ops = ['analyze-complexity', 'find-dependencies', 'detect-patterns',
                       'security-scan', 'project-health']
        
        if parsed.operation not in analysis_ops:
            return True, []
        
        # All analysis operations need at least one target
        if len(parsed.primary_args) < 1:
            errors.append(f"Operation '{parsed.operation}' requires a target file or directory")
        
        return len(errors) == 0, errors
    
    def validate_generation_command(self, parsed: ParsedCommand) -> Tuple[bool, List[str]]:
        """Validate generation operation commands"""
        errors = []
        
        generation_ops = ['generate-component', 'generate-api', 'generate-tests', 'scaffold-project']
        
        if parsed.operation not in generation_ops:
            return True, []
        
        if parsed.operation == 'generate-component':
            if len(parsed.primary_args) < 2:
                errors.append("generate-component requires: type, name")
        
        elif parsed.operation == 'generate-api':
            if len(parsed.primary_args) < 1:
                errors.append("generate-api requires: specification")
        
        elif parsed.operation == 'generate-tests':
            if len(parsed.primary_args) < 1:
                errors.append("generate-tests requires: file")
        
        elif parsed.operation == 'scaffold-project':
            if len(parsed.primary_args) < 2:
                errors.append("scaffold-project requires: type, name")
        
        return len(errors) == 0, errors
    
    def suggest_corrections(self, parsed: ParsedCommand) -> List[str]:
        """Suggest corrections for invalid commands"""
        suggestions = []
        
        # Suggest similar commands
        all_commands = list(self.operation_aliases.values()) + list(self.operation_aliases.keys())
        
        for cmd in all_commands:
            if self._similarity_score(parsed.operation, cmd) > 0.6:
                suggestions.append(f"Did you mean '{cmd}'?")
        
        # Suggest common patterns based on arguments
        if len(parsed.primary_args) >= 2:
            file_arg = parsed.primary_args[0]
            if '.' in file_arg:  # Looks like a file
                suggestions.append("For file operations, try: create|replace|after|before file pattern [content]")
        
        return suggestions
    
    def _similarity_score(self, s1: str, s2: str) -> float:
        """Calculate similarity score between two strings"""
        if len(s1) == 0 or len(s2) == 0:
            return 0.0
        
        # Simple character-based similarity
        longer = s2 if len(s2) > len(s1) else s1
        shorter = s1 if len(s1) < len(s2) else s2
        
        if len(longer) == 0:
            return 1.0
        
        matches = sum(1 for i, char in enumerate(shorter) if i < len(longer) and char == longer[i])
        return matches / len(longer)
    
    def extract_file_info(self, args: List[str]) -> Optional[Dict[str, Any]]:
        """Extract file information from arguments"""
        if not args:
            return None
        
        file_path = args[0]
        
        # Check if it looks like a file path
        if '.' in file_path:
            file_ext = file_path.split('.')[-1].lower()
            
            file_types = {
                'py': 'python',
                'js': 'javascript', 
                'jsx': 'javascript',
                'ts': 'typescript',
                'tsx': 'typescript',
                'java': 'java',
                'cpp': 'cpp',
                'c': 'c',
                'cs': 'csharp',
                'php': 'php',
                'rb': 'ruby',
                'go': 'go',
                'rs': 'rust',
                'html': 'markup',
                'css': 'stylesheet',
                'json': 'config',
                'yaml': 'config',
                'yml': 'config'
            }
            
            return {
                'path': file_path,
                'extension': file_ext,
                'type': file_types.get(file_ext, 'unknown'),
                'exists': True  # We'll check this in the engine
            }
        
        return None
    
    def format_command_help(self, operation: str) -> str:
        """Format help text for a specific operation"""
        help_texts = {
            'create': "Create a new file with content\nUsage: codecraft create <file> <content>",
            'replace': "Replace pattern in file\nUsage: codecraft replace <file> <pattern> <new_content>",
            'after': "Insert content after pattern\nUsage: codecraft after <file> <pattern> <content>",
            'before': "Insert content before pattern\nUsage: codecraft before <file> <pattern> <content>",
            'append': "Append content to file\nUsage: codecraft append <file> <content>",
            'delete': "Delete pattern from file\nUsage: codecraft delete <file> <pattern>",
            'extract-method': "Extract method from lines\nUsage: codecraft extract-method <file> <start> <end> <method_name>",
            'analyze-complexity': "Analyze code complexity\nUsage: codecraft analyze-complexity <target> [--format=summary|detailed|json]",
            'generate-component': "Generate component\nUsage: codecraft generate-component <type> <name> [--framework=react|vue|angular]"
        }
        
        return help_texts.get(operation, f"No help available for '{operation}'")