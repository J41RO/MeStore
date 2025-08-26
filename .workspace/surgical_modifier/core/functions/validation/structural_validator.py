import ast
import logging
import os
from typing import List, Dict, Any, Optional, Tuple


class StructuralValidator:
   """
   Validador de integridad estructural para código Python.
   
   Proporciona métodos para validar sintaxis, indentación y estructura
   de archivos Python antes y después de operaciones de modificación.
   """
   
   def __init__(self, logger_name: str = 'structural_validator'):
       """
       Inicializa el validador estructural.
       
       Args:
           logger_name: Nombre del logger para reportes
       """
       self.logger = logging.getLogger(logger_name)
       self.logger.setLevel(logging.INFO)
       
       # Configurar handler si no existe
       if not self.logger.handlers:
           handler = logging.StreamHandler()
           formatter = logging.Formatter(
               '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
           )
           handler.setFormatter(formatter)
           self.logger.addHandler(handler)
   
   def validate_python_syntax(self, file_path: str) -> Tuple[bool, Optional[str]]:
       """
       Valida la sintaxis Python de un archivo usando ast.parse().
       
       Args:
           file_path: Ruta al archivo Python a validar
           
       Returns:
           Tuple[bool, Optional[str]]: (es_válido, mensaje_error)
       """
       if not os.path.exists(file_path):
           error_msg = f'Archivo no encontrado: {file_path}'
           self.logger.error(error_msg)
           return False, error_msg
       
       try:
           with open(file_path, 'r', encoding='utf-8') as f:
               content = f.read()
           
           # Intentar parsear con AST
           ast.parse(content)
           self.logger.info(f'Sintaxis válida: {file_path}')
           return True, None
           
       except SyntaxError as e:
           error_msg = f'Error de sintaxis en {file_path}:{e.lineno}: {e.msg}'
           self.logger.error(error_msg)
           return False, error_msg
       except Exception as e:
           error_msg = f'Error inesperado validando {file_path}: {str(e)}'
           self.logger.error(error_msg)
           return False, error_msg
   
   def validate_indentation(self, file_path: str) -> Tuple[bool, List[str]]:
       """
       Valida la consistencia de indentación en un archivo Python.
       
       Args:
           file_path: Ruta al archivo Python a validar
           
       Returns:
           Tuple[bool, List[str]]: (es_consistente, lista_de_problemas)
       """
       if not os.path.exists(file_path):
           return False, [f'Archivo no encontrado: {file_path}']
       
       issues = []
       try:
           with open(file_path, 'r', encoding='utf-8') as f:
               lines = f.readlines()
           
           # Analizar indentación línea por línea
           indent_levels = []
           for line_num, line in enumerate(lines, 1):
               if line.strip():  # Ignorar líneas vacías
                   leading_spaces = len(line) - len(line.lstrip())
                   if leading_spaces > 0:
                       indent_levels.append((line_num, leading_spaces))
           
           # Verificar consistencia (múltiplos de 4 espacios)
           for line_num, spaces in indent_levels:
               if spaces % 4 != 0:
                   issues.append(f'Línea {line_num}: Indentación inconsistente ({spaces} espacios)')
           
           if not issues:
               self.logger.info(f'Indentación consistente: {file_path}')
           else:
               self.logger.warning(f'Problemas de indentación en {file_path}: {len(issues)} issues')
               
       except Exception as e:
           issues.append(f'Error leyendo archivo: {str(e)}')
           
       return len(issues) == 0, issues
   
   def analyze_structure(self, file_path: str) -> Dict[str, Any]:
       """
       Analiza la estructura de un archivo Python y mapea clases/métodos/funciones.
       
       Args:
           file_path: Ruta al archivo Python a analizar
           
       Returns:
           Dict con información estructural del archivo
       """
       if not os.path.exists(file_path):
           return {'error': f'Archivo no encontrado: {file_path}'}
       
       try:
           with open(file_path, 'r', encoding='utf-8') as f:
               content = f.read()
           
           tree = ast.parse(content)
           
           structure = {
               'classes': [],
               'functions': [],
               'imports': [],
               'total_lines': len(content.splitlines()),
               'file_path': file_path
           }
           
           for node in ast.walk(tree):
               if isinstance(node, ast.ClassDef):
                   structure['classes'].append({
                       'name': node.name,
                       'line': node.lineno,
                       'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                   })
               elif isinstance(node, ast.FunctionDef):
                   structure['functions'].append({
                       'name': node.name,
                       'line': node.lineno,
                       'args': len(node.args.args)
                   })
               elif isinstance(node, (ast.Import, ast.ImportFrom)):
                   structure['imports'].append({
                       'line': node.lineno,
                       'module': getattr(node, 'module', None)
                   })
           
           self.logger.info(f'Estructura analizada: {file_path} - {len(structure["classes"])} clases, {len(structure["functions"])} funciones')
           return structure
           
       except Exception as e:
           error_msg = f'Error analizando estructura: {str(e)}'
           self.logger.error(error_msg)
           return {'error': error_msg}


   def detect_incomplete_constructs(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Detecta métodos y clases incompletos usando AST walker.
        
        Args:
            file_path: Ruta al archivo Python a analizar
            
        Returns:
            List[Dict]: Lista de problemas encontrados
        """
        if not os.path.exists(file_path):
            return [{'type': 'file_error', 'message': f'Archivo no encontrado: {file_path}'}]
        
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Verificar clases sin métodos __init__
                    has_init = any(n.name == '__init__' for n in node.body if isinstance(n, ast.FunctionDef))
                    if not has_init and len([n for n in node.body if isinstance(n, ast.FunctionDef)]) > 0:
                        issues.append({
                            'type': 'missing_init',
                            'line': node.lineno,
                            'message': f'Clase {node.name} sin método __init__'
                        })
                    
                    # Verificar clases completamente vacías
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        issues.append({
                            'type': 'empty_class',
                            'line': node.lineno,
                            'message': f'Clase {node.name} completamente vacía (solo pass)'
                        })
                
                elif isinstance(node, ast.FunctionDef):
                    # Verificar funciones con solo pass
                    if (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
                        issues.append({
                            'type': 'empty_function',
                            'line': node.lineno,
                            'message': f'Función {node.name} vacía (solo pass)'
                        })
                    
                    # Verificar funciones con solo Ellipsis (...)
                    elif (len(node.body) == 1 and 
                          isinstance(node.body[0], ast.Expr) and 
                          isinstance(node.body[0].value, ast.Constant) and 
                          node.body[0].value.value is ...):
                        issues.append({
                            'type': 'ellipsis_function',
                            'line': node.lineno,
                            'message': f'Función {node.name} con solo ellipsis (...)'
                        })
            
            if issues:
                self.logger.warning(f'Detectados {len(issues)} constructos incompletos en {file_path}')
            else:
                self.logger.info(f'No se encontraron constructos incompletos en {file_path}')
                
            return issues
            
        except Exception as e:
            error_issue = {
                'type': 'analysis_error',
                'message': f'Error analizando {file_path}: {str(e)}'
            }
            self.logger.error(error_issue['message'])
            return [error_issue]