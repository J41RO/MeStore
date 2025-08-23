#!/usr/bin/env python3
"""
Surgical Modifier v6.0 - CLI Principal
"""
import sys
import argparse
from core.operations.basic import after_operation, before_operation, create_operation, replace_operation, append_operation

def main():
    parser = argparse.ArgumentParser(description='Surgical Modifier v6.0')
    parser.add_argument('operation', choices=['create', 'replace', 'after', 'before', 'append', 'extract', 'update', 'delete'])
    parser.add_argument('file', help='Archivo objetivo')
    parser.add_argument('pattern', help='Patrón a buscar')
    parser.add_argument('content', nargs='?', help='Contenido a insertar')
    parser.add_argument('--verbose', action='store_true', help='Output detallado')
    
    args = parser.parse_args()
    
    try:
        if args.operation == 'create':
            result = create_operation(args.file, "", args.content or args.pattern)
        elif args.operation == 'replace':
            result = replace_operation(args.file, args.pattern, args.content)
        elif args.operation == 'after':
            result = after_operation(args.file, args.pattern, args.content)
        elif args.operation == 'before':
            result = before_operation(args.file, args.pattern, args.content)
        elif args.operation == 'append':
            result = append_operation(args.file, args.pattern, args.content)
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
            updated_content = content.replace(args.pattern, args.content)
            with open(args.file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f'Updated pattern "{args.pattern}" with "{args.content}" in {args.file}')
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