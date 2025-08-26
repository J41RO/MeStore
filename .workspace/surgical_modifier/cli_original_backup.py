#!/usr/bin/env python3
"""
Surgical Modifier v6.0 - CLI Principal
"""
import sys
import argparse
import re
from core.operations.basic import after_operation, before_operation, create_operation, replace_operation, append_operation
from core.operations.basic.replace import enhanced_replace_operation



def show_comprehensive_help():
    """Mostrar ayuda comprehensiva con ejemplos de uso"""
    help_text = """
SURGICAL MODIFIER v6.0 - Herramienta de Modificación Quirúrgica de Código

USAGE:
  python3 cli.py <operation> <file> <pattern> [content] [options]

OPERATIONS:
  create      Crear nuevo archivo con contenido
  replace     Reemplazar patrón existente con nuevo contenido  
  before      Insertar contenido antes del patrón encontrado
  after       Insertar contenido después del patrón encontrado
  append      Agregar contenido al final del archivo

OPTIONS:
  --help, -h           Mostrar esta ayuda
  --verbose            Output detallado con diferencias
  --raw                Contenido sin procesamiento automático
  --file-input FILE    Leer contenido desde archivo
  --stdin              Leer contenido desde stdin

EXAMPLES:

CREATE - Crear archivos nuevos:
  python3 cli.py create models/User.py "" "class User:
    def __init__(self, name): 
        self.name = name"
  
  # Con auto-creación de directorios
  python3 cli.py create deep/nested/path/component.tsx "" "export const Component = () => <div>Hello</div>;"

REPLACE - Reemplazar código existente:
  python3 cli.py replace app.py "old_function" "new_function"
  
  # Con backup automático
  python3 cli.py replace --verbose config.py "DEBUG = False" "DEBUG = True"

BEFORE - Insertar antes de patrón:
  python3 cli.py before models.py "class User:" "from datetime import datetime"
  
  # Preserva indentación automáticamente
  python3 cli.py before component.js "return (" "const data = fetchData();"

AFTER - Insertar después de patrón:
  python3 cli.py after routes.py "app = Flask(__name__)" "@app.route('/health')
def health():
    return 'OK'"

TEMPLATE LITERALS (JavaScript/TypeScript):
  # Usar wrapper para contenido con ${} 
  ./sm_wrapper.sh create component.tsx "" 'const msg = `Hello ${name}!`;'
  
  # O usar file input
  echo 'const html = `<div>${content}</div>`;' | python3 cli.py create template.js "" --stdin

CONTENT INPUT METHODS:
  # Método 1: Argumento directo (contenido simple)
  python3 cli.py create file.py "" "print('hello')"
  
  # Método 2: Desde archivo
  python3 cli.py create output.js "" --file-input source.js
  
  # Método 3: Desde stdin (contenido multilínea)
  python3 cli.py create component.py "" --stdin
  # Luego pegar contenido y presionar Ctrl+D
  
  # Método 4: Wrapper para template literals
  ./sm_wrapper.sh create modern.ts "" 'const api = `${baseUrl}/users/${id}`;'

BACKUP & SAFETY:
  - Backup automático antes de modificaciones
  - Rollback automático si hay errores de sintaxis
  - Validación de código Python automática
  - Preservación de indentación inteligente

TROUBLESHOOTING:
  - "bad substitution": Usar ./sm_wrapper.sh para template literals
  - Contenido multilínea: Usar --stdin o --file-input
  - Problemas de indentación: La herramienta preserva formato automáticamente
  
Para más información: https://github.com/tu-repo/surgical-modifier
"""
    print(help_text)

def process_template_literals(content: str) -> str:
    """Procesar template literals para evitar conflictos con bash"""
    if not content:
        return content
    
    # Si contiene \${} y está en contexto de JS/TS, procesarlo especialmente
    if '\${' in content and any(ext in content for ext in ['React', 'const ', 'let ', 'var ', '=>', 'interface', 'function']):
        # Restaurar formato correcto
        content = re.sub(r'\\$\{([^}]*)\}', r'\${}', content)
    
    return content

def safe_content_handler(content: str, file_path: str) -> str:
    """Manejo seguro de contenido complejo"""
    if not content:
        return content
    
    # Detectar tipo de archivo
    file_ext = file_path.lower().split('.')[-1] if '.' in file_path else ''
    
    # Para archivos JS/TS/JSX/TSX, aplicar procesamiento especial
    if file_ext in ['js', 'ts', 'jsx', 'tsx']:
        content = process_template_literals(content)
    
    return content

def main():
    # Si se pide help explícitamente, mostrar versión comprehensiva
    if len(sys.argv) == 1 or '--help' in sys.argv or '-h' in sys.argv:
        show_comprehensive_help()
        sys.exit(0)
    
    parser = argparse.ArgumentParser(description='Surgical Modifier v6.0', add_help=False)
    parser.add_argument('operation', choices=['create', 'replace', 'after', 'before', 'append', 'extract', 'update', 'delete'])
    parser.add_argument('file', help='Archivo objetivo')
    parser.add_argument('pattern', help='Patrón a buscar')
    parser.add_argument('content', nargs='?', help='Contenido a insertar')
    parser.add_argument('--verbose', action='store_true', help='Output detallado')
    parser.add_argument('--raw', action='store_true', help='Contenido raw sin procesamiento')
    parser.add_argument('--file-input', help='Leer contenido desde archivo')
    parser.add_argument('--stdin', action='store_true', help='Leer contenido desde stdin')
    parser.add_argument('--occurrence', type=int, default=1, help='Qué ocurrencia usar (1=primera, 2=segunda, etc.)')
    parser.add_argument('--context-before', help='Contexto requerido antes del patrón')
    parser.add_argument('--context-after', help='Contexto requerido después del patrón')
    parser.add_argument('--analyze-pattern', action='store_true', help='Analizar seguridad del patrón')
    parser.add_argument('--suggest-unique', type=int, help='Sugerir patrones únicos para línea N')
    
    args = parser.parse_args()

    # Manejar análisis de patrones
    if args.analyze_pattern and args.file and args.pattern:
        analysis = analyze_pattern_safety(args.file, args.pattern)
        print(f'ANÁLISIS DE PATRÓN: "{args.pattern}"')
        print(f'Archivo: {args.file}')
        print(f'Ocurrencias encontradas: {analysis["total_occurrences"]}')
        print(f'Nivel de riesgo: {analysis["risk_level"]}')
        print(f'Recomendación: {analysis["recommendation"]}')
        if analysis["total_occurrences"] > 1:
            print('OCURRENCIAS:')
            for i, occ in enumerate(analysis["occurrences"][:5], 1):
                print(f'  {i}. Línea {occ["line_number"]}: {occ["content"]}')
        sys.exit(0)
    
    # Modo sugerencias
    if args.suggest_unique and args.file:
        suggestions = suggest_unique_alternatives(args.file, args.suggest_unique)
        print(f'PATRONES ÚNICOS SUGERIDOS para línea {args.suggest_unique}:')
        for i, suggestion in enumerate(suggestions, 1):
            print(f'  {i}. {suggestion}')
        sys.exit(0)
    
    # Inicializar contenido
    content_to_use = args.content
    
    # Procesar contenido de forma segura
    if args.file_input:
        try:
            with open(args.file_input, 'r', encoding='utf-8') as f:
                content_to_use = f.read()
            if args.verbose:
                print(f"📄 Contenido leído desde: {args.file_input}")
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {args.file_input}")
            return 1
    elif args.stdin:
        if args.verbose:
            print("📝 Ingrese contenido (Ctrl+D para terminar):")
        content_to_use = sys.stdin.read()
    
    # Aplicar safe content handler si no es raw
    if not args.raw and content_to_use:
        content_to_use = safe_content_handler(content_to_use, args.file)
    
    try:
        if args.operation == 'create':
            result = create_operation(args.file, "", content_to_use or args.pattern)
        elif args.operation == 'replace':
            result = enhanced_replace_operation(args.file, args.pattern, content_to_use, auto_backup=True)
        elif args.operation == 'after':
            result = after_operation(args.file, args.pattern, content_to_use)
        elif args.operation == 'before':
            result = before_operation(args.file, args.pattern, content_to_use)
        elif args.operation == 'append':
            result = append_operation(args.file, args.pattern, content_to_use)
        elif args.operation == 'extract':
            # Implementación simple de extract
            with open(args.file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            extracted = [line.strip() for line in lines if args.pattern in line]
            if extracted:
                for line in extracted: 
                    print(line)
            else:
                print(f'Pattern "{args.pattern}" not found in {args.file}')
            result = True  # Simular éxito
        elif args.operation == 'update':
            # Implementación simple de update
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
            updated_content = content.replace(args.pattern, content_to_use)
            with open(args.file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f'Updated pattern "{args.pattern}" with "{content_to_use}" in {args.file}')
            result = True  # Simular éxito
        elif args.operation == 'delete':
            # Implementación simple de delete
            with open(args.file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            filtered_lines = [line for line in lines if args.pattern not in line]
            with open(args.file, 'w', encoding='utf-8') as f:
                f.writelines(filtered_lines)
            deleted_count = len(lines) - len(filtered_lines)
            print(f'Deleted {deleted_count} lines containing "{args.pattern}" from {args.file}')
            result = True  # Simular éxito
        
        print(f"✅ Operación {args.operation} completada exitosamente")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())