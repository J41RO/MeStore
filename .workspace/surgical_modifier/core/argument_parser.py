"""
Surgical Modifier v6.0 - Extensible Argument Parser
Dynamic argument parsing and validation system
"""

import click
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import re

@dataclass
class ArgumentSpec:
    """Specification for an operation argument"""
    name: str
    type: type = str
    required: bool = True
    default: Any = None
    help: str = ""
    choices: Optional[List[str]] = None
    validator: Optional[Callable] = None
    example: str = ""

@dataclass
class OperationSpec:
    """Complete specification for an operation"""
    name: str
    description: str
    arguments: List[ArgumentSpec] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    category: str = "basic"
    
class ArgumentParser:
    """
    Extensible argument parser for operations
    Automatically generates Click decorators and validation
    """
    
    def __init__(self):
        self.operation_specs: Dict[str, OperationSpec] = {}
        self.validators: Dict[str, Callable] = {}
        
    def register_operation_spec(self, spec: OperationSpec):
        """Register an operation specification"""
        self.operation_specs[spec.name] = spec
        
    def create_click_decorators(self, operation_name: str) -> List[Callable]:
        """
        Create Click decorators for an operation based on its spec
        Returns list of decorators to apply to the command function
        """
        spec = self.operation_specs.get(operation_name)
        if not spec:
            return []
            
        decorators = []
        
        for arg_spec in spec.arguments:
            if arg_spec.required:
                # Required argument
                decorator = click.argument(
                    arg_spec.name.upper(),
                    type=self._get_click_type(arg_spec)
                )
            else:
                # Optional option
                decorator = click.option(
                    f'--{arg_spec.name}',
                    default=arg_spec.default,
                    help=arg_spec.help,
                    type=self._get_click_type(arg_spec)
                )
            decorators.append(decorator)
            
        return decorators
    
    def _get_click_type(self, arg_spec: ArgumentSpec) -> click.ParamType:
        """Convert Python type to Click type"""
        if arg_spec.choices:
            return click.Choice(arg_spec.choices)
        elif arg_spec.type == int:
            return click.INT
        elif arg_spec.type == float:
            return click.FLOAT
        elif arg_spec.type == bool:
            return click.BOOL
        else:
            return click.STRING
    
    def validate_arguments(self, operation_name: str, **kwargs) -> Dict[str, Any]:
        """
        Validate arguments for an operation
        Returns validated and processed arguments
        """
        spec = self.operation_specs.get(operation_name)
        if not spec:
            return kwargs
            
        validated = {}
        errors = []
        
        for arg_spec in spec.arguments:
            value = kwargs.get(arg_spec.name)
            
            # Check required arguments
            if arg_spec.required and value is None:
                errors.append(f"Required argument '{arg_spec.name}' is missing")
                continue
                
            # Apply default if needed
            if value is None:
                value = arg_spec.default
                
            # Type conversion
            if value is not None and arg_spec.type != str:
                try:
                    value = arg_spec.type(value)
                except (ValueError, TypeError):
                    errors.append(f"Invalid type for '{arg_spec.name}': expected {arg_spec.type.__name__}")
                    continue
            
            # Choice validation
            if arg_spec.choices and value not in arg_spec.choices:
                errors.append(f"Invalid choice for '{arg_spec.name}': must be one of {arg_spec.choices}")
                continue
                
            # Custom validator
            if arg_spec.validator:
                try:
                    if not arg_spec.validator(value):
                        errors.append(f"Validation failed for '{arg_spec.name}'")
                        continue
                except Exception as e:
                    errors.append(f"Validator error for '{arg_spec.name}': {e}")
                    continue
            
            validated[arg_spec.name] = value
            
        if errors:
            raise click.BadParameter("\n".join(errors))
            
        return validated

    def get_operation_help(self, operation_name: str) -> str:
        """Generate comprehensive help text for an operation"""
        spec = self.operation_specs.get(operation_name)
        if not spec:
            return f"No help available for {operation_name}"
            
        help_text = f"{spec.description}\n\n"
        
        if spec.arguments:
            help_text += "Arguments:\n"
            for arg_spec in spec.arguments:
                req_text = "required" if arg_spec.required else f"optional, default: {arg_spec.default}"
                help_text += f"  {arg_spec.name}: {arg_spec.help} ({req_text})\n"
                if arg_spec.example:
                    help_text += f"    Example: {arg_spec.example}\n"
        
        if spec.examples:
            help_text += "\nExamples:\n"
            for example in spec.examples:
                help_text += f"  {example}\n"
                
        return help_text

# Global parser instance
argument_parser = ArgumentParser()

# Register common argument specs for future operations
def register_common_specs():
    """Register common operation specifications"""
    
    # CREATE operation spec
    create_spec = OperationSpec(
        name="create",
        description="Create a new file with specified content",
        arguments=[
            ArgumentSpec("file", str, True, help="Path to the file to create", example="components/Button.tsx"),
            ArgumentSpec("content", str, True, help="Content to write to the file", example="export const Button = () => <button />")
        ],
        examples=[
            "made create components/Button.tsx 'export const Button = () => <button />'",
            "made create utils/helper.py 'def helper(): pass'"
        ],
        category="basic"
    )
    argument_parser.register_operation_spec(create_spec)
    
    # REPLACE operation spec
    replace_spec = OperationSpec(
        name="replace",
        description="Replace a pattern in a file with new content",
        arguments=[
            ArgumentSpec("file", str, True, help="Path to the file to modify", example="app.py"),
            ArgumentSpec("pattern", str, True, help="Pattern to find and replace", example="old_function"),
            ArgumentSpec("replacement", str, True, help="New content to replace with", example="new_function")
        ],
        examples=[
            "made replace app.py 'old_function' 'new_function'",
            "made replace config.js 'localhost:3000' 'production.com'"
        ],
        category="basic"
    )
    argument_parser.register_operation_spec(replace_spec)
    
    # AFTER operation spec
    after_spec = OperationSpec(
        name="after",
        description="Insert content after a specified pattern in a file",
        arguments=[
            ArgumentSpec("file", str, True, help="Path to the file to modify", example="models.py"),
            ArgumentSpec("pattern", str, True, help="Pattern to find", example="class User:"),
            ArgumentSpec("content", str, True, help="Content to insert after pattern", example="    email = models.EmailField()")
        ],
        examples=[
            "made after models.py 'class User:' '    email = models.EmailField()'",
            "made after config.js 'module.exports = {' '    port: 3000,'"
        ],
        category="basic"
    )
    argument_parser.register_operation_spec(after_spec)
    
    # BEFORE operation spec
    before_spec = OperationSpec(
        name="before",
        description="Insert content before a specified pattern in a file",
        arguments=[
            ArgumentSpec("file", str, True, help="Path to the file to modify", example="app.py"),
            ArgumentSpec("pattern", str, True, help="Pattern to find", example="if __name__ == '__main__':"),
            ArgumentSpec("content", str, True, help="Content to insert before pattern", example="# Setup logging")
        ],
        examples=[
            "made before app.py 'if __name__ == \"__main__\":' '# Setup logging'",
            "made before component.jsx 'export default' 'Component.propTypes = {};'"
        ],
        category="basic"
    )
    argument_parser.register_operation_spec(before_spec)

# Initialize common specs
register_common_specs()
