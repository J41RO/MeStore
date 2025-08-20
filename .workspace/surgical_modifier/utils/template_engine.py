"""
Surgical Modifier v6.0 - Intelligent Template Engine
Advanced template system with framework detection and smart suggestions
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import textwrap

try:
    from utils.path_resolver import path_resolver
    from utils.logger import logger
    PATH_INTEGRATION = True
except ImportError:
    PATH_INTEGRATION = False

class IntelligentTemplateEngine:
    """
    Intelligent template engine with framework detection and context awareness
    """
    
    def __init__(self):
        self.project_templates = {}
        self.custom_templates = {}
        self.template_usage_stats = {}
        self._initialize_project_specific_templates()
    
    def _initialize_project_specific_templates(self):
        """Initialize templates based on current project context"""
        if not PATH_INTEGRATION:
            # Default templates when no path integration
            self.project_templates['python'] = self._get_python_templates()
            self.project_templates['javascript'] = self._get_javascript_templates()
            return
        
        # Try to detect project type
        try:
            project_info = path_resolver.get_project_info()
            project_type = project_info.get('type', 'unknown')
            
            # Always include Python templates
            self.project_templates['python'] = self._get_python_templates()
            
            # Check for JavaScript/Node.js
            if Path('package.json').exists():
                self.project_templates['javascript'] = self._get_javascript_templates()
                self.project_templates['react'] = self._get_react_templates()
            
            # Check for FastAPI
            if any(Path(f).exists() for f in ['main.py', 'app.py']):
                self.project_templates['fastapi'] = self._get_fastapi_templates()
                
        except Exception:
            # Fallback to basic templates
            self.project_templates['python'] = self._get_python_templates()
            self.project_templates['javascript'] = self._get_javascript_templates()
    
    def _get_python_templates(self) -> Dict[str, str]:
        """Python specific templates"""
        return {
            'function': textwrap.dedent("""
            def {name}({params}):
                \"\"\"
                {description}
                \"\"\"
                {body}
                return {return_value}
            """).strip(),
            
            'class': textwrap.dedent("""
            class {name}({inheritance}):
                \"\"\"
                {description}
                \"\"\"
                
                def __init__(self{init_params}):
                    {init_body}
                
                {methods}
            """).strip(),
        }
    
    def _get_javascript_templates(self) -> Dict[str, str]:
        """JavaScript specific templates"""
        return {
            'function': textwrap.dedent("""
            function {name}({params}) {{
                // {description}
                {body}
                return {return_value};
            }}
            """).strip(),
            
            'arrow_function': textwrap.dedent("""
            const {name} = ({params}) => {{
                // {description}
                {body}
                return {return_value};
            }};
            """).strip(),
        }
    
    def _get_react_templates(self) -> Dict[str, str]:
        """React specific templates"""
        return {
            'component': textwrap.dedent("""
            import React from 'react';
            
            const {name} = ({{ {props} }}) => {{
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
    
    def _get_fastapi_templates(self) -> Dict[str, str]:
        """FastAPI specific templates"""
        return {
            'endpoint': textwrap.dedent("""
            @app.{method}("/{path}")
            async def {name}({params}):
                \"\"\"
                {description}
                \"\"\"
                try:
                    {body}
                    return {{"message": "Success", "data": result}}
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            """).strip(),
        }
    
    def detect_project_frameworks(self) -> List[str]:
        """Detect available frameworks in current project"""
        return list(self.project_templates.keys())
    
    def get_template(self, framework: str, template_type: str, **kwargs) -> str:
        """Get template with intelligent parameter handling"""
        if framework in self.project_templates:
            framework_templates = self.project_templates[framework]
        else:
            if PATH_INTEGRATION and logger:
                logger.warning(f"Framework '{framework}' not found in project templates")
            return f"# Template for {framework}/{template_type} not available"
        
        if template_type not in framework_templates:
            available = list(framework_templates.keys())
            if PATH_INTEGRATION and logger:
                logger.warning(f"Template type '{template_type}' not available. Available: {available}")
            return f"# Template type '{template_type}' not found. Available: {', '.join(available)}"
        
        template = framework_templates[template_type]
        
        # Track usage
        key = f"{framework}/{template_type}"
        self.template_usage_stats[key] = self.template_usage_stats.get(key, 0) + 1
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            missing_param = str(e).strip("'\"")
            if PATH_INTEGRATION and logger:
                logger.error(f"Missing template parameter: {missing_param}")
            return f"# Error: Missing parameter '{missing_param}'\n# Template: {framework}/{template_type}\n{template}"
    
    def suggest_templates_for_content(self, content_hint: str) -> List[Dict[str, str]]:
        """Suggest templates based on content hint and project context"""
        suggestions = []
        content_lower = content_hint.lower()
        available_frameworks = self.detect_project_frameworks()
        
        # Python suggestions
        if 'python' in available_frameworks:
            if any(keyword in content_lower for keyword in ['function', 'def']):
                suggestions.append({
                    'framework': 'python',
                    'template': 'function',
                    'description': 'Python function with docstring'
                })
            if any(keyword in content_lower for keyword in ['class', 'model']):
                suggestions.append({
                    'framework': 'python',
                    'template': 'class',
                    'description': 'Python class with __init__ method'
                })
        
        # FastAPI suggestions
        if 'fastapi' in available_frameworks:
            if any(keyword in content_lower for keyword in ['api', 'endpoint', 'route']):
                suggestions.append({
                    'framework': 'fastapi',
                    'template': 'endpoint',
                    'description': 'FastAPI endpoint with error handling'
                })
        
        # React suggestions
        if 'react' in available_frameworks:
            if any(keyword in content_lower for keyword in ['component', 'react']):
                suggestions.append({
                    'framework': 'react',
                    'template': 'component',
                    'description': 'React functional component'
                })
        
        return suggestions[:5]  # Top 5 suggestions
    
    def get_template_parameters(self, framework: str, template_type: str) -> List[str]:
        """Get required parameters for a template"""
        if framework not in self.project_templates:
            return []
        
        if template_type not in self.project_templates[framework]:
            return []
        
        template = self.project_templates[framework][template_type]
        
        # Extract parameters from template
        parameters = re.findall(r'\{(\w+)\}', template)
        return list(set(parameters))  # Remove duplicates
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get template usage statistics"""
        return {
            'template_usage': self.template_usage_stats.copy(),
            'available_frameworks': self.detect_project_frameworks(),
            'total_templates': sum(len(templates) for templates in self.project_templates.values()),
            'most_used': max(self.template_usage_stats.items(), key=lambda x: x[1]) if self.template_usage_stats else None
        }

# Global template engine
template_engine = IntelligentTemplateEngine()
