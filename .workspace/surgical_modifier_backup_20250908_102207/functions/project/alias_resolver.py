import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)

class AliasResolver:
    """
    Resolvedor de alias de rutas para proyectos TypeScript/JavaScript.
    
    Analiza configuraciones de rutas de:
    - tsconfig.json (TypeScript paths)
    - jsconfig.json (JavaScript paths)
    - vite.config.js/ts (Vite aliases)
    - webpack.config.js (Webpack aliases)
    """
    
    def __init__(self, project_path: str = '.'):
        """
        Inicializa el resolvedor en el directorio especificado.
        
        Args:
            project_path: Ruta del proyecto a analizar
        """
        self.project_path = Path(project_path).resolve()
        self.tsconfig_data = None
        self.jsconfig_data = None
        self.resolved_aliases = {}
        
    def load_typescript_config(self) -> bool:
        """
        Carga la configuración de TypeScript desde tsconfig.json.
        
        Returns:
            True si se cargó exitosamente, False en caso contrario
        """
        tsconfig_path = self.project_path / 'tsconfig.json'
        
        if not tsconfig_path.exists():
            logger.info('No se encontró tsconfig.json')
            return False
            
        try:
            with open(tsconfig_path, 'r', encoding='utf-8') as f:
                self.tsconfig_data = json.load(f)
            logger.info('tsconfig.json cargado exitosamente')
            return True
            
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f'Error cargando tsconfig.json: {e}')
            return False
    
    def load_javascript_config(self) -> bool:
        """
        Carga la configuración de JavaScript desde jsconfig.json.
        
        Returns:
            True si se cargó exitosamente, False en caso contrario
        """
        jsconfig_path = self.project_path / 'jsconfig.json'
        
        if not jsconfig_path.exists():
            logger.info('No se encontró jsconfig.json')
            return False
            
        try:
            with open(jsconfig_path, 'r', encoding='utf-8') as f:
                self.jsconfig_data = json.load(f)
            logger.info('jsconfig.json cargado exitosamente')
            return True
            
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f'Error cargando jsconfig.json: {e}')
            return False
    
    def extract_typescript_paths(self) -> Dict[str, List[str]]:
        """
        Extrae las configuraciones de paths desde tsconfig.json.
        
        Returns:
            Diccionario con alias y sus rutas correspondientes
        """
        if not self.tsconfig_data:
            return {}
            
        compiler_options = self.tsconfig_data.get('compilerOptions', {})
        paths = compiler_options.get('paths', {})
        
        if paths:
            logger.info(f'Encontrados {len(paths)} alias en tsconfig.json')
        
        return paths
    
    def extract_javascript_paths(self) -> Dict[str, List[str]]:
        """
        Extrae las configuraciones de paths desde jsconfig.json.
        
        Returns:
            Diccionario con alias y sus rutas correspondientes
        """
        if not self.jsconfig_data:
            return {}
            
        compiler_options = self.jsconfig_data.get('compilerOptions', {})
        paths = compiler_options.get('paths', {})
        
        if paths:
            logger.info(f'Encontrados {len(paths)} alias en jsconfig.json')
        
        return paths
    
    def get_base_url(self, config_type: str = 'typescript') -> str:
        """
        Obtiene la baseUrl configurada.
        
        Args:
            config_type: 'typescript' o 'javascript'
            
        Returns:
            BaseUrl configurada o string vacío
        """
        if config_type == 'typescript' and self.tsconfig_data:
            return self.tsconfig_data.get('compilerOptions', {}).get('baseUrl', '')
        elif config_type == 'javascript' and self.jsconfig_data:
            return self.jsconfig_data.get('compilerOptions', {}).get('baseUrl', '')
        
        return ''
    
    def resolve_alias_to_absolute_path(self, alias: str, alias_path: str, base_url: str = '') -> str:
        """
        Convierte un alias y su ruta relativa a una ruta absoluta.
        
        Args:
            alias: El alias (ej: '@/*')
            alias_path: La ruta del alias (ej: 'src/*')
            base_url: BaseUrl desde la configuración
            
        Returns:
            Ruta absoluta resuelta
        """
        # Limpiar el alias y la ruta (quitar wildcards)
        clean_alias = alias.replace('/*', '').replace('*', '')
        clean_path = alias_path.replace('/*', '').replace('*', '')
        
        # Combinar con baseUrl si existe
        if base_url:
            full_relative_path = os.path.join(base_url, clean_path)
        else:
            full_relative_path = clean_path
        
        # Resolver a ruta absoluta
        absolute_path = (self.project_path / full_relative_path).resolve()
        
        return str(absolute_path)
    
    def resolve_all_aliases(self) -> Dict[str, Dict[str, Union[str, bool]]]:
        """
        Resuelve todos los alias encontrados a rutas absolutas.
        
        Returns:
            Diccionario con información completa de alias resueltos
        """
        resolved = {}
        
        # Cargar configuraciones
        ts_loaded = self.load_typescript_config()
        js_loaded = self.load_javascript_config()
        
        if not ts_loaded and not js_loaded:
            logger.warning('No se encontraron archivos de configuración con alias')
            return resolved
        
        # Procesar alias de TypeScript
        if ts_loaded:
            ts_paths = self.extract_typescript_paths()
            ts_base_url = self.get_base_url('typescript')
            
            for alias, path_list in ts_paths.items():
                if path_list:  # Tomar la primera ruta si hay múltiples
                    absolute_path = self.resolve_alias_to_absolute_path(
                        alias, path_list[0], ts_base_url
                    )
                    
                    resolved[alias] = {
                        'absolute_path': absolute_path,
                        'relative_path': path_list[0],
                        'base_url': ts_base_url,
                        'exists': Path(absolute_path).exists(),
                        'source': 'tsconfig.json',
                        'all_paths': path_list
                    }
        
        # Procesar alias de JavaScript (si no están ya en TypeScript)
        if js_loaded:
            js_paths = self.extract_javascript_paths()
            js_base_url = self.get_base_url('javascript')
            
            for alias, path_list in js_paths.items():
                if alias not in resolved and path_list:
                    absolute_path = self.resolve_alias_to_absolute_path(
                        alias, path_list[0], js_base_url
                    )
                    
                    resolved[alias] = {
                        'absolute_path': absolute_path,
                        'relative_path': path_list[0],
                        'base_url': js_base_url,
                        'exists': Path(absolute_path).exists(),
                        'source': 'jsconfig.json',
                        'all_paths': path_list
                    }
        
        self.resolved_aliases = resolved
        logger.info(f'Resueltos {len(resolved)} alias totales')
        return resolved
    
    def get_alias_by_pattern(self, pattern: str) -> List[Dict[str, Union[str, bool]]]:
        """
        Busca alias que coincidan con un patrón específico.
        
        Args:
            pattern: Patrón a buscar (ej: '@', '~', etc.)
            
        Returns:
            Lista de alias que coinciden con el patrón
        """
        if not self.resolved_aliases:
            self.resolve_all_aliases()
            
        matching_aliases = []
        for alias, info in self.resolved_aliases.items():
            clean_alias = alias.replace('/*', '').replace('*', '')
            if pattern in clean_alias:
                matching_aliases.append({
                    'alias': alias,
                    'clean_alias': clean_alias,
                    **info
                })
        
        return matching_aliases
    
    def get_common_aliases(self) -> Dict[str, Dict[str, Union[str, bool]]]:
        """
        Obtiene los alias más comunes utilizados en proyectos.
        
        Returns:
            Diccionario con alias comunes encontrados
        """
        if not self.resolved_aliases:
            self.resolve_all_aliases()
            
        common_patterns = ['@/', '@', '~/', '~', 'src/', 'lib/', 'utils/', 'components/']
        common_aliases = {}
        
        for alias, info in self.resolved_aliases.items():
            clean_alias = alias.replace('/*', '').replace('*', '')
            for pattern in common_patterns:
                if clean_alias.startswith(pattern.replace('/', '')):
                    common_aliases[alias] = info
                    break
        
        return common_aliases
    
    def validate_alias_paths(self) -> Dict[str, Dict[str, Union[str, bool, List[str]]]]:
        """
        Valida que las rutas de los alias realmente existan en el sistema de archivos.
        
        Returns:
            Diccionario con información de validación de cada alias
        """
        if not self.resolved_aliases:
            self.resolve_all_aliases()
            
        validation_results = {}
        
        for alias, info in self.resolved_aliases.items():
            absolute_path = Path(info['absolute_path'])
            
            # Verificar existencia y tipo
            exists = absolute_path.exists()
            is_directory = absolute_path.is_dir() if exists else False
            is_file = absolute_path.is_file() if exists else False
            
            # Buscar archivos en la carpeta si es directorio
            contained_files = []
            if is_directory:
                try:
                    contained_files = [f.name for f in absolute_path.iterdir() if f.is_file()][:10]  # Limitar a 10
                except PermissionError:
                    contained_files = ['<sin permisos>']
            
            validation_results[alias] = {
                'exists': exists,
                'is_directory': is_directory,
                'is_file': is_file,
                'absolute_path': str(absolute_path),
                'relative_path': info['relative_path'],
                'source': info['source'],
                'contained_files': contained_files,
                'validation_status': 'valid' if exists else 'invalid'
            }
        
        return validation_results
    
    def get_alias_suggestions(self) -> List[Dict[str, str]]:
        """
        Sugiere alias comunes que podrían ser útiles en el proyecto.
        
        Returns:
            Lista de sugerencias de alias
        """
        suggestions = []
        
        # Verificar directorios comunes que podrían beneficiarse de alias
        common_dirs = {
            'src': '@',
            'src/components': '@/components',
            'src/utils': '@/utils',
            'src/lib': '@/lib',
            'src/hooks': '@/hooks',
            'src/services': '@/services',
            'src/assets': '@/assets',
            'lib': '~/lib',
            'utils': '~/utils',
            'components': '~/components'
        }
        
        for dir_path, suggested_alias in common_dirs.items():
            full_path = self.project_path / dir_path
            if full_path.exists() and full_path.is_dir():
                # Verificar si ya existe un alias para este directorio
                already_aliased = False
                for existing_alias, info in self.resolved_aliases.items():
                    if Path(info['absolute_path']) == full_path:
                        already_aliased = True
                        break
                
                if not already_aliased:
                    suggestions.append({
                        'suggested_alias': suggested_alias,
                        'target_path': dir_path,
                        'absolute_path': str(full_path),
                        'reason': f'Directorio común {dir_path} encontrado sin alias'
                    })
        
        return suggestions
    
    def get_complete_analysis(self) -> Dict[str, Union[Dict, List, int, bool]]:
        """
        Realiza un análisis completo de los alias del proyecto.
        
        Returns:
            Diccionario con análisis completo de alias
        """
        analysis = {
            'project_path': str(self.project_path),
            'has_typescript_config': (self.project_path / 'tsconfig.json').exists(),
            'has_javascript_config': (self.project_path / 'jsconfig.json').exists(),
            'resolved_aliases': self.resolve_all_aliases(),
            'alias_count': len(self.resolved_aliases),
            'common_aliases': self.get_common_aliases(),
            'validation_results': self.validate_alias_paths(),
            'suggestions': self.get_alias_suggestions(),
            'summary': {
                'total_aliases': len(self.resolved_aliases),
                'valid_aliases': sum(1 for info in self.resolved_aliases.values() if info['exists']),
                'invalid_aliases': sum(1 for info in self.resolved_aliases.values() if not info['exists']),
                'typescript_aliases': sum(1 for info in self.resolved_aliases.values() if info['source'] == 'tsconfig.json'),
                'javascript_aliases': sum(1 for info in self.resolved_aliases.values() if info['source'] == 'jsconfig.json'),
                'suggested_improvements': len(self.get_alias_suggestions())
            }
        }
        
        return analysis
    
    def format_alias_for_usage(self, alias: str, target_file: str) -> str:
        """
        Formatea un alias para su uso en imports.
        
        Args:
            alias: El alias a formatear
            target_file: Archivo específico dentro del alias
            
        Returns:
            Import path formateado
        """
        clean_alias = alias.replace('/*', '').replace('*', '')
        
        # Manejar diferentes casos
        if target_file.startswith('/'):
            target_file = target_file[1:]  # Quitar slash inicial
        
        if clean_alias.endswith('/'):
            return f'{clean_alias}{target_file}'
        else:
            return f'{clean_alias}/{target_file}'
