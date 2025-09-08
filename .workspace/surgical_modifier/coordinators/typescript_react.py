from pathlib import Path
from typing import Dict, Any
import sys
import os
import logging
import json
import re
from functions.pattern.pattern_factory import PatternMatcherFactory
from functions.backup.intelligent_manager import IntelligentBackupManager
from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter
from functions.content.validator import ContentValidator
from functions.debugging.context_extractor import ContextExtractor
from functions.debugging.pattern_suggester import PatternSuggester
from functions.validation.path_checker import PathChecker


class TypeScriptReactCoordinator:
    """Coordinador especializado para operaciones TypeScript/React con análisis JSX"""
    
    def __init__(self):
        self.pattern_factory = PatternMatcherFactory()
        self.backup_manager = IntelligentBackupManager()
        self.reader = ContentReader()
        self.writer = ContentWriter()
        self.context_extractor = ContextExtractor()
        self.pattern_suggester = PatternSuggester()
        self.validator = ContentValidator()
        self.path_checker = PathChecker()
        self.logger = logging.getLogger(__name__)
        
    def execute(self, file_path: str, operation: str, **kwargs) -> Dict[str, Any]:
        """Ejecuta operaciones especializadas para TypeScript/React"""
        try:
            # Analizar contexto TypeScript/React
            context = self.analyze_jsx_context(file_path)
            
            # Ejecutar operación según tipo
            if operation == 'replace':
                return self._execute_replace(file_path, context, **kwargs)
            elif operation == 'after':
                return self._execute_after(file_path, context, **kwargs)
            elif operation == 'before':
                return self._execute_before(file_path, context, **kwargs)
            elif operation == 'create':
                return self._execute_create(file_path, context, **kwargs)
            else:
                return {'success': False, 'error': f'Operación no soportada: {operation}'}
                
        except Exception as e:
            self.logger.error(f'Error en TypeScriptReactCoordinator: {e}')
            return {'success': False, 'error': str(e)}
    
    def analyze_jsx_context(self, file_path: str) -> Dict[str, Any]:
        """Analiza contexto JSX y TypeScript en el archivo"""
        context = {
            'has_jsx': False,
            'has_typescript': False,
            'react_imports': [],
            'hooks_used': [],
            'components': [],
            'props_interfaces': []
        }
        
        if not os.path.exists(file_path):
            return context
            
        try:
            file_content = self.reader.read_file(file_path)
            content = file_content.get('content', '') if isinstance(file_content, dict) else str(file_content)
            
            # Detectar JSX
            jsx_patterns = [r'<\w+.*?>', r'React\.createElement', r'jsx']
            context['has_jsx'] = any(re.search(pattern, content) for pattern in jsx_patterns)
            
            # Detectar TypeScript
            ts_patterns = [r':\s*(string|number|boolean|any)', r'interface\s+\w+', r'type\s+\w+']
            context['has_typescript'] = any(re.search(pattern, content) for pattern in ts_patterns)
            
            # Detectar imports de React
            react_import_pattern = r'import.*?[\'"](react|@types/react).*?[\'"]'
            context['react_imports'] = re.findall(react_import_pattern, content, re.IGNORECASE)
            
            # Detectar hooks
            hook_pattern = r'use[A-Z]\w*'
            context['hooks_used'] = list(set(re.findall(hook_pattern, content)))
            
            # Detectar componentes
            component_pattern = r'(?:function|const)\s+([A-Z]\w*)'
            context['components'] = re.findall(component_pattern, content)
            
            # Detectar interfaces de props
            props_pattern = r'interface\s+(\w*Props?\w*)'
            context['props_interfaces'] = re.findall(props_pattern, content)
            
        except Exception as e:
            self.logger.warning(f'Error analizando contexto JSX: {e}')
            
        return context
    
    def detect_hooks(self, content: str) -> list:
        """Detecta hooks de React en el contenido"""
        hook_pattern = r'use[A-Z]\w*\s*\('
        return re.findall(hook_pattern, content)
    
    def validate_typescript_syntax(self, content: str) -> Dict[str, Any]:
        """Valida sintaxis básica de TypeScript"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Verificar balanceado de brackets JSX
        open_tags = len(re.findall(r'<[^/][^>]*[^/]>', content))
        close_tags = len(re.findall(r'</[^>]+>', content))
        self_closing = len(re.findall(r'<[^>]+/>', content))
        
        if open_tags != close_tags + self_closing:
            validation['errors'].append('JSX tags no balanceados')
            validation['valid'] = False
            
        # Verificar sintaxis básica de TypeScript
        if ':' in content and not re.search(r':\s*(string|number|boolean|any|\w+)', content):
            validation['warnings'].append('Posibles anotaciones de tipo incompletas')
            
        return validation
    
    def resolve_imports(self, file_path: str) -> Dict[str, Any]:
        """Resuelve y analiza imports específicos de React/TypeScript"""
        imports = {
            'react_imports': [],
            'local_imports': [],
            'type_imports': []
        }
        
        try:
            file_content = self.reader.read_file(file_path)
            content = file_content.get('content', '') if isinstance(file_content, dict) else str(file_content)
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('import'):
                    if 'react' in line.lower():
                        imports['react_imports'].append(line)
                    elif 'type' in line:
                        imports['type_imports'].append(line)
                    elif line.startswith('import') and ('./' in line or '../' in line):
                        imports['local_imports'].append(line)
                        
        except Exception as e:
            self.logger.warning(f'Error resolviendo imports: {e}')
            
        return imports
    
    def _execute_replace(self, file_path: str, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Ejecuta replace con consideraciones JSX/TypeScript"""
        from functions.workflow.replace_workflow import ReplaceWorkflow
        
        # Crear backup específico para TypeScript/React
        backup_info = self.backup_manager.create_backup(file_path, 'typescript_react_replace')
        
        # Ejecutar workflow de replace estándar con contexto mejorado
        workflow = ReplaceWorkflow()
        result = workflow.execute_sequence(
            file_path=file_path,
            pattern=kwargs.get('pattern', ''),
            replacement=kwargs.get('replacement', ''),
            context=context,
            **kwargs
        )
        
        # Validar resultado específico para TypeScript/React
        if result.get('success'):
            validation = self.validate_typescript_syntax(result.get('final_content', ''))
            result['typescript_validation'] = validation
            
        return result
    
    def _execute_after(self, file_path: str, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Ejecuta after con análisis JSX"""
        from functions.workflow.after_workflow import AfterWorkflow
        
        backup_info = self.backup_manager.create_backup(file_path, 'typescript_react_after')
        
        workflow = AfterWorkflow()
        result = workflow.execute_sequence(
            file_path=file_path,
            pattern=kwargs.get('pattern', ''),
            content=kwargs.get('content', ''),
            context=context,
            **kwargs
        )
        
        return result
    
    def _execute_before(self, file_path: str, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Ejecuta before con consideraciones TypeScript"""
        from functions.workflow.before_workflow import BeforeWorkflow
        
        backup_info = self.backup_manager.create_backup(file_path, 'typescript_react_before')
        
        workflow = BeforeWorkflow()
        result = workflow.execute_sequence(
            file_path=file_path,
            pattern=kwargs.get('pattern', ''),
            content=kwargs.get('content', ''),
            context=context,
            **kwargs
        )
        
        return result
    
    def _execute_create(self, file_path: str, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Crea archivos TypeScript/React con templates"""
        from functions.workflow.create_workflow import CreateWorkflow
        
        workflow = CreateWorkflow()
        # Extraer content de kwargs para evitar duplicación
        content = kwargs.pop('content', '')
        result = workflow.execute_sequence(
            file_path=file_path,
            content=content,
            context=context,
            path_checker=self.path_checker,
            writer=self.writer,
            validator=self.validator,
            backup_manager=self.backup_manager,
            **kwargs
        )
        
        return result