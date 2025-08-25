#!/usr/bin/env python3
"""
Surgical Modifier v6.0 - CLI Principal
"""
import sys
import argparse
import re
from core.operations.basic import after_operation, before_operation, create_operation, replace_operation, append_operation
from core.operations.basic.replace import enhanced_replace_operation


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
    parser = argparse.ArgumentParser(description='Surgical Modifier v6.0')
    parser.add_argument('operation', choices=['create', 'replace', 'after', 'before', 'append', 'extract', 'update', 'delete'])
    parser.add_argument('file', help='Archivo objetivo')
    parser.add_argument('pattern', help='Patrón a buscar')
    parser.add_argument('content', nargs='?', help='Contenido a insertar')
    parser.add_argument('--verbose', action='store_true', help='Output detallado')
    parser.add_argument('--raw', action='store_true', help='Contenido raw sin procesamiento')
    parser.add_argument('--file-input', help='Leer contenido desde archivo')
    parser.add_argument('--stdin', action='store_true', help='Leer contenido desde stdin')
    
    args = parser.parse_args()
    
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