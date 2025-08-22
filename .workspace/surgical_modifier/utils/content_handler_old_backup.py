"""
Surgical Modifier v6.0 - Extreme Content Handler
Robust content handling with special character escape, templates, and validation
"""

import re
import json
import ast
import shlex
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
from enum import Enum
import textwrap
from dataclasses import dataclass

try:
    from utils.logger import logger
    from utils.path_resolver import path_resolver
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    logger = None
    path_resolver = None

class ContentType(Enum):
    """Content type enumeration for specialized handling"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JSON = "json"
    SQL = "sql"
    REGEX = "regex"
    MULTILINE = "multiline"
    TEMPLATE = "template"
    PLAIN_TEXT = "plain_text"

@dataclass
class ContentValidationResult:
    """Result of content validation"""
    is_valid: bool
    issues: List[str]
    suggestions: List[str]
    content_type: ContentType
    line_count: int
    char_count: int

class ExtremeContentHandler:
    """
    Extreme content handler with advanced features:
    - Robust escape handling for all special characters
    - Incremental mode for large content
    - Framework-specific templates
    - Automatic validation and suggestions
    - Performance optimization
    """
    
    def __init__(self):
        self.escape_patterns = self._initialize_escape_patterns()
        self.framework_templates = self._initialize_framework_templates()
        self.validation_rules = self._initialize_validation_rules()
        self.incremental_threshold = 20  # Lines
        self.performance_stats = {
            'escape_operations': 0,
            'validation_operations': 0,
            'template_operations': 0
        }
    
    def _initialize_escape_patterns(self) -> Dict[str, Dict]:
        """Initialize comprehensive escape patterns for different contexts"""
        return {
            'python_string': {
                'patterns': [
                    (r'\\', r'\\\\'),  # Backslashes first
                    (r'"', r'\\"'),    # Double quotes
                    (r"'", r"\\'"),    # Single quotes
                    (r'\n', r'\\n'),   # Newlines
                    (r'\t', r'\\t'),   # Tabs
                    (r'\r', r'\\r'),   # Carriage returns
                ],
                'safe_chars': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,;:!?()[]{}+-*/<>=&|^~`@#$%_')
            },
            'json_content': {
                'patterns': [
                    (r'\\', r'\\\\'),
                    (r'"', r'\\"'),
                    (r'\b', r'\\b'),
                    (r'\f', r'\\f'),
                    (r'\n', r'\\n'),
                    (r'\r', r'\\r'),
                    (r'\t', r'\\t'),
                ],
                'safe_chars': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,;:!?()[]{}+-*/<>=&|^~`@#$%_')
            },
            'shell_command': {
                'patterns': [
                    (r'\\', r'\\\\'),
                    (r'"', r'\\"'),
                    (r"'", r"\\'"),
                    (r'`', r'\\`'),
                    (r'\$', r'\\$'),
                    (r'&', r'\\&'),
                    (r';', r'\\;'),
                    (r'\|', r'\\|'),
                ],
                'safe_chars': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?()[]{}+-*/@#%_')
            }
        }
    
    def _initialize_framework_templates(self) -> Dict[str, Dict]:
        """Initialize framework-specific templates"""
        return {
            'python': {
                'function': textwrap.dedent("""
                def {name}({params}):
                    \"\"\"
                    {docstring}
                    \"\"\"
                    {body}
                    return {return_value}
                """).strip(),
                
                'class': textwrap.dedent("""
                class {name}({inheritance}):
                    \"\"\"
                    {docstring}
                    \"\"\"
                    
                    def __init__(self{init_params}):
                        {init_body}
                    
                    {methods}
                """).strip(),
            },
            
            'javascript': {
                'function': textwrap.dedent("""
                function {name}({params}) {{
                    // {comment}
                    {body}
                    return {return_value};
                }}
                """).strip(),
                
                'react_component': textwrap.dedent("""
                const {name} = ({{props}}) => {{
                    // {comment}
                    {hooks}
                    
                    return (
                        <div className="{className}">
                            {jsx_content}
                        </div>
                    );
                }};
                
                export default {name};
                """).strip(),
            }
        }
    
    def _initialize_validation_rules(self) -> Dict[str, List]:
        """Initialize content validation rules"""
        return {
            'python': [
                ('syntax_check', 'Check Python syntax validity'),
                ('indentation_check', 'Check consistent indentation'),
            ],
            'json': [
                ('json_validity', 'Check JSON format validity'),
                ('quote_consistency', 'Check quote consistency'),
            ],
            'general': [
                ('encoding_check', 'Check character encoding'),
                ('line_ending_check', 'Check line ending consistency'),
            ]
        }
    
    def detect_content_type(self, content: str) -> ContentType:
        """Intelligently detect content type for appropriate handling"""
        content_lower = content.lower().strip()
        
        # JSON detection - IMPROVED: Check structure first
        if content.strip().startswith(('{', '[')):
            try:
                json.loads(content)
                return ContentType.JSON
            except json.JSONDecodeError:
                # If it starts with JSON brackets but is invalid, still treat as JSON
                if content.strip().startswith('{') and ('}' in content or content.count('{') > 0):
                    return ContentType.JSON
                if content.strip().startswith('[') and (']' in content or content.count('[') > 0):
                    return ContentType.JSON
        
        # Python code detection
        if any(keyword in content for keyword in ['def ', 'class ', 'import ', 'from ', 'if __name__']):
            return ContentType.PYTHON
        
        # JavaScript/TypeScript detection
        if any(keyword in content for keyword in ['function ', 'const ', 'let ', 'var ', '=>', 'console.']):
            return ContentType.JAVASCRIPT
        
        # SQL detection
        if any(keyword in content_lower for keyword in ['select ', 'insert ', 'update ', 'delete ']):
            return ContentType.SQL
        
        # Multiline detection
        if '\n' in content and content.count('\n') > 2:
            return ContentType.MULTILINE
        
        # Template detection
        if any(pattern in content for pattern in ['${', '{', 'f"', "f'"]):
            return ContentType.TEMPLATE
        
        return ContentType.PLAIN_TEXT
    
    def escape_content(self, content: str, target_context: str = 'auto') -> str:
        """Escape content based on target context with extreme robustness"""
        self.performance_stats['escape_operations'] += 1
        
        if target_context == 'auto':
            content_type = self.detect_content_type(content)
            if content_type == ContentType.PYTHON:
                target_context = 'python_string'
            elif content_type == ContentType.JSON:
                target_context = 'json_content'
            else:
                target_context = 'python_string'  # Default
        
        if target_context not in self.escape_patterns:
            if INTEGRATION_AVAILABLE and logger:
                logger.warning(f"Unknown escape context: {target_context}, using python_string")
            target_context = 'python_string'
        
        escaped_content = content
        patterns = self.escape_patterns[target_context]['patterns']
        
        # Apply escape patterns in order
        for pattern, replacement in patterns:
            escaped_content = re.sub(pattern, replacement, escaped_content)
        
        return escaped_content
    
    def process_large_content(self, content: str, operation: str = 'insert') -> Dict[str, Any]:
        """Process large content (>20 lines) in incremental mode"""
        lines = content.split('\n')
        line_count = len(lines)
        
        if line_count <= self.incremental_threshold:
            return {
                'mode': 'direct',
                'content': content,
                'chunks': 1,
                'estimated_time': 0.1,
                'total_lines': line_count
            }
        
        # Incremental mode
        chunk_size = max(10, self.incremental_threshold // 2)
        chunks = []
        
        for i in range(0, line_count, chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_content = '\n'.join(chunk_lines)
            chunks.append({
                'index': len(chunks),
                'content': chunk_content,
                'line_start': i + 1,
                'line_end': min(i + chunk_size, line_count),
                'size': len(chunk_content)
            })
        
        estimated_time = len(chunks) * 0.2  # 200ms per chunk
        
        if INTEGRATION_AVAILABLE and logger:
            logger.info(f"Large content detected: {line_count} lines, processing in {len(chunks)} chunks")
        
        return {
            'mode': 'incremental',
            'content': content,
            'chunks': chunks,
            'chunk_count': len(chunks),
            'total_lines': line_count,
            'estimated_time': estimated_time
        }
    
    def validate_content(self, content: str, content_type: Optional[ContentType] = None) -> ContentValidationResult:
        """Comprehensive content validation with suggestions"""
        self.performance_stats['validation_operations'] += 1
        
        if content_type is None:
            content_type = self.detect_content_type(content)
        
        issues = []
        suggestions = []
        line_count = content.count('\n') + 1
        char_count = len(content)
        
        # General validations
        if not content.strip():
            issues.append("Content is empty or contains only whitespace")
            suggestions.append("Add meaningful content")
        
        # Encoding validation
        try:
            content.encode('utf-8')
        except UnicodeEncodeError as e:
            issues.append(f"Character encoding issue: {e}")
            suggestions.append("Check for invalid characters")
        
        # Content-type specific validations
        if content_type == ContentType.PYTHON:
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append(f"Python syntax error: {e}")
                suggestions.append("Fix Python syntax")
        elif content_type == ContentType.JSON:
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                issues.append(f"JSON format error: {e}")
                suggestions.append("Fix JSON syntax")
        
        is_valid = len(issues) == 0
        
        return ContentValidationResult(
            is_valid=is_valid,
            issues=issues,
            suggestions=suggestions,
            content_type=content_type,
            line_count=line_count,
            char_count=char_count
        )
    
    def prepare_content(self, content: str, target_context: str = 'auto', 
                       validate: bool = True) -> Dict[str, Any]:
        """Main method to prepare content with all features"""
        result = {
            'original_content': content,
            'processed_content': content,
            'content_type': self.detect_content_type(content),
            'validation_result': None,
            'processing_mode': 'direct',
            'escape_applied': False,
            'performance_stats': self.performance_stats.copy()
        }
        
        # Content validation
        if validate:
            validation_result = self.validate_content(result['processed_content'])
            result['validation_result'] = validation_result
            
            if not validation_result.is_valid and INTEGRATION_AVAILABLE and logger:
                logger.warning(f"Content validation issues: {len(validation_result.issues)}")
        
        # Large content processing
        processing_info = self.process_large_content(result['processed_content'])
        result['processing_mode'] = processing_info['mode']
        result['processing_info'] = processing_info
        
        # Escape handling
        if target_context != 'none':
            escaped_content = self.escape_content(result['processed_content'], target_context)
            result['processed_content'] = escaped_content
            result['escape_applied'] = True
            result['escape_context'] = target_context
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get content handler performance statistics"""
        return {
            'performance_stats': self.performance_stats.copy(),
            'available_frameworks': list(self.framework_templates.keys()),
            'available_escape_contexts': list(self.escape_patterns.keys()),
            'incremental_threshold': self.incremental_threshold,
            'integration_available': INTEGRATION_AVAILABLE
        }

# Global content handler instance
content_handler = ExtremeContentHandler()
