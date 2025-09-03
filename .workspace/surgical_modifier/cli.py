import py_compile
#!/usr/bin/env python3
"""CLI principal de Surgical Modifier."""

import click
import re
import sys
import os
from pathlib import Path
from rich.console import Console

# Agregar path para importar coordinadores
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from coordinators.replace import ReplaceCoordinator
from coordinators.after import AfterCoordinator
from coordinators.before import BeforeCoordinator

console = Console()


# Funciones helper para validación
def validate_class_insertion(pattern, content):
    """Validar inserción después de definición de clase para evitar IndentationError"""
    # Detectar si pattern es definición de clase
    if re.search(r'class\s+\w+.*:', pattern):
        # Si content no tiene indentación, añadir indentación mínima
        if content and not content.startswith('    '):
            # Añadir indentación si no está presente
            lines = content.split('\n')
            indented_lines = ['    ' + line if line.strip() else line for line in lines]
            content = '\n'.join(indented_lines)
    return content

def backup_file(filepath):
    """Crear backup antes de modificación"""
    backup_path = f"{filepath}.backup_temp"
    try:
        with open(filepath, 'r', encoding='utf-8') as original:
            with open(backup_path, 'w', encoding='utf-8') as backup:
                backup.write(original.read())
        return backup_path
    except Exception as e:
        console.print(f"❌ Error creando backup: {e}", style="red")
        return None

def restore_from_backup(filepath, backup_path):
    """Restaurar archivo desde backup"""
    try:
        with open(backup_path, 'r', encoding='utf-8') as backup:
            with open(filepath, 'w', encoding='utf-8') as original:
                original.write(backup.read())
        os.remove(backup_path)  # Limpiar backup temporal
        return True
    except Exception as e:
        console.print(f"❌ Error restaurando backup: {e}", style="red")
        return False


@click.group()
@click.version_option(version="0.1.0")
@click.option("--verbose", "-v", is_flag=True, help="Modo verbose")
@click.option("--dry-run", is_flag=True, help="Simular sin ejecutar")
def main(verbose, dry_run):
    """Surgical Modifier - Sistema de Modificación Precisa de Código."""
    if verbose:
        print("Modo verbose activado")
    if dry_run:
        print("Modo dry-run activado")


@main.command()
@click.argument("filepath")
@click.argument("content", required=False, default="")
@click.option("--template", help="Tipo de template a usar")
@click.option("--from-stdin", is_flag=True, help="Leer contenido desde stdin")
def create(filepath, content, template, from_stdin):
    """Crear nuevos archivos con contenido directo o templates."""
    try:
        # Validar que no se usen ambas opciones
        if content and from_stdin:
            click.echo("Error: No se puede usar contenido directo y --from-stdin simultáneamente", err=True)
            return
            
        # Leer desde stdin si se especifica
        if from_stdin:
            content = sys.stdin.read()
            
        # Crear directorio padre si no existe
        filepath_obj = Path(filepath)
        filepath_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Verificar si archivo existe
        if filepath_obj.exists():
            click.echo(f"Error: El archivo {filepath} ya existe", err=True)
            return
            
        # Escribir archivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        click.echo(f"✅ Archivo {filepath} creado exitosamente")
        
    except Exception as e:
        click.echo(f"Error creando archivo: {e}", err=True)


@main.command()
@click.argument("filepath")
@click.argument("pattern")
@click.argument("replacement")
@click.option("--fuzzy", is_flag=True, help="Usar matching aproximado")
@click.option("--regex", is_flag=True, help="Usar patrones regex") 
@click.option("--threshold", type=float, default=0.8, help="Threshold fuzzy (0.0-1.0)")
def replace(filepath, pattern, replacement, fuzzy=False, regex=False, threshold=0.8):
    """Reemplazar contenido en archivos usando ReplaceCoordinator."""
    try:
        # Determinar tipo de matcher basado en opciones
        matcher_type = 'literal'  # default
        matcher_options = {}

        if fuzzy:
            matcher_type = 'fuzzy'
            matcher_options['threshold'] = threshold
        elif regex:
            matcher_type = 'regex'

        # Agregar matcher_type a matcher_options
        matcher_options['matcher_type'] = matcher_type

        # Usar ReplaceCoordinator para ejecutar replace real
        coordinator = ReplaceCoordinator()
        result = coordinator.execute(
            file_path=filepath,
            pattern=pattern,
            replacement=replacement,
            **matcher_options
        )

        if result.get('success'):
            click.echo(f"✅ Reemplazo exitoso en {filepath}")
            if result.get('matches_count'):
                click.echo(f"📊 Coincidencias reemplazadas: {result['matches_count']}")
        else:
            click.echo(f"❌ Error: {result.get('error', 'Unknown error')}", err=True)
            return 1

    except Exception as e:
        click.echo(f"❌ Error inesperado: {str(e)}", err=True)
        return 1


@main.command()
@click.argument("filepath")
@click.argument("pattern")
@click.argument("content", required=False, default="")
@click.option('--from-stdin', is_flag=True, help='Leer contenido desde stdin para contenido multilínea')
def before(filepath, pattern, content, from_stdin):
    """Insertar contenido antes de un patrón."""
    # Si --from-stdin está activado, leer contenido desde stdin
    if from_stdin:
        content = sys.stdin.read().strip()
    
    # PRE-VALIDACIÓN: Validar inserción en clases
    validated_content = validate_class_insertion(pattern, content)
    
    # BACKUP: Crear backup antes de modificación
    backup_path = None
    if os.path.exists(filepath):
        backup_path = backup_file(filepath)
        if not backup_path:
            console.print("❌ Error creando backup, abortando operación", style="red")
            sys.exit(1)
    
    try:
        coordinator = BeforeCoordinator()
        result = coordinator.execute(filepath, pattern, validated_content)
        
        if result.get('success', False):
            # POST-VALIDACIÓN: Verificar sintaxis si es archivo Python
            if filepath.endswith('.py'):
                try:
                    py_compile.compile(filepath, doraise=True)
                    # Sintaxis válida - limpiar backup
                    if backup_path:
                        os.remove(backup_path)
                    console.print(f"✅ Contenido insertado antes de '{pattern}' en {filepath}", style="green")
                    if result.get('message'):
                        console.print(f"📝 {result['message']}", style="blue")
                except py_compile.PyCompileError as syntax_error:
                    # Sintaxis inválida - hacer rollback
                    console.print(f"❌ Error de sintaxis detectado tras modificación", style="red")
                    console.print(f"📝 {str(syntax_error)}", style="yellow")
                    if backup_path:
                        if restore_from_backup(filepath, backup_path):
                            console.print("🔄 Archivo restaurado desde backup", style="cyan")
                        else:
                            console.print("❌ Error restaurando backup", style="red")
                    sys.exit(1)
            else:
                # No es archivo Python - limpiar backup
                if backup_path:
                    os.remove(backup_path)
                console.print(f"✅ Contenido insertado antes de '{pattern}' en {filepath}", style="green")
                if result.get('message'):
                    console.print(f"📝 {result['message']}", style="blue")
        else:
            # Operación falló - restaurar backup si existe
            console.print(f"❌ Error: {result.get('error', 'Operación fallida')}", style="red")
            if backup_path:
                restore_from_backup(filepath, backup_path)
            sys.exit(1)
            
    except Exception as e:
        # Excepción inesperada - restaurar backup si existe
        console.print(f"❌ Error ejecutando operación before: {str(e)}", style="red")
        if backup_path:
            restore_from_backup(filepath, backup_path)
        sys.exit(1)


@main.command()
@click.argument("filepath")
@click.argument("pattern")
@click.argument("content", required=False, default="")
@click.option('--from-stdin', is_flag=True, help='Leer contenido desde stdin para contenido multilínea')
def after(filepath, pattern, content, from_stdin):
    """Insertar contenido después de un patrón."""
    # Si --from-stdin está activado, leer contenido desde stdin
    if from_stdin:
        content = sys.stdin.read().strip()
    
    # PRE-VALIDACIÓN: Validar inserción en clases
    validated_content = validate_class_insertion(pattern, content)
    
    # BACKUP: Crear backup antes de modificación
    backup_path = None
    if os.path.exists(filepath):
        backup_path = backup_file(filepath)
        if not backup_path:
            click.echo("❌ Error creando backup, abortando operación", err=True)
            return 1
    
    try:
        coordinator = AfterCoordinator()
        result = coordinator.execute(filepath, pattern, validated_content)
        
        if result.get('success', False):
            # POST-VALIDACIÓN: Verificar sintaxis si es archivo Python
            if filepath.endswith('.py'):
                try:
                    py_compile.compile(filepath, doraise=True)
                    # Sintaxis válida - limpiar backup
                    if backup_path:
                        os.remove(backup_path)
                    click.echo(f"✅ Contenido insertado exitosamente después de '{pattern}' en {filepath}")
                    return 0
                except py_compile.PyCompileError as syntax_error:
                    # Sintaxis inválida - hacer rollback
                    click.echo(f"❌ Error de sintaxis detectado tras modificación", err=True)
                    click.echo(f"📝 {str(syntax_error)}", err=True)
                    if backup_path:
                        if restore_from_backup(filepath, backup_path):
                            click.echo("🔄 Archivo restaurado desde backup", err=True)
                        else:
                            click.echo("❌ Error restaurando backup", err=True)
                    return 1
            else:
                # No es archivo Python - limpiar backup
                if backup_path:
                    os.remove(backup_path)
                click.echo(f"✅ Contenido insertado exitosamente después de '{pattern}' en {filepath}")
                return 0
        else:
            # Operación falló - restaurar backup si existe
            error_msg = result.get('error', 'Error desconocido')
            click.echo(f"❌ Error: {error_msg}", err=True)
            if backup_path:
                restore_from_backup(filepath, backup_path)
            return 1
            
    except Exception as e:
        # Excepción inesperada - restaurar backup si existe
        click.echo(f"❌ Error inesperado: {str(e)}", err=True)
        if backup_path:
            restore_from_backup(filepath, backup_path)
        return 1


@main.command()
@click.argument("path")
@click.option("--analyze", is_flag=True, help="Analizar estructura")
def explore(path, analyze):
    """Explorar y analizar estructura de código."""
    print(f"Explorando {path} (análisis: {analyze})")


@main.command("list-commands")
def list_commands():
    """Listar todos los comandos disponibles."""
    print("Comandos disponibles:")
    print("  - create")
    print("  - replace") 
    print("  - before")
    print("  - after")
    print("  - explore")
    print("  - list-commands")


if __name__ == "__main__":
    main()